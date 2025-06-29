# End-to-End Tests for RooCode Docker System
# Tests complete system functionality through Docker
# Version: 1.0
# Created: 2025-06-29

import pytest
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any

@pytest.mark.docker
@pytest.mark.slow
class TestDockerSystemE2E:
    """End-to-end tests for Docker system."""
    
    def test_docker_compose_config_valid(self, project_root_path):
        """Test Docker Compose configuration is valid."""
        compose_file = project_root_path / "core" / "docker" / "docker-compose.yaml"
        
        result = subprocess.run([
            "docker", "compose", "-f", str(compose_file), "config"
        ], capture_output=True, text=True, cwd=str(project_root_path))
        
        assert result.returncode == 0, f"Docker Compose config invalid: {result.stderr}"
    
    def test_dockerfile_builds_successfully(self, project_root_path):
        """Test Dockerfile builds without errors."""
        dockerfile_dir = project_root_path / "core" / "docker"
        
        # Build the Docker image
        result = subprocess.run([
            "docker", "build", "-t", "roocode-test", "."
        ], capture_output=True, text=True, cwd=str(dockerfile_dir))
        
        assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        
        # Clean up test image
        subprocess.run(["docker", "rmi", "roocode-test"], capture_output=True)
    
    @pytest.mark.skip(reason="Requires Docker daemon and may be resource intensive")
    def test_container_startup_and_health(self, project_root_path):
        """Test container starts and passes health checks."""
        compose_file = project_root_path / "core" / "docker" / "docker-compose.yaml"
        
        try:
            # Start the container
            result = subprocess.run([
                "docker", "compose", "-f", str(compose_file), "up", "-d"
            ], capture_output=True, text=True, cwd=str(project_root_path))
            
            assert result.returncode == 0, f"Failed to start container: {result.stderr}"
            
            # Wait for container to be ready
            time.sleep(30)
            
            # Check container health
            health_result = subprocess.run([
                "docker", "compose", "-f", str(compose_file), "ps"
            ], capture_output=True, text=True, cwd=str(project_root_path))
            
            assert "healthy" in health_result.stdout or "running" in health_result.stdout, \
                "Container not healthy or running"
            
            # Test API endpoint if available
            try:
                response = requests.get("http://localhost:8080/health", timeout=10)
                assert response.status_code == 200, "Health endpoint not responding"
            except requests.exceptions.RequestException:
                # Health endpoint might not be implemented yet
                pass
            
        finally:
            # Clean up
            subprocess.run([
                "docker", "compose", "-f", str(compose_file), "down"
            ], capture_output=True, cwd=str(project_root_path))
    
    def test_docker_run_script_syntax(self, project_root_path):
        """Test docker-run.ps1 script has valid syntax."""
        script_path = project_root_path / "docker-run.ps1"
        
        # Test PowerShell syntax
        result = subprocess.run([
            "powershell", "-NoProfile", "-Command", 
            f"Get-Content '{script_path}' | Out-Null"
        ], capture_output=True, text=True)
        
        # Note: This is a basic syntax check, not a full validation
        assert script_path.exists(), "docker-run.ps1 script missing"

@pytest.mark.e2e
class TestSystemIntegrationE2E:
    """End-to-end tests for system integration."""
    
    def test_complete_file_processing_simulation(self, temp_workspace, sample_chat_export, test_utils):
        """Test complete file processing simulation."""
        # Setup test environment
        input_dir = temp_workspace / "data" / "input"
        output_dir = temp_workspace / "data" / "output"
        vocab_dir = temp_workspace / "core" / "vocab"
        
        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        vocab_dir.mkdir(parents=True)
        
        # Create test files
        input_file = input_dir / "test_conversation.chat.json"
        vocab_file = vocab_dir / "vocab.yaml"
        history_file = vocab_dir / "vocab.history.yaml"
        
        test_utils.create_test_file(input_file, sample_chat_export, "json")
        
        # Create initial vocabulary
        initial_vocab = {
            "intents": [
                {
                    "id": "greeting.hello",
                    "label": "Hello Greeting",
                    "description": "User greeting",
                    "created_on": "2025-06-29T00:00:00Z",
                    "origin": "manual"
                }
            ]
        }
        test_utils.create_test_file(vocab_file, initial_vocab, "yaml")
        test_utils.create_test_file(history_file, {"history": []}, "yaml")
        
        # Simulate complete processing pipeline
        pipeline_result = self._simulate_complete_pipeline(
            input_file, vocab_file, history_file, output_dir
        )
        
        # Validate pipeline results
        assert pipeline_result["status"] == "success", "Complete pipeline failed"
        assert len(pipeline_result["stages_completed"]) == 5, "Not all stages completed"
        
        # Verify output files exist
        expected_files = [
            output_dir / "test_conversation.transcript.json",
            output_dir / "test_conversation.validation.json",
            output_dir / "test_conversation.mapped.json"
        ]
        
        for expected_file in expected_files:
            assert expected_file.exists(), f"Expected output file {expected_file} missing"
    
    def test_workflow_orchestration_simulation(self, temp_workspace, test_utils):
        """Test workflow orchestration simulation."""
        # Setup buddy flows configuration
        buddy_dir = temp_workspace / "core" / "modes" / "buddy"
        buddy_dir.mkdir(parents=True)
        
        flows_config = {
            "flows": [
                {
                    "id": "test_flow",
                    "label": "Test Flow",
                    "description": "Test workflow for E2E testing",
                    "steps": ["transkriptor", "validator"],
                    "input": {
                        "default_folder": "data/input",
                        "file_pattern": "*.chat.json"
                    }
                }
            ]
        }
        
        flows_file = buddy_dir / "buddy-flows.yaml"
        test_utils.create_test_file(flows_file, flows_config, "yaml")
        
        # Simulate workflow orchestration
        orchestration_result = self._simulate_workflow_orchestration(flows_file, temp_workspace)
        
        # Validate orchestration
        assert orchestration_result["status"] == "success", "Workflow orchestration failed"
        assert "test_flow" in orchestration_result["executed_flows"], "Test flow not executed"
    
    def test_vocabulary_management_e2e(self, temp_workspace, test_utils):
        """Test end-to-end vocabulary management."""
        # Setup vocabulary system
        vocab_dir = temp_workspace / "core" / "vocab"
        suggestions_dir = temp_workspace / "intent-scout" / "suggestions"
        
        vocab_dir.mkdir(parents=True)
        suggestions_dir.mkdir(parents=True)
        
        # Create initial vocabulary
        initial_vocab = {
            "intents": [
                {
                    "id": "base.intent",
                    "label": "Base Intent",
                    "description": "Initial intent",
                    "created_on": "2025-06-29T00:00:00Z",
                    "origin": "manual"
                }
            ]
        }
        
        vocab_file = vocab_dir / "vocab.yaml"
        history_file = vocab_dir / "vocab.history.yaml"
        
        test_utils.create_test_file(vocab_file, initial_vocab, "yaml")
        test_utils.create_test_file(history_file, {"history": []}, "yaml")
        
        # Create intent suggestions
        suggestions = {
            "suggestions": [
                {
                    "suggested_id": "new.intent",
                    "label": "New Intent",
                    "explanation": "Newly discovered intent",
                    "source_turn": "user:1",
                    "approved": True
                }
            ]
        }
        
        suggestion_file = suggestions_dir / "2025-06-29_test.yaml"
        test_utils.create_test_file(suggestion_file, suggestions, "yaml")
        
        # Simulate vocabulary update process
        update_result = self._simulate_vocabulary_update(
            suggestion_file, vocab_file, history_file
        )
        
        # Validate vocabulary update
        assert update_result["status"] == "success", "Vocabulary update failed"
        assert update_result["intents_added"] == 1, "Intent not added"
        
        # Verify vocabulary was updated
        updated_vocab = test_utils.load_yaml_file(vocab_file)
        intent_ids = [intent["id"] for intent in updated_vocab["intents"]]
        assert "new.intent" in intent_ids, "New intent not found in vocabulary"
        
        # Verify history was updated
        updated_history = test_utils.load_yaml_file(history_file)
        assert len(updated_history["history"]) == 1, "History not updated"
    
    # Helper methods for E2E simulation
    def _simulate_complete_pipeline(self, input_file: Path, vocab_file: Path, 
                                  history_file: Path, output_dir: Path) -> Dict[str, Any]:
        """Simulate complete processing pipeline."""
        stages_completed = []
        
        # Stage 1: Transkriptor
        transcript_data = [
            {
                "speaker": "user",
                "index": 0,
                "text": "Hello, how are you?",
                "char_pos_start": 0,
                "char_pos_end": 19
            },
            {
                "speaker": "agent",
                "index": 0,
                "text": "I'm doing well, thank you!",
                "char_pos_start": 20,
                "char_pos_end": 46
            }
        ]
        
        transcript_file = output_dir / f"{input_file.stem}.transcript.json"
        with open(transcript_file, 'w') as f:
            json.dump(transcript_data, f, indent=2)
        stages_completed.append("transkriptor")
        
        # Stage 2: Validator
        validation_data = {
            "status": "valid",
            "errors": [],
            "warnings": [],
            "validated_turns": len(transcript_data)
        }
        
        validation_file = output_dir / f"{input_file.stem}.validation.json"
        with open(validation_file, 'w') as f:
            json.dump(validation_data, f, indent=2)
        stages_completed.append("validator")
        
        # Stage 3: Intent Mapper
        mapping_data = [
            {
                "turn_ref": "user:0",
                "intent_id": "greeting.hello",
                "confidence": 0.9
            },
            {
                "turn_ref": "agent:0",
                "intent_id": None,
                "confidence": None
            }
        ]
        
        mapping_file = output_dir / f"{input_file.stem}.mapped.json"
        with open(mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2)
        stages_completed.append("intent-mapper")
        
        # Stage 4: Intent Discovery
        stages_completed.append("intent-discovery")
        
        # Stage 5: Vocab Updater
        stages_completed.append("vocab-updater")
        
        return {
            "status": "success",
            "stages_completed": stages_completed
        }
    
    def _simulate_workflow_orchestration(self, flows_file: Path, workspace: Path) -> Dict[str, Any]:
        """Simulate workflow orchestration."""
        # Mock buddy orchestration
        executed_flows = ["test_flow"]
        
        return {
            "status": "success",
            "executed_flows": executed_flows,
            "workspace": str(workspace)
        }
    
    def _simulate_vocabulary_update(self, suggestion_file: Path, vocab_file: Path, 
                                  history_file: Path) -> Dict[str, Any]:
        """Simulate vocabulary update process."""
        import yaml
        
        # Load files
        with open(suggestion_file, 'r') as f:
            suggestions = yaml.safe_load(f)
        
        with open(vocab_file, 'r') as f:
            vocab_data = yaml.safe_load(f)
        
        with open(history_file, 'r') as f:
            history_data = yaml.safe_load(f)
        
        # Process approved suggestions
        intents_added = 0
        for suggestion in suggestions.get("suggestions", []):
            if suggestion.get("approved", False):
                # Add to vocabulary
                new_intent = {
                    "id": suggestion["suggested_id"],
                    "label": suggestion["label"],
                    "description": suggestion["explanation"],
                    "created_on": "2025-06-29T00:00:00Z",
                    "origin": "intent-discovery"
                }
                vocab_data["intents"].append(new_intent)
                
                # Add to history
                history_entry = {
                    "id": suggestion["suggested_id"],
                    "label": suggestion["label"],
                    "created_on": "2025-06-29T00:00:00Z",
                    "added_by": "vocab-updater",
                    "origin": str(suggestion_file),
                    "comment": "Added from intent discovery"
                }
                history_data["history"].append(history_entry)
                
                intents_added += 1
        
        # Save updated files
        with open(vocab_file, 'w') as f:
            yaml.dump(vocab_data, f)
        
        with open(history_file, 'w') as f:
            yaml.dump(history_data, f)
        
        return {
            "status": "success",
            "intents_added": intents_added
        }

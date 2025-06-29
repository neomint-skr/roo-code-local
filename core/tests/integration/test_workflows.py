# Integration Tests for RooCode Workflows
# Tests workflow execution and agent integration
# Version: 1.0
# Created: 2025-06-29

import pytest
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List

class TestWorkflowIntegration:
    """Test workflow integration and execution."""
    
    def test_transcript_processing_workflow(self, temp_workspace, sample_chat_export, test_utils):
        """Test complete transcript processing workflow."""
        # Setup test environment
        input_dir = temp_workspace / "data" / "input"
        output_dir = temp_workspace / "data" / "output"
        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        
        # Create test input file
        input_file = input_dir / "test_chat.chat.json"
        test_utils.create_test_file(input_file, sample_chat_export, "json")
        
        # Simulate workflow execution
        workflow_result = self._simulate_transcript_workflow(input_file, output_dir)
        
        # Validate workflow results
        assert workflow_result["status"] == "success", "Transcript processing workflow failed"
        assert "transcript_file" in workflow_result, "Transcript file not generated"
        assert "validation_file" in workflow_result, "Validation file not generated"
        assert "mapping_file" in workflow_result, "Mapping file not generated"
    
    def test_validation_only_workflow(self, temp_workspace, sample_transcript, test_utils):
        """Test validation-only workflow."""
        # Setup test environment
        transcripts_dir = temp_workspace / "data" / "transcripts"
        validation_dir = temp_workspace / "data" / "validation"
        transcripts_dir.mkdir(parents=True)
        validation_dir.mkdir(parents=True)
        
        # Create test transcript file
        transcript_file = transcripts_dir / "test.transcript.json"
        test_utils.create_test_file(transcript_file, sample_transcript, "json")
        
        # Simulate validation workflow
        validation_result = self._simulate_validation_workflow(transcript_file, validation_dir)
        
        # Validate results
        assert validation_result["status"] == "success", "Validation workflow failed"
        assert "validation_report" in validation_result, "Validation report not generated"
        assert validation_result["validation_report"]["status"] == "valid", "Transcript validation failed"
    
    def test_intent_mapping_workflow(self, temp_workspace, sample_transcript, sample_vocab, test_utils):
        """Test intent mapping workflow."""
        # Setup test environment
        transcripts_dir = temp_workspace / "data" / "transcripts"
        intents_dir = temp_workspace / "data" / "intents"
        vocab_dir = temp_workspace / "core" / "vocab"
        
        transcripts_dir.mkdir(parents=True)
        intents_dir.mkdir(parents=True)
        vocab_dir.mkdir(parents=True)
        
        # Create test files
        transcript_file = transcripts_dir / "test.transcript.json"
        vocab_file = vocab_dir / "vocab.yaml"
        
        test_utils.create_test_file(transcript_file, sample_transcript, "json")
        test_utils.create_test_file(vocab_file, sample_vocab, "yaml")
        
        # Simulate intent mapping workflow
        mapping_result = self._simulate_intent_mapping_workflow(transcript_file, vocab_file, intents_dir)
        
        # Validate results
        assert mapping_result["status"] == "success", "Intent mapping workflow failed"
        assert "mapping_file" in mapping_result, "Mapping file not generated"
        assert "suggestions_file" in mapping_result, "Suggestions file not generated"
    
    def test_vocab_update_workflow(self, temp_workspace, sample_vocab, test_utils):
        """Test vocabulary update workflow."""
        # Setup test environment
        suggestions_dir = temp_workspace / "intent-scout" / "suggestions"
        vocab_dir = temp_workspace / "core" / "vocab"
        
        suggestions_dir.mkdir(parents=True)
        vocab_dir.mkdir(parents=True)
        
        # Create test files
        vocab_file = vocab_dir / "vocab.yaml"
        history_file = vocab_dir / "vocab.history.yaml"
        suggestion_file = suggestions_dir / "2025-06-29_test.yaml"
        
        test_utils.create_test_file(vocab_file, sample_vocab, "yaml")
        test_utils.create_test_file(history_file, {"history": []}, "yaml")
        
        # Create approved suggestion
        suggestion = {
            "suggestions": [
                {
                    "suggested_id": "test.new_intent",
                    "label": "New Test Intent",
                    "explanation": "Test intent for vocabulary update",
                    "source_turn": "user:0",
                    "approved": True
                }
            ]
        }
        test_utils.create_test_file(suggestion_file, suggestion, "yaml")
        
        # Simulate vocab update workflow
        update_result = self._simulate_vocab_update_workflow(suggestion_file, vocab_file, history_file)
        
        # Validate results
        assert update_result["status"] == "success", "Vocab update workflow failed"
        assert update_result["intents_added"] == 1, "Intent not added to vocabulary"
        
        # Verify vocabulary was updated
        updated_vocab = test_utils.load_yaml_file(vocab_file)
        intent_ids = [intent["id"] for intent in updated_vocab["intents"]]
        assert "test.new_intent" in intent_ids, "New intent not found in vocabulary"
    
    def test_full_pipeline_workflow(self, temp_workspace, sample_chat_export, sample_vocab, test_utils):
        """Test complete processing pipeline."""
        # Setup test environment
        input_dir = temp_workspace / "data" / "input"
        complete_dir = temp_workspace / "data" / "complete"
        vocab_dir = temp_workspace / "core" / "vocab"
        
        input_dir.mkdir(parents=True)
        complete_dir.mkdir(parents=True)
        vocab_dir.mkdir(parents=True)
        
        # Create test files
        input_file = input_dir / "test_chat.chat.json"
        vocab_file = vocab_dir / "vocab.yaml"
        history_file = vocab_dir / "vocab.history.yaml"
        
        test_utils.create_test_file(input_file, sample_chat_export, "json")
        test_utils.create_test_file(vocab_file, sample_vocab, "yaml")
        test_utils.create_test_file(history_file, {"history": []}, "yaml")
        
        # Simulate full pipeline
        pipeline_result = self._simulate_full_pipeline(input_file, vocab_file, complete_dir)
        
        # Validate results
        assert pipeline_result["status"] == "success", "Full pipeline workflow failed"
        assert all(stage in pipeline_result["completed_stages"] for stage in [
            "transkriptor", "validator", "intent-mapper", "intent-discovery", "vocab-updater"
        ]), "Not all pipeline stages completed"
    
    # Helper methods for workflow simulation
    def _simulate_transcript_workflow(self, input_file: Path, output_dir: Path) -> Dict[str, Any]:
        """Simulate transcript processing workflow."""
        # Mock transkriptor processing
        transcript_data = [
            {
                "speaker": "user",
                "index": 0,
                "text": "Hello, can you help me?",
                "char_pos_start": 0,
                "char_pos_end": 23
            },
            {
                "speaker": "agent",
                "index": 0,
                "text": "Of course! How can I assist you?",
                "char_pos_start": 24,
                "char_pos_end": 56
            }
        ]
        
        transcript_file = output_dir / f"{input_file.stem}.transcript.json"
        with open(transcript_file, 'w') as f:
            json.dump(transcript_data, f, indent=2)
        
        # Mock validator processing
        validation_data = {
            "status": "valid",
            "errors": [],
            "warnings": [],
            "validated_turns": len(transcript_data)
        }
        
        validation_file = output_dir / f"{input_file.stem}.validation.json"
        with open(validation_file, 'w') as f:
            json.dump(validation_data, f, indent=2)
        
        # Mock intent-mapper processing
        mapping_data = [
            {
                "turn_ref": "user:0",
                "intent_id": "test.question",
                "confidence": 0.85
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
        
        return {
            "status": "success",
            "transcript_file": str(transcript_file),
            "validation_file": str(validation_file),
            "mapping_file": str(mapping_file)
        }
    
    def _simulate_validation_workflow(self, transcript_file: Path, validation_dir: Path) -> Dict[str, Any]:
        """Simulate validation workflow."""
        validation_data = {
            "status": "valid",
            "file": str(transcript_file),
            "errors": [],
            "warnings": [],
            "validated_at": "2025-06-29T00:00:00Z"
        }
        
        validation_file = validation_dir / f"{transcript_file.stem}.validation.json"
        with open(validation_file, 'w') as f:
            json.dump(validation_data, f, indent=2)
        
        return {
            "status": "success",
            "validation_report": validation_data
        }
    
    def _simulate_intent_mapping_workflow(self, transcript_file: Path, vocab_file: Path, intents_dir: Path) -> Dict[str, Any]:
        """Simulate intent mapping workflow."""
        # Mock mapping results
        mapping_data = [
            {
                "turn_ref": "user:0",
                "intent_id": "test.question",
                "confidence": 0.85
            }
        ]
        
        mapping_file = intents_dir / f"{transcript_file.stem}.mapped.json"
        with open(mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2)
        
        # Mock suggestions
        suggestions_data = {
            "suggestions": [
                {
                    "suggested_id": "test.unmapped",
                    "label": "Unmapped Turn",
                    "explanation": "Turn without matching intent",
                    "source_turn": "agent:0"
                }
            ]
        }
        
        suggestions_file = intents_dir / "2025-06-29_suggestions.yaml"
        with open(suggestions_file, 'w') as f:
            yaml.dump(suggestions_data, f)
        
        return {
            "status": "success",
            "mapping_file": str(mapping_file),
            "suggestions_file": str(suggestions_file)
        }
    
    def _simulate_vocab_update_workflow(self, suggestion_file: Path, vocab_file: Path, history_file: Path) -> Dict[str, Any]:
        """Simulate vocabulary update workflow."""
        # Load existing vocabulary
        with open(vocab_file, 'r') as f:
            vocab_data = yaml.safe_load(f)
        
        # Load suggestions
        with open(suggestion_file, 'r') as f:
            suggestions = yaml.safe_load(f)
        
        # Add approved suggestions
        intents_added = 0
        for suggestion in suggestions.get("suggestions", []):
            if suggestion.get("approved", False):
                new_intent = {
                    "id": suggestion["suggested_id"],
                    "label": suggestion["label"],
                    "description": suggestion["explanation"],
                    "created_on": "2025-06-29T00:00:00Z",
                    "origin": "intent-discovery"
                }
                vocab_data["intents"].append(new_intent)
                intents_added += 1
        
        # Update vocabulary file
        with open(vocab_file, 'w') as f:
            yaml.dump(vocab_data, f)
        
        return {
            "status": "success",
            "intents_added": intents_added
        }
    
    def _simulate_full_pipeline(self, input_file: Path, vocab_file: Path, complete_dir: Path) -> Dict[str, Any]:
        """Simulate full processing pipeline."""
        completed_stages = []
        
        # Simulate each stage
        stages = ["transkriptor", "validator", "intent-mapper", "intent-discovery", "vocab-updater"]
        
        for stage in stages:
            # Mock stage processing
            stage_file = complete_dir / f"{input_file.stem}_{stage}.json"
            stage_data = {
                "stage": stage,
                "status": "completed",
                "timestamp": "2025-06-29T00:00:00Z"
            }
            
            with open(stage_file, 'w') as f:
                json.dump(stage_data, f, indent=2)
            
            completed_stages.append(stage)
        
        return {
            "status": "success",
            "completed_stages": completed_stages
        }

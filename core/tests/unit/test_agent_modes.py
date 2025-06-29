# Unit Tests for RooCode Agent Modes
# Tests individual agent mode configurations and functionality
# Version: 1.0
# Created: 2025-06-29

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any

class TestAgentModeConfigurations:
    """Test agent mode configuration files."""
    
    def test_buddy_mode_configuration(self, project_root_path):
        """Test buddy mode configuration is valid."""
        buddy_config_path = project_root_path / "core" / "modes" / "mode.buddy.yaml"
        assert buddy_config_path.exists(), "Buddy mode configuration file missing"
        
        with open(buddy_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["slug", "agent", "description", "version", "model_source", "tools"]
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing in buddy mode config"
        
        # Validate specific values
        assert config["slug"] == "buddy", "Buddy mode slug incorrect"
        assert config["agent"] == "buddy", "Buddy mode agent incorrect"
        assert "tools" in config and len(config["tools"]) > 0, "Buddy mode tools not configured"
    
    def test_transkriptor_mode_configuration(self, project_root_path):
        """Test transkriptor mode configuration is valid."""
        transkriptor_config_path = project_root_path / "core" / "modes" / "mode.transkriptor.yaml"
        assert transkriptor_config_path.exists(), "Transkriptor mode configuration file missing"
        
        with open(transkriptor_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["slug", "agent", "description", "version"]
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing in transkriptor mode config"
        
        assert config["slug"] == "transkriptor", "Transkriptor mode slug incorrect"
    
    def test_validator_mode_configuration(self, project_root_path):
        """Test validator mode configuration is valid."""
        validator_config_path = project_root_path / "core" / "modes" / "validator" / "mode.validator.yaml"
        assert validator_config_path.exists(), "Validator mode configuration file missing"
        
        with open(validator_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["slug", "agent", "description", "tools"]
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing in validator mode config"
        
        assert config["slug"] == "validator", "Validator mode slug incorrect"
    
    def test_intent_mapper_mode_configuration(self, project_root_path):
        """Test intent-mapper mode configuration is valid."""
        intent_mapper_config_path = project_root_path / "core" / "modes" / "intent-mapper" / "mode.intent-mapper.yaml"
        assert intent_mapper_config_path.exists(), "Intent-mapper mode configuration file missing"
        
        with open(intent_mapper_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["slug", "agent", "description", "vocabulary_integration"]
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing in intent-mapper mode config"
        
        assert config["slug"] == "intent-mapper", "Intent-mapper mode slug incorrect"
    
    def test_intent_discovery_mode_configuration(self, project_root_path):
        """Test intent-discovery mode configuration is valid."""
        intent_discovery_config_path = project_root_path / "core" / "modes" / "intent-discovery" / "mode.intent-discovery.yaml"
        assert intent_discovery_config_path.exists(), "Intent-discovery mode configuration file missing"
        
        with open(intent_discovery_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["slug", "agent", "description", "suggestion_structure"]
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing in intent-discovery mode config"
        
        assert config["slug"] == "intent-discovery", "Intent-discovery mode slug incorrect"
    
    def test_vocab_updater_mode_configuration(self, project_root_path):
        """Test vocab-updater mode configuration is valid."""
        vocab_updater_config_path = project_root_path / "core" / "modes" / "vocab-updater" / "mode.vocab-updater.yaml"
        assert vocab_updater_config_path.exists(), "Vocab-updater mode configuration file missing"
        
        with open(vocab_updater_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ["slug", "agent", "description", "vocabulary_update"]
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing in vocab-updater mode config"
        
        assert config["slug"] == "vocab-updater", "Vocab-updater mode slug incorrect"

class TestBuddyWorkflows:
    """Test buddy workflow configurations."""
    
    def test_buddy_flows_configuration(self, project_root_path):
        """Test buddy flows configuration is valid."""
        buddy_flows_path = project_root_path / "core" / "modes" / "buddy" / "buddy-flows.yaml"
        assert buddy_flows_path.exists(), "Buddy flows configuration file missing"
        
        with open(buddy_flows_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate structure
        assert "flows" in config, "Flows section missing in buddy-flows.yaml"
        assert len(config["flows"]) > 0, "No flows defined in buddy-flows.yaml"
        
        # Validate each flow
        for flow in config["flows"]:
            required_flow_fields = ["id", "label", "description", "steps"]
            for field in required_flow_fields:
                assert field in flow, f"Required field '{field}' missing in flow"
            
            assert len(flow["steps"]) > 0, f"Flow '{flow['id']}' has no steps defined"
    
    def test_workflow_mode_references(self, project_root_path):
        """Test that all workflow steps reference valid modes."""
        buddy_flows_path = project_root_path / "core" / "modes" / "buddy" / "buddy-flows.yaml"
        modes_dir = project_root_path / "core" / "modes"
        
        with open(buddy_flows_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Get all available mode slugs
        available_modes = set()
        
        # Check direct mode files
        for mode_file in modes_dir.glob("mode.*.yaml"):
            with open(mode_file, 'r', encoding='utf-8') as f:
                mode_config = yaml.safe_load(f)
                if "slug" in mode_config:
                    available_modes.add(mode_config["slug"])
        
        # Check mode subdirectories
        for mode_dir in modes_dir.iterdir():
            if mode_dir.is_dir():
                mode_file = mode_dir / f"mode.{mode_dir.name}.yaml"
                if mode_file.exists():
                    with open(mode_file, 'r', encoding='utf-8') as f:
                        mode_config = yaml.safe_load(f)
                        if "slug" in mode_config:
                            available_modes.add(mode_config["slug"])
        
        # Validate workflow references
        for flow in config["flows"]:
            for step in flow["steps"]:
                assert step in available_modes, f"Flow '{flow['id']}' references unknown mode '{step}'"

class TestModeValidation:
    """Test mode validation logic."""
    
    def test_mode_slug_uniqueness(self, project_root_path):
        """Test that all mode slugs are unique."""
        modes_dir = project_root_path / "core" / "modes"
        mode_slugs = []
        
        # Collect all mode slugs
        for mode_file in modes_dir.glob("mode.*.yaml"):
            with open(mode_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if "slug" in config:
                    mode_slugs.append(config["slug"])
        
        for mode_dir in modes_dir.iterdir():
            if mode_dir.is_dir():
                mode_file = mode_dir / f"mode.{mode_dir.name}.yaml"
                if mode_file.exists():
                    with open(mode_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if "slug" in config:
                            mode_slugs.append(config["slug"])
        
        # Check for duplicates
        assert len(mode_slugs) == len(set(mode_slugs)), f"Duplicate mode slugs found: {mode_slugs}"
    
    def test_mode_agent_consistency(self, project_root_path):
        """Test that mode slug and agent names are consistent."""
        modes_dir = project_root_path / "core" / "modes"
        
        # Check direct mode files
        for mode_file in modes_dir.glob("mode.*.yaml"):
            with open(mode_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if "slug" in config and "agent" in config:
                    assert config["slug"] == config["agent"], f"Mode slug and agent mismatch in {mode_file}"
        
        # Check mode subdirectories
        for mode_dir in modes_dir.iterdir():
            if mode_dir.is_dir():
                mode_file = mode_dir / f"mode.{mode_dir.name}.yaml"
                if mode_file.exists():
                    with open(mode_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if "slug" in config and "agent" in config:
                            assert config["slug"] == config["agent"], f"Mode slug and agent mismatch in {mode_file}"

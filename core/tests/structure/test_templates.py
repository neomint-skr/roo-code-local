# Structure Tests for RooCode Templates and CI
# Tests template compliance and CI validation
# Version: 1.0
# Created: 2025-06-29

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List

class TestTemplateStructure:
    """Test template file structure and compliance."""
    
    def test_template_files_exist(self, project_root_path):
        """Test that all required template files exist."""
        templates_dir = project_root_path / "core" / "templates"
        
        required_templates = [
            "template.mode.yaml",
            "template.spec.yaml",
            "template.vocab-entry.yaml",
            "template.intent-suggestion.yaml",
            "template.buddy-flows.yaml",
            "template.llm-config.yaml"
        ]
        
        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Required template {template} missing"
    
    def test_mode_template_structure(self, project_root_path):
        """Test mode template has correct structure."""
        template_path = project_root_path / "core" / "templates" / "template.mode.yaml"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        required_fields = ["slug", "agent", "description", "version", "model_source", "tools"]
        for field in required_fields:
            assert field in template, f"Required field '{field}' missing in mode template"
    
    def test_spec_template_structure(self, project_root_path):
        """Test spec template has correct structure."""
        template_path = project_root_path / "core" / "templates" / "template.spec.yaml"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        required_fields = ["specification", "validation_rules", "constraints"]
        for field in required_fields:
            assert field in template, f"Required field '{field}' missing in spec template"
    
    def test_vocab_entry_template_structure(self, project_root_path):
        """Test vocabulary entry template has correct structure."""
        template_path = project_root_path / "core" / "templates" / "template.vocab-entry.yaml"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        required_fields = ["id", "label", "description", "created_on", "origin"]
        for field in required_fields:
            assert field in template, f"Required field '{field}' missing in vocab entry template"
    
    def test_intent_suggestion_template_structure(self, project_root_path):
        """Test intent suggestion template has correct structure."""
        template_path = project_root_path / "core" / "templates" / "template.intent-suggestion.yaml"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        required_fields = ["suggested_id", "label", "explanation", "source_turn"]
        for field in required_fields:
            assert field in template, f"Required field '{field}' missing in intent suggestion template"
    
    def test_buddy_flows_template_structure(self, project_root_path):
        """Test buddy flows template has correct structure."""
        template_path = project_root_path / "core" / "templates" / "template.buddy-flows.yaml"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        assert "flows" in template, "Flows section missing in buddy flows template"
        
        if template["flows"]:
            flow_template = template["flows"][0]
            required_flow_fields = ["id", "label", "description", "steps", "input"]
            for field in required_flow_fields:
                assert field in flow_template, f"Required field '{field}' missing in flow template"

class TestCIValidation:
    """Test CI validation system."""
    
    def test_ci_rules_file_exists(self, project_root_path):
        """Test CI rules file exists and is valid."""
        ci_rules_path = project_root_path / "core" / "ci" / "ci.rules.yaml"
        assert ci_rules_path.exists(), "CI rules file missing"
        
        with open(ci_rules_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        assert "validation_rules" in rules, "Validation rules section missing"
        assert "file_patterns" in rules, "File patterns section missing"
    
    def test_template_validator_exists(self, project_root_path):
        """Test template validator script exists."""
        validator_path = project_root_path / "core" / "ci" / "template_validator.py"
        assert validator_path.exists(), "Template validator script missing"
        
        # Check if it's a valid Python file
        with open(validator_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "def" in content, "Template validator appears to be empty or invalid"

class TestVocabularyStructure:
    """Test vocabulary system structure."""
    
    def test_vocab_file_structure(self, project_root_path):
        """Test vocabulary file has correct structure."""
        vocab_path = project_root_path / "core" / "vocab" / "vocab.yaml"
        assert vocab_path.exists(), "Vocabulary file missing"
        
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab = yaml.safe_load(f)
        
        assert "intents" in vocab, "Intents section missing in vocabulary"
        
        if vocab["intents"]:
            intent = vocab["intents"][0]
            required_fields = ["id", "label", "created_on", "origin"]
            for field in required_fields:
                assert field in intent, f"Required field '{field}' missing in vocabulary intent"
    
    def test_vocab_history_structure(self, project_root_path):
        """Test vocabulary history file has correct structure."""
        history_path = project_root_path / "core" / "vocab" / "vocab.history.yaml"
        assert history_path.exists(), "Vocabulary history file missing"
        
        with open(history_path, 'r', encoding='utf-8') as f:
            history = yaml.safe_load(f)
        
        assert "history" in history, "History section missing in vocabulary history"
        
        if history["history"]:
            entry = history["history"][0]
            required_fields = ["id", "label", "created_on", "added_by", "origin"]
            for field in required_fields:
                assert field in entry, f"Required field '{field}' missing in vocabulary history entry"
    
    def test_vocab_consistency(self, project_root_path):
        """Test vocabulary and history consistency."""
        vocab_path = project_root_path / "core" / "vocab" / "vocab.yaml"
        history_path = project_root_path / "core" / "vocab" / "vocab.history.yaml"
        
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab = yaml.safe_load(f)
        
        with open(history_path, 'r', encoding='utf-8') as f:
            history = yaml.safe_load(f)
        
        # Get all intent IDs from vocabulary
        vocab_ids = {intent["id"] for intent in vocab.get("intents", [])}
        
        # Get all intent IDs from history
        history_ids = {entry["id"] for entry in history.get("history", [])}
        
        # Check that every vocabulary entry has a history entry
        missing_in_history = vocab_ids - history_ids
        assert not missing_in_history, f"Vocabulary entries missing in history: {missing_in_history}"
        
        # Check that every history entry has a vocabulary entry
        missing_in_vocab = history_ids - vocab_ids
        assert not missing_in_vocab, f"History entries missing in vocabulary: {missing_in_vocab}"

class TestProjectStructure:
    """Test overall project structure compliance."""
    
    def test_roocode_directory_structure(self, project_root_path):
        """Test RooCode directory structure compliance."""
        required_dirs = [
            "core",
            "core/modes",
            "core/templates",
            "core/ci",
            "core/vocab",
            "core/config",
            "core/bootstrap",
            "core/docker",
            "core/tests",
            "core/history",
            "modules",
            "modules/llm-admin",
            "pim",
            "docs",
            "data/input",
            "data/output",
            "intent-scout/suggestions"
        ]
        
        for dir_path in required_dirs:
            full_path = project_root_path / dir_path
            assert full_path.exists(), f"Required directory {dir_path} missing"
            assert full_path.is_dir(), f"Path {dir_path} exists but is not a directory"
    
    def test_required_files_exist(self, project_root_path):
        """Test that all required files exist."""
        required_files = [
            "README.md",
            "requirements.txt",
            "LICENSE",
            "docker-run.ps1",
            "pim/tasks",
            "pim/status.yaml",
            "pim/templates/task.yaml",
            "core/config/llm.config.yaml",
            "core/vocab/vocab.yaml",
            "core/vocab/vocab.history.yaml",
            "core/modes/mode.buddy.yaml",
            "core/modes/mode.transkriptor.yaml",
            "core/modes/buddy/buddy-flows.yaml"
        ]
        
        for file_path in required_files:
            full_path = project_root_path / file_path
            assert full_path.exists(), f"Required file {file_path} missing"
            assert full_path.is_file(), f"Path {file_path} exists but is not a file"
    
    def test_gitkeep_files_in_empty_dirs(self, project_root_path):
        """Test that empty directories have .gitkeep files."""
        empty_dirs_with_gitkeep = [
            "core/history",
            "data/input",
            "data/output",
            "intent-scout/suggestions"
        ]
        
        for dir_path in empty_dirs_with_gitkeep:
            gitkeep_path = project_root_path / dir_path / ".gitkeep"
            assert gitkeep_path.exists(), f".gitkeep file missing in {dir_path}"

class TestDocumentationStructure:
    """Test documentation structure and completeness."""
    
    def test_docs_directory_structure(self, project_root_path):
        """Test documentation directory structure."""
        docs_dir = project_root_path / "docs"
        
        required_docs = [
            "README.md",
            "core.md",
            "modules.md"
        ]
        
        for doc in required_docs:
            doc_path = docs_dir / doc
            assert doc_path.exists(), f"Required documentation {doc} missing"
    
    def test_documentation_content(self, project_root_path):
        """Test that documentation files have content."""
        docs_dir = project_root_path / "docs"
        
        doc_files = ["README.md", "core.md", "modules.md"]
        
        for doc_file in doc_files:
            doc_path = docs_dir / doc_file
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                assert len(content) > 100, f"Documentation file {doc_file} appears to be too short or empty"
                assert "RooCode" in content, f"Documentation file {doc_file} doesn't mention RooCode"

#!/usr/bin/env python3
"""
Tool-Tests für Bootstrap, Templates und History-Konsistenz
Validiert Systemkomponenten und Hilfswerkzeuge
"""

import pytest
import yaml
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

class TestBootstrapValidation:
    """Test-Klasse für Bootstrap-Validierung"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    def test_bootstrap_script_exists(self, project_root):
        """Prüft, ob Bootstrap-Skript existiert"""
        bootstrap_script = project_root / "core" / "bootstrap" / "bootstrap.ps1"
        assert bootstrap_script.exists(), "Bootstrap script not found"
        
        # Prüfe, ob Skript lesbar ist
        with open(bootstrap_script, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0, "Bootstrap script is empty"
            assert "RooCode" in content, "Bootstrap script doesn't mention RooCode"
    
    def test_required_root_files_exist(self, project_root):
        """Prüft, ob alle erforderlichen Root-Dateien existieren"""
        required_files = [
            ".gitignore",
            "README.md",
            "LICENSE",
            "requirements.txt",
            "pyproject.toml"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Required root file missing: {file_name}"
    
    def test_requirements_txt_validity(self, project_root):
        """Prüft Gültigkeit der requirements.txt"""
        requirements_file = project_root / "requirements.txt"
        assert requirements_file.exists(), "requirements.txt not found"
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Prüfe, dass Abhängigkeiten mit Versionen definiert sind
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Prüfe auf Versionsspezifikation
                assert '==' in line or '>=' in line or '<=' in line, \
                    f"Dependency without version specification: {line}"
    
    def test_gitignore_completeness(self, project_root):
        """Prüft Vollständigkeit der .gitignore"""
        gitignore_file = project_root / ".gitignore"
        assert gitignore_file.exists(), ".gitignore not found"
        
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Prüfe erforderliche Einträge
        required_patterns = [
            ".venv",
            "__pycache__",
            "*.log",
            "*.tmp",
            "*.checkpoint",
            "*.mapped.json",
            "*.transcript.json",
            ".env"
        ]
        
        for pattern in required_patterns:
            assert pattern in content, f"Missing .gitignore pattern: {pattern}"
    
    @patch('subprocess.run')
    def test_bootstrap_execution_simulation(self, mock_subprocess, project_root):
        """Simuliert Bootstrap-Ausführung"""
        # Mock erfolgreiche Subprocess-Aufrufe
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Bootstrap completed successfully"
        
        bootstrap_script = project_root / "core" / "bootstrap" / "bootstrap.ps1"
        
        if bootstrap_script.exists():
            # Simuliere Bootstrap-Ausführung
            # (Tatsächliche Ausführung würde Systemveränderungen verursachen)
            
            # Prüfe, dass Skript PowerShell-Syntax verwendet
            with open(bootstrap_script, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "param(" in content, "Bootstrap script should accept parameters"
                assert "$ErrorActionPreference" in content, "Bootstrap script should set error handling"
    
    def test_pyproject_toml_validity(self, project_root):
        """Prüft Gültigkeit der pyproject.toml"""
        pyproject_file = project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml not found"
        
        # Prüfe, dass Datei parsbar ist (vereinfachte Prüfung)
        with open(pyproject_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "[build-system]" in content, "Missing [build-system] section"
            assert "[project]" in content, "Missing [project] section"
            assert "requires-python" in content, "Missing Python version requirement"

class TestTemplateValidation:
    """Test-Klasse für Template-Validierung"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    @pytest.fixture
    def templates_dir(self, project_root):
        """Gibt das Templates-Verzeichnis zurück"""
        return project_root / "core" / "templates"
    
    def load_yaml_safe(self, file_path: Path):
        """Lädt YAML-Datei sicher"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_all_templates_exist(self, templates_dir):
        """Prüft, ob alle erforderlichen Templates existieren"""
        required_templates = [
            "template.spec.yaml",
            "template.mode.yaml",
            "template.vocab-entry.yaml",
            "template.intent-suggestion.yaml",
            "template.buddy-flows.yaml",
            "template.llm-config.yaml"
        ]
        
        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Template missing: {template}"
    
    def test_template_structure_validity(self, templates_dir):
        """Prüft Strukturgültigkeit aller Templates"""
        template_files = list(templates_dir.glob("template.*.yaml"))
        
        for template_file in template_files:
            template_data = self.load_yaml_safe(template_file)
            assert template_data is not None, f"Template not parsable: {template_file}"
            
            # Prüfe auf REQUIRED_* Platzhalter
            template_str = str(template_data)
            if "REQUIRED_" in template_str:
                # Template enthält Platzhalter (erwartet)
                assert "REQUIRED_STRING" in template_str or \
                       "REQUIRED_INTEGER" in template_str or \
                       "REQUIRED_BOOLEAN" in template_str, \
                       f"Template {template_file} has invalid REQUIRED_ placeholders"
    
    def test_template_validator_script_exists(self, project_root):
        """Prüft, ob Template-Validator-Skript existiert"""
        validator_script = project_root / "core" / "ci" / "template_validator.py"
        assert validator_script.exists(), "Template validator script not found"
        
        # Prüfe Python-Syntax (vereinfacht)
        with open(validator_script, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "class TemplateValidator" in content, "TemplateValidator class not found"
            assert "def validate_file" in content, "validate_file method not found"

class TestCIValidation:
    """Test-Klasse für CI-Validierung"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    @pytest.fixture
    def ci_dir(self, project_root):
        """Gibt das CI-Verzeichnis zurück"""
        return project_root / "core" / "ci"
    
    def test_ci_scripts_exist(self, ci_dir):
        """Prüft, ob alle CI-Skripte existieren"""
        required_scripts = [
            "validate_all.ps1",
            "template_validator.py",
            "ci.rules.yaml"
        ]
        
        for script in required_scripts:
            script_path = ci_dir / script
            assert script_path.exists(), f"CI script missing: {script}"
    
    def test_ci_rules_validity(self, ci_dir):
        """Prüft Gültigkeit der CI-Regeln"""
        rules_file = ci_dir / "ci.rules.yaml"
        assert rules_file.exists(), "CI rules file not found"
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_data = yaml.safe_load(f)
        
        # Prüfe Grundstruktur
        assert "validation_rules" in rules_data, "validation_rules section missing"
        assert "subsystem_validation" in rules_data, "subsystem_validation section missing"
        assert "output_configuration" in rules_data, "output_configuration section missing"
    
    @patch('subprocess.run')
    def test_ci_validation_execution(self, mock_subprocess, project_root):
        """Simuliert CI-Validierung-Ausführung"""
        # Mock erfolgreiche CI-Validierung
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "CI validation passed"
        
        ci_script = project_root / "core" / "ci" / "validate_all.ps1"
        
        if ci_script.exists():
            # Simuliere CI-Ausführung
            # (Tatsächliche Ausführung würde alle Dateien prüfen)
            
            # Prüfe, dass Skript Parameter akzeptiert
            with open(ci_script, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "param(" in content, "CI script should accept parameters"
                assert "Subsystem" in content, "CI script should support subsystem filtering"

class TestHistoryConsistency:
    """Test-Klasse für History-Konsistenz"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    def test_vocab_history_structure(self, project_root):
        """Prüft Struktur der Vokabular-History"""
        history_file = project_root / "vocab.history.yaml"
        if not history_file.exists():
            pytest.skip("vocab.history.yaml does not exist yet")
        
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = yaml.safe_load(f)
        
        # Prüfe, dass es eine Liste ist
        assert isinstance(history_data, list), "vocab.history.yaml should contain a list"
        
        # Prüfe Struktur der Einträge
        for entry in history_data:
            required_fields = ["action", "intent_id", "timestamp"]
            for field in required_fields:
                assert field in entry, f"Required field {field} missing in history entry"
    
    def test_project_structure_consistency(self, project_root):
        """Prüft Konsistenz der Projektstruktur"""
        required_dirs = [
            "core",
            "core/modes",
            "core/templates",
            "core/ci",
            "core/bootstrap",
            "core/config",
            "core/tests",
            "modules"
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Required directory missing: {dir_path}"
            assert full_path.is_dir(), f"Path is not a directory: {dir_path}"

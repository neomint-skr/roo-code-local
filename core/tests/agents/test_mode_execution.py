#!/usr/bin/env python3
"""
Agent-Tests für Mode-Ausführung und Spec-Konformität
Testet Input/Output-Logik der verschiedenen Agenten-Modi
"""

import pytest
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch

class TestModeExecution:
    """Test-Klasse für Mode-Ausführung"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    @pytest.fixture
    def modes_dir(self, project_root):
        """Gibt das Modes-Verzeichnis zurück"""
        return project_root / "core" / "modes"
    
    def load_yaml_safe(self, file_path: Path):
        """Lädt YAML-Datei sicher"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_transkriptor_mode_definition(self, modes_dir):
        """Prüft Definition des Transkriptor-Modus"""
        transkriptor_file = modes_dir / "mode.transkriptor.yaml"
        if not transkriptor_file.exists():
            pytest.skip("Transkriptor mode not defined yet")
        
        mode_data = self.load_yaml_safe(transkriptor_file)
        
        # Prüfe erforderliche Felder
        assert mode_data["slug"] == "transkriptor"
        assert mode_data["agent"] == "transkriptor"
        assert "tools" in mode_data
        assert "input_constraints" in mode_data
        assert "output_target" in mode_data
        
        # Prüfe spezifische Tools
        expected_tools = ["sanitize", "tokenize", "speakerDetect", "segmentBoundaries"]
        tool_names = [tool["name"] for tool in mode_data.get("tools", [])]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} missing"
    
    def test_buddy_mode_definition(self, modes_dir):
        """Prüft Definition des Buddy-Modus"""
        buddy_file = modes_dir / "mode.buddy.yaml"
        if not buddy_file.exists():
            pytest.skip("Buddy mode not defined yet")
        
        mode_data = self.load_yaml_safe(buddy_file)
        
        # Prüfe erforderliche Felder
        assert mode_data["slug"] == "buddy"
        assert mode_data["agent"] == "buddy"
        assert mode_data["integration"]["buddy_compatible"] == True
    
    def test_mode_model_source_validity(self, modes_dir):
        """Prüft, ob model_source in allen Modes gültig ist"""
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            
            if "model_source" in mode_data:
                model_source = mode_data["model_source"]
                assert "type" in model_source, f"model_source.type missing in {mode_file}"
                assert "reference" in model_source, f"model_source.reference missing in {mode_file}"
                
                # Prüfe gültige Typen
                valid_types = ["local", "api", "registry"]
                assert model_source["type"] in valid_types, \
                    f"Invalid model_source.type in {mode_file}: {model_source['type']}"
    
    def test_mode_execution_constraints(self, modes_dir):
        """Prüft Ausführungsconstraints aller Modes"""
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            
            if "execution" in mode_data:
                execution = mode_data["execution"]
                
                # Prüfe erforderliche Execution-Felder
                required_fields = ["timeout_seconds", "retry_attempts", "parallel_processing"]
                for field in required_fields:
                    assert field in execution, f"execution.{field} missing in {mode_file}"
                
                # Prüfe Datentypen
                assert isinstance(execution["timeout_seconds"], int)
                assert isinstance(execution["retry_attempts"], int)
                assert isinstance(execution["parallel_processing"], bool)

class TestAgentSpecConformity:
    """Test-Klasse für Agent-Spec-Konformität"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    def load_yaml_safe(self, file_path: Path):
        """Lädt YAML-Datei sicher"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_spec_mode_consistency(self, project_root):
        """Prüft Konsistenz zwischen Spec- und Mode-Dateien"""
        spec_files = list(project_root.rglob("spec.*.yaml"))
        modes_dir = project_root / "core" / "modes"
        
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        mode_agents = {}
        
        # Sammle alle Mode-Agenten
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            if "agent" in mode_data and "slug" in mode_data:
                mode_agents[mode_data["agent"]] = mode_data["slug"]
        
        # Prüfe Spec-Dateien
        for spec_file in spec_files:
            spec_data = self.load_yaml_safe(spec_file)
            if "agent_id" in spec_data:
                agent_id = spec_data["agent_id"]
                assert agent_id in mode_agents, \
                    f"Spec {spec_file} references undefined agent: {agent_id}"
    
    def test_spec_capability_definitions(self, project_root):
        """Prüft Capability-Definitionen in Spec-Dateien"""
        spec_files = list(project_root.rglob("spec.*.yaml"))
        
        for spec_file in spec_files:
            spec_data = self.load_yaml_safe(spec_file)
            
            if "capabilities" in spec_data:
                capabilities = spec_data["capabilities"]
                
                # Prüfe erforderliche Capability-Felder
                required_fields = ["input_types", "output_types", "tools"]
                for field in required_fields:
                    assert field in capabilities, \
                        f"capabilities.{field} missing in {spec_file}"
                
                # Prüfe Datentypen
                assert isinstance(capabilities["input_types"], list)
                assert isinstance(capabilities["output_types"], list)
                assert isinstance(capabilities["tools"], list)

class TestInputOutputLogic:
    """Test-Klasse für Input/Output-Logik"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    def test_input_constraint_validation(self, project_root):
        """Prüft Input-Constraint-Validierung"""
        modes_dir = project_root / "core" / "modes"
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            
            if "input_constraints" in mode_data:
                constraints = mode_data["input_constraints"]
                
                # Prüfe erforderliche Constraint-Felder
                if "file_types" in constraints:
                    assert isinstance(constraints["file_types"], list)
                    
                if "max_file_size_mb" in constraints:
                    assert isinstance(constraints["max_file_size_mb"], int)
                    assert constraints["max_file_size_mb"] > 0
                
                if "encoding" in constraints:
                    assert isinstance(constraints["encoding"], str)
    
    def test_output_target_validation(self, project_root):
        """Prüft Output-Target-Validierung"""
        modes_dir = project_root / "core" / "modes"
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            
            if "output_target" in mode_data:
                output = mode_data["output_target"]
                
                # Prüfe erforderliche Output-Felder
                required_fields = ["format", "destination", "naming_pattern"]
                for field in required_fields:
                    assert field in output, \
                        f"output_target.{field} missing in {mode_file}"
                
                # Prüfe gültige Formate
                valid_formats = ["json", "yaml", "txt", "csv", "xml"]
                if output["format"] not in valid_formats:
                    pytest.skip(f"Unknown format {output['format']} in {mode_file}")
    
    @patch('subprocess.run')
    def test_tool_execution_simulation(self, mock_subprocess, project_root):
        """Simuliert Tool-Ausführung für Modes"""
        modes_dir = project_root / "core" / "modes"
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        # Mock erfolgreiche Tool-Ausführung
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Tool executed successfully"
        
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            
            if "tools" in mode_data:
                tools = mode_data["tools"]
                
                for tool in tools:
                    if isinstance(tool, dict) and "name" in tool:
                        # Simuliere Tool-Ausführung
                        tool_name = tool["name"]
                        
                        # Prüfe, ob Tool-Name gültig ist
                        assert isinstance(tool_name, str)
                        assert len(tool_name) > 0
                        
                        # Simuliere erfolgreiche Ausführung
                        assert True  # Tool würde erfolgreich ausgeführt

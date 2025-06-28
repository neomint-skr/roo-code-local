#!/usr/bin/env python3
"""
Struktur-Tests für YAML-Spezifikationen und Vokabular
Prüft schema- und referenzbasierte Validierung
"""

import pytest
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any

class TestYAMLStructure:
    """Test-Klasse für YAML-Strukturvalidierung"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    @pytest.fixture
    def templates_dir(self, project_root):
        """Gibt das Templates-Verzeichnis zurück"""
        return project_root / "core" / "templates"
    
    def load_yaml_safe(self, file_path: Path) -> Dict[str, Any]:
        """Lädt YAML-Datei sicher"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_templates_exist(self, templates_dir):
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
            assert template_path.exists(), f"Template {template} not found"
            
            # Prüfe, ob Template gültiges YAML ist
            template_data = self.load_yaml_safe(template_path)
            assert template_data is not None, f"Template {template} is not valid YAML"
    
    def test_template_required_fields(self, templates_dir):
        """Prüft, ob Templates REQUIRED_* Felder enthalten"""
        template_path = templates_dir / "template.mode.yaml"
        if template_path.exists():
            template_data = self.load_yaml_safe(template_path)
            
            # Prüfe auf REQUIRED_* Felder
            required_fields = ["slug", "agent", "description"]
            for field in required_fields:
                assert field in template_data, f"Required field {field} missing in mode template"
    
    def test_yaml_syntax_validation(self, project_root):
        """Prüft YAML-Syntax aller YAML-Dateien im Projekt"""
        yaml_files = list(project_root.rglob("*.yaml"))
        
        # Filtere Template-Dateien aus (die enthalten Platzhalter)
        yaml_files = [f for f in yaml_files if not f.name.startswith("template.")]
        
        for yaml_file in yaml_files:
            try:
                self.load_yaml_safe(yaml_file)
            except yaml.YAMLError as e:
                pytest.fail(f"YAML syntax error in {yaml_file}: {e}")
    
    def test_mode_files_structure(self, project_root):
        """Prüft Struktur von mode.*.yaml Dateien"""
        modes_dir = project_root / "core" / "modes"
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            
            # Prüfe erforderliche Felder
            required_fields = ["slug", "agent", "description"]
            for field in required_fields:
                assert field in mode_data, f"Required field {field} missing in {mode_file}"
    
    def test_spec_files_structure(self, project_root):
        """Prüft Struktur von spec.*.yaml Dateien"""
        spec_files = list(project_root.rglob("spec.*.yaml"))
        
        for spec_file in spec_files:
            spec_data = self.load_yaml_safe(spec_file)
            
            # Prüfe erforderliche Felder
            required_fields = ["agent_id", "name", "description", "version"]
            for field in required_fields:
                assert field in spec_data, f"Required field {field} missing in {spec_file}"
    
    def test_vocab_file_structure(self, project_root):
        """Prüft Struktur der vocab.yaml Datei"""
        vocab_file = project_root / "vocab.yaml"
        if not vocab_file.exists():
            pytest.skip("vocab.yaml does not exist yet")
        
        vocab_data = self.load_yaml_safe(vocab_file)
        
        # Prüfe, ob es eine Liste ist
        assert isinstance(vocab_data, list), "vocab.yaml should contain a list of entries"
        
        # Prüfe Struktur der Einträge
        for entry in vocab_data:
            required_fields = ["id", "label", "created_on", "origin"]
            for field in required_fields:
                assert field in entry, f"Required field {field} missing in vocab entry"
    
    def test_buddy_flows_structure(self, project_root):
        """Prüft Struktur der buddy-flows.yaml Datei"""
        flows_file = project_root / "buddy-flows.yaml"
        if not flows_file.exists():
            pytest.skip("buddy-flows.yaml does not exist yet")
        
        flows_data = self.load_yaml_safe(flows_file)
        
        # Prüfe erforderliche Felder
        required_fields = ["flow_id", "name", "description", "trigger", "steps"]
        for field in required_fields:
            assert field in flows_data, f"Required field {field} missing in buddy-flows.yaml"
    
    def test_llm_config_structure(self, project_root):
        """Prüft Struktur der llm.config.yaml Datei"""
        config_file = project_root / "core" / "config" / "llm.config.yaml"
        if not config_file.exists():
            pytest.skip("llm.config.yaml does not exist yet")
        
        config_data = self.load_yaml_safe(config_file)
        
        # Prüfe erforderliche Hauptbereiche
        required_sections = ["model", "engine", "context", "performance", "defaults"]
        for section in required_sections:
            assert section in config_data, f"Required section {section} missing in llm.config.yaml"

class TestReferentialIntegrity:
    """Test-Klasse für referenzielle Konsistenz"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    def load_yaml_safe(self, file_path: Path) -> Dict[str, Any]:
        """Lädt YAML-Datei sicher"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_mode_spec_consistency(self, project_root):
        """Prüft, ob spec.*.yaml Dateien existierende Modes referenzieren"""
        modes_dir = project_root / "core" / "modes"
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        # Sammle alle Mode-Slugs
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        mode_slugs = set()
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            if "slug" in mode_data:
                mode_slugs.add(mode_data["slug"])
        
        # Prüfe Spec-Dateien
        spec_files = list(project_root.rglob("spec.*.yaml"))
        for spec_file in spec_files:
            spec_data = self.load_yaml_safe(spec_file)
            if "agent_id" in spec_data:
                assert spec_data["agent_id"] in mode_slugs, \
                    f"Spec {spec_file} references non-existent mode: {spec_data['agent_id']}"
    
    def test_intent_mapping_consistency(self, project_root):
        """Prüft, ob *.mapped.json Dateien nur existierende Intents referenzieren"""
        vocab_file = project_root / "vocab.yaml"
        if not vocab_file.exists():
            pytest.skip("vocab.yaml does not exist yet")
        
        # Sammle alle Intent-IDs
        vocab_data = self.load_yaml_safe(vocab_file)
        intent_ids = set()
        
        if isinstance(vocab_data, list):
            for entry in vocab_data:
                if "id" in entry:
                    intent_ids.add(entry["id"])
        
        # Prüfe Mapping-Dateien
        mapping_files = list(project_root.rglob("*.mapped.json"))
        for mapping_file in mapping_files:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # Prüfe Intent-Referenzen (vereinfachte Struktur)
            if isinstance(mapping_data, list):
                for entry in mapping_data:
                    if "intent_id" in entry and entry["intent_id"]:
                        assert entry["intent_id"] in intent_ids, \
                            f"Mapping {mapping_file} references non-existent intent: {entry['intent_id']}"

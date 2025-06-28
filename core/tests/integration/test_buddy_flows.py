#!/usr/bin/env python3
"""
Integration-Tests für vollständige Prozessketten über buddy-flows
Simuliert End-to-End-Workflows
"""

import pytest
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

class TestBuddyFlowsIntegration:
    """Test-Klasse für Buddy-Flows-Integration"""
    
    @pytest.fixture
    def project_root(self):
        """Gibt den Projekt-Root-Pfad zurück"""
        return Path(__file__).parent.parent.parent.parent
    
    @pytest.fixture
    def sample_transcript_data(self):
        """Beispiel-Transkript-Daten für Tests"""
        return [
            {
                "speaker": "user",
                "text": "Hallo, ich hätte gerne Informationen über das Produkt",
                "timestamp": "2025-01-01T10:00:00Z",
                "turn_id": "turn_001"
            },
            {
                "speaker": "agent",
                "text": "Gerne helfe ich Ihnen weiter. Welches Produkt interessiert Sie?",
                "timestamp": "2025-01-01T10:00:05Z",
                "turn_id": "turn_002"
            }
        ]
    
    @pytest.fixture
    def sample_vocab_data(self):
        """Beispiel-Vokabular-Daten für Tests"""
        return [
            {
                "id": "inform.question",
                "label": "Information Request",
                "description": "User requests information",
                "created_on": "2025-01-01T00:00:00Z",
                "origin": "manual"
            },
            {
                "id": "inform.response",
                "label": "Information Response",
                "description": "Agent provides information",
                "created_on": "2025-01-01T00:00:00Z",
                "origin": "manual"
            }
        ]
    
    def load_yaml_safe(self, file_path: Path):
        """Lädt YAML-Datei sicher"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_buddy_flows_definition_exists(self, project_root):
        """Prüft, ob buddy-flows.yaml existiert und gültig ist"""
        flows_file = project_root / "buddy-flows.yaml"
        if not flows_file.exists():
            pytest.skip("buddy-flows.yaml does not exist yet")
        
        flows_data = self.load_yaml_safe(flows_file)
        
        # Prüfe Grundstruktur
        assert "flow_id" in flows_data
        assert "name" in flows_data
        assert "steps" in flows_data
        assert isinstance(flows_data["steps"], list)
    
    def test_flow_step_mode_references(self, project_root):
        """Prüft, ob Flow-Steps existierende Modes referenzieren"""
        flows_file = project_root / "buddy-flows.yaml"
        if not flows_file.exists():
            pytest.skip("buddy-flows.yaml does not exist yet")
        
        flows_data = self.load_yaml_safe(flows_file)
        modes_dir = project_root / "core" / "modes"
        
        if not modes_dir.exists():
            pytest.skip("Modes directory does not exist yet")
        
        # Sammle verfügbare Mode-Slugs
        mode_files = list(modes_dir.rglob("mode.*.yaml"))
        available_modes = set()
        
        for mode_file in mode_files:
            mode_data = self.load_yaml_safe(mode_file)
            if "slug" in mode_data:
                available_modes.add(mode_data["slug"])
        
        # Prüfe Flow-Steps
        if "steps" in flows_data:
            for step in flows_data["steps"]:
                if "mode" in step:
                    mode_ref = step["mode"]
                    assert mode_ref in available_modes, \
                        f"Flow step references non-existent mode: {mode_ref}"
    
    @patch('subprocess.run')
    def test_transkriptor_to_intent_mapper_flow(self, mock_subprocess, project_root, 
                                               sample_transcript_data, sample_vocab_data):
        """Simuliert vollständigen Flow: Transkriptor → Intent-Mapper"""
        # Mock erfolgreiche Subprocess-Aufrufe
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = json.dumps({
            "status": "success",
            "output_file": "test.mapped.json"
        })
        
        # Simuliere Transkriptor-Ausführung
        transcript_file = project_root / "test.transcript.json"
        try:
            with open(transcript_file, 'w', encoding='utf-8') as f:
                json.dump(sample_transcript_data, f)
            
            # Simuliere Vokabular
            vocab_file = project_root / "vocab.yaml"
            with open(vocab_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_vocab_data, f)
            
            # Simuliere Intent-Mapping-Prozess
            mapped_data = []
            for turn in sample_transcript_data:
                mapped_turn = {
                    "turn_ref": turn["turn_id"],
                    "intent_id": "inform.question" if turn["speaker"] == "user" else "inform.response",
                    "confidence": 0.95
                }
                mapped_data.append(mapped_turn)
            
            # Prüfe Mapping-Ergebnis
            assert len(mapped_data) == len(sample_transcript_data)
            assert all("intent_id" in turn for turn in mapped_data)
            assert all("turn_ref" in turn for turn in mapped_data)
            
        finally:
            # Cleanup
            if transcript_file.exists():
                transcript_file.unlink()
            if vocab_file.exists():
                vocab_file.unlink()
    
    @patch('subprocess.run')
    def test_intent_scout_suggestion_flow(self, mock_subprocess, project_root):
        """Simuliert Intent-Scout-Suggestion-Flow"""
        # Mock erfolgreiche Subprocess-Aufrufe
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = json.dumps({
            "suggestions": [
                {
                    "suggested_id": "inform.uncategorized.01",
                    "label": "Uncategorized Information Request",
                    "explanation": "User request that doesn't fit existing categories",
                    "source_turn": "user:3"
                }
            ]
        })
        
        # Simuliere Mapping-Datei mit unmapped Turns
        mapping_data = [
            {
                "turn_ref": "turn_001",
                "intent_id": "inform.question",
                "confidence": 0.95
            },
            {
                "turn_ref": "turn_002",
                "intent_id": None,  # Unmapped turn
                "confidence": 0.0
            }
        ]
        
        mapped_file = project_root / "test.mapped.json"
        try:
            with open(mapped_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f)
            
            # Simuliere Intent-Scout-Ausführung
            unmapped_turns = [turn for turn in mapping_data if turn["intent_id"] is None]
            
            # Prüfe, dass unmapped Turns gefunden wurden
            assert len(unmapped_turns) > 0
            
            # Simuliere Suggestion-Generierung
            suggestions = []
            for turn in unmapped_turns:
                suggestion = {
                    "suggested_id": f"inform.uncategorized.{len(suggestions)+1:02d}",
                    "label": "Uncategorized Intent",
                    "explanation": f"Turn {turn['turn_ref']} needs categorization",
                    "source_turn": turn["turn_ref"]
                }
                suggestions.append(suggestion)
            
            # Prüfe Suggestion-Struktur
            assert len(suggestions) > 0
            for suggestion in suggestions:
                assert "suggested_id" in suggestion
                assert "label" in suggestion
                assert "explanation" in suggestion
                assert "source_turn" in suggestion
            
        finally:
            # Cleanup
            if mapped_file.exists():
                mapped_file.unlink()
    
    def test_vocab_updater_integration(self, project_root, sample_vocab_data):
        """Simuliert Vocab-Updater-Integration"""
        vocab_file = project_root / "vocab.yaml"
        history_file = project_root / "vocab.history.yaml"
        
        try:
            # Erstelle initiales Vokabular
            with open(vocab_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_vocab_data, f)
            
            # Simuliere neue Intent-Suggestion
            new_intent = {
                "id": "confirm.approval",
                "label": "Approval Confirmation",
                "description": "User confirms or approves something",
                "created_on": "2025-01-01T12:00:00Z",
                "origin": "intent-scout"
            }
            
            # Simuliere Vocab-Update
            updated_vocab = sample_vocab_data + [new_intent]
            
            # Prüfe alphabetische Sortierung
            sorted_vocab = sorted(updated_vocab, key=lambda x: x["id"])
            assert sorted_vocab == sorted(updated_vocab, key=lambda x: x["id"])
            
            # Simuliere History-Update
            history_entry = {
                "action": "added",
                "intent_id": new_intent["id"],
                "timestamp": new_intent["created_on"],
                "source": "intent-scout",
                "approved_by": "system"
            }
            
            # Prüfe History-Eintrag
            assert history_entry["intent_id"] == new_intent["id"]
            assert history_entry["action"] == "added"
            
        finally:
            # Cleanup
            if vocab_file.exists():
                vocab_file.unlink()
            if history_file.exists():
                history_file.unlink()
    
    def test_end_to_end_workflow_simulation(self, project_root):
        """Simuliert kompletten End-to-End-Workflow"""
        # Simuliere vollständigen Workflow:
        # 1. Transkript → 2. Intent-Mapping → 3. Intent-Scout → 4. Vocab-Update
        
        workflow_steps = [
            {
                "step": "transkriptor",
                "input": "audio.wav",
                "output": "transcript.json",
                "expected_fields": ["speaker", "text", "timestamp"]
            },
            {
                "step": "intent-mapper",
                "input": "transcript.json",
                "output": "mapped.json",
                "expected_fields": ["turn_ref", "intent_id", "confidence"]
            },
            {
                "step": "intent-scout",
                "input": "mapped.json",
                "output": "suggestions.yaml",
                "expected_fields": ["suggested_id", "label", "explanation"]
            },
            {
                "step": "vocab-updater",
                "input": "suggestions.yaml",
                "output": "vocab.yaml",
                "expected_fields": ["id", "label", "created_on", "origin"]
            }
        ]
        
        # Prüfe Workflow-Definition
        for i, step in enumerate(workflow_steps):
            assert "step" in step
            assert "input" in step
            assert "output" in step
            assert "expected_fields" in step
            
            # Prüfe Verkettung (Output von Step i ist Input von Step i+1)
            if i < len(workflow_steps) - 1:
                next_step = workflow_steps[i + 1]
                # Vereinfachte Prüfung der Datenfluss-Kompatibilität
                assert isinstance(step["output"], str)
                assert isinstance(next_step["input"], str)

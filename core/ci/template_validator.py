#!/usr/bin/env python3
"""
RooCode Template Validator
Prüft YAML-Dateien gegen ihre entsprechenden Templates
"""

import yaml
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple

class TemplateValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "core" / "templates"
        self.errors = []
        self.warnings = []
    
    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Lädt YAML-Datei sicher"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.add_error("yaml_load_error", str(file_path), "", "", str(e))
            return {}
    
    def add_error(self, error_type: str, file_path: str, yaml_path: str = "", 
                  expected: str = "", actual: str = "", line_num: int = 0):
        """Fügt Validierungsfehler hinzu"""
        self.errors.append({
            "error_type": error_type,
            "affected_file": file_path,
            "yaml_path": yaml_path,
            "expected_value": expected,
            "actual_value": actual,
            "line_number": line_num
        })
    
    def add_warning(self, warning_type: str, file_path: str, message: str):
        """Fügt Warnung hinzu"""
        self.warnings.append({
            "warning_type": warning_type,
            "affected_file": file_path,
            "message": message
        })
    
    def get_template_for_file(self, file_path: Path) -> Path:
        """Bestimmt das entsprechende Template für eine Datei"""
        file_name = file_path.name
        
        if file_name.startswith("mode.") and file_name.endswith(".yaml"):
            return self.templates_dir / "template.mode.yaml"
        elif file_name.startswith("spec.") and file_name.endswith(".yaml"):
            return self.templates_dir / "template.spec.yaml"
        elif file_name == "vocab.yaml":
            return self.templates_dir / "template.vocab-entry.yaml"
        elif file_name == "buddy-flows.yaml":
            return self.templates_dir / "template.buddy-flows.yaml"
        elif file_name == "llm.config.yaml":
            return self.templates_dir / "template.llm-config.yaml"
        else:
            return None
    
    def validate_required_fields(self, data: Dict, template: Dict, 
                                file_path: str, path_prefix: str = ""):
        """Validiert erforderliche Felder gegen Template"""
        for key, value in template.items():
            current_path = f"{path_prefix}.{key}" if path_prefix else key
            
            if key not in data:
                self.add_error("missing_required_field", file_path, current_path, 
                             str(value), "missing")
                continue
            
            if isinstance(value, str) and value.startswith("REQUIRED_"):
                # Prüfe Typ basierend auf REQUIRED_TYPE
                expected_type = value.replace("REQUIRED_", "").lower()
                actual_value = data[key]
                
                if not self.validate_field_type(actual_value, expected_type):
                    self.add_error("invalid_field_type", file_path, current_path,
                                 expected_type, type(actual_value).__name__)
            
            elif isinstance(value, dict) and isinstance(data[key], dict):
                # Rekursive Validierung für verschachtelte Objekte
                self.validate_required_fields(data[key], value, file_path, current_path)
            
            elif isinstance(value, list) and len(value) > 0:
                # Validierung für Listen
                if not isinstance(data[key], list):
                    self.add_error("invalid_field_type", file_path, current_path,
                                 "list", type(data[key]).__name__)
    
    def validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validiert Feldtyp gegen erwarteten Typ"""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "list_of_strings": list,
            "iso8601_timestamp": str,
            "semver": str
        }
        
        expected_python_type = type_mapping.get(expected_type, str)
        
        if isinstance(expected_python_type, tuple):
            return isinstance(value, expected_python_type)
        else:
            return isinstance(value, expected_python_type)
    
    def validate_file(self, file_path: Path) -> bool:
        """Validiert eine einzelne Datei gegen ihr Template"""
        template_path = self.get_template_for_file(file_path)
        
        if not template_path:
            self.add_warning("no_template_found", str(file_path), 
                           f"No template found for {file_path.name}")
            return True
        
        if not template_path.exists():
            self.add_error("template_missing", str(file_path), "", 
                         str(template_path), "missing")
            return False
        
        # Lade Datei und Template
        file_data = self.load_yaml(file_path)
        template_data = self.load_yaml(template_path)
        
        if not file_data or not template_data:
            return False
        
        # Validiere erforderliche Felder
        self.validate_required_fields(file_data, template_data, str(file_path))
        
        return len(self.errors) == 0
    
    def validate_project(self, subsystem: str = "all") -> bool:
        """Validiert das gesamte Projekt oder ein Subsystem"""
        if subsystem == "all":
            yaml_files = list(self.project_root.rglob("*.yaml"))
            # Filtere Template-Dateien und CI-Dateien aus
            yaml_files = [f for f in yaml_files 
                         if not f.name.startswith("template.") 
                         and not f.name.startswith("ci.")]
        else:
            # Subsystem-spezifische Validierung
            yaml_files = self.get_subsystem_files(subsystem)
        
        validation_passed = True
        
        for file_path in yaml_files:
            if not self.validate_file(file_path):
                validation_passed = False
        
        return validation_passed
    
    def get_subsystem_files(self, subsystem: str) -> List[Path]:
        """Gibt Dateien für ein spezifisches Subsystem zurück"""
        if subsystem == "vocab":
            return list(self.project_root.rglob("vocab.yaml")) + \
                   list(self.project_root.rglob("vocab.history.yaml"))
        elif subsystem == "modes":
            return list(self.project_root.rglob("mode.*.yaml")) + \
                   list(self.project_root.rglob("spec.*.yaml"))
        elif subsystem == "flows":
            return list(self.project_root.rglob("buddy-flows.yaml"))
        else:
            return []
    
    def generate_report(self) -> Dict[str, Any]:
        """Generiert Validierungsbericht"""
        return {
            "validation_summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "validation_passed": len(self.errors) == 0
            },
            "errors": self.errors,
            "warnings": self.warnings
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python template_validator.py <project_root> [subsystem]")
        sys.exit(1)
    
    project_root = sys.argv[1]
    subsystem = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    validator = TemplateValidator(project_root)
    validation_passed = validator.validate_project(subsystem)
    
    # Generiere Bericht
    report = validator.generate_report()
    
    # Ausgabe als JSON für weitere Verarbeitung
    print(json.dumps(report, indent=2))
    
    sys.exit(0 if validation_passed else 1)

if __name__ == "__main__":
    main()

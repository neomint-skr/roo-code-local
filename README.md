# RooCode Local Agent System

Ein lokal betreibbares, agentenbasiertes RooCode-Projekt für deterministische KI-Workflows.

## Schnellstart

```bash
# System initialisieren
bash bootstrap.sh

# Mit Buddy-Profil starten
./start.ps1 --profile buddy
```

## Architektur

### Verzeichnisstruktur

```
├── core/                    # Systemkritische Komponenten
│   ├── modes/              # Agenten-Modi (transkriptor, buddy, etc.)
│   ├── templates/          # YAML-Templates für CI-Validierung
│   └── ci/                 # Prüf- und Automatisierungsskripte
├── modules/                # Optionale Funktionsmodule
│   └── llm-admin/         # LLM-Verwaltung und API-Integration
└── pim/                   # Project Information Management
    ├── tasks/             # YAML-basierte Task-Definitionen
    └── status.yaml        # Aktueller Ausführungsstatus
```

### Hauptkomponenten

- **Modes**: Definierte Agenten-Modi mit spezifischen Fähigkeiten
- **LLM-Admin**: Lokale Modellverwaltung und API-Server
- **Templates**: CI-validierbare Strukturvorlagen
- **Bootstrap**: Deterministische Systeminitialisierung

## Systemvoraussetzungen

- **Python**: ≥3.11
- **Betriebssystem**: Windows 11 Pro (PowerShell), Linux (Bash)
- **Speicher**: Mindestens 8GB RAM für lokale LLM-Modelle

## Nutzung

### Agenten-Modi

- `transkriptor`: Audio-zu-Text-Verarbeitung mit Intent-Mapping
- `buddy`: Zentraler Koordinations-Agent
- `intent-mapper`: Intent-Klassifikation für Transkripte
- `vocab-updater`: Vokabular-Management

### LLM-Verwaltung

```powershell
# Verfügbare Modelle anzeigen
llm list

# Modell aktivieren
llm use mistral

# Modell ausführen
llm run input.txt
```

## Erweiterung

Neue Agenten-Modi werden über YAML-Spezifikationen in `core/modes/` definiert.
Templates in `core/templates/` stellen strukturelle Konsistenz sicher.

## CI/CD

Das System validiert automatisch:
- YAML-Strukturintegrität
- Template-Konformität
- Referenzielle Konsistenz
- Deterministische Reihenfolge

Ausführung: `core/ci/validate_all.ps1`
*EXPERIMENTAL*

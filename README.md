# RooCode Local Agent System

Ein lokal betreibbares, agentenbasiertes RooCode-Projekt für deterministische KI-Workflows.
Vollständig containerisiert für einfache Installation und Ausführung.

## Quickstart (Task 39 Implementation)

**Single Entry Point - No Local Dependencies Required**

```powershell
# Windows - One command start
git clone https://github.com/neomint-skr/roo-code-local
cd roo-code-local
./docker-run.ps1
```

```bash
# Linux/macOS - Direct Docker run
git clone https://github.com/neomint-skr/roo-code-local
cd roo-code-local
docker run -it --rm -v $(pwd):/project -p 11434:11434 -p 8080:8080 neomint/roo-agent-buddy:latest
```

## Task 39: Docker-Only System

**Alle lokalen Skripte entfernt - Nur noch Docker-basierte Ausführung**

Das System läuft vollständig in Docker-Containern. Alle PowerShell-Skripte wurden entfernt:
- ❌ `start.ps1` (entfernt)
- ❌ `bootstrap.ps1` (entfernt)
- ❌ `validate_all.ps1` (entfernt)
- ❌ `*-run.ps1` Engine-Skripte (entfernt)
- ❌ `test_registry.ps1` (entfernt)
- ❌ Template-Dateien (entfernt)

### Einziger Einstiegspunkt

```powershell
# Windows - Einziger Befehl für alles
./docker-run.ps1

# Verschiedene Profile
./docker-run.ps1 -Profile buddy
./docker-run.ps1 -Profile transkriptor
```

### Erweiterte Docker-Befehle

```bash
# Container starten
docker compose up --build --detach

# Logs anzeigen
docker logs roo-system -f

# Shell-Zugriff
docker exec -it roo-system bash

# System stoppen
docker compose down

# Komplett neu starten
docker compose down && docker compose up --build --detach
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
- **Docker**: Containerisierte Systeminitialisierung

## Systemvoraussetzungen

- **Docker**: Docker Desktop (Windows/macOS) oder Docker Engine (Linux)
- **Speicher**: Mindestens 8GB RAM für lokale LLM-Modelle
- **Festplatte**: 10GB freier Speicherplatz für Container und Modelle
- **Betriebssystem**: Windows 10/11, macOS, oder Linux mit Docker-Unterstützung

### Keine lokalen Abhängigkeiten erforderlich

Das System läuft vollständig in Docker-Containern. Python, LLM-Engines und alle anderen Abhängigkeiten sind bereits im Container enthalten.

## Nutzung

### System-Zugriff

Nach dem Start ist das System über folgende Endpunkte erreichbar:

- **API-Server**: http://localhost:8080
- **LLM-Engine**: http://localhost:11434
- **API-Key**: `local-mode-key`
- **Standard-Profil**: `buddy`

### Agenten-Modi

- `buddy`: Zentraler Koordinations-Agent (Standard)
- `transkriptor`: Audio-zu-Text-Verarbeitung mit Intent-Mapping
- `intent-mapper`: Intent-Klassifikation für Transkripte
- `vocab-updater`: Vokabular-Management

### Container-Verwaltung

```bash
# Status prüfen
docker ps

# Logs anzeigen
docker logs roo-system

# Container-Shell öffnen
docker exec -it roo-system bash

# System neu starten
docker restart roo-system
```

### Konfiguration

Die Konfiguration erfolgt über Umgebungsvariablen in `.env.docker`:

```bash
# Profil ändern
PROFILE=buddy

# Ports anpassen
API_PORT=8080
LLM_PORT=11434

# Log-Level setzen
LOG_LEVEL=INFO
```

## Entwicklung und Erweiterung

### Neue Agenten-Modi

Neue Agenten-Modi werden über YAML-Spezifikationen in `core/modes/` definiert.
Templates in `core/templates/` stellen strukturelle Konsistenz sicher.

### Lokale Entwicklung

```bash
# Container mit Volume-Mapping für Entwicklung
docker run -it --rm \
  -v $(pwd):/app \
  -p 8080:8080 \
  -p 11434:11434 \
  neomint/roo-agent-buddy bash

# Änderungen testen
docker compose up --build
```

### CI/CD und Validierung

Das System validiert automatisch:
- YAML-Strukturintegrität
- Template-Konformität
- Referenzielle Konsistenz
- Docker-Container-Funktionalität

```bash
# Validierung im Container ausführen
docker exec roo-system python -m pytest core/tests/
```

## Fehlerbehebung

### Häufige Probleme

**Container startet nicht:**
```bash
# Logs prüfen
docker logs roo-system

# Container neu erstellen
docker compose down
docker compose up --build
```

**Port bereits belegt:**
```bash
# Andere Ports verwenden
./docker-run.ps1 -Port 8081 -LLMPort 11435
```

**Speicherprobleme:**
```bash
# Docker-Ressourcen erhöhen in Docker Desktop
# Oder Container-Limits anpassen in docker-compose.yaml
```

## Support

- **Logs**: `docker logs roo-system`
- **Konfiguration**: `.env.docker`
- **Gesundheitsprüfung**: http://localhost:8080/health
- **Container-Shell**: `docker exec -it roo-system bash`

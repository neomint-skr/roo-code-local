# RooCode Local Agent System

> Lokal betreibbares, agentenbasiertes RooCode-Projekt für deterministische KI-Workflows mit vollständiger Docker-Containerisierung

[![Runtime: Docker](https://img.shields.io/badge/runtime-Docker-blue)](https://docker.com)
[![Deployment: Single Command](https://img.shields.io/badge/deployment-Single%20Command-informational)](./docker-run.ps1)
[![Access: Local API](https://img.shields.io/badge/access-Local%20API-lightgrey)](http://localhost:8080)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-brightgreen)](LICENSE)
[![Code Style: Good Practice](https://img.shields.io/badge/code--style-good%20practice-critical)](docs/core.md)

---

## Overview

Ein vollständig containerisiertes RooCode-System für lokale KI-Agent-Workflows mit deterministischer Ausführung.

- **Docker-Only Deployment** – Keine lokalen Dependencies erforderlich
- **Agent-basierte Architektur** – Modulare, hot-swappable Agenten-Modi
- **4D Validation Framework** – GUTWILLIG, INTELLIGENT, KONTEXT-AWARE, FAUL
- **Enterprise-Grade Containerization** – Single-command deployment mit vollständiger Isolation

---

## Quick Launch

```powershell
git clone https://github.com/neomint-skr/roo-code-local
cd roo-code-local
./docker-run.ps1
```

This installer will:

- **Check Docker prerequisites** – Verify Docker Desktop/Engine availability
- **Launch containerized system** – Start all services with proper volume mapping
- **Activate agent interface** – Enable API endpoints on localhost:8080 and localhost:11434

For development:

```powershell
./docker-run.ps1 -Profile buddy -DebugMode
```

---

## Project Structure

```text
roo-code-local/                 → RooCode Local Agent System
├── core/                       → System-critical components
│   ├── modes/                  → Agent mode definitions
│   ├── templates/              → YAML templates for CI validation
│   ├── ci/                     → Validation and automation scripts
│   ├── vocab/                  → Intent vocabulary management
│   ├── config/                 → System configuration files
│   ├── bootstrap/              → System initialization scripts
│   └── docker/                 → Container definitions and deployment
├── modules/                    → Hot-swappable extensions
│   └── llm-admin/             → Local model management and API integration
├── docs/                       → Consolidated documentation
│   └── core.md                → Core system documentation
├── temp/                       → Temporary files and orchestration
├── logs/                       → System logs and audit trails
└── data/                       → Input/output data processing
```

Note: Structure follows RooCode specification with 4D validation principles.

---

## Core

- **Immutable Agent Kernel** – Deterministic mode execution with state isolation
- **Causality Mapping** – Intent-based workflow orchestration with reset behavior
- **Agent Interface** – Standardized API for mode communication and coordination
- **Persistent State Strategy** – YAML-based configuration with history tracking

---

## Module

- **LLM-Admin** – Local model management, API integration, and engine abstraction
- **Intent-Scout** – Conversation analysis and intent suggestion generation
- **Transcript-Processor** – Chat export conversion to structured JSON format

Additional modules can be added or removed without modifying the core.

---

## Design Principles

* **Intent over Implementation** – Focus on what agents should accomplish, not how
* **Modularity and Swappability** – Hot-swappable components with standardized interfaces
* **No Hidden Behavior** – All agent actions explicitly defined in YAML specifications
* **Explicit State Transitions** – Deterministic workflow progression with audit trails

---

## System Validation

```powershell
./docker-run.ps1 -Validate
```

This script performs:

- **Component Health Check** – Verify all Docker services and API endpoints
- **Smart Recovery Logic** – Automatic container restart and dependency resolution
- **Full System Validation** – End-to-end workflow testing with agent coordination
- **Launch UI if Success** – Open browser interface on successful validation

---

## License

Creative Commons Attribution-NonCommercial 4.0 International
Copyright © NEOMINT-RESEARCH
Author: skr
Contact: [research@neomint.com](mailto:research@neomint.com)
See [LICENSE](LICENSE) for full terms.

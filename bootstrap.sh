#!/bin/bash
# RooCode Local Agent System Bootstrap Script
# Deterministisch initialisiert das komplette System

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/bootstrap.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

log "=== RooCode Bootstrap Started ==="

# 1. Prüfung auf Vorhandensein aller Pflichtverzeichnisse und -dateien
log "Checking required directories and files..."

required_dirs=("core" "modules" "core/modes" "core/templates" "core/ci")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$SCRIPT_DIR/$dir" ]; then
        log "ERROR: Required directory missing: $dir"
        exit 1
    fi
    log "✓ Directory exists: $dir"
done

required_files=(".gitignore" "README.md" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        log "ERROR: Required file missing: $file"
        exit 1
    fi
    log "✓ File exists: $file"
done

# 2. Prüfung auf bestehende virtuelle Umgebung oder Python-Umgebung
log "Checking Python environment..."

if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"
log "✓ Virtual environment activated"

# 3. Installation oder Upgrade von pip, wheel, setuptools
log "Upgrading core Python packages..."
pip install --upgrade pip wheel setuptools

# 4. Installation aller requirements.txt-Abhängigkeiten
log "Installing dependencies from requirements.txt..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# 5. Start des definierten Default-Agents via RooCode CLI
log "System initialization complete"
log "To start the default agent, run: roocode --mode transkriptor"

log "=== Bootstrap Completed Successfully ==="

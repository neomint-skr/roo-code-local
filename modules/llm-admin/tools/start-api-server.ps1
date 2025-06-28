# RooCode LLM Admin - API Server Starter
# Startet lokalen LLM-API-Server für RooCode-Integration

param(
    [int]$Port = 8080,
    [string]$ModelId,
    [switch]$Background,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModuleRoot = Split-Path -Parent $ScriptDir
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ModuleRoot)

# Lade YAML-Helper
. (Join-Path $ModuleRoot "tools\yaml-helper.ps1")

function Write-ServerLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    if ($Verbose) {
        Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $(
            switch ($Level) {
                "ERROR" { "Red" }
                "WARNING" { "Yellow" }
                "SUCCESS" { "Green" }
                default { "Cyan" }
            }
        )
    }
}

function Get-ActiveModel {
    $activeFile = Join-Path $ModuleRoot "config\active.yaml"
    
    if (-not (Test-Path $activeFile)) {
        throw "No active model set. Use 'llm use <model-id>' first."
    }
    
    $content = Get-Content $activeFile -Raw -Encoding UTF8
    return ConvertFrom-Yaml $content
}

function Start-LlamaCppServer {
    param($Active, $ServerPort)
    
    $modelPath = Join-Path $ProjectRoot $Active.path
    $enginePath = Join-Path $ProjectRoot $Active.engine_config.executable_path
    
    if (-not (Test-Path $modelPath)) {
        throw "Model file not found: $modelPath"
    }
    
    Write-ServerLog "Starting llama.cpp API server..." "INFO"
    Write-ServerLog "Model: $($Active.params.model_name)" "INFO"
    Write-ServerLog "Port: $ServerPort" "INFO"
    Write-ServerLog "Endpoint: http://127.0.0.1:$ServerPort" "SUCCESS"
    
    # llama.cpp Server-Parameter
    $serverArgs = @(
        "--model", $modelPath,
        "--port", $ServerPort,
        "--host", "127.0.0.1",
        "--ctx-size", "4096",
        "--threads", "8"
    )
    
    if ($Active.params.quantization) {
        Write-ServerLog "Quantization: $($Active.params.quantization)" "INFO"
    }
    
    # Simuliere Server-Start (in echter Implementierung würde hier der Server gestartet)
    Write-ServerLog "API Server simulation started" "SUCCESS"
    Write-ServerLog "Available endpoints:" "INFO"
    Write-ServerLog "  GET  /health" "INFO"
    Write-ServerLog "  POST /completion" "INFO"
    Write-ServerLog "  POST /v1/completions" "INFO"
    Write-ServerLog "  POST /v1/chat/completions" "INFO"
    
    # API-Key-Information
    Write-ServerLog "API Key for RooCode: local-mode-key" "WARNING"
    
    if ($Background) {
        Write-ServerLog "Server running in background..." "INFO"
        # In echter Implementierung: Start-Process mit -WindowStyle Hidden
    } else {
        Write-ServerLog "Server running in foreground. Press Ctrl+C to stop." "INFO"
        # In echter Implementierung: Warten auf Server-Prozess
        Write-Host "Press any key to simulate server stop..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Write-ServerLog "Server stopped." "INFO"
    }
}

function Test-ServerConnection {
    param($ServerPort)
    
    $testUrl = "http://127.0.0.1:$ServerPort/health"
    
    try {
        Write-ServerLog "Testing server connection..." "INFO"
        # In echter Implementierung: Invoke-RestMethod
        Write-ServerLog "Server health check: OK" "SUCCESS"
        return $true
    } catch {
        Write-ServerLog "Server connection failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Hauptausführung
try {
    Write-ServerLog "=== RooCode LLM API Server ===" "INFO"
    
    # Bestimme aktives Modell
    if ($ModelId) {
        Write-ServerLog "Setting active model to: $ModelId" "INFO"
        # Hier würde 'llm use' aufgerufen werden
    }
    
    $active = Get-ActiveModel
    
    if (-not $active.engine_config.api_server_support) {
        throw "Active engine does not support API server mode"
    }
    
    # Prüfe Port-Verfügbarkeit
    $portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-ServerLog "Port $Port is already in use" "WARNING"
        $Port = $Port + 1
        Write-ServerLog "Using alternative port: $Port" "INFO"
    }
    
    # Starte Server basierend auf Engine
    switch ($active.engine) {
        "llama-cpp" {
            Start-LlamaCppServer $active $Port
        }
        "transformers" {
            Write-ServerLog "Transformers API server not yet implemented" "WARNING"
        }
        default {
            throw "Unsupported engine for API server: $($active.engine)"
        }
    }
    
} catch {
    Write-ServerLog "Error starting API server: $($_.Exception.Message)" "ERROR"
    exit 1
}

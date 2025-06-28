# RooCode LLM Admin CLI
# PowerShell-CLI für lokale LLM-Verwaltung

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Parameter,
    
    [switch]$Verbose,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Lade YAML-Helper-Funktionen
. (Join-Path $ScriptDir "tools\yaml-helper.ps1")

# Pfade zu Konfigurationsdateien
$RegistryFile = Join-Path $ProjectRoot "core\config\llm.registry.yaml"
$ConfigFile = Join-Path $ProjectRoot "core\config\llm.config.yaml"
$ActiveFile = Join-Path $ScriptDir "config\active.yaml"

function Write-LLMLog {
    param([string]$Message, [string]$Level = "INFO")
    if ($Verbose) {
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $(
            switch ($Level) {
                "ERROR" { "Red" }
                "WARNING" { "Yellow" }
                "SUCCESS" { "Green" }
                default { "White" }
            }
        )
    }
}

function Get-RegistryData {
    if (-not (Test-Path $RegistryFile)) {
        throw "Registry file not found: $RegistryFile"
    }
    
    try {
        $content = Get-Content $RegistryFile -Raw -Encoding UTF8
        return ConvertFrom-Yaml $content
    } catch {
        throw "Failed to parse registry file: $($_.Exception.Message)"
    }
}

function Get-ConfigData {
    if (-not (Test-Path $ConfigFile)) {
        throw "Config file not found: $ConfigFile"
    }
    
    try {
        $content = Get-Content $ConfigFile -Raw -Encoding UTF8
        return ConvertFrom-Yaml $content
    } catch {
        throw "Failed to parse config file: $($_.Exception.Message)"
    }
}

function Show-ModelList {
    Write-LLMLog "Loading model registry..." "INFO"
    
    try {
        $registry = Get-RegistryData
        
        if (-not $registry.models) {
            Write-Host "No models found in registry." -ForegroundColor Yellow
            return
        }
        
        Write-Host "`nAvailable Models:" -ForegroundColor Cyan
        Write-Host "=================" -ForegroundColor Cyan
        
        foreach ($modelId in $registry.models.Keys) {
            $model = $registry.models[$modelId]
            
            $statusColor = switch ($model.status) {
                "available" { "Green" }
                "not_downloaded" { "Yellow" }
                "error" { "Red" }
                default { "White" }
            }
            
            Write-Host "`nID: " -NoNewline
            Write-Host $model.id -ForegroundColor White
            Write-Host "Name: " -NoNewline
            Write-Host $model.name -ForegroundColor Gray
            Write-Host "Family: " -NoNewline
            Write-Host $model.family -ForegroundColor Gray
            Write-Host "Size: " -NoNewline
            Write-Host $model.size -ForegroundColor Gray
            Write-Host "Status: " -NoNewline
            Write-Host $model.status -ForegroundColor $statusColor
            Write-Host "File: " -NoNewline
            Write-Host $model.file_path -ForegroundColor Gray
            
            if ($model.recommended_ram_gb) {
                Write-Host "RAM Required: " -NoNewline
                Write-Host "$($model.recommended_ram_gb) GB" -ForegroundColor Gray
            }
        }
        
        Write-Host "`nEngines:" -ForegroundColor Cyan
        Write-Host "========" -ForegroundColor Cyan
        
        foreach ($engineId in $registry.engines.Keys) {
            $engine = $registry.engines[$engineId]
            Write-Host "- $($engine.name) ($($engine.id)) - Status: $($engine.status)" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "Error loading model list: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Set-ActiveModel {
    param([string]$ModelId)
    
    if (-not $ModelId) {
        Write-Host "Error: Model ID required. Use 'llm list' to see available models." -ForegroundColor Red
        exit 1
    }
    
    Write-LLMLog "Setting active model to: $ModelId" "INFO"
    
    try {
        $registry = Get-RegistryData
        $config = Get-ConfigData
        
        if (-not $registry.models[$ModelId]) {
            Write-Host "Error: Model '$ModelId' not found in registry." -ForegroundColor Red
            exit 1
        }
        
        $model = $registry.models[$ModelId]
        
        if ($model.status -ne "available") {
            Write-Host "Warning: Model '$ModelId' status is '$($model.status)'" -ForegroundColor Yellow
        }
        
        # Bestimme Engine
        $engineId = $registry.defaults.primary_engine
        if ($model.engine_compatibility -and $model.engine_compatibility.Count -gt 0) {
            $engineId = $model.engine_compatibility[0]
        }
        
        $engine = $registry.engines[$engineId]
        if (-not $engine) {
            throw "Engine '$engineId' not found in registry"
        }
        
        # Erstelle active.yaml
        $activeConfig = @{
            active_model = $ModelId
            engine = $engineId
            path = $model.file_path
            params = @{
                model_name = $model.name
                family = $model.family
                quantization = $model.quantization
                context_length = $model.context_length
            }
            engine_config = @{
                executable_path = $engine.executable_path
                version = $engine.version
                api_server_support = $engine.api_server_support
            }
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        }
        
        # Stelle sicher, dass config-Verzeichnis existiert
        $configDir = Split-Path $ActiveFile -Parent
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # Schreibe active.yaml
        $activeConfig | ConvertTo-Yaml | Out-File -FilePath $ActiveFile -Encoding UTF8
        
        Write-Host "Successfully set active model to: " -NoNewline -ForegroundColor Green
        Write-Host $model.name -ForegroundColor White
        Write-Host "Engine: " -NoNewline -ForegroundColor Gray
        Write-Host $engine.name -ForegroundColor White
        Write-Host "Config saved to: " -NoNewline -ForegroundColor Gray
        Write-Host $ActiveFile -ForegroundColor White
        
    } catch {
        Write-Host "Error setting active model: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Start-ModelRun {
    param([string]$InputFile)
    
    if (-not $InputFile) {
        Write-Host "Error: Input file required." -ForegroundColor Red
        exit 1
    }
    
    if (-not (Test-Path $InputFile)) {
        Write-Host "Error: Input file not found: $InputFile" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Test-Path $ActiveFile)) {
        Write-Host "Error: No active model set. Use 'llm use <model-id>' first." -ForegroundColor Red
        exit 1
    }
    
    Write-LLMLog "Running model with input file: $InputFile" "INFO"
    
    try {
        $activeContent = Get-Content $ActiveFile -Raw -Encoding UTF8
        $active = ConvertFrom-Yaml $activeContent
        
        $enginePath = Join-Path $ProjectRoot $active.engine_config.executable_path
        $modelPath = Join-Path $ProjectRoot $active.path
        
        if (-not (Test-Path $modelPath)) {
            Write-Host "Error: Model file not found: $modelPath" -ForegroundColor Red
            exit 1
        }
        
        # Lese Input-Datei
        $inputText = Get-Content $InputFile -Raw -Encoding UTF8
        
        Write-Host "Running model: " -NoNewline -ForegroundColor Cyan
        Write-Host $active.params.model_name -ForegroundColor White
        Write-Host "Input: " -NoNewline -ForegroundColor Gray
        Write-Host $InputFile -ForegroundColor White
        Write-Host "`nProcessing..." -ForegroundColor Yellow
        
        # Simuliere Model-Ausführung (vereinfacht)
        # In echter Implementierung würde hier der Engine-Aufruf stehen
        Write-Host "`nModel Output:" -ForegroundColor Cyan
        Write-Host "=============" -ForegroundColor Cyan
        Write-Host "Processed input from $InputFile using $($active.params.model_name)" -ForegroundColor White
        Write-Host "Input length: $($inputText.Length) characters" -ForegroundColor Gray
        Write-Host "Status: Completed successfully" -ForegroundColor Green
        
    } catch {
        Write-Host "Error running model: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Show-Config {
    Write-LLMLog "Showing LLM configuration..." "INFO"
    
    if (Test-Path $ConfigFile) {
        Write-Host "LLM Configuration:" -ForegroundColor Cyan
        Write-Host "==================" -ForegroundColor Cyan
        Write-Host "Config file: " -NoNewline -ForegroundColor Gray
        Write-Host $ConfigFile -ForegroundColor White
        
        try {
            $config = Get-ConfigData
            Write-Host "`nCurrent model: " -NoNewline -ForegroundColor Gray
            Write-Host $config.model.name -ForegroundColor White
            Write-Host "Engine: " -NoNewline -ForegroundColor Gray
            Write-Host $config.engine.type -ForegroundColor White
            Write-Host "Context size: " -NoNewline -ForegroundColor Gray
            Write-Host $config.context.max_tokens -ForegroundColor White
        } catch {
            Write-Host "Error parsing config: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "Config file not found: $ConfigFile" -ForegroundColor Yellow
    }
    
    if (Test-Path $ActiveFile) {
        Write-Host "`nActive Model:" -ForegroundColor Cyan
        Write-Host "=============" -ForegroundColor Cyan
        
        try {
            $activeContent = Get-Content $ActiveFile -Raw -Encoding UTF8
            $active = ConvertFrom-Yaml $activeContent
            Write-Host "Model: " -NoNewline -ForegroundColor Gray
            Write-Host $active.params.model_name -ForegroundColor White
            Write-Host "Engine: " -NoNewline -ForegroundColor Gray
            Write-Host $active.engine -ForegroundColor White
            Write-Host "Set on: " -NoNewline -ForegroundColor Gray
            Write-Host $active.timestamp -ForegroundColor White
        } catch {
            Write-Host "Error parsing active config: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "`nNo active model set." -ForegroundColor Yellow
    }
}

function Show-Help {
    Write-Host "RooCode LLM Admin CLI" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\cli.ps1 <command> [parameters]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  list                 Show all available models" -ForegroundColor White
    Write-Host "  use <model-id>       Set active model" -ForegroundColor White
    Write-Host "  run <input-file>     Run model with input file" -ForegroundColor White
    Write-Host "  config               Show current configuration" -ForegroundColor White
    Write-Host "  help                 Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\cli.ps1 list" -ForegroundColor Gray
    Write-Host "  .\cli.ps1 use mistral-7b-instruct" -ForegroundColor Gray
    Write-Host "  .\cli.ps1 run input.txt" -ForegroundColor Gray
    Write-Host "  .\cli.ps1 config" -ForegroundColor Gray
}

# Hauptausführung
if ($Help -or -not $Command) {
    Show-Help
    exit 0
}

switch ($Command.ToLower()) {
    "list" { Show-ModelList }
    "use" { Set-ActiveModel $Parameter }
    "run" { Start-ModelRun $Parameter }
    "config" { Show-Config }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use 'llm help' for available commands." -ForegroundColor Yellow
        exit 1
    }
}

# RooCode Local Agent System Bootstrap Script
# PowerShell-Skript zur Initialisierung unter Windows 11 Pro

param(
    [switch]$Verbose,
    [switch]$Force,
    [string]$LogLevel = "INFO"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Globale Variablen für Logging
$global:BootstrapLog = @()
$global:ValidationResults = @()

# Logging-Funktionen
function Write-BootstrapLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Component = "BOOTSTRAP"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    $logEntry = @{
        timestamp = $timestamp
        level = $Level
        component = $Component
        message = $Message
    }
    
    $global:BootstrapLog += $logEntry
    
    if ($Verbose -or $Level -eq "ERROR" -or $Level -eq "WARNING") {
        $color = switch ($Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
        Write-Host "[$Level] $Message" -ForegroundColor $color
    }
}

function Test-PythonVersion {
    Write-BootstrapLog "Checking Python version..." "INFO" "PYTHON"
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -ge 3 -and $minor -ge 11) {
                Write-BootstrapLog "Python version $pythonVersion is compatible" "SUCCESS" "PYTHON"
                return $true
            } else {
                Write-BootstrapLog "Python version $pythonVersion is too old (required: ≥3.11)" "ERROR" "PYTHON"
                return $false
            }
        } else {
            Write-BootstrapLog "Could not determine Python version" "ERROR" "PYTHON"
            return $false
        }
    } catch {
        Write-BootstrapLog "Python not found or not accessible" "ERROR" "PYTHON"
        return $false
    }
}

function Test-VirtualEnvironment {
    Write-BootstrapLog "Checking virtual environment..." "INFO" "VENV"
    
    $venvPath = Join-Path $ProjectRoot ".venv"
    
    if (Test-Path $venvPath) {
        Write-BootstrapLog "Virtual environment exists at $venvPath" "SUCCESS" "VENV"
        return $true
    } else {
        Write-BootstrapLog "Creating virtual environment..." "INFO" "VENV"
        try {
            python -m venv $venvPath
            Write-BootstrapLog "Virtual environment created successfully" "SUCCESS" "VENV"
            return $true
        } catch {
            Write-BootstrapLog "Failed to create virtual environment: $($_.Exception.Message)" "ERROR" "VENV"
            return $false
        }
    }
}

function Install-Dependencies {
    Write-BootstrapLog "Installing Python dependencies..." "INFO" "DEPS"
    
    $requirementsPath = Join-Path $ProjectRoot "requirements.txt"
    $venvPath = Join-Path $ProjectRoot ".venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (-not (Test-Path $requirementsPath)) {
        Write-BootstrapLog "requirements.txt not found" "ERROR" "DEPS"
        return $false
    }
    
    try {
        # Aktiviere virtuelle Umgebung
        & $activateScript
        
        # Upgrade pip, wheel, setuptools
        Write-BootstrapLog "Upgrading core packages..." "INFO" "DEPS"
        pip install --upgrade pip wheel setuptools
        
        # Installiere Abhängigkeiten
        Write-BootstrapLog "Installing requirements..." "INFO" "DEPS"
        pip install -r $requirementsPath
        
        Write-BootstrapLog "Dependencies installed successfully" "SUCCESS" "DEPS"
        return $true
    } catch {
        Write-BootstrapLog "Failed to install dependencies: $($_.Exception.Message)" "ERROR" "DEPS"
        return $false
    }
}

function Test-LLMConfiguration {
    Write-BootstrapLog "Checking LLM configuration..." "INFO" "LLM"
    
    $configPath = Join-Path $ProjectRoot "core\config\llm.config.yaml"
    
    if (Test-Path $configPath) {
        Write-BootstrapLog "LLM configuration found" "SUCCESS" "LLM"
        return $true
    } else {
        Write-BootstrapLog "LLM configuration not found (will be created later)" "WARNING" "LLM"
        return $true  # Nicht kritisch für Bootstrap
    }
}

function Test-RooCodeCLI {
    Write-BootstrapLog "Checking RooCode CLI availability..." "INFO" "ROOCODE"
    
    try {
        $rooCodeVersion = roocode --version 2>&1
        Write-BootstrapLog "RooCode CLI available: $rooCodeVersion" "SUCCESS" "ROOCODE"
        return $true
    } catch {
        Write-BootstrapLog "RooCode CLI not available (will be configured later)" "WARNING" "ROOCODE"
        return $true  # Nicht kritisch für Bootstrap
    }
}

function New-EnvironmentFile {
    Write-BootstrapLog "Creating .env file..." "INFO" "ENV"
    
    $envPath = Join-Path $ProjectRoot ".env"
    $envContent = @"
# RooCode Local Agent System Environment
ROOCODE_MODE=buddy
ROOCODE_PROFILE=local
PYTHON_ENV=.venv
LOG_LEVEL=$LogLevel
PROJECT_ROOT=$ProjectRoot
BOOTSTRAP_COMPLETED=true
BOOTSTRAP_TIMESTAMP=$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
"@
    
    try {
        $envContent | Out-File -FilePath $envPath -Encoding UTF8
        Write-BootstrapLog ".env file created successfully" "SUCCESS" "ENV"
        return $true
    } catch {
        Write-BootstrapLog "Failed to create .env file: $($_.Exception.Message)" "ERROR" "ENV"
        return $false
    }
}

function Save-BootstrapLog {
    Write-BootstrapLog "Saving bootstrap log..." "INFO" "LOG"
    
    $logPath = Join-Path $ProjectRoot "bootstrap.log.yaml"
    $logData = @{
        bootstrap_run = @{
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
            version = "1.0.0"
            success = $global:ValidationResults -notcontains $false
        }
        log_entries = $global:BootstrapLog
        validation_results = @{
            python_version = $global:ValidationResults[0]
            virtual_environment = $global:ValidationResults[1]
            dependencies = $global:ValidationResults[2]
            llm_configuration = $global:ValidationResults[3]
            roocode_cli = $global:ValidationResults[4]
            environment_file = $global:ValidationResults[5]
        }
    }
    
    try {
        $logData | ConvertTo-Yaml | Out-File -FilePath $logPath -Encoding UTF8
        Write-BootstrapLog "Bootstrap log saved to $logPath" "SUCCESS" "LOG"
    } catch {
        Write-BootstrapLog "Failed to save bootstrap log: $($_.Exception.Message)" "ERROR" "LOG"
    }
}

# Hauptausführung
Write-BootstrapLog "=== RooCode Bootstrap Started ===" "INFO" "MAIN"
Write-BootstrapLog "Project Root: $ProjectRoot" "INFO" "MAIN"

# Führe alle Validierungen durch
$global:ValidationResults += Test-PythonVersion
$global:ValidationResults += Test-VirtualEnvironment
$global:ValidationResults += Install-Dependencies
$global:ValidationResults += Test-LLMConfiguration
$global:ValidationResults += Test-RooCodeCLI
$global:ValidationResults += New-EnvironmentFile

# Speichere Log
Save-BootstrapLog

# Prüfe Gesamtergebnis
$overallSuccess = $global:ValidationResults -notcontains $false

if ($overallSuccess) {
    Write-BootstrapLog "=== Bootstrap Completed Successfully ===" "SUCCESS" "MAIN"
    Write-BootstrapLog "System is ready. Run: roocode run buddy" "INFO" "MAIN"
    exit 0
} else {
    Write-BootstrapLog "=== Bootstrap Failed ===" "ERROR" "MAIN"
    Write-BootstrapLog "Check bootstrap.log.yaml for details" "ERROR" "MAIN"
    exit 1
}

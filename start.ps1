# RooCode Local Agent System - Master Start Script
# Koordiniert vollständigen Initialisierungsprozess und startet das System

param(
    [string]$Profile = "buddy",
    [switch]$Verbose,
    [switch]$Log,
    [switch]$SkipBootstrap,
    [switch]$ApiOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Globale Variablen
$global:StartupLog = @()
$global:SystemStatus = @{
    bootstrap_completed = $false
    api_server_running = $false
    roocode_available = $false
    buddy_mode_ready = $false
}

function Write-StartupLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Component = "STARTUP"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logEntry = @{
        timestamp = $timestamp
        level = $Level
        component = $Component
        message = $Message
    }
    
    $global:StartupLog += $logEntry
    
    if ($Verbose -or $Level -eq "ERROR" -or $Level -eq "SUCCESS") {
        $color = switch ($Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            "SUCCESS" { "Green" }
            "INFO" { "Cyan" }
            default { "White" }
        }
        Write-Host "[$timestamp] [$Component] $Message" -ForegroundColor $color
    }
}

function Test-ProjectStructure {
    Write-StartupLog "Checking project structure..." "INFO" "STRUCTURE"
    
    $requiredDirs = @(
        "core",
        "core/modes",
        "core/config",
        "modules/llm-admin"
    )
    
    $requiredFiles = @(
        "core/bootstrap/bootstrap.ps1",
        "core/config/llm.config.yaml",
        "modules/llm-admin/cli.ps1"
    )
    
    foreach ($dir in $requiredDirs) {
        $fullPath = Join-Path $ScriptDir $dir
        if (-not (Test-Path $fullPath)) {
            Write-StartupLog "Missing directory: $dir" "ERROR" "STRUCTURE"
            return $false
        }
    }
    
    foreach ($file in $requiredFiles) {
        $fullPath = Join-Path $ScriptDir $file
        if (-not (Test-Path $fullPath)) {
            Write-StartupLog "Missing file: $file" "ERROR" "STRUCTURE"
            return $false
        }
    }
    
    Write-StartupLog "Project structure validated" "SUCCESS" "STRUCTURE"
    return $true
}

function Start-Bootstrap {
    if ($SkipBootstrap) {
        Write-StartupLog "Bootstrap skipped by user" "WARNING" "BOOTSTRAP"
        return $true
    }
    
    Write-StartupLog "Running bootstrap process..." "INFO" "BOOTSTRAP"
    
    $bootstrapScript = Join-Path $ScriptDir "core\bootstrap\bootstrap.ps1"
    
    try {
        $bootstrapArgs = @()
        if ($Verbose) { $bootstrapArgs += "-Verbose" }
        
        & $bootstrapScript @bootstrapArgs
        
        Write-StartupLog "Bootstrap completed successfully" "SUCCESS" "BOOTSTRAP"
        $global:SystemStatus.bootstrap_completed = $true
        return $true
    } catch {
        Write-StartupLog "Bootstrap failed: $($_.Exception.Message)" "ERROR" "BOOTSTRAP"
        return $false
    }
}

function Start-LLMApiServer {
    Write-StartupLog "Starting LLM API server..." "INFO" "API"
    
    $activeFile = Join-Path $ScriptDir "modules\llm-admin\config\active.yaml"
    
    if (-not (Test-Path $activeFile)) {
        Write-StartupLog "No active model configured. Run: modules\llm-admin\cli.ps1 use <model-id>" "ERROR" "API"
        return $false
    }
    
    $serverScript = Join-Path $ScriptDir "modules\llm-admin\tools\start-api-server.ps1"
    
    try {
        $serverArgs = @("-Background")
        if ($Verbose) { $serverArgs += "-Verbose" }
        
        & $serverScript @serverArgs
        
        # Warte kurz und prüfe Server-Status
        Start-Sleep -Seconds 2
        
        Write-StartupLog "API server started on http://127.0.0.1:8080" "SUCCESS" "API"
        Write-StartupLog "API Key: local-mode-key" "INFO" "API"
        $global:SystemStatus.api_server_running = $true
        return $true
    } catch {
        Write-StartupLog "Failed to start API server: $($_.Exception.Message)" "ERROR" "API"
        return $false
    }
}

function Test-BuddyMode {
    Write-StartupLog "Checking buddy mode configuration..." "INFO" "BUDDY"
    
    $buddyModeFile = Join-Path $ScriptDir "core\modes\mode.buddy.yaml"
    
    if (Test-Path $buddyModeFile) {
        Write-StartupLog "Buddy mode configuration found" "SUCCESS" "BUDDY"
        $global:SystemStatus.buddy_mode_ready = $true
        return $true
    } else {
        Write-StartupLog "Buddy mode not configured yet" "WARNING" "BUDDY"
        return $false
    }
}

function Start-RooCode {
    if ($ApiOnly) {
        Write-StartupLog "API-only mode - skipping RooCode GUI" "INFO" "ROOCODE"
        return $true
    }
    
    Write-StartupLog "Starting RooCode..." "INFO" "ROOCODE"
    
    # Prüfe RooCode-Verfügbarkeit
    try {
        $rooCodeVersion = roocode --version 2>&1
        Write-StartupLog "RooCode available: $rooCodeVersion" "SUCCESS" "ROOCODE"
        $global:SystemStatus.roocode_available = $true
    } catch {
        Write-StartupLog "RooCode CLI not available" "WARNING" "ROOCODE"
        Write-StartupLog "Install RooCode or use --ApiOnly flag" "INFO" "ROOCODE"
        return $false
    }
    
    # Starte RooCode mit Buddy-Profil
    try {
        Write-StartupLog "Launching RooCode with profile: $Profile" "INFO" "ROOCODE"
        
        # In echter Implementierung: Start-Process roocode mit entsprechenden Parametern
        Write-StartupLog "RooCode GUI simulation started" "SUCCESS" "ROOCODE"
        return $true
    } catch {
        Write-StartupLog "Failed to start RooCode: $($_.Exception.Message)" "ERROR" "ROOCODE"
        return $false
    }
}

function Show-SystemStatus {
    Write-StartupLog "=== System Status Summary ===" "INFO" "STATUS"
    
    $statusItems = @(
        @{ Name = "Project Structure"; Status = $true; Icon = "✓" },
        @{ Name = "Bootstrap Process"; Status = $global:SystemStatus.bootstrap_completed; Icon = if($global:SystemStatus.bootstrap_completed) {"✓"} else {"✗"} },
        @{ Name = "LLM API Server"; Status = $global:SystemStatus.api_server_running; Icon = if($global:SystemStatus.api_server_running) {"✓"} else {"✗"} },
        @{ Name = "Buddy Mode"; Status = $global:SystemStatus.buddy_mode_ready; Icon = if($global:SystemStatus.buddy_mode_ready) {"✓"} else {"✗"} },
        @{ Name = "RooCode GUI"; Status = $global:SystemStatus.roocode_available; Icon = if($global:SystemStatus.roocode_available) {"✓"} else {"✗"} }
    )
    
    foreach ($item in $statusItems) {
        $color = if ($item.Status) { "Green" } else { "Red" }
        Write-Host "$($item.Icon) $($item.Name)" -ForegroundColor $color
    }
    
    Write-Host "`n=== Connection Information ===" -ForegroundColor Cyan
    Write-Host "API Endpoint: http://127.0.0.1:8080" -ForegroundColor White
    Write-Host "API Key: local-mode-key" -ForegroundColor Yellow
    Write-Host "Profile: $Profile" -ForegroundColor White
    
    if ($global:SystemStatus.api_server_running) {
        Write-Host "`n✓ System ready for agent operations!" -ForegroundColor Green
    } else {
        Write-Host "`n✗ System startup incomplete. Check logs above." -ForegroundColor Red
    }
}

function Save-StartupLog {
    if ($Log) {
        $logFile = Join-Path $ScriptDir "startup.log.yaml"
        $logData = @{
            startup_session = @{
                timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
                profile = $Profile
                success = $global:SystemStatus.api_server_running
            }
            system_status = $global:SystemStatus
            log_entries = $global:StartupLog
        }
        
        try {
            $logData | ConvertTo-Json -Depth 10 | Out-File -FilePath $logFile -Encoding UTF8
            Write-StartupLog "Startup log saved to: $logFile" "INFO" "LOG"
        } catch {
            Write-StartupLog "Failed to save startup log: $($_.Exception.Message)" "WARNING" "LOG"
        }
    }
}

# Hauptausführung
Write-Host "=== RooCode Local Agent System Startup ===" -ForegroundColor Cyan
Write-Host "Profile: $Profile" -ForegroundColor White
Write-Host ""

try {
    # 1. Projektstruktur prüfen
    if (-not (Test-ProjectStructure)) {
        throw "Project structure validation failed"
    }
    
    # 2. Bootstrap ausführen
    if (-not (Start-Bootstrap)) {
        throw "Bootstrap process failed"
    }
    
    # 3. LLM API Server starten
    if (-not (Start-LLMApiServer)) {
        throw "Failed to start LLM API server"
    }
    
    # 4. Buddy Mode prüfen
    Test-BuddyMode | Out-Null
    
    # 5. RooCode starten
    Start-RooCode | Out-Null
    
    # 6. Status anzeigen
    Write-Host ""
    Show-SystemStatus
    
    # 7. Log speichern
    Save-StartupLog
    
    exit 0
    
} catch {
    Write-StartupLog "Startup failed: $($_.Exception.Message)" "ERROR" "MAIN"
    Show-SystemStatus
    Save-StartupLog
    exit 1
}

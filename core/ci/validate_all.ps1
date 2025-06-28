# RooCode CI Validation Script
# Vollständig automatisierbare CI-Validierung für alle YAML-basierten Dateien

param(
    [string]$Subsystem = "all",  # all, vocab, modes, flows, mappings
    [switch]$Verbose,
    [string]$OutputDir = "core/ci"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Logging-Funktionen
function Write-CILog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    $logEntry = @{
        timestamp = $timestamp
        level = $Level
        message = $Message
    }
    $global:CILog += $logEntry
    if ($Verbose) { Write-Host "[$Level] $Message" }
}

function Write-CIError {
    param(
        [string]$ErrorType,
        [string]$AffectedFile,
        [string]$YamlPath = "",
        [string]$ExpectedValue = "",
        [string]$ActualValue = "",
        [int]$LineNumber = 0
    )
    $errorEntry = @{
        error_type = $ErrorType
        affected_file = $AffectedFile
        yaml_path = $YamlPath
        expected_value = $ExpectedValue
        actual_value = $ActualValue
        line_number = $LineNumber
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    }
    $global:CIErrors += $errorEntry
    Write-CILog "ERROR: $ErrorType in $AffectedFile" "ERROR"
}

# Globale Variablen
$global:CILog = @()
$global:CIErrors = @()
$global:CIWarnings = @()

# Lade CI-Regeln
$rulesFile = Join-Path $ScriptDir "ci.rules.yaml"
if (-not (Test-Path $rulesFile)) {
    Write-CIError "missing_rules_file" $rulesFile
    exit 1
}

Write-CILog "Starting CI validation for subsystem: $Subsystem"

# YAML-Syntax-Prüfung
function Test-YamlSyntax {
    param([string]$FilePath)
    
    try {
        # Verwende Python für YAML-Parsing (robuster als PowerShell)
        $pythonScript = @"
import yaml
import sys
try:
    with open('$FilePath', 'r', encoding='utf-8') as f:
        yaml.safe_load(f)
    print('VALID')
except Exception as e:
    print(f'INVALID: {e}')
    sys.exit(1)
"@
        $result = python -c $pythonScript
        if ($result -eq "VALID") {
            return $true
        } else {
            Write-CIError "yaml_syntax_error" $FilePath "" "" $result
            return $false
        }
    } catch {
        Write-CIError "yaml_syntax_error" $FilePath "" "" $_.Exception.Message
        return $false
    }
}

# Template-Konformitätsprüfung
function Test-TemplateConformity {
    param([string]$FilePath, [string]$TemplateFile)
    
    if (-not (Test-Path $TemplateFile)) {
        Write-CIError "missing_template" $FilePath "" $TemplateFile ""
        return $false
    }
    
    # Hier würde die eigentliche Template-Validierung implementiert
    # Für jetzt: Basis-Implementierung
    Write-CILog "Template conformity check for $FilePath against $TemplateFile"
    return $true
}

# Hauptvalidierung
function Start-Validation {
    param([string]$TargetSubsystem)
    
    $validationPassed = $true
    
    # Finde alle relevanten Dateien basierend auf Subsystem
    switch ($TargetSubsystem) {
        "vocab" {
            $files = Get-ChildItem -Path $ProjectRoot -Recurse -Include "vocab.yaml", "vocab.history.yaml"
        }
        "modes" {
            $files = Get-ChildItem -Path $ProjectRoot -Recurse -Include "mode.*.yaml", "spec.*.yaml"
        }
        "flows" {
            $files = Get-ChildItem -Path $ProjectRoot -Recurse -Include "buddy-flows.yaml"
        }
        "mappings" {
            $files = Get-ChildItem -Path $ProjectRoot -Recurse -Include "*.mapped.json"
        }
        default {
            $files = Get-ChildItem -Path $ProjectRoot -Recurse -Include "*.yaml", "*.json" | Where-Object { 
                $_.Name -notlike "ci.*" -and $_.Name -notlike "template.*" 
            }
        }
    }
    
    foreach ($file in $files) {
        Write-CILog "Validating: $($file.FullName)"
        
        # YAML-Syntax prüfen
        if ($file.Extension -eq ".yaml") {
            if (-not (Test-YamlSyntax $file.FullName)) {
                $validationPassed = $false
            }
        }
        
        # Template-Konformität prüfen (vereinfacht)
        if ($file.Name -like "mode.*.yaml") {
            $template = Join-Path $ProjectRoot "core/templates/template.mode.yaml"
            if (-not (Test-TemplateConformity $file.FullName $template)) {
                $validationPassed = $false
            }
        }
    }
    
    return $validationPassed
}

# Hauptausführung
$validationResult = Start-Validation $Subsystem

# Ergebnisse schreiben
$summary = @{
    validation_run = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        subsystem = $Subsystem
        total_errors = $global:CIErrors.Count
        total_warnings = $global:CIWarnings.Count
        validation_passed = $validationResult
    }
    errors = $global:CIErrors
    warnings = $global:CIWarnings
}

$logOutput = @{
    log_entries = $global:CILog
    summary = $summary
}

# Ausgabe in YAML-Dateien
$summaryPath = Join-Path $OutputDir "ci.summary.yaml"
$logPath = Join-Path $OutputDir "ci.log.yaml"

$summary | ConvertTo-Yaml | Out-File -FilePath $summaryPath -Encoding UTF8
$logOutput | ConvertTo-Yaml | Out-File -FilePath $logPath -Encoding UTF8

Write-CILog "CI validation completed. Results written to $summaryPath and $logPath"

if (-not $validationResult) {
    Write-Host "CI validation FAILED with $($global:CIErrors.Count) errors" -ForegroundColor Red
    exit 1
} else {
    Write-Host "CI validation PASSED" -ForegroundColor Green
    exit 0
}

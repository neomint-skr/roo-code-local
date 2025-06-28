# RooCode Test Suite - Einheitlicher Einstiegspunkt
# Führt alle struktur-, agenten- und flowbasierten Tests aus

param(
    [string]$TestType = "all",  # all, structure, agents, integration, tools
    [switch]$Coverage,
    [switch]$Verbose,
    [string]$OutputDir = "core/tests"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Globale Test-Variablen
$global:TestResults = @()
$global:TestSummary = @{
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    coverage_percentage = 0
}

function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    if ($Verbose) { Write-Host "[$Level] $Message" }
    
    $global:TestResults += @{
        timestamp = $timestamp
        level = $Level
        message = $Message
    }
}

function Test-StructureComponents {
    Write-TestLog "Running structure tests..." "INFO"
    
    $structureTestsPath = Join-Path $ScriptDir "structure"
    $testsPassed = $true
    
    # YAML-Syntax-Tests
    Write-TestLog "Testing YAML syntax..." "INFO"
    try {
        yamllint $ProjectRoot --config-file (Join-Path $ProjectRoot "pyproject.toml")
        Write-TestLog "YAML syntax tests passed" "SUCCESS"
        $global:TestSummary.passed_tests++
    } catch {
        Write-TestLog "YAML syntax tests failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        $testsPassed = $false
    }
    
    # Template-Konformitätstests
    Write-TestLog "Testing template conformity..." "INFO"
    try {
        python (Join-Path $ProjectRoot "core\ci\template_validator.py") $ProjectRoot
        Write-TestLog "Template conformity tests passed" "SUCCESS"
        $global:TestSummary.passed_tests++
    } catch {
        Write-TestLog "Template conformity tests failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        $testsPassed = $false
    }
    
    $global:TestSummary.total_tests += 2
    return $testsPassed
}

function Test-AgentComponents {
    Write-TestLog "Running agent tests..." "INFO"
    
    $agentTestsPath = Join-Path $ScriptDir "agents"
    $testsPassed = $true
    
    # Pytest für Agent-Tests
    try {
        $pytestArgs = @(
            $agentTestsPath,
            "--verbose"
        )
        
        if ($Coverage) {
            $pytestArgs += @("--cov=core", "--cov-report=term-missing")
        }
        
        pytest @pytestArgs
        Write-TestLog "Agent tests passed" "SUCCESS"
        $global:TestSummary.passed_tests++
    } catch {
        Write-TestLog "Agent tests failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        $testsPassed = $false
    }
    
    $global:TestSummary.total_tests++
    return $testsPassed
}

function Test-IntegrationComponents {
    Write-TestLog "Running integration tests..." "INFO"
    
    $integrationTestsPath = Join-Path $ScriptDir "integration"
    $testsPassed = $true
    
    # Integration-Tests mit pytest
    try {
        pytest $integrationTestsPath --verbose
        Write-TestLog "Integration tests passed" "SUCCESS"
        $global:TestSummary.passed_tests++
    } catch {
        Write-TestLog "Integration tests failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        $testsPassed = $false
    }
    
    $global:TestSummary.total_tests++
    return $testsPassed
}

function Test-ToolComponents {
    Write-TestLog "Running tool tests..." "INFO"
    
    $toolTestsPath = Join-Path $ScriptDir "tools"
    $testsPassed = $true
    
    # Bootstrap-Tests
    Write-TestLog "Testing bootstrap functionality..." "INFO"
    try {
        # Simuliere Bootstrap-Test (ohne tatsächliche Ausführung)
        $bootstrapScript = Join-Path $ProjectRoot "core\bootstrap\bootstrap.ps1"
        if (Test-Path $bootstrapScript) {
            Write-TestLog "Bootstrap script exists and is accessible" "SUCCESS"
            $global:TestSummary.passed_tests++
        } else {
            throw "Bootstrap script not found"
        }
    } catch {
        Write-TestLog "Bootstrap tests failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        $testsPassed = $false
    }
    
    # CI-Validierung-Tests
    Write-TestLog "Testing CI validation..." "INFO"
    try {
        & (Join-Path $ProjectRoot "core\ci\validate_all.ps1") -Subsystem "all"
        Write-TestLog "CI validation tests passed" "SUCCESS"
        $global:TestSummary.passed_tests++
    } catch {
        Write-TestLog "CI validation tests failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        $testsPassed = $false
    }
    
    $global:TestSummary.total_tests += 2
    return $testsPassed
}

function Test-PythonCodeQuality {
    Write-TestLog "Running Python code quality checks..." "INFO"
    
    try {
        # Ruff für Code-Qualität
        ruff check $ProjectRoot
        Write-TestLog "Python code quality checks passed" "SUCCESS"
        $global:TestSummary.passed_tests++
    } catch {
        Write-TestLog "Python code quality checks failed: $($_.Exception.Message)" "ERROR"
        $global:TestSummary.failed_tests++
        return $false
    }
    
    $global:TestSummary.total_tests++
    return $true
}

# Hauptausführung
Write-TestLog "=== RooCode Test Suite Started ===" "INFO"
Write-TestLog "Test Type: $TestType" "INFO"
Write-TestLog "Project Root: $ProjectRoot" "INFO"

$overallSuccess = $true

# Führe Tests basierend auf TestType aus
switch ($TestType) {
    "structure" {
        $overallSuccess = Test-StructureComponents
    }
    "agents" {
        $overallSuccess = Test-AgentComponents
    }
    "integration" {
        $overallSuccess = Test-IntegrationComponents
    }
    "tools" {
        $overallSuccess = Test-ToolComponents
    }
    "quality" {
        $overallSuccess = Test-PythonCodeQuality
    }
    default {
        # Alle Tests ausführen
        $results = @(
            Test-StructureComponents,
            Test-AgentComponents,
            Test-IntegrationComponents,
            Test-ToolComponents,
            Test-PythonCodeQuality
        )
        $overallSuccess = $results -notcontains $false
    }
}

# Generiere Testbericht
$testReport = @{
    test_run = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        test_type = $TestType
        success = $overallSuccess
        duration_seconds = 0  # Würde in echter Implementierung gemessen
    }
    summary = $global:TestSummary
    test_results = $global:TestResults
}

# Speichere Testbericht
$reportPath = Join-Path $OutputDir "test.report.yaml"
try {
    $testReport | ConvertTo-Yaml | Out-File -FilePath $reportPath -Encoding UTF8
    Write-TestLog "Test report saved to $reportPath" "INFO"
} catch {
    Write-TestLog "Failed to save test report: $($_.Exception.Message)" "ERROR"
}

# Ausgabe und Exit
if ($overallSuccess) {
    Write-TestLog "=== All Tests Passed ===" "SUCCESS"
    Write-Host "Test Suite PASSED: $($global:TestSummary.passed_tests)/$($global:TestSummary.total_tests) tests" -ForegroundColor Green
    exit 0
} else {
    Write-TestLog "=== Some Tests Failed ===" "ERROR"
    Write-Host "Test Suite FAILED: $($global:TestSummary.failed_tests)/$($global:TestSummary.total_tests) tests failed" -ForegroundColor Red
    exit 1
}

# RooCode Pytest Test Suite Runner
# Executes comprehensive pytest-based test suite with reporting
# Version: 1.0
# Created: 2025-06-29

param(
    [string]$TestType = "all",  # all, unit, integration, structure, e2e
    [switch]$Verbose,
    [switch]$Coverage,
    [string]$OutputDir = "test_results",
    [switch]$SkipDocker
)

# Configuration
$ErrorActionPreference = "Stop"
$TestsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $TestsDir)
$OutputPath = Join-Path $ProjectRoot $OutputDir

Write-Host "RooCode Pytest Test Suite Runner" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Test Type: $TestType" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host "Output Directory: $OutputPath" -ForegroundColor Gray

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# Check Python availability
try {
    $PythonVersion = python --version 2>&1
    Write-Host "Python Version: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python not found. Please install Python 3.11+ or run tests in Docker container."
    exit 1
}

# Check pytest availability
try {
    $PytestVersion = python -m pytest --version 2>&1
    Write-Host "Pytest Version: $PytestVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing pytest..." -ForegroundColor Yellow
    python -m pip install pytest pytest-cov pyyaml requests
}

# Test execution function
function Invoke-PytestSuite {
    param(
        [string]$Type,
        [string]$Pattern,
        [string]$Description
    )
    
    Write-Host "`nRunning $Description..." -ForegroundColor Yellow
    
    $TestArgs = @(
        "-v",
        "--tb=short",
        "--color=yes"
    )
    
    if ($Coverage) {
        $TestArgs += @(
            "--cov=core",
            "--cov-report=html:$OutputPath/coverage_$Type",
            "--cov-report=xml:$OutputPath/coverage_$Type.xml"
        )
    }
    
    if ($Pattern) {
        $TestArgs += @("-k", $Pattern)
    }
    
    if ($SkipDocker) {
        $TestArgs += @("-m", "not docker")
    }
    
    $TestArgs += @("--junitxml=$OutputPath/junit_$Type.xml")
    
    # Add test directory
    $TestDir = Join-Path $TestsDir $Type
    if (Test-Path $TestDir) {
        $TestArgs += $TestDir
    } else {
        $TestArgs += $TestsDir
    }
    
    $StartTime = Get-Date
    
    try {
        $Result = python -m pytest @TestArgs
        $ExitCode = $LASTEXITCODE
        $EndTime = Get-Date
        $Duration = $EndTime - $StartTime
        
        if ($ExitCode -eq 0) {
            Write-Host "✅ $Description completed successfully" -ForegroundColor Green
            Write-Host "   Duration: $($Duration.TotalSeconds) seconds" -ForegroundColor Gray
        } else {
            Write-Host "❌ $Description failed" -ForegroundColor Red
            Write-Host "   Duration: $($Duration.TotalSeconds) seconds" -ForegroundColor Gray
        }
        
        return @{
            Type = $Type
            Description = $Description
            ExitCode = $ExitCode
            Duration = $Duration.TotalSeconds
            Success = ($ExitCode -eq 0)
        }
    } catch {
        Write-Host "❌ $Description failed with exception: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            Type = $Type
            Description = $Description
            ExitCode = 1
            Duration = 0
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

# Main test execution
$TestResults = @()
$OverallStartTime = Get-Date

try {
    # Change to project root for test execution
    Push-Location $ProjectRoot
    
    switch ($TestType.ToLower()) {
        "unit" {
            $TestResults += Invoke-PytestSuite -Type "unit" -Description "Unit Tests"
        }
        "integration" {
            $TestResults += Invoke-PytestSuite -Type "integration" -Description "Integration Tests"
        }
        "structure" {
            $TestResults += Invoke-PytestSuite -Type "structure" -Description "Structure Tests"
        }
        "e2e" {
            if (-not $SkipDocker) {
                Write-Host "`nChecking Docker availability..." -ForegroundColor Yellow
                try {
                    docker --version | Out-Null
                    $TestResults += Invoke-PytestSuite -Type "e2e" -Description "End-to-End Tests"
                } catch {
                    Write-Host "⚠️  Docker not available, skipping E2E tests" -ForegroundColor Yellow
                }
            } else {
                Write-Host "⚠️  Docker tests skipped by user request" -ForegroundColor Yellow
            }
        }
        "all" {
            $TestResults += Invoke-PytestSuite -Type "unit" -Description "Unit Tests"
            $TestResults += Invoke-PytestSuite -Type "integration" -Description "Integration Tests"
            $TestResults += Invoke-PytestSuite -Type "structure" -Description "Structure Tests"
            
            if (-not $SkipDocker) {
                try {
                    docker --version | Out-Null
                    $TestResults += Invoke-PytestSuite -Type "e2e" -Description "End-to-End Tests"
                } catch {
                    Write-Host "⚠️  Docker not available, skipping E2E tests" -ForegroundColor Yellow
                }
            }
        }
        default {
            Write-Error "Invalid test type: $TestType. Valid options: all, unit, integration, structure, e2e"
            exit 1
        }
    }
    
} finally {
    Pop-Location
}

$OverallEndTime = Get-Date
$TotalDuration = $OverallEndTime - $OverallStartTime

# Generate test report
Write-Host "`n" + "="*50 -ForegroundColor Green
Write-Host "PYTEST SUITE SUMMARY" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Green

$SuccessfulTests = $TestResults | Where-Object { $_.Success }
$FailedTests = $TestResults | Where-Object { -not $_.Success }

Write-Host "Total Duration: $($TotalDuration.TotalSeconds) seconds" -ForegroundColor Gray
Write-Host "Tests Run: $($TestResults.Count)" -ForegroundColor Cyan
Write-Host "Successful: $($SuccessfulTests.Count)" -ForegroundColor Green
Write-Host "Failed: $($FailedTests.Count)" -ForegroundColor Red

foreach ($result in $TestResults) {
    $status = if ($result.Success) { "✅" } else { "❌" }
    $color = if ($result.Success) { "Green" } else { "Red" }
    Write-Host "$status $($result.Description) ($($result.Duration)s)" -ForegroundColor $color
    
    if ($result.Error) {
        Write-Host "   Error: $($result.Error)" -ForegroundColor Red
    }
}

# Generate JSON report
$JsonReport = @{
    timestamp = $OverallStartTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
    total_duration = $TotalDuration.TotalSeconds
    test_type = $TestType
    results = $TestResults
    summary = @{
        total = $TestResults.Count
        successful = $SuccessfulTests.Count
        failed = $FailedTests.Count
        success_rate = if ($TestResults.Count -gt 0) { 
            [math]::Round(($SuccessfulTests.Count / $TestResults.Count) * 100, 2) 
        } else { 0 }
    }
}

$JsonReportPath = Join-Path $OutputPath "pytest_report.json"
$JsonReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $JsonReportPath -Encoding UTF8

Write-Host "`nTest report saved to: $JsonReportPath" -ForegroundColor Gray

if ($Coverage) {
    Write-Host "Coverage reports saved to: $OutputPath/coverage_*" -ForegroundColor Gray
}

# Exit with appropriate code
if ($FailedTests.Count -gt 0) {
    Write-Host "`n❌ Test suite completed with failures" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n✅ All tests passed successfully!" -ForegroundColor Green
    exit 0
}

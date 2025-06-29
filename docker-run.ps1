# RooCode Docker Runner - Working Version
# Minimal Docker operations with hierarchical dependency integration

[CmdletBinding()]
param(
    [ValidateSet("buddy", "dev", "test", "prod")]
    [string]$AgentProfile = "buddy",
    [switch]$EnableLLM,
    [switch]$CleanBuild,
    [switch]$DebugMode,
    [ValidateRange(1,5)]
    [int]$RetryAttempts = 3,
    [switch]$Build,
    [switch]$Detach,
    [switch]$Clean,
    [switch]$Logs
)

$ErrorActionPreference = "Stop"
if ($Build) { $CleanBuild = $true }

# Simple logging
$LogsDir = "logs"
if (-not (Test-Path $LogsDir)) { 
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null 
}
$LogFile = Join-Path $LogsDir "docker-run-$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param([string]$Level, [string]$Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) { 
        "INFO" { "White" } 
        "WARN" { "Yellow" } 
        "ERROR" { "Red" } 
        default { "Gray" } 
    }
    if ($DebugMode -or $Level -ne "DEBUG") { 
        Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color 
    }
    "[$timestamp] [$Level] $Message" | Add-Content $LogFile -Encoding UTF8
}

function Test-DockerAvailability {
    $result = @{ IsInstalled = $false; IsRunning = $false; InstallationPath = $null }
    $paths = @(
        "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe",
        "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
        "${env:LOCALAPPDATA}\Programs\Docker\Docker\Docker Desktop.exe"
    )
    foreach ($path in $paths) {
        if (Test-Path $path) { 
            $result.IsInstalled = $true
            $result.InstallationPath = $path
            break 
        }
    }
    if ($result.IsInstalled) {
        try { 
            docker info 2>$null | Out-Null
            $result.IsRunning = ($LASTEXITCODE -eq 0) 
        } catch { 
            $result.IsRunning = $false 
        }
    }
    return $result
}

function Start-DockerDesktop {
    param([string]$InstallationPath)
    Write-Log "INFO" "Starting Docker Desktop"
    if (-not $InstallationPath) { 
        throw "Docker Desktop installation path not found" 
    }
    Start-Process -FilePath $InstallationPath -WindowStyle Hidden | Out-Null
    $elapsed = 0
    while ($elapsed -lt 60) {
        Start-Sleep 2
        $elapsed += 2
        $percent = [Math]::Min(90, ($elapsed / 60) * 100)
        Write-Progress -Activity "Docker Management" -Status "Waiting for Docker daemon..." -PercentComplete $percent
        try { 
            docker info 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { 
                Write-Log "INFO" "Docker Desktop started"
                return $true 
            } 
        } catch { 
            # Continue waiting
        }
    }
    throw "Docker Desktop failed to start within 60 seconds"
}

function Test-DependencyFiles {
    $result = @{ IsValid = $true; MissingFiles = @() }
    $requiredFiles = @("core/config/requirements.txt")
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) { 
            $result.MissingFiles += $file
            $result.IsValid = $false 
        }
    }
    return $result
}

function Invoke-WithRetry {
    param([scriptblock]$Action, [int]$MaxAttempts = 3, [string]$OperationName)
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $result = & $Action
            if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) { 
                return $result 
            }
            if ($attempt -lt $MaxAttempts) { 
                Write-Log "WARN" "$OperationName failed. Retrying..."
                Start-Sleep ($attempt * 2) 
            } else { 
                throw "$OperationName failed with exit code $LASTEXITCODE" 
            }
        } catch {
            if ($attempt -lt $MaxAttempts) { 
                Write-Log "WARN" "$OperationName failed: $($_.Exception.Message). Retrying..."
                Start-Sleep ($attempt * 2) 
            } else { 
                Write-Log "ERROR" "$OperationName failed after $MaxAttempts attempts: $($_.Exception.Message)"
                throw 
            }
        }
    }
}

Write-Host "=== RooCode Docker Runner ===" -ForegroundColor Cyan
Write-Host "Profile: $AgentProfile" -ForegroundColor White
Write-Log "INFO" "Docker runner session started - Profile: $AgentProfile"

try {
    # Check Docker availability
    $dockerCheck = Test-DockerAvailability
    if (-not $dockerCheck.IsInstalled) {
        Write-Host "❌ Docker Desktop is not installed" -ForegroundColor Red
        Write-Host "📥 Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
    
    if (-not $dockerCheck.IsRunning) {
        if ($dockerCheck.InstallationPath) {
            try {
                $started = Start-DockerDesktop $dockerCheck.InstallationPath
                if ($started) { 
                    Write-Host "✓ Docker Desktop started successfully" -ForegroundColor Green 
                }
            } catch {
                Write-Host "❌ Failed to start Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "❌ Docker Desktop is not running and cannot auto-start" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
    }

    # Validate dependency structure
    $depCheck = Test-DependencyFiles
    if (-not $depCheck.IsValid) {
        Write-Host "❌ Dependency structure validation failed" -ForegroundColor Red
        foreach ($missing in $depCheck.MissingFiles) { 
            Write-Host "   Missing: $missing" -ForegroundColor Red 
        }
        exit 1
    } else {
        Write-Host "✓ Dependency structure validated" -ForegroundColor Green
    }

    # Clean up existing containers if requested
    if ($Clean -or $CleanBuild) {
        Invoke-WithRetry -OperationName "Container cleanup" -Action {
            docker stop roo-system 2>$null | Out-Null
            docker rm roo-system 2>$null | Out-Null
            if ($CleanBuild) { 
                docker rmi neomint/roo-agent-buddy:latest 2>$null | Out-Null 
            }
        } -MaxAttempts 2
        Write-Host "✓ Container cleanup completed" -ForegroundColor Green
    }

    # Show logs if requested
    if ($Logs) { 
        Write-Host "Showing container logs..." -ForegroundColor Cyan
        docker logs roo-system -f
        return 
    }

    # Use docker-compose for detached mode if available
    if ($Detach -and (Test-Path "core/docker/docker-compose.yaml")) {
        Write-Host "Using docker-compose for detached mode..." -ForegroundColor Cyan
        Push-Location "core/docker"
        try {
            Invoke-WithRetry -OperationName "Docker compose startup" -Action { 
                & docker compose up --build --detach 
            } -MaxAttempts $RetryAttempts
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Container started in detached mode" -ForegroundColor Green
                Write-Host "Use 'docker logs roo-system -f' to view logs" -ForegroundColor White
            }
        } finally { 
            Pop-Location 
        }
        return
    }

    # Build Docker image if requested
    if ($Build -or $CleanBuild) {
        $buildArgs = @("build", "-t", "neomint/roo-agent-buddy:latest", "-f", "core/docker/Dockerfile", ".")
        if ($CleanBuild) { 
            $buildArgs += "--no-cache" 
        }
        try {
            Invoke-WithRetry -OperationName "Docker build" -Action { 
                & docker @buildArgs 
            } -MaxAttempts $RetryAttempts
            Write-Host "✓ Docker image built successfully" -ForegroundColor Green
        } catch {
            Write-Host "❌ Docker build failed: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    }

    # Prepare Docker run arguments
    $dockerArgs = @("run")
    if (-not $Detach) { 
        $dockerArgs += "-it" 
    }
    if (-not $DebugMode) { 
        $dockerArgs += "--rm" 
    }
    $dockerArgs += "-v", "${PWD}:/project", "-p", "11434:11434", "-p", "8080:8080"
    $dockerArgs += "-e", "PROFILE=$AgentProfile", "-e", "ENABLE_LLM=$($EnableLLM.IsPresent)", "-e", "DEBUG_MODE=$($DebugMode.IsPresent)"
    $dockerArgs += "--memory=2g", "neomint/roo-agent-buddy:latest"

    Write-Host "Starting RooCode container..." -ForegroundColor Cyan
    Write-Host "Command: docker $($dockerArgs -join ' ')" -ForegroundColor Gray

    # Run docker container with retry logic
    try {
        Invoke-WithRetry -OperationName "Container startup" -Action { 
            & docker @dockerArgs 
        } -MaxAttempts $RetryAttempts
    } catch {
        Write-Host "❌ Container startup failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }

    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
        Write-Host ""
        Write-Host "✓ RooCode container started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== Connection Information ===" -ForegroundColor Cyan
        Write-Host "API Endpoint: http://localhost:8080" -ForegroundColor White
        Write-Host "LLM Endpoint: http://localhost:11434" -ForegroundColor White
        Write-Host "API Key: local-mode-key" -ForegroundColor Yellow
        Write-Host "Profile: $AgentProfile" -ForegroundColor White
        Write-Host ""
        Write-Host "=== Dependency Structure ===" -ForegroundColor Cyan
        Write-Host "Core: core/config/requirements.txt" -ForegroundColor Gray
        Write-Host "Profile ($AgentProfile): core/config/requirements-$AgentProfile.txt" -ForegroundColor Gray
        if ($EnableLLM) { 
            Write-Host "LLM Module: modules/llm-admin/requirements.txt" -ForegroundColor Gray 
        }
        if (-not $Detach) { 
            Write-Host ""
            Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Yellow 
        }
        Write-Log "INFO" "Docker runner session completed successfully"
    } else {
        Write-Host "✗ Failed to start RooCode container (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "✗ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Log "ERROR" "Unexpected error in docker runner: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "🔍 Troubleshooting Information:" -ForegroundColor Yellow
    Write-Host "   - Check logs: $LogFile" -ForegroundColor Gray
    Write-Host "   - Use -DebugMode for verbose output" -ForegroundColor Gray
    exit 1
} finally {
    Write-Progress -Activity "Docker Runner" -Completed
}

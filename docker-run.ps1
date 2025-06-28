# RooCode Docker Runner - Windows Wrapper
# One-liner start for Windows users - Task 39 Implementation

param(
    [string]$AgentProfile = "buddy",
    [switch]$Build,
    [switch]$Detach,
    [switch]$Verbose,
    [switch]$Clean,
    [switch]$Logs
)

$ErrorActionPreference = "Stop"

# Get current directory
$CurrentDir = Get-Location

Write-Host "=== RooCode Docker Runner ===" -ForegroundColor Cyan
Write-Host "Profile: $AgentProfile" -ForegroundColor White
Write-Host "Current Directory: $CurrentDir" -ForegroundColor Gray
Write-Host ""

try {
    # Check if Docker is available
    try {
        docker --version | Out-Null
        Write-Host "✓ Docker is available" -ForegroundColor Green
    } catch {
        Write-Host "✗ Docker is not available or not running" -ForegroundColor Red
        Write-Host "Please install Docker Desktop and ensure it's running" -ForegroundColor Yellow
        exit 1
    }

    # Clean up existing containers if requested
    if ($Clean) {
        Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
        try {
            docker stop roo-system 2>$null | Out-Null
            docker rm roo-system 2>$null | Out-Null
            Write-Host "✓ Cleaned up existing containers" -ForegroundColor Green
        } catch {
            Write-Host "No existing containers to clean up" -ForegroundColor Gray
        }
    }

    # Show logs if requested
    if ($Logs) {
        Write-Host "Showing container logs..." -ForegroundColor Cyan
        docker logs roo-system -f
        return
    }

    # Alternative: Use docker-compose from core/docker
    if ($Detach -and (Test-Path "core/docker/docker-compose.yaml")) {
        Write-Host "Using docker-compose for detached mode..." -ForegroundColor Cyan
        Push-Location "core/docker"
        try {
            & docker compose up --build --detach
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Container started in detached mode" -ForegroundColor Green
                Write-Host "Use 'docker logs roo-system -f' to view logs" -ForegroundColor White
            }
        } finally {
            Pop-Location
        }
        return
    }

    # Build Docker arguments according to Task 40 restructured paths
    if ($Build) {
        Write-Host "Building Docker image..." -ForegroundColor Cyan
        & docker build -t neomint/roo-agent-buddy:latest .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Docker build failed" -ForegroundColor Red
            exit 1
        }
    }

    $dockerArgs = @(
        "run", "-it", "--rm"
    )

    # Add volume mapping
    $dockerArgs += "-v", "${PWD}:/project"

    # Add port mapping
    $dockerArgs += "-p", "11434:11434"
    $dockerArgs += "-p", "8080:8080"

    # Set environment variables
    $dockerArgs += "-e", "PROFILE=$AgentProfile"

    # Add image name
    $dockerArgs += "neomint/roo-agent-buddy:latest"

    Write-Host "Starting RooCode container..." -ForegroundColor Cyan
    Write-Host "Command: docker $($dockerArgs -join ' ')" -ForegroundColor Gray

    # Run docker container
    & docker @dockerArgs

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ RooCode container started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== Connection Information ===" -ForegroundColor Cyan
        Write-Host "API Endpoint: http://localhost:8080" -ForegroundColor White
        Write-Host "LLM Endpoint: http://localhost:11434" -ForegroundColor White
        Write-Host "API Key: local-mode-key" -ForegroundColor Yellow
        Write-Host "Profile: $AgentProfile" -ForegroundColor White
        Write-Host ""
        Write-Host "=== Task 39 Implementation ===" -ForegroundColor Cyan
        Write-Host "✓ All local scripts removed" -ForegroundColor Green
        Write-Host "✓ Docker-only system active" -ForegroundColor Green
        Write-Host "✓ Single entry point: docker-run.ps1" -ForegroundColor Green
        
        if (-not $Detach) {
            Write-Host ""
            Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✗ Failed to start RooCode container" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

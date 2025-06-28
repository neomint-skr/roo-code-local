# Docker Deployment Guide

## Overview

The RooCode system is fully containerized and requires only Docker to run. No local Python installation or dependencies are needed.

## Quick Start

### Windows
```powershell
git clone https://github.com/neomint-skr/roo-code-local
cd roo-code-local
./docker-run.ps1
```

### Linux/macOS
```bash
git clone https://github.com/neomint-skr/roo-code-local
cd roo-code-local
docker run -it --rm -v $(pwd):/project -p 11434:11434 -p 8080:8080 neomint/roo-agent-buddy:latest
```

## Docker Components

### 1. Dockerfile
- Base: `python:3.11-slim`
- Working directory: `/project`
- Entrypoint: `entrypoint.sh`
- Ports: 8080 (API), 11434 (LLM)

### 2. Docker Compose
- Service orchestration
- Volume mapping
- Environment configuration
- Health checks

### 3. Entry Scripts
- `docker-run.ps1`: Windows wrapper
- `entrypoint.sh`: Container initialization
- `docker-entrypoint.sh`: Advanced initialization

## Configuration

### Environment Variables
Configure via `.env.docker`:

```bash
# Core settings
PROFILE=buddy
API_PORT=8080
LLM_PORT=11434

# Performance
MEMORY_LIMIT=4G
CPU_LIMIT=2.0

# Features
ENABLE_BUDDY_MODE=true
ENABLE_HEALTH_CHECKS=true
```

### Volume Mapping
- Project files: `./:/project`
- Models: `./models:/project/models`
- Logs: `./logs:/project/logs`
- Data: `./data:/project/data`

## Container Management

### Basic Commands
```bash
# Start system
docker compose up --build --detach

# View logs
docker logs roo-system -f

# Shell access
docker exec -it roo-system bash

# Stop system
docker compose down

# Restart
docker restart roo-system
```

### Health Monitoring
```bash
# Check container status
docker ps

# Health check endpoint
curl http://localhost:8080/health

# Resource usage
docker stats roo-system
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs roo-system

# Rebuild image
docker compose down
docker compose up --build
```

**Port conflicts:**
```bash
# Use different ports
./docker-run.ps1 -Port 8081 -LLMPort 11435
```

**Memory issues:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yaml or Docker Desktop settings
```

### Debug Mode
```bash
# Run with shell access
docker run -it --rm -v $(pwd):/project neomint/roo-agent-buddy bash

# Interactive debugging
docker exec -it roo-system bash
```

## Production Deployment

### Resource Requirements
- **Memory**: 4GB minimum, 8GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Storage**: 10GB for models and data

### Security Considerations
- Container runs as non-root user
- API key authentication required
- CORS configuration available
- Health checks enabled

### Scaling
- Single container deployment
- Horizontal scaling via load balancer
- Model sharing via volume mounts

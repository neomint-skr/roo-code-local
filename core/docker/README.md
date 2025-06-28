# Core Docker Components

This directory contains all Docker-related scripts and configurations for the RooCode system.

## Files

- `Dockerfile`: Container definition
- `docker-compose.yaml`: Service orchestration
- `docker-entrypoint.sh`: Container initialization
- `entrypoint.sh`: Simplified entrypoint
- `.env.docker`: Environment configuration

## Usage

All Docker components are managed through the root-level `docker-run.ps1` script, which provides a simplified interface to the Docker infrastructure defined in this directory.

## Development

When modifying Docker components:
1. Update files in this directory
2. Test with `docker compose config`
3. Validate with `docker build .`
4. Update documentation as needed

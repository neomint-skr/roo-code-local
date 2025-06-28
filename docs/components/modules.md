# Modules Documentation

## Overview

The `modules/` directory contains hot-swappable extensions that provide optional functionality to the RooCode system.

## Directory Structure

```
modules/
└── llm-admin/          # LLM management module
    ├── config/         # Module configuration
    ├── engines/        # LLM engine scripts
    ├── tools/          # Utility tools
    ├── templates/      # Module templates
    └── test/           # Module tests
```

## Available Modules

### LLM-Admin Module

The LLM-Admin module provides comprehensive local model management and API integration.

#### Features
- Model registry management
- Engine abstraction (llama.cpp, transformers)
- API server integration
- Configuration management
- Model downloading and validation

#### Components

##### 1. Configuration (`modules/llm-admin/config/`)
- `active.yaml`: Currently active model configuration
- `llm.registry.yaml`: Available models registry
- Runtime configuration management

##### 2. Engines (`modules/llm-admin/engines/`)
- Engine-specific execution scripts
- Abstraction layer for different LLM backends
- Performance optimization

##### 3. Tools (`modules/llm-admin/tools/`)
- `download.ps1`: Model downloading utility
- `generate-mode.ps1`: Mode generation tool
- Utility scripts for model management

##### 4. CLI Interface
- `cli.ps1`: PowerShell command-line interface
- Commands: `list`, `use`, `run`, `config`
- Modular, documented, CI-testable

## Module Development

### Creating New Modules

1. **Directory Structure**
```
modules/new-module/
├── config/
├── tools/
├── templates/
├── test/
└── README.md
```

2. **Configuration**
- Follow existing patterns
- Use YAML for configuration
- Include validation rules

3. **Integration**
- Register with core system
- Follow template structure
- Add CI validation

### Module Guidelines

#### File Organization
- Keep module-specific files within module directory
- Use consistent naming conventions
- Separate configuration from implementation

#### Configuration Management
- Use YAML for configuration files
- Follow template structure
- Include validation and defaults

#### Testing
- Include module-specific tests
- Test integration with core system
- Validate configuration files

#### Documentation
- Include module README
- Document API interfaces
- Provide usage examples

## LLM-Admin Module Details

### CLI Commands

#### `llm list`
Lists all available models from the registry.
```powershell
./modules/llm-admin/cli.ps1 list
```

#### `llm use <model-id>`
Activates a specific model by writing to `active.yaml`.
```powershell
./modules/llm-admin/cli.ps1 use mistral-7b-instruct
```

#### `llm run <file>`
Executes the active model with input from a file.
```powershell
./modules/llm-admin/cli.ps1 run input.txt
```

#### `llm config`
Opens or validates the LLM configuration.
```powershell
./modules/llm-admin/cli.ps1 config
```

### Model Registry

The model registry (`llm.registry.yaml`) defines available models:

```yaml
models:
  - id: "mistral-7b-instruct"
    name: "Mistral 7B Instruct v0.2"
    family: "mistral"
    size: "7B"
    quantization: "Q4_K_M"
    engine: "llama-cpp"
    path: "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    download_url: "https://huggingface.co/..."
    context_length: 32768
    parameters:
      temperature: 0.7
      top_p: 0.9
      top_k: 40
```

### Active Configuration

The active configuration (`active.yaml`) specifies the currently used model:

```yaml
active_model: "mistral-7b-instruct"
engine: "llama-cpp"
path: "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
api_config:
  api_url: "http://127.0.0.1:8080"
  api_key: "local-mode-key"
  server_mode: true
timestamp: "2025-06-28T23:45:00Z"
set_by: "cli"
```

## Integration with Core

### Mode Integration
Modules integrate with core modes through configuration references:

```yaml
# In mode definition
model_source:
  type: "local"
  reference: "modules/llm-admin/config/active.yaml"
```

### API Integration
Modules can expose API endpoints that integrate with the core API server.

### Workflow Integration
Modules participate in buddy-orchestrated workflows through defined interfaces.

## Best Practices

### Module Design
- Keep modules self-contained
- Minimize dependencies on other modules
- Provide clear interfaces

### Configuration
- Use consistent YAML structure
- Include validation and defaults
- Document all configuration options

### Testing
- Test module functionality independently
- Test integration with core system
- Include performance tests

### Documentation
- Document all public interfaces
- Provide usage examples
- Keep documentation up-to-date

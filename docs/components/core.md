# Core Components Documentation

## Overview

The `core/` directory contains all system-critical components that are essential for the RooCode system to function.

## Directory Structure

```
core/
├── modes/          # Agent mode definitions
├── templates/      # YAML templates for validation
├── ci/            # CI rules and validation
├── config/        # Core system configuration
└── tests/         # Test suite
```

## Components

### 1. Modes (`core/modes/`)

Agent mode definitions that specify behavior and capabilities.

#### Available Modes
- **buddy**: Central coordination agent
- **transkriptor**: Audio-to-text processing
- **intent-mapper**: Intent classification

#### Mode Structure
```yaml
slug: "mode-name"
agent: "agent-name"
description: "Mode description"
version: "1.0.0"

model_source:
  type: "local"
  reference: "modules/llm-admin/config/active.yaml"

tools:
  - name: "tool-name"
    type: "tool-type"
    config: {}

input_constraints:
  file_types: ["yaml", "json", "txt"]
  max_file_size_mb: 50
  encoding: "utf-8"

output_target:
  format: "json"
  destination: "output/"
  naming_pattern: "{id}.result.json"
```

### 2. Templates (`core/templates/`)

YAML templates that define structure and validation rules.

#### Available Templates
- `template.mode.yaml`: Mode definition template
- `template.spec.yaml`: Agent specification template
- `template.vocab-entry.yaml`: Vocabulary entry template
- `template.intent-suggestion.yaml`: Intent suggestion template
- `template.buddy-flows.yaml`: Workflow definition template

#### Template Usage
Templates are used for:
- Creating new components
- CI validation
- Structure enforcement
- Documentation generation

### 3. CI (`core/ci/`)

Continuous integration rules and validation scripts.

#### Components
- `ci.rules.yaml`: Validation rules definition
- `template_validator.py`: Template validation logic
- Automated structure checking
- Referential integrity validation

#### Validation Rules
- YAML syntax validation
- Template conformity checking
- Cross-reference validation
- Alphabetical ordering
- Chronological consistency

### 4. Configuration (`core/config/`)

Core system configuration files.

#### Files
- `llm.config.yaml`: LLM engine configuration
- `llm.registry.yaml`: Available models registry
- System-wide settings

### 5. Tests (`core/tests/`)

Comprehensive test suite for system validation.

#### Test Categories
- **Structure**: YAML structure and template conformity
- **Agents**: Mode execution and specification compliance
- **Integration**: Full workflow simulation
- **Tools**: Bootstrap and template validation

#### Running Tests
```bash
# All tests
python -m pytest core/tests/

# Specific category
python -m pytest core/tests/structure/

# With coverage
python -m pytest --cov=core core/tests/
```

## Development Guidelines

### Adding New Modes
1. Create mode definition in `core/modes/`
2. Follow `template.mode.yaml` structure
3. Add corresponding tests
4. Update documentation

### Template Modifications
1. Update template in `core/templates/`
2. Update validation rules in `core/ci/`
3. Test with existing files
4. Update documentation

### CI Rule Changes
1. Modify `core/ci/ci.rules.yaml`
2. Update validation logic if needed
3. Test against existing codebase
4. Document rule changes

## Best Practices

### File Naming
- Modes: `mode.{name}.yaml`
- Specs: `spec.{agent}.yaml`
- Templates: `template.{type}.yaml`

### YAML Structure
- Use consistent indentation (2 spaces)
- Follow template structure exactly
- Include all required fields
- Validate before committing

### Testing
- Write tests for new components
- Ensure CI validation passes
- Test integration scenarios
- Document test cases

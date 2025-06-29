# RooCode Core System Documentation

This document describes the core system components of the RooCode Local Agent System.

## Overview

The core system provides the essential components for a minimum viable RooCode system, following the 4D validation principles:
- **GUTWILLIG** (Complete/Willing): Create maximum value, prevent destruction
- **INTELLIGENT** (Smart/Optimized): Choose optimal solutions, avoid redundancy  
- **KONTEXT-AWARE** (Context-Sensitive): Respect dependencies and requirements
- **FAUL** (Lazy/Efficient): Act minimally, simplify implementation

## Directory Structure

### `core/modes/`
Agent mode definitions with one subdirectory per mode:

- **`mode.buddy.yaml`** - Central orchestration agent, main entry point
- **`mode.transkriptor.yaml`** - Transcript processing agent
- Additional modes as defined in task specifications

Each mode contains:
- Mode definition with slug, agent, description
- Tool specifications and capabilities
- Input/output type definitions
- Integration points with other modes

### `core/templates/`
YAML templates for CI validation and generation:

- **`template.mode.yaml`** - Template for agent mode definitions
- **`template.spec.yaml`** - Template for agent specifications
- **`template.vocab-entry.yaml`** - Template for vocabulary entries
- **`template.intent-suggestion.yaml`** - Template for intent suggestions
- **`template.buddy-flows.yaml`** - Template for workflow definitions
- **`template.llm-config.yaml`** - Template for LLM configuration

### `core/ci/`
Validation and automation scripts:

- **`ci.rules.yaml`** - CI validation rules and dependencies
- **`template_validator.py`** - Python script for template validation
- Structural integrity checking
- Reference consistency validation
- Deterministic ordering verification

### `core/vocab/`
Intent vocabulary management:

- **`vocab.yaml`** - Central intent vocabulary with unique IDs
- **`vocab.history.yaml`** - Immutable change history
- Alphabetically sorted entries
- ISO 8601 timestamps
- Origin tracking for all changes

### `core/config/`
System configuration files:

- **`llm.config.yaml`** - LLM model configuration and parameters
- **`llm.registry.yaml`** - Available model registry
- Profile-based configuration support
- API endpoint definitions

### `core/bootstrap/`
System initialization scripts:

- **`bootstrap.ps1`** - PowerShell initialization script for Windows
- Environment validation
- Dependency installation
- Virtual environment setup
- Configuration verification

### `core/docker/`
Container definitions and deployment:

- **`Dockerfile`** - Container image definition
- **`docker-compose.yaml`** - Multi-service orchestration
- **`docker-entrypoint.sh`** - Container entry point script
- **`entrypoint.sh`** - Alternative entry point
- Environment configuration support

### `core/tests/`
Comprehensive test suite:

- **`structure/`** - YAML specification and vocabulary tests
- **`agents/`** - Mode execution and spec conformity tests
- **`integration/`** - Full process chain simulation tests
- **`tools/`** - Bootstrap, template, and history consistency tests
- **`run_all.ps1`** - Unified test execution script

## Agent Modes

### Buddy Mode
Central orchestration agent providing:
- Single entry point for human users
- Deterministic agent coordination
- Workflow definition execution
- Process logging and status management
- Error handling and recovery

### Transkriptor Mode
Transcript processing agent providing:
- Chat export file processing
- Speaker detection and segmentation
- Structured JSON output generation
- Character position tracking
- Content preservation without interpretation

## Validation System

The core system implements comprehensive validation:

### Structural Validation
- YAML syntax and structure checking
- Template conformity verification
- Required field presence validation
- Data type consistency checking

### Referential Validation
- Intent ID consistency across vocab and mappings
- Mode slug references in workflows
- File path and extension verification
- Dependency chain validation

### Content Validation
- Deterministic ordering (alphabetical, chronological)
- Unique identifier enforcement
- ISO 8601 timestamp format validation
- No duplicate entries or conflicts

## Configuration Management

### LLM Configuration
Supports multiple model configurations:
- Local model paths and parameters
- API endpoint definitions
- Performance tuning settings
- Profile-based selection

### Environment Configuration
- Virtual environment isolation
- Dependency pinning and management
- Local vs. containerized execution
- Development vs. production settings

## Integration Points

### With Modules
- Hot-swappable module discovery
- No hardcoded dependencies in core
- Auto-discovery integration patterns
- Graceful degradation when modules unavailable

### With PIM System
- Task specification consumption
- Status tracking and reporting
- Template-based validation
- Progress monitoring and logging

### With Documentation
- Automated documentation generation
- Template-based consistency
- Version tracking and history
- Cross-reference validation

## Development Guidelines

### Adding New Modes
1. Create mode definition in `core/modes/`
2. Follow template structure from `core/templates/`
3. Add validation rules to `core/ci/`
4. Update documentation and tests
5. Verify CI validation passes

### Extending Vocabulary
1. Use vocab-updater agent for additions
2. Maintain alphabetical ordering
3. Ensure unique ID assignment
4. Document in vocab.history.yaml
5. Validate against existing mappings

### Configuration Changes
1. Update templates first
2. Modify configuration files
3. Update validation rules
4. Test with bootstrap script
5. Verify Docker compatibility

## Troubleshooting

### Common Issues
- **Missing dependencies**: Run bootstrap script
- **Validation failures**: Check CI rules and templates
- **Mode conflicts**: Verify unique slugs and IDs
- **Configuration errors**: Validate against templates

### Debug Tools
- CI validation scripts in `core/ci/`
- Test suite in `core/tests/`
- Bootstrap validation in `core/bootstrap/`
- Docker health checks in `core/docker/`

## Security Considerations

### Local Execution
- Virtual environment isolation
- No global system modifications
- Local-only API keys and endpoints
- Sandboxed container execution

### Data Protection
- No external network dependencies
- Local model execution only
- Encrypted configuration options
- Audit trail in history files

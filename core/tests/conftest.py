# RooCode Testing Framework Configuration
# Pytest configuration and shared fixtures for comprehensive testing
# Version: 1.0
# Created: 2025-06-29

import pytest
import yaml
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import os
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEMP_DIR = Path(tempfile.gettempdir()) / "roocode_tests"

@pytest.fixture(scope="session")
def project_root_path():
    """Provide project root path for tests."""
    return project_root

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path."""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    return TEST_DATA_DIR

@pytest.fixture(scope="function")
def temp_workspace():
    """Create temporary workspace for test isolation."""
    workspace = TEMP_DIR / f"test_{pytest.current_test_id}"
    workspace.mkdir(parents=True, exist_ok=True)
    yield workspace
    shutil.rmtree(workspace, ignore_errors=True)

@pytest.fixture(scope="session")
def sample_vocab():
    """Provide sample vocabulary for testing."""
    return {
        "intents": [
            {
                "id": "test.question",
                "label": "Test Question",
                "description": "Sample question intent for testing",
                "created_on": "2025-06-29T00:00:00Z",
                "origin": "test"
            },
            {
                "id": "test.confirmation",
                "label": "Test Confirmation",
                "description": "Sample confirmation intent for testing",
                "created_on": "2025-06-29T00:00:00Z",
                "origin": "test"
            }
        ]
    }

@pytest.fixture(scope="session")
def sample_transcript():
    """Provide sample transcript for testing."""
    return [
        {
            "speaker": "user",
            "index": 0,
            "text": "Hello, can you help me with this task?",
            "char_pos_start": 0,
            "char_pos_end": 40
        },
        {
            "speaker": "agent",
            "index": 0,
            "text": "Of course! I'd be happy to help you.",
            "char_pos_start": 41,
            "char_pos_end": 77
        },
        {
            "speaker": "user",
            "index": 1,
            "text": "Great, thank you!",
            "char_pos_start": 78,
            "char_pos_end": 95
        }
    ]

@pytest.fixture(scope="session")
def sample_chat_export():
    """Provide sample chat export for testing."""
    return {
        "conversation_id": "test_conv_001",
        "created_at": "2025-06-29T00:00:00Z",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you help me with this task?",
                "timestamp": "2025-06-29T00:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Of course! I'd be happy to help you.",
                "timestamp": "2025-06-29T00:00:01Z"
            },
            {
                "role": "user",
                "content": "Great, thank you!",
                "timestamp": "2025-06-29T00:00:02Z"
            }
        ]
    }

@pytest.fixture(scope="function")
def mock_llm_config():
    """Provide mock LLM configuration for testing."""
    return {
        "model": {
            "name": "test-model",
            "path": "/test/models/test-model.gguf",
            "family": "llama",
            "quantization": "Q4_K_M"
        },
        "engine": {
            "type": "llama-cpp",
            "parameters": {
                "context_length": 2048,
                "temperature": 0.7,
                "top_p": 0.9
            }
        },
        "interface": {
            "api_port": 8080,
            "endpoint_prefix": "/v1"
        }
    }

@pytest.fixture(scope="function")
def mock_mode_config():
    """Provide mock mode configuration for testing."""
    return {
        "slug": "test-mode",
        "agent": "test-agent",
        "description": "Test mode for unit testing",
        "version": "1.0.0",
        "model_source": {
            "type": "local",
            "reference": "test/config/active.yaml"
        },
        "tools": [
            {
                "name": "test_tool",
                "type": "test_processing",
                "config": {
                    "test_param": True
                }
            }
        ]
    }

# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_test_file(path: Path, content: Any, format: str = "yaml"):
        """Create a test file with specified content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "yaml":
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False)
        elif format == "json":
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(content))
    
    @staticmethod
    def load_yaml_file(path: Path) -> Dict[Any, Any]:
        """Load YAML file and return content."""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def load_json_file(path: Path) -> Dict[Any, Any]:
        """Load JSON file and return content."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def validate_yaml_structure(content: Dict[Any, Any], required_fields: List[str]) -> bool:
        """Validate YAML structure has required fields."""
        return all(field in content for field in required_fields)

@pytest.fixture(scope="session")
def test_utils():
    """Provide test utilities."""
    return TestUtils

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "docker: mark test as requiring Docker"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Add slow marker for tests that might take longer
        if "docker" in str(item.fspath) or "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

# Test data setup
def pytest_sessionstart(session):
    """Set up test session."""
    # Create test data directory
    TEST_DATA_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)

def pytest_sessionfinish(session, exitstatus):
    """Clean up test session."""
    # Clean up temporary files
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

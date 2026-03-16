"""
Pytest configuration for Vivago AI Skill tests

This file is automatically loaded by pytest and handles:
- Path setup for importing scripts module
- Shared fixtures
- Test configuration
"""
import os
import sys
import pytest

# Add scripts directory to path (done once here instead of in every test file)
scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Import after path setup
from vivago_client import VivagoClient
from template_manager import TemplateManager


@pytest.fixture
def mock_token():
    """Mock API token for testing"""
    return "mock-token-for-testing"


@pytest.fixture
def client(mock_token):
    """Create a test client with mock token"""
    return VivagoClient(token=mock_token)


@pytest.fixture
def template_manager():
    """Create a template manager instance"""
    return TemplateManager()

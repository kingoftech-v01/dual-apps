"""
Pytest configuration for dual-apps package tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def app_name():
    """Sample app name for tests."""
    return "testapp"


@pytest.fixture
def model_name():
    """Sample model name for tests."""
    return "TestModel"


@pytest.fixture
def project_name():
    """Sample project name for tests."""
    return "testproject"


@pytest.fixture
def sample_fields():
    """Sample fields string for tests."""
    return "title:str,price:decimal,is_active:bool"


@pytest.fixture
def parsed_fields():
    """Parsed fields list for tests."""
    return [
        {"name": "title", "type": "str"},
        {"name": "price", "type": "decimal"},
        {"name": "is_active", "type": "bool"},
    ]

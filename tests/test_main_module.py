"""
Tests for __main__.py module entry point.
"""

import pytest
import subprocess
import sys


class TestMainModule:
    """Test the __main__.py entry point."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from dual_apps import __main__
        assert hasattr(__main__, 'app')

    def test_module_has_app(self):
        """Test that the module exposes the app."""
        from dual_apps.__main__ import app
        assert app is not None

    def test_run_module_help(self):
        """Test running module with --help."""
        result = subprocess.run(
            [sys.executable, "-m", "dual_apps", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "init" in result.stdout

    def test_run_module_version(self):
        """Test running module with --version."""
        result = subprocess.run(
            [sys.executable, "-m", "dual_apps", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestPackageInit:
    """Test package __init__.py."""

    def test_version_exposed(self):
        """Test version is exposed at package level."""
        from dual_apps import __version__
        assert __version__ == "3.1.0"

    def test_generators_exposed(self):
        """Test generators are exposed."""
        from dual_apps import AppGenerator, ProjectGenerator
        assert AppGenerator is not None
        assert ProjectGenerator is not None

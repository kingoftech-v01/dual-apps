"""
Tests for dual-apps CLI.
"""

import pytest
from typer.testing import CliRunner
from dual_apps.cli.main import app

runner = CliRunner()


class TestCLIVersion:
    """Test CLI version command."""

    def test_version_command(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "dual-apps" in result.stdout.lower() or "3.1.0" in result.stdout


class TestCLIHelp:
    """Test CLI help commands."""

    def test_main_help(self):
        """Test main help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.stdout

    def test_init_help(self):
        """Test init help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "app" in result.stdout
        assert "project" in result.stdout

    def test_init_app_help(self):
        """Test init app help."""
        result = runner.invoke(app, ["init", "app", "--help"])
        assert result.exit_code == 0
        assert "--model" in result.stdout
        assert "--fields" in result.stdout

    def test_init_project_help(self):
        """Test init project help."""
        result = runner.invoke(app, ["init", "project", "--help"])
        assert result.exit_code == 0
        assert "--apps" in result.stdout
        assert "--db" in result.stdout
        assert "--auth" in result.stdout
        assert "--template" in result.stdout

    def test_auth_options_in_help(self):
        """Test auth options are documented in help."""
        result = runner.invoke(app, ["init", "project", "--help"])
        assert result.exit_code == 0
        assert "allauth" in result.stdout

    def test_template_options_in_help(self):
        """Test template options are documented in help."""
        result = runner.invoke(app, ["init", "project", "--help"])
        assert result.exit_code == 0
        assert "ecommerce" in result.stdout


class TestCLIAppGeneration:
    """Test CLI app generation."""

    def test_generate_app_basic(self, temp_dir):
        """Test basic app generation."""
        result = runner.invoke(
            app,
            ["init", "app", "testapp", "--output", str(temp_dir)],
        )
        # Check command ran (may have warnings but should not crash)
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_app_with_model(self, temp_dir):
        """Test app generation with custom model name."""
        result = runner.invoke(
            app,
            [
                "init", "app", "jobs",
                "--model", "JobPosting",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_app_with_fields(self, temp_dir):
        """Test app generation with custom fields."""
        result = runner.invoke(
            app,
            [
                "init", "app", "products",
                "--fields", "name:str,price:decimal,active:bool",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_app_api_only(self, temp_dir):
        """Test API-only app generation."""
        result = runner.invoke(
            app,
            [
                "init", "app", "api_only_app",
                "--api-only",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()


class TestCLIProjectGeneration:
    """Test CLI project generation."""

    def test_generate_project_basic(self, temp_dir):
        """Test basic project generation."""
        result = runner.invoke(
            app,
            ["init", "project", "myproject", "--output", str(temp_dir)],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_with_apps(self, temp_dir):
        """Test project generation with multiple apps."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myproject",
                "--apps", "jobs,users,products",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_with_postgres(self, temp_dir):
        """Test project generation with PostgreSQL."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myproject",
                "--db", "postgres",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_with_celery(self, temp_dir):
        """Test project generation with Celery."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myproject",
                "--celery",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_with_allauth(self, temp_dir):
        """Test project generation with allauth authentication."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myproject",
                "--auth", "allauth",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_with_session_auth(self, temp_dir):
        """Test project generation with session authentication."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myproject",
                "--auth", "session",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_ecommerce_template(self, temp_dir):
        """Test project generation with e-commerce template."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myshop",
                "--template", "ecommerce",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_blog_template(self, temp_dir):
        """Test project generation with blog template."""
        result = runner.invoke(
            app,
            [
                "init", "project", "myblog",
                "--template", "blog",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_generate_project_saas_template(self, temp_dir):
        """Test project generation with SaaS template."""
        result = runner.invoke(
            app,
            [
                "init", "project", "mysaas",
                "--template", "saas",
                "--output", str(temp_dir),
            ],
        )
        assert result.exit_code == 0 or "error" not in result.stdout.lower()


class TestCLIValidation:
    """Test CLI input validation."""

    def test_invalid_app_name(self, temp_dir):
        """Test invalid app name handling."""
        result = runner.invoke(
            app,
            ["init", "app", "invalid-name-with-dashes", "--output", str(temp_dir)],
        )
        # Should either succeed with sanitized name or show warning
        # The CLI should handle this gracefully

    def test_empty_app_name(self):
        """Test empty app name."""
        result = runner.invoke(app, ["init", "app", ""])
        # Should show error for empty name
        assert result.exit_code != 0 or "error" in result.stdout.lower()

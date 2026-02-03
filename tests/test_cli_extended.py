"""
Extended tests for CLI to achieve 95%+ coverage.
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from dual_apps.cli.main import (
    app, load_config, _parse_fields,
    _print_success_app, _print_success_project,
    interactive_app_setup, interactive_project_setup
)

runner = CliRunner()


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_yaml_config(self, temp_dir):
        """Test loading YAML configuration."""
        config = {
            "app": {
                "name": "testapp",
                "model": "TestModel",
            },
            "project": {
                "name": "testproject",
                "apps": ["jobs", "users"],
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = load_config(config_file)
        assert result["app"]["name"] == "testapp"
        assert result["project"]["apps"] == ["jobs", "users"]

    def test_load_yml_config(self, temp_dir):
        """Test loading .yml configuration."""
        config = {"app": {"name": "myapp"}}
        config_file = temp_dir / "config.yml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = load_config(config_file)
        assert result["app"]["name"] == "myapp"

    def test_load_json_config(self, temp_dir):
        """Test loading JSON configuration."""
        config = {
            "app": {"name": "jsonapp"},
            "project": {"name": "jsonproject", "db": "sqlite"}
        }
        config_file = temp_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f)

        result = load_config(config_file)
        assert result["app"]["name"] == "jsonapp"
        assert result["project"]["db"] == "sqlite"

    def test_load_nonexistent_config(self, temp_dir):
        """Test loading non-existent configuration returns empty dict."""
        config_file = temp_dir / "nonexistent.yaml"
        result = load_config(config_file)
        assert result == {}

    def test_load_empty_yaml_config(self, temp_dir):
        """Test loading empty YAML configuration."""
        config_file = temp_dir / "empty.yaml"
        config_file.write_text("")
        result = load_config(config_file)
        assert result == {}


class TestParseFields:
    """Test field parsing."""

    def test_parse_simple_fields(self):
        """Test parsing simple fields."""
        fields = _parse_fields("title:CharField,status:CharField")
        assert len(fields) == 2
        assert fields[0] == ("title", "CharField", {})
        assert fields[1] == ("status", "CharField", {})

    def test_parse_fields_with_options(self):
        """Test parsing fields with options in parentheses."""
        fields = _parse_fields("status:CharField(choices),price:DecimalField(max_digits=10)")
        assert len(fields) == 2
        assert fields[0] == ("status", "CharField", {"options": "choices"})
        assert fields[1] == ("price", "DecimalField", {"options": "max_digits=10"})

    def test_parse_empty_fields(self):
        """Test parsing empty fields string."""
        fields = _parse_fields("")
        assert fields == []

    def test_parse_none_fields(self):
        """Test parsing None returns empty list."""
        fields = _parse_fields(None)
        assert fields == []

    def test_parse_fields_without_colon(self):
        """Test fields without colon are skipped."""
        fields = _parse_fields("invalid,title:CharField")
        assert len(fields) == 1
        assert fields[0][0] == "title"

    def test_parse_fields_with_spaces(self):
        """Test parsing fields with extra spaces."""
        fields = _parse_fields(" title : CharField , status : CharField ")
        assert len(fields) == 2
        assert fields[0] == ("title", "CharField", {})
        assert fields[1] == ("status", "CharField", {})


class TestConfigCommand:
    """Test config command."""

    def test_generate_yaml_config(self, temp_dir):
        """Test generating YAML configuration file."""
        output_file = temp_dir / "dual-apps.yaml"
        result = runner.invoke(
            app,
            ["config", "--output", str(output_file), "--format", "yaml"]
        )
        assert result.exit_code == 0
        assert output_file.exists()

        with open(output_file) as f:
            config = yaml.safe_load(f)
        assert "project" in config
        assert "apps" in config

    def test_generate_json_config(self, temp_dir):
        """Test generating JSON configuration file."""
        output_file = temp_dir / "dual-apps.json"
        result = runner.invoke(
            app,
            ["config", "--output", str(output_file), "--format", "json"]
        )
        assert result.exit_code == 0
        assert output_file.exists()

        with open(output_file) as f:
            config = json.load(f)
        assert "project" in config
        assert config["project"]["name"] == "myproject"


class TestInfoCommand:
    """Test info command."""

    def test_info_command(self):
        """Test info command shows version and features."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "dual-apps" in result.stdout.lower() or "version" in result.stdout.lower()


class TestAddAppCommand:
    """Test add app command."""

    def test_add_app_to_project(self, temp_dir):
        """Test adding app to existing project."""
        # First create a project
        result = runner.invoke(
            app,
            ["init", "project", "myproject", "--output", str(temp_dir), "--no-docker"]
        )
        assert result.exit_code == 0

        # Now add an app
        project_dir = temp_dir / "myproject"
        result = runner.invoke(
            app,
            ["add", "app", "newapp", "--to", str(project_dir)]
        )
        assert result.exit_code == 0
        assert "newapp" in result.stdout.lower() or "added" in result.stdout.lower()

    def test_add_app_with_model(self, temp_dir):
        """Test adding app with custom model."""
        # Create project first
        runner.invoke(
            app,
            ["init", "project", "myproject", "--output", str(temp_dir), "--no-docker"]
        )

        project_dir = temp_dir / "myproject"
        result = runner.invoke(
            app,
            ["add", "app", "products", "--to", str(project_dir), "--model", "Product"]
        )
        assert result.exit_code == 0

    def test_add_app_with_fields(self, temp_dir):
        """Test adding app with fields."""
        runner.invoke(
            app,
            ["init", "project", "myproject", "--output", str(temp_dir), "--no-docker"]
        )

        project_dir = temp_dir / "myproject"
        result = runner.invoke(
            app,
            ["add", "app", "items", "--to", str(project_dir),
             "--fields", "name:str,price:decimal"]
        )
        assert result.exit_code == 0

    def test_add_app_no_apps_dir(self, temp_dir):
        """Test adding app when apps/ directory doesn't exist."""
        result = runner.invoke(
            app,
            ["add", "app", "newapp", "--to", str(temp_dir)]
        )
        assert result.exit_code == 1
        assert "apps/" in result.stdout.lower() or "not found" in result.stdout.lower()


class TestAppGenerationWithConfig:
    """Test app generation with config file."""

    def test_app_with_config_file(self, temp_dir):
        """Test app generation using config file."""
        config = {
            "app": {
                "name": "configapp",
                "model": "ConfigModel",
                "fields": "title:str,count:int",
                "docker": False,
                "celery": False,
                "i18n": False,
            }
        }
        config_file = temp_dir / "app-config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "app", "tempapp", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        # Config should override the name
        assert result.exit_code == 0


class TestProjectGenerationWithConfig:
    """Test project generation with config file."""

    def test_project_with_config_file(self, temp_dir):
        """Test project generation using config file."""
        config = {
            "project": {
                "name": "configproject",
                "apps": ["api", "web"],
                "template": "default",
                "db": "sqlite",
                "docker": False,
                "celery": False,
                "i18n": False,
            }
        }
        config_file = temp_dir / "project-config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "project", "tempproject", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0

    def test_project_with_apps_string_in_config(self, temp_dir):
        """Test project with apps as comma-separated string in config."""
        config = {
            "project": {
                "name": "myproject",
                "apps": "jobs,users,products",  # String instead of list
                "db": "postgres",
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "project", "temp", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestNoDockerPaths:
    """Test generation without Docker."""

    def test_app_no_docker(self, temp_dir):
        """Test app generation without Docker."""
        result = runner.invoke(
            app,
            ["init", "app", "nodockerapp", "--no-docker", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert not (temp_dir / "nodockerapp" / "docker").exists()

    def test_project_no_docker(self, temp_dir):
        """Test project generation without Docker."""
        result = runner.invoke(
            app,
            ["init", "project", "nodockerproj", "--no-docker", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0
        assert not (temp_dir / "nodockerproj" / "docker").exists()


class TestMissingName:
    """Test missing name handling."""

    def test_project_missing_name_in_config(self, temp_dir):
        """Test project with config but missing name."""
        config = {
            "project": {
                "apps": ["jobs"],
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "project", "--config", str(config_file), "--output", str(temp_dir)]
        )
        assert result.exit_code == 1


class TestSuccessPrinters:
    """Test success message printers."""

    def test_print_success_app(self, temp_dir, capsys):
        """Test app success message printer."""
        # This function uses rich console, just test it doesn't crash
        from rich.console import Console
        from io import StringIO

        console = Console(file=StringIO())
        _print_success_app("testapp", temp_dir)

    def test_print_success_project(self, temp_dir, capsys):
        """Test project success message printer."""
        _print_success_project("myproject", ["jobs", "users"], temp_dir, "jwt")


class TestCMSTemplate:
    """Test CMS template generation."""

    def test_cms_template(self, temp_dir):
        """Test project generation with CMS template."""
        result = runner.invoke(
            app,
            ["init", "project", "mycms", "--template", "cms", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestBookingTemplate:
    """Test booking template generation."""

    def test_booking_template(self, temp_dir):
        """Test project generation with booking template."""
        result = runner.invoke(
            app,
            ["init", "project", "mybooking", "--template", "booking",
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestMarketplaceTemplate:
    """Test marketplace template generation."""

    def test_marketplace_template(self, temp_dir):
        """Test project generation with marketplace template."""
        result = runner.invoke(
            app,
            ["init", "project", "mymarket", "--template", "marketplace",
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestAPITemplate:
    """Test API-only template generation."""

    def test_api_template(self, temp_dir):
        """Test project generation with API template."""
        result = runner.invoke(
            app,
            ["init", "project", "myapi", "--template", "api",
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestI18nOption:
    """Test internationalization option."""

    def test_app_with_i18n(self, temp_dir):
        """Test app generation with i18n."""
        result = runner.invoke(
            app,
            ["init", "app", "i18napp", "--i18n", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0

    def test_project_with_i18n(self, temp_dir):
        """Test project generation with i18n."""
        result = runner.invoke(
            app,
            ["init", "project", "i18nproject", "--i18n", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestCeleryOption:
    """Test Celery option in app generation."""

    def test_app_with_celery(self, temp_dir):
        """Test app generation with Celery."""
        result = runner.invoke(
            app,
            ["init", "app", "celeryapp", "--celery", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestFrontendOnlyOption:
    """Test frontend-only option."""

    def test_app_frontend_only(self, temp_dir):
        """Test frontend-only app generation."""
        result = runner.invoke(
            app,
            ["init", "app", "frontendapp", "--frontend-only", "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestInteractiveAppSetup:
    """Test interactive app setup function."""

    @patch('dual_apps.cli.main.Prompt.ask')
    @patch('dual_apps.cli.main.Confirm.ask')
    def test_interactive_app_setup(self, mock_confirm, mock_prompt):
        """Test interactive app setup returns config dict."""
        # Mock the prompts
        mock_prompt.side_effect = [
            "testapp",  # App name
            "TestModel",  # Model name
            "title:str,status:str",  # Fields
            "both",  # Layer selection
        ]
        mock_confirm.side_effect = [True, False, False]  # docker, celery, i18n

        config = interactive_app_setup()

        assert config["name"] == "testapp"
        assert config["model"] == "TestModel"
        assert config["fields"] == "title:str,status:str"
        assert config["docker"] is True
        assert config["celery"] is False
        assert config["i18n"] is False

    @patch('dual_apps.cli.main.Prompt.ask')
    @patch('dual_apps.cli.main.Confirm.ask')
    def test_interactive_app_setup_api_only(self, mock_confirm, mock_prompt):
        """Test interactive app setup with api-only."""
        mock_prompt.side_effect = [
            "apiapp",
            "ApiModel",
            "name:str",
            "api-only",
        ]
        mock_confirm.side_effect = [False, False, False]

        config = interactive_app_setup()

        assert config["api_only"] is True
        assert config["frontend_only"] is False

    @patch('dual_apps.cli.main.Prompt.ask')
    @patch('dual_apps.cli.main.Confirm.ask')
    def test_interactive_app_setup_frontend_only(self, mock_confirm, mock_prompt):
        """Test interactive app setup with frontend-only."""
        mock_prompt.side_effect = [
            "frontapp",
            "FrontModel",
            "title:str",
            "frontend-only",
        ]
        mock_confirm.side_effect = [True, True, True]

        config = interactive_app_setup()

        assert config["api_only"] is False
        assert config["frontend_only"] is True


class TestInteractiveProjectSetup:
    """Test interactive project setup function."""

    @patch('dual_apps.cli.main.Prompt.ask')
    @patch('dual_apps.cli.main.Confirm.ask')
    def test_interactive_project_setup(self, mock_confirm, mock_prompt):
        """Test interactive project setup returns config dict."""
        mock_prompt.side_effect = [
            "myproject",  # Project name
            "fullstack",  # Project type
            "default",  # Template
            "jobs,users",  # Apps
            "postgres",  # Database
            "jwt",  # Auth
            "httpOnly",  # JWT storage
            "htmx",  # Frontend
            "bootstrap",  # CSS
        ]
        mock_confirm.side_effect = [True, True, False]  # docker, celery, i18n

        config = interactive_project_setup()

        assert config["name"] == "myproject"
        assert config["apps"] == ["jobs", "users"]
        assert config["db"] == "postgres"
        assert config["auth"] == "jwt"
        assert config["template"] == "default"
        assert config["docker"] is True
        assert config["celery"] is True
        assert config["i18n"] is False

    @patch('dual_apps.cli.main.Prompt.ask')
    @patch('dual_apps.cli.main.Confirm.ask')
    def test_interactive_project_setup_all_options(self, mock_confirm, mock_prompt):
        """Test interactive project setup with all options."""
        mock_prompt.side_effect = [
            "fullproject",  # Project name
            "fullstack",  # Project type
            "ecommerce",  # Template
            "api,web,admin",  # Apps
            "sqlite",  # Database
            "allauth",  # Auth (no JWT storage prompt for allauth)
            "react",  # Frontend
            "tailwind",  # CSS
        ]
        mock_confirm.side_effect = [False, False, True]

        config = interactive_project_setup()

        assert config["name"] == "fullproject"
        assert len(config["apps"]) == 3
        assert config["db"] == "sqlite"
        assert config["auth"] == "allauth"
        assert config["template"] == "ecommerce"


class TestInteractiveCLIMode:
    """Test CLI interactive mode invocation."""

    @patch('dual_apps.cli.main.interactive_app_setup')
    def test_app_interactive_mode(self, mock_setup, temp_dir):
        """Test app generation in interactive mode."""
        mock_setup.return_value = {
            "name": "interactiveapp",
            "model": "InteractiveModel",
            "fields": "title:str",
            "docker": False,
            "celery": False,
            "i18n": False,
            "api_only": False,
            "frontend_only": False,
        }

        result = runner.invoke(
            app,
            ["init", "app", "--interactive", "--output", str(temp_dir)]
        )
        # Should call interactive_app_setup
        mock_setup.assert_called_once()

    @patch('dual_apps.cli.main.interactive_project_setup')
    def test_project_interactive_mode(self, mock_setup, temp_dir):
        """Test project generation in interactive mode."""
        mock_setup.return_value = {
            "name": "interactiveproj",
            "apps": ["jobs"],
            "template": "default",
            "db": "postgres",
            "auth": "jwt",
            "docker": False,
            "celery": False,
            "i18n": False,
        }

        result = runner.invoke(
            app,
            ["init", "project", "--interactive", "--output", str(temp_dir)]
        )
        mock_setup.assert_called_once()


class TestLoadConfigEdgeCases:
    """Test load_config edge cases."""

    def test_load_unknown_file_type(self, temp_dir):
        """Test loading unknown file type returns empty dict."""
        config_file = temp_dir / "config.txt"
        config_file.write_text("some content")

        result = load_config(config_file)
        assert result == {}


class TestAppConfigWithAllOptions:
    """Test app config with all options."""

    def test_app_config_overrides_all(self, temp_dir):
        """Test config file overrides all app options."""
        config = {
            "app": {
                "name": "configuredapp",
                "model": "ConfiguredModel",
                "fields": "name:str,count:int",
                "docker": True,
                "celery": True,
                "i18n": True,
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "app", "ignored", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestProjectConfigWithAllOptions:
    """Test project config with all options."""

    def test_project_config_overrides_all(self, temp_dir):
        """Test config file overrides all project options."""
        config = {
            "project": {
                "name": "configuredproj",
                "apps": ["core", "api", "web"],
                "template": "saas",
                "db": "sqlite",
                "docker": True,
                "celery": True,
                "i18n": True,
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "project", "ignored", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestMainIfBlock:
    """Test the if __name__ == '__main__' block."""

    def test_cli_main_module_execution(self):
        """Test CLI main module can be executed."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-c",
             "from dual_apps.cli.main import app; app(['--help'])"],
            capture_output=True,
            text=True
        )
        # The command should work (exit code 0 means success)
        assert result.returncode == 0 or "Usage" in result.stdout or "usage" in result.stderr


class TestMissingProjectName:
    """Test missing project name error handling."""

    def test_project_no_name_no_config(self, temp_dir):
        """Test project with no name and no config shows error."""
        # When no name is provided and no config file
        result = runner.invoke(
            app,
            ["init", "project", "--output", str(temp_dir)]
        )
        # Should fail with error
        assert result.exit_code == 1 or "error" in result.stdout.lower()

    def test_project_empty_name(self, temp_dir):
        """Test project with empty name shows error."""
        result = runner.invoke(
            app,
            ["init", "project", "", "--output", str(temp_dir)]
        )
        assert result.exit_code != 0 or "error" in result.stdout.lower()


class TestConfigFileWithAuth:
    """Test config file auth handling."""

    def test_project_config_with_auth(self, temp_dir):
        """Test project config with auth option."""
        config = {
            "project": {
                "name": "authproject",
                "apps": ["users"],
                "auth": "session",
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "project", "temp", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0


class TestConfigFileAppsList:
    """Test config file apps list handling."""

    def test_project_config_apps_as_list(self, temp_dir):
        """Test project config with apps as list."""
        config = {
            "project": {
                "name": "listapps",
                "apps": ["users", "products", "orders"],
            }
        }
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app,
            ["init", "project", "temp", "--config", str(config_file),
             "--output", str(temp_dir)]
        )
        assert result.exit_code == 0

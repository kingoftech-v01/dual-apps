"""
Extended tests for ProjectGenerator to achieve 95%+ coverage.
"""

import pytest
from pathlib import Path
from dual_apps.generators.project_generator import ProjectGenerator


class TestProjectGeneratorI18n:
    """Test ProjectGenerator i18n support."""

    def test_i18n_in_context(self, temp_dir):
        """Test i18n flag in context."""
        gen = ProjectGenerator(
            project_name="i18nproject",
            i18n=True,
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["i18n"] is True


class TestProjectGeneratorAPITemplate:
    """Test ProjectGenerator API-only template."""

    def test_api_template(self, temp_dir):
        """Test API template generation."""
        gen = ProjectGenerator(
            project_name="apiproject",
            template="api",
            output_dir=temp_dir
        )
        assert gen.template == "api"
        ctx = gen.get_context()
        assert ctx["template"] == "api"


class TestProjectGeneratorTemplateExists:
    """Test ProjectGenerator template_exists method."""

    def test_existing_template(self, temp_dir):
        """Test template_exists for existing template."""
        gen = ProjectGenerator(
            project_name="test",
            output_dir=temp_dir
        )
        assert gen.template_exists("app/models.py.j2") is True

    def test_non_existing_template(self, temp_dir):
        """Test template_exists for non-existing template."""
        gen = ProjectGenerator(
            project_name="test",
            output_dir=temp_dir
        )
        assert gen.template_exists("nonexistent.j2") is False


class TestProjectGeneratorStats:
    """Test ProjectGenerator statistics."""

    def test_get_stats(self, temp_dir):
        """Test getting generation statistics."""
        gen = ProjectGenerator(
            project_name="statsproject",
            apps=["jobs"],
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_settings()

        stats = gen.get_stats()
        assert stats["files_created"] > 0
        assert stats["dirs_created"] > 0


class TestProjectGeneratorAllTemplates:
    """Test all specialized templates."""

    def test_all_template_types(self, temp_dir):
        """Test all template types can be initialized."""
        templates = ["default", "ecommerce", "blog", "saas", "cms", "booking", "marketplace", "api"]

        for template in templates:
            gen = ProjectGenerator(
                project_name=f"{template}_project",
                template=template,
                output_dir=temp_dir
            )
            ctx = gen.get_context()
            assert ctx["template"] == template


class TestProjectGeneratorAuthVariants:
    """Test all auth variants."""

    def test_auth_none(self, temp_dir):
        """Test auth=none option."""
        gen = ProjectGenerator(
            project_name="noauth",
            auth="none",
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["use_jwt"] is False
        assert ctx["use_session"] is False
        assert ctx["use_allauth"] is False


class TestProjectGeneratorDockerDisabled:
    """Test ProjectGenerator with Docker disabled."""

    def test_no_docker_dir(self, temp_dir):
        """Test docker=False doesn't create docker directory."""
        gen = ProjectGenerator(
            project_name="nodockerproj",
            docker=False,
            output_dir=temp_dir
        )
        gen.create_structure()

        assert not (temp_dir / "nodockerproj" / "docker").exists()


class TestProjectGeneratorCeleryDisabled:
    """Test ProjectGenerator with Celery disabled."""

    def test_no_celery_file(self, temp_dir):
        """Test celery=False doesn't create celery.py."""
        gen = ProjectGenerator(
            project_name="noceleryproj",
            celery=False,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_settings()

        assert not (temp_dir / "noceleryproj" / "noceleryproj" / "celery.py").exists()


class TestProjectGeneratorMultipleApps:
    """Test ProjectGenerator with multiple apps."""

    def test_many_apps(self, temp_dir):
        """Test project with many apps."""
        gen = ProjectGenerator(
            project_name="manyapps",
            apps=["users", "products", "orders", "payments", "notifications"],
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_apps()

        apps_dir = temp_dir / "manyapps" / "apps"
        assert (apps_dir / "users").exists()
        assert (apps_dir / "products").exists()
        assert (apps_dir / "orders").exists()
        assert (apps_dir / "payments").exists()
        assert (apps_dir / "notifications").exists()


class TestProjectGeneratorAppsConfig:
    """Test apps_config in context."""

    def test_apps_config_structure(self, temp_dir):
        """Test apps_config has correct structure."""
        gen = ProjectGenerator(
            project_name="test",
            apps=["user_profiles", "job_postings"],
            output_dir=temp_dir
        )
        ctx = gen.get_context()

        assert len(ctx["apps_config"]) == 2

        user_config = ctx["apps_config"][0]
        assert user_config["name"] == "user_profiles"
        assert user_config["name_pascal"] == "UserProfiles"

        job_config = ctx["apps_config"][1]
        assert job_config["name"] == "job_postings"
        assert job_config["name_pascal"] == "JobPostings"


class TestProjectGeneratorSQLite:
    """Test ProjectGenerator with SQLite."""

    def test_sqlite_context(self, temp_dir):
        """Test SQLite database context flags."""
        gen = ProjectGenerator(
            project_name="sqliteproj",
            db="sqlite",
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["db"] == "sqlite"
        assert ctx["use_postgres"] is False


class TestProjectGeneratorWriteFile:
    """Test ProjectGenerator write_file method."""

    def test_write_executable(self, temp_dir):
        """Test writing executable file."""
        import os
        import stat

        gen = ProjectGenerator(
            project_name="test",
            output_dir=temp_dir
        )
        gen.write_file(Path("script.sh"), "#!/bin/bash\necho test", executable=True)

        file_path = temp_dir / "script.sh"
        assert file_path.exists()
        mode = os.stat(file_path).st_mode
        assert mode & stat.S_IXUSR


class TestProjectGeneratorGenerateScripts:
    """Test script generation."""

    def test_generate_scripts(self, temp_dir):
        """Test script generation."""
        gen = ProjectGenerator(
            project_name="scriptstest",
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_scripts()

        scripts_dir = temp_dir / "scriptstest" / "scripts"
        assert scripts_dir.exists()


class TestProjectGeneratorGitHubActions:
    """Test GitHub Actions generation."""

    def test_generate_github_actions(self, temp_dir):
        """Test GitHub Actions generation."""
        gen = ProjectGenerator(
            project_name="actionstest",
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_github_actions()

        workflows_dir = temp_dir / "actionstest" / ".github" / "workflows"
        assert workflows_dir.exists()

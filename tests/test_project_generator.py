"""
Tests for ProjectGenerator class.
"""

import pytest
from pathlib import Path
from dual_apps.generators.project_generator import ProjectGenerator


class TestProjectGeneratorInit:
    """Test ProjectGenerator initialization."""

    def test_default_apps(self, temp_dir):
        """Test default apps list."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        assert gen.apps == ["jobs"]

    def test_custom_apps(self, temp_dir):
        """Test custom apps list."""
        gen = ProjectGenerator(
            project_name="myproject",
            apps=["jobs", "users", "products"],
            output_dir=temp_dir
        )
        assert gen.apps == ["jobs", "users", "products"]

    def test_project_name_normalization(self, temp_dir):
        """Test project name is normalized."""
        gen = ProjectGenerator(project_name="MyProject", output_dir=temp_dir)
        assert gen.project_name == "my_project"

    def test_default_database(self, temp_dir):
        """Test default database is postgres."""
        gen = ProjectGenerator(project_name="test", output_dir=temp_dir)
        assert gen.db == "postgres"

    def test_sqlite_database(self, temp_dir):
        """Test SQLite database option."""
        gen = ProjectGenerator(project_name="test", db="sqlite", output_dir=temp_dir)
        assert gen.db == "sqlite"


class TestProjectGeneratorContext:
    """Test ProjectGenerator context generation."""

    def test_context_has_project_name(self, temp_dir):
        """Test context contains project name."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        ctx = gen.get_context()
        assert ctx["project_name"] == "myproject"

    def test_context_has_apps(self, temp_dir):
        """Test context contains apps list."""
        gen = ProjectGenerator(
            project_name="myproject",
            apps=["jobs", "users"],
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["apps"] == ["jobs", "users"]

    def test_context_has_apps_config(self, temp_dir):
        """Test context contains apps config with name variants."""
        gen = ProjectGenerator(
            project_name="myproject",
            apps=["jobs"],
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert "apps_config" in ctx
        assert len(ctx["apps_config"]) == 1
        assert ctx["apps_config"][0]["name"] == "jobs"
        assert ctx["apps_config"][0]["name_pascal"] == "Jobs"

    def test_context_has_database_flag(self, temp_dir):
        """Test context contains database flags."""
        gen = ProjectGenerator(project_name="test", db="postgres", output_dir=temp_dir)
        ctx = gen.get_context()
        assert ctx["use_postgres"] is True
        assert ctx["db"] == "postgres"

    def test_context_has_celery_flag(self, temp_dir):
        """Test context contains celery flag."""
        gen = ProjectGenerator(project_name="test", celery=True, output_dir=temp_dir)
        ctx = gen.get_context()
        assert ctx["celery"] is True


class TestProjectGeneratorStructure:
    """Test ProjectGenerator directory structure."""

    def test_create_structure(self, temp_dir):
        """Test directory structure is created."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        gen.create_structure()

        project_dir = temp_dir / "myproject"
        assert project_dir.exists()
        assert (project_dir / "myproject").exists()
        assert (project_dir / "myproject" / "settings").exists()
        assert (project_dir / "apps").exists()
        assert (project_dir / "templates").exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / "docs").exists()

    def test_create_structure_with_docker(self, temp_dir):
        """Test Docker directories are created."""
        gen = ProjectGenerator(project_name="test", docker=True, output_dir=temp_dir)
        gen.create_structure()

        project_dir = temp_dir / "test"
        assert (project_dir / "docker").exists()
        assert (project_dir / "docker" / "nginx").exists()

    def test_create_structure_without_docker(self, temp_dir):
        """Test Docker directories are not created when disabled."""
        gen = ProjectGenerator(project_name="test", docker=False, output_dir=temp_dir)
        gen.create_structure()

        project_dir = temp_dir / "test"
        assert not (project_dir / "docker").exists()

    def test_create_structure_with_i18n(self, temp_dir):
        """Test locale directory is created with i18n."""
        gen = ProjectGenerator(project_name="test", i18n=True, output_dir=temp_dir)
        gen.create_structure()

        project_dir = temp_dir / "test"
        assert (project_dir / "locale").exists()


class TestProjectGeneratorSettings:
    """Test ProjectGenerator settings generation."""

    def test_generate_settings(self, temp_dir):
        """Test settings files are generated."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_settings()

        settings_dir = temp_dir / "myproject" / "myproject" / "settings"
        assert (settings_dir / "__init__.py").exists()
        assert (settings_dir / "base.py").exists()
        assert (settings_dir / "dev.py").exists()
        assert (settings_dir / "prod.py").exists()
        assert (settings_dir / "security.py").exists()

    def test_generate_core_files(self, temp_dir):
        """Test core project files are generated."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_settings()

        project_module = temp_dir / "myproject" / "myproject"
        assert (project_module / "urls.py").exists()
        assert (project_module / "wsgi.py").exists()
        assert (project_module / "asgi.py").exists()

    def test_generate_manage_py(self, temp_dir):
        """Test manage.py is generated."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_settings()

        assert (temp_dir / "myproject" / "manage.py").exists()

    def test_generate_celery_when_enabled(self, temp_dir):
        """Test celery.py is generated when celery is enabled."""
        gen = ProjectGenerator(project_name="test", celery=True, output_dir=temp_dir)
        gen.create_structure()
        gen.generate_settings()

        assert (temp_dir / "test" / "test" / "celery.py").exists()


class TestProjectGeneratorApps:
    """Test ProjectGenerator app generation."""

    def test_generate_apps(self, temp_dir):
        """Test apps are generated."""
        gen = ProjectGenerator(
            project_name="myproject",
            apps=["jobs", "users"],
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_apps()

        apps_dir = temp_dir / "myproject" / "apps"
        assert (apps_dir / "jobs").exists()
        assert (apps_dir / "users").exists()

    def test_apps_have_models(self, temp_dir):
        """Test generated apps have model files."""
        gen = ProjectGenerator(
            project_name="myproject",
            apps=["jobs"],
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_apps()

        assert (temp_dir / "myproject" / "apps" / "jobs" / "jobs" / "models.py").exists()


class TestProjectGeneratorDocs:
    """Test ProjectGenerator documentation."""

    def test_generate_docs(self, temp_dir):
        """Test documentation is generated."""
        gen = ProjectGenerator(project_name="myproject", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_docs()

        project_dir = temp_dir / "myproject"
        assert (project_dir / "README.md").exists()
        assert (project_dir / "CHANGELOG.md").exists()
        assert (project_dir / "docs" / "DEVELOPMENT.md").exists()


class TestProjectGeneratorFull:
    """Test full project generation."""

    def test_full_generation(self, temp_dir):
        """Test complete project generation."""
        gen = ProjectGenerator(
            project_name="fullproject",
            apps=["jobs", "users"],
            db="postgres",
            docker=True,
            celery=True,
            output_dir=temp_dir,
        )

        gen.create_structure()
        gen.generate_settings()
        gen.generate_apps()
        gen.generate_tests()
        gen.generate_docs()
        gen.generate_github_actions()
        gen.generate_scripts()

        if gen.docker:
            gen.generate_docker()

        gen.finalize()

        project_dir = temp_dir / "fullproject"

        # Check structure
        assert project_dir.exists()
        assert (project_dir / "fullproject" / "settings").exists()
        assert (project_dir / "apps" / "jobs").exists()
        assert (project_dir / "apps" / "users").exists()
        assert (project_dir / "docker").exists()
        assert (project_dir / ".github" / "workflows").exists()

        # Check key files
        assert (project_dir / "manage.py").exists()
        assert (project_dir / "fullproject" / "celery.py").exists()
        assert (project_dir / "docker-compose.yml").exists()
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "README.md").exists()

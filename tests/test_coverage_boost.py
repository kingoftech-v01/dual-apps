"""Additional tests to boost coverage to 95%+."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from dual_apps.generators.project_generator import ProjectGenerator
from dual_apps.generators.app_generator import AppGenerator


class TestProjectTypeVariations:
    """Test all project type variations."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_backend_project_type(self, temp_dir):
        """Test backend-only project type."""
        generator = ProjectGenerator(
            project_name="test_backend",
            output_dir=Path(temp_dir),
            project_type="backend",
        )

        ctx = generator.get_context()
        assert ctx["project_type"] == "backend"
        assert ctx["is_backend_only"] is True
        assert ctx["is_fullstack"] is False
        assert ctx["is_frontend_only"] is False
        assert ctx["has_frontend"] is False
        assert ctx["has_api"] is True

    def test_frontend_project_type(self, temp_dir):
        """Test frontend-only project type."""
        generator = ProjectGenerator(
            project_name="test_frontend",
            output_dir=Path(temp_dir),
            project_type="frontend",
        )

        ctx = generator.get_context()
        assert ctx["project_type"] == "frontend"
        assert ctx["is_frontend_only"] is True
        assert ctx["is_fullstack"] is False
        assert ctx["is_backend_only"] is False
        assert ctx["has_frontend"] is True
        assert ctx["has_api"] is False

    def test_fullstack_project_type(self, temp_dir):
        """Test fullstack project type (default)."""
        generator = ProjectGenerator(
            project_name="test_fullstack",
            output_dir=Path(temp_dir),
            project_type="fullstack",
        )

        ctx = generator.get_context()
        assert ctx["project_type"] == "fullstack"
        assert ctx["is_fullstack"] is True
        assert ctx["is_backend_only"] is False
        assert ctx["is_frontend_only"] is False
        assert ctx["has_frontend"] is True
        assert ctx["has_api"] is True


class TestSpecializedTemplates:
    """Test specialized template handling."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_specialized_template_default_apps(self, temp_dir, template_type):
        """Test that specialized templates use their default apps."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            template=template_type,
        )

        # Should have at least one app
        assert len(generator.apps) >= 1

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_specialized_template_custom_apps(self, temp_dir, template_type):
        """Test that custom apps override defaults."""
        custom_apps = ["custom_app", "another_app"]
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            template=template_type,
            apps=custom_apps,
        )

        assert generator.apps == custom_apps


class TestFrontendOptions:
    """Test frontend framework and CSS options."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.parametrize("frontend", ["html", "htmx", "react"])
    def test_frontend_framework_context(self, temp_dir, frontend):
        """Test frontend framework is in context."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            frontend=frontend,
        )

        ctx = generator.get_context()
        assert ctx["frontend"] == frontend

    @pytest.mark.parametrize("css", ["bootstrap", "tailwind"])
    def test_css_framework_context(self, temp_dir, css):
        """Test CSS framework is in context."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            css=css,
        )

        ctx = generator.get_context()
        assert ctx["css"] == css

    @pytest.mark.parametrize("jwt_storage", ["httpOnly", "localStorage"])
    def test_jwt_storage_context(self, temp_dir, jwt_storage):
        """Test JWT storage option is in context."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            jwt_storage=jwt_storage,
        )

        ctx = generator.get_context()
        assert ctx["jwt_storage"] == jwt_storage


class TestDatabaseOptions:
    """Test database configuration options."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.parametrize("db", ["postgres", "mysql", "sqlite"])
    def test_database_config(self, temp_dir, db):
        """Test database configuration in context."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            db=db,
        )

        ctx = generator.get_context()
        assert ctx["db"] == db


class TestAuthOptions:
    """Test authentication options."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.parametrize("auth", ["jwt", "session", "allauth"])
    def test_auth_config(self, temp_dir, auth):
        """Test authentication configuration in context."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            auth=auth,
        )

        ctx = generator.get_context()
        assert ctx["auth"] == auth
        assert ctx["use_jwt"] == (auth == "jwt")


class TestDockerCeleryOptions:
    """Test Docker and Celery options."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_docker_enabled(self, temp_dir):
        """Test Docker option enabled."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            docker=True,
        )

        ctx = generator.get_context()
        assert ctx["docker"] is True

    def test_docker_disabled(self, temp_dir):
        """Test Docker option disabled."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            docker=False,
        )

        ctx = generator.get_context()
        assert ctx["docker"] is False

    def test_celery_enabled(self, temp_dir):
        """Test Celery option enabled."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            celery=True,
        )

        ctx = generator.get_context()
        assert ctx["celery"] is True

    def test_celery_disabled(self, temp_dir):
        """Test Celery option disabled."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            celery=False,
        )

        ctx = generator.get_context()
        assert ctx["celery"] is False


class TestI18nOption:
    """Test internationalization option."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_i18n_enabled(self, temp_dir):
        """Test i18n option enabled."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            i18n=True,
        )

        ctx = generator.get_context()
        assert ctx["i18n"] is True

    def test_i18n_disabled(self, temp_dir):
        """Test i18n option disabled."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            i18n=False,
        )

        ctx = generator.get_context()
        assert ctx["i18n"] is False


class TestProjectNameConversions:
    """Test project name conversions."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_project_name_conversions(self, temp_dir):
        """Test various name conversions."""
        generator = ProjectGenerator(
            project_name="my_test_project",
            output_dir=Path(temp_dir),
        )

        ctx = generator.get_context()
        assert ctx["project_name"] == "my_test_project"
        assert "project_name_pascal" in ctx
        assert "project_name_display" in ctx

    def test_apps_config_structure(self, temp_dir):
        """Test apps config structure."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            apps=["users", "products"],
        )

        ctx = generator.get_context()
        assert len(ctx["apps_config"]) == 2

        for app_cfg in ctx["apps_config"]:
            assert "name" in app_cfg
            assert "name_pascal" in app_cfg
            assert "name_title" in app_cfg


class TestGeneratorGenerate:
    """Test the generate method."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_creates_project_directory(self, temp_dir):
        """Test that create_structure creates the project directory."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()

        project_path = Path(temp_dir) / "test_project"
        assert project_path.exists()

    def test_generate_with_all_options(self, temp_dir):
        """Test generation with all options enabled."""
        generator = ProjectGenerator(
            project_name="full_project",
            output_dir=Path(temp_dir),
            db="postgres",
            docker=True,
            celery=True,
            i18n=True,
            auth="jwt",
            apps=["users", "products"],
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / "full_project"
        assert project_path.exists()
        assert (project_path / "manage.py").exists()

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_generate_specialized_templates(self, temp_dir, template_type):
        """Test generating each specialized template."""
        generator = ProjectGenerator(
            project_name=f"test_{template_type}",
            output_dir=Path(temp_dir),
            template=template_type,
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / f"test_{template_type}"
        assert project_path.exists()


class TestAppGenerator:
    """Test the AppGenerator class."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_app_generator_init(self, temp_dir):
        """Test AppGenerator initialization."""
        generator = AppGenerator(
            app_name="new_app",
            output_dir=Path(temp_dir),
        )

        assert generator.app_name == "new_app"

    def test_app_generator_context(self, temp_dir):
        """Test AppGenerator context."""
        generator = AppGenerator(
            app_name="new_app",
            output_dir=Path(temp_dir),
        )

        ctx = generator.get_context()
        assert ctx["app_name"] == "new_app"
        assert "app_name_pascal" in ctx


class TestBaseGeneratorMethods:
    """Test base generator methods."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_to_pascal_case(self, temp_dir):
        """Test _to_pascal_case method."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        assert generator._to_pascal_case("hello_world") == "HelloWorld"
        assert generator._to_pascal_case("my_app") == "MyApp"
        assert generator._to_pascal_case("test") == "Test"

    def test_to_title_case(self, temp_dir):
        """Test _to_title_case method."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        assert generator._to_title_case("hello_world") == "Hello World"
        assert generator._to_title_case("my_app") == "My App"

    def test_template_exists(self, temp_dir):
        """Test template_exists method."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        # A core template should exist
        assert generator.template_exists("project/manage.py.j2") is True
        # A non-existent template should not exist
        assert generator.template_exists("non_existent_template.j2") is False


class TestRenderAndWrite:
    """Test render_and_write functionality."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_render_and_write_creates_file(self, temp_dir):
        """Test that render_and_write creates a file."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        output_path = Path(temp_dir) / "test_output.py"
        ctx = generator.get_context()

        # Use an existing template
        generator.render_and_write(
            "project/manage.py.j2",
            output_path,
            ctx,
        )

        assert output_path.exists()

    def test_render_and_write_creates_directories(self, temp_dir):
        """Test that render_and_write creates parent directories."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        output_path = Path(temp_dir) / "deep" / "nested" / "path" / "test.py"
        ctx = generator.get_context()

        generator.render_and_write(
            "project/manage.py.j2",
            output_path,
            ctx,
        )

        assert output_path.exists()


class TestGetStats:
    """Test get_stats method."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_get_stats_returns_dict(self, temp_dir):
        """Test that get_stats returns a dictionary."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()
        generator.generate_settings()
        stats = generator.get_stats()

        assert isinstance(stats, dict)
        assert "files_created" in stats
        assert "dirs_created" in stats


class TestFrontendGeneration:
    """Test frontend generation methods."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_html_frontend_generation(self, temp_dir):
        """Test HTML frontend generation."""
        generator = ProjectGenerator(
            project_name="test_html",
            output_dir=Path(temp_dir),
            frontend="html",
            project_type="fullstack",
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / "test_html"
        assert project_path.exists()

    def test_htmx_frontend_generation(self, temp_dir):
        """Test HTMX frontend generation."""
        generator = ProjectGenerator(
            project_name="test_htmx",
            output_dir=Path(temp_dir),
            frontend="htmx",
            project_type="fullstack",
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / "test_htmx"
        assert project_path.exists()

    def test_react_frontend_generation(self, temp_dir):
        """Test React frontend generation."""
        generator = ProjectGenerator(
            project_name="test_react",
            output_dir=Path(temp_dir),
            frontend="react",
            project_type="fullstack",
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / "test_react"
        assert project_path.exists()


class TestContextFlags:
    """Test boolean context flags."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_all_flags_present(self, temp_dir):
        """Test that all expected flags are in context."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        ctx = generator.get_context()

        # Check essential flags exist
        expected_flags = [
            "docker",
            "celery",
            "i18n",
            "use_jwt",
            "has_frontend",
            "has_api",
        ]

        for flag in expected_flags:
            assert flag in ctx, f"Missing flag: {flag}"


class TestMultipleApps:
    """Test handling multiple apps."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_multiple_apps_generation(self, temp_dir):
        """Test generating project with multiple apps."""
        apps = ["users", "products", "orders", "reviews"]

        generator = ProjectGenerator(
            project_name="multi_app_project",
            output_dir=Path(temp_dir),
            apps=apps,
        )

        ctx = generator.get_context()
        assert ctx["apps"] == apps
        assert len(ctx["apps_config"]) == len(apps)

    def test_single_app_generation(self, temp_dir):
        """Test generating project with single app."""
        generator = ProjectGenerator(
            project_name="single_app_project",
            output_dir=Path(temp_dir),
            apps=["myapp"],
        )

        ctx = generator.get_context()
        assert ctx["apps"] == ["myapp"]
        assert len(ctx["apps_config"]) == 1


class TestJWTStorageFlags:
    """Test JWT storage boolean flags."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_httponly_jwt_flag(self, temp_dir):
        """Test httpOnly JWT storage flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            jwt_storage="httpOnly",
        )

        ctx = generator.get_context()
        assert ctx["use_httponly_jwt"] is True
        assert ctx["use_localstorage_jwt"] is False

    def test_localstorage_jwt_flag(self, temp_dir):
        """Test localStorage JWT storage flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            jwt_storage="localStorage",
        )

        ctx = generator.get_context()
        assert ctx["use_httponly_jwt"] is False
        assert ctx["use_localstorage_jwt"] is True


class TestDatabaseFlags:
    """Test database boolean flags."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_postgres_flag(self, temp_dir):
        """Test PostgreSQL flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            db="postgres",
        )

        ctx = generator.get_context()
        assert ctx["use_postgres"] is True
        assert ctx["use_mysql"] is False
        assert ctx["use_sqlite"] is False

    def test_mysql_flag(self, temp_dir):
        """Test MySQL flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            db="mysql",
        )

        ctx = generator.get_context()
        assert ctx["use_postgres"] is False
        assert ctx["use_mysql"] is True
        assert ctx["use_sqlite"] is False

    def test_sqlite_flag(self, temp_dir):
        """Test SQLite flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            db="sqlite",
        )

        ctx = generator.get_context()
        assert ctx["use_postgres"] is False
        assert ctx["use_mysql"] is False
        assert ctx["use_sqlite"] is True


class TestFrontendFlags:
    """Test frontend boolean flags."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_html_flag(self, temp_dir):
        """Test HTML flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            frontend="html",
        )

        ctx = generator.get_context()
        assert ctx["use_html"] is True
        assert ctx["use_htmx"] is False
        assert ctx["use_react"] is False

    def test_htmx_flag(self, temp_dir):
        """Test HTMX flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            frontend="htmx",
        )

        ctx = generator.get_context()
        assert ctx["use_html"] is False
        assert ctx["use_htmx"] is True
        assert ctx["use_react"] is False

    def test_react_flag(self, temp_dir):
        """Test React flag."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            frontend="react",
        )

        ctx = generator.get_context()
        assert ctx["use_html"] is False
        assert ctx["use_htmx"] is False
        assert ctx["use_react"] is True


class TestSpecializedTemplateFlag:
    """Test specialized template flag."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_default_template_flag(self, temp_dir):
        """Test default template is not specialized."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            template="default",
        )

        ctx = generator.get_context()
        assert ctx["is_specialized_template"] is False

    @pytest.mark.parametrize("template", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_specialized_template_flag(self, temp_dir, template):
        """Test specialized templates are flagged."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
            template=template,
        )

        ctx = generator.get_context()
        assert ctx["is_specialized_template"] is True


class TestFinalizeMethod:
    """Test the finalize method and its components."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_finalize_creates_config_files(self, temp_dir):
        """Test that finalize creates configuration files."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()
        generator.finalize()

        project_path = Path(temp_dir) / "test_project"
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "pytest.ini").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / ".env.example").exists()

    def test_finalize_with_react(self, temp_dir):
        """Test finalize with React frontend."""
        generator = ProjectGenerator(
            project_name="test_react_full",
            output_dir=Path(temp_dir),
            frontend="react",
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()
        generator.finalize()

        project_path = Path(temp_dir) / "test_react_full"
        assert project_path.exists()


class TestSecurityModuleGeneration:
    """Test security module generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_security_module(self, temp_dir):
        """Test security module generation."""
        generator = ProjectGenerator(
            project_name="test_security",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()
        generator.generate_security_module()

        project_path = Path(temp_dir) / "test_security"
        # Security module is at apps/core/security
        security_dir = project_path / "apps" / "core" / "security"
        assert security_dir.exists()


class TestDockerGeneration:
    """Test Docker file generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_docker_files(self, temp_dir):
        """Test Docker file generation."""
        generator = ProjectGenerator(
            project_name="test_docker",
            output_dir=Path(temp_dir),
            docker=True,
        )

        generator.create_structure()
        generator.generate_docker()

        project_path = Path(temp_dir) / "test_docker"
        assert (project_path / "docker").exists()
        assert (project_path / "docker-compose.yml").exists()


class TestDocsGeneration:
    """Test documentation generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_docs(self, temp_dir):
        """Test documentation generation."""
        generator = ProjectGenerator(
            project_name="test_docs",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()
        generator.generate_docs()

        project_path = Path(temp_dir) / "test_docs"
        docs_dir = project_path / "docs"
        assert docs_dir.exists()


class TestTestsGeneration:
    """Test test file generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_tests(self, temp_dir):
        """Test test file generation."""
        generator = ProjectGenerator(
            project_name="test_tests",
            output_dir=Path(temp_dir),
            apps=["myapp"],
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()
        generator.generate_tests()

        project_path = Path(temp_dir) / "test_tests"
        tests_dir = project_path / "tests"
        assert tests_dir.exists()


class TestGitHubActionsGeneration:
    """Test GitHub Actions generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_github_actions(self, temp_dir):
        """Test GitHub Actions generation."""
        generator = ProjectGenerator(
            project_name="test_actions",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()
        generator.generate_github_actions()

        project_path = Path(temp_dir) / "test_actions"
        github_dir = project_path / ".github" / "workflows"
        assert github_dir.exists()


class TestScriptsGeneration:
    """Test scripts generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_scripts(self, temp_dir):
        """Test scripts generation."""
        generator = ProjectGenerator(
            project_name="test_scripts",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()
        generator.generate_scripts()

        project_path = Path(temp_dir) / "test_scripts"
        scripts_dir = project_path / "scripts"
        assert scripts_dir.exists()


class TestTemplatesStaticGeneration:
    """Test templates and static files generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_templates_static_html(self, temp_dir):
        """Test HTML templates and static files."""
        generator = ProjectGenerator(
            project_name="test_html_static",
            output_dir=Path(temp_dir),
            frontend="html",
        )

        generator.create_structure()
        generator.generate_templates_static()

        project_path = Path(temp_dir) / "test_html_static"
        templates_dir = project_path / "templates"
        assert templates_dir.exists()

    def test_generate_templates_static_htmx(self, temp_dir):
        """Test HTMX templates and static files."""
        generator = ProjectGenerator(
            project_name="test_htmx_static",
            output_dir=Path(temp_dir),
            frontend="htmx",
        )

        generator.create_structure()
        generator.generate_templates_static()

        project_path = Path(temp_dir) / "test_htmx_static"
        templates_dir = project_path / "templates"
        assert templates_dir.exists()


class TestAppGeneratorMethods:
    """Test AppGenerator methods."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_app_generator_create_structure(self, temp_dir):
        """Test AppGenerator create_structure."""
        generator = AppGenerator(
            app_name="test_app",
            output_dir=Path(temp_dir),
        )

        generator.create_structure()

        app_path = Path(temp_dir) / "test_app"
        assert app_path.exists()

    def test_app_generator_with_docker(self, temp_dir):
        """Test AppGenerator with Docker enabled."""
        generator = AppGenerator(
            app_name="dockerized_app",
            output_dir=Path(temp_dir),
            docker=True,
        )

        generator.create_structure()
        generator.generate_docker()

        app_path = Path(temp_dir) / "dockerized_app"
        assert app_path.exists()

    def test_app_generator_with_celery(self, temp_dir):
        """Test AppGenerator with Celery enabled."""
        generator = AppGenerator(
            app_name="celery_app",
            output_dir=Path(temp_dir),
            celery=True,
        )

        ctx = generator.get_context()
        assert ctx["celery"] is True

    def test_app_generator_with_i18n(self, temp_dir):
        """Test AppGenerator with i18n enabled."""
        generator = AppGenerator(
            app_name="i18n_app",
            output_dir=Path(temp_dir),
            i18n=True,
        )

        ctx = generator.get_context()
        assert ctx["i18n"] is True

    def test_app_generator_custom_model(self, temp_dir):
        """Test AppGenerator with custom model name."""
        generator = AppGenerator(
            app_name="custom_app",
            output_dir=Path(temp_dir),
            model_name="CustomModel",
        )

        assert generator.model_name == "CustomModel"

    def test_app_generator_custom_fields(self, temp_dir):
        """Test AppGenerator with custom fields."""
        fields = [
            ("name", "CharField", {"max_length": 100}),
            ("email", "EmailField", {}),
        ]

        generator = AppGenerator(
            app_name="fields_app",
            output_dir=Path(temp_dir),
            fields=fields,
        )

        assert generator.fields == fields


class TestProjectTypeGeneration:
    """Test different project types."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_backend_project_generation(self, temp_dir):
        """Test backend-only project generation."""
        generator = ProjectGenerator(
            project_name="backend_proj",
            output_dir=Path(temp_dir),
            project_type="backend",
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / "backend_proj"
        assert project_path.exists()

    def test_frontend_project_generation(self, temp_dir):
        """Test frontend-only project generation."""
        generator = ProjectGenerator(
            project_name="frontend_proj",
            output_dir=Path(temp_dir),
            project_type="frontend",
        )

        generator.create_structure()
        generator.generate_settings()

        project_path = Path(temp_dir) / "frontend_proj"
        assert project_path.exists()


class TestCSSFrameworks:
    """Test CSS framework options."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_bootstrap_css(self, temp_dir):
        """Test Bootstrap CSS framework."""
        generator = ProjectGenerator(
            project_name="bootstrap_proj",
            output_dir=Path(temp_dir),
            css="bootstrap",
        )

        ctx = generator.get_context()
        assert ctx["use_bootstrap"] is True
        assert ctx["use_tailwind"] is False

    def test_tailwind_css(self, temp_dir):
        """Test Tailwind CSS framework."""
        generator = ProjectGenerator(
            project_name="tailwind_proj",
            output_dir=Path(temp_dir),
            css="tailwind",
        )

        ctx = generator.get_context()
        assert ctx["use_bootstrap"] is False
        assert ctx["use_tailwind"] is True


class TestAllAuthGeneration:
    """Test allauth template generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_allauth_full_generation(self, temp_dir):
        """Test full generation with allauth."""
        generator = ProjectGenerator(
            project_name="allauth_proj",
            output_dir=Path(temp_dir),
            auth="allauth",
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()
        generator.generate_templates_static()

        project_path = Path(temp_dir) / "allauth_proj"
        templates_dir = project_path / "templates"
        assert templates_dir.exists()


class TestSpecializedAppGeneration:
    """Test specialized template app generation."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.parametrize("template,expected_dir", [
        ("ecommerce", "shop"),
        ("blog", "blog"),
    ])
    def test_specialized_app_dirs(self, temp_dir, template, expected_dir):
        """Test specialized templates create correct app directories."""
        generator = ProjectGenerator(
            project_name=f"{template}_app",
            output_dir=Path(temp_dir),
            template=template,
        )

        generator.create_structure()
        generator.generate_settings()
        generator.generate_apps()

        project_path = Path(temp_dir) / f"{template}_app"
        apps_dir = project_path / "apps"
        assert apps_dir.exists()

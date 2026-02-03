"""
Extended tests for AppGenerator to achieve 95%+ coverage.
"""

import pytest
from pathlib import Path
from dual_apps.generators.app_generator import AppGenerator


class TestAppGeneratorI18n:
    """Test AppGenerator i18n support."""

    def test_i18n_creates_locale_dir(self, temp_dir):
        """Test i18n creates locale directory for standalone apps."""
        gen = AppGenerator(
            app_name="i18napp",
            i18n=True,
            output_dir=temp_dir
        )
        gen.create_structure()

        assert (temp_dir / "i18napp" / "locale").exists()

    def test_i18n_in_context(self, temp_dir):
        """Test i18n flag in context."""
        gen = AppGenerator(
            app_name="i18napp",
            i18n=True,
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["i18n"] is True


class TestAppGeneratorCelery:
    """Test AppGenerator Celery support."""

    def test_celery_generates_tasks_file(self, temp_dir):
        """Test Celery generates tasks.py file."""
        gen = AppGenerator(
            app_name="celeryapp",
            celery=True,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_django_files()

        tasks_file = temp_dir / "celeryapp" / "celeryapp" / "tasks.py"
        assert tasks_file.exists()

    def test_celery_in_context(self, temp_dir):
        """Test celery flag in context."""
        gen = AppGenerator(
            app_name="celeryapp",
            celery=True,
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["celery"] is True


class TestAppGeneratorNonStandalone:
    """Test AppGenerator non-standalone mode."""

    def test_non_standalone_flat_structure(self, temp_dir):
        """Test non-standalone creates flat structure."""
        gen = AppGenerator(
            app_name="flatapp",
            standalone=False,
            app_full_name="apps.flatapp",
            output_dir=temp_dir
        )
        gen.create_structure()

        # Flat structure - no nested app_name/app_name
        assert (temp_dir / "flatapp").exists()
        assert (temp_dir / "flatapp" / "migrations").exists()
        assert not (temp_dir / "flatapp" / "flatapp").exists()

    def test_non_standalone_generates_files_in_root(self, temp_dir):
        """Test non-standalone generates files in app root."""
        gen = AppGenerator(
            app_name="flatapp",
            standalone=False,
            app_full_name="apps.flatapp",
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_django_files()

        # Files should be directly in flatapp/, not flatapp/flatapp/
        assert (temp_dir / "flatapp" / "models.py").exists()
        assert (temp_dir / "flatapp" / "admin.py").exists()
        assert (temp_dir / "flatapp" / "urls.py").exists()

    def test_non_standalone_app_full_name_in_context(self, temp_dir):
        """Test app_full_name is in context for non-standalone."""
        gen = AppGenerator(
            app_name="projectapp",
            standalone=False,
            app_full_name="apps.projectapp",
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["app_full_name"] == "apps.projectapp"

    def test_non_standalone_no_static_files(self, temp_dir):
        """Test non-standalone doesn't generate static files."""
        gen = AppGenerator(
            app_name="projectapp",
            standalone=False,
            app_full_name="apps.projectapp",
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_django_files()

        # Static files should not be generated for project apps
        assert not (temp_dir / "projectapp" / "static").exists()


class TestAppGeneratorFrontendOnly:
    """Test AppGenerator frontend-only mode."""

    def test_frontend_only_no_api_files(self, temp_dir):
        """Test frontend-only doesn't generate API files."""
        gen = AppGenerator(
            app_name="frontendapp",
            frontend_only=True,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_django_files()

        app_dir = temp_dir / "frontendapp" / "frontendapp"
        assert not (app_dir / "views_api.py").exists()
        assert not (app_dir / "serializers.py").exists()
        assert (app_dir / "views_frontend.py").exists()

    def test_frontend_only_context(self, temp_dir):
        """Test frontend-only context flags."""
        gen = AppGenerator(
            app_name="frontendapp",
            frontend_only=True,
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["frontend_only"] is True
        assert ctx["has_frontend"] is True
        assert ctx["has_api"] is False


class TestAppGeneratorAPIOnly:
    """Test AppGenerator API-only mode."""

    def test_api_only_no_frontend_files(self, temp_dir):
        """Test API-only doesn't generate frontend files."""
        gen = AppGenerator(
            app_name="apiapp",
            api_only=True,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_django_files()

        app_dir = temp_dir / "apiapp" / "apiapp"
        assert (app_dir / "views_api.py").exists()
        assert (app_dir / "serializers.py").exists()
        assert not (app_dir / "views_frontend.py").exists()

    def test_api_only_no_templates_or_static(self, temp_dir):
        """Test API-only doesn't create templates/static dirs."""
        gen = AppGenerator(
            app_name="apiapp",
            api_only=True,
            output_dir=temp_dir
        )
        gen.create_structure()

        assert not (temp_dir / "apiapp" / "templates").exists()
        assert not (temp_dir / "apiapp" / "static").exists()


class TestAppGeneratorCustomFields:
    """Test AppGenerator with custom fields."""

    def test_custom_fields_in_context(self, temp_dir):
        """Test custom fields appear in context."""
        custom_fields = [
            ("name", "CharField", {"max_length": 100}),
            ("price", "DecimalField", {"max_digits": 10, "decimal_places": 2}),
            ("quantity", "IntegerField", {"default": 0}),
        ]
        gen = AppGenerator(
            app_name="products",
            model_name="Product",
            fields=custom_fields,
            output_dir=temp_dir
        )
        ctx = gen.get_context()

        assert len(ctx["fields"]) == 3
        assert ctx["fields"][0][0] == "name"
        assert ctx["fields"][1][0] == "price"
        assert ctx["fields"][2][0] == "quantity"


class TestAppGeneratorDocker:
    """Test AppGenerator Docker support."""

    def test_docker_disabled_no_docker_dir(self, temp_dir):
        """Test docker=False doesn't create docker directory."""
        gen = AppGenerator(
            app_name="nodockerapp",
            docker=False,
            output_dir=temp_dir
        )
        gen.create_structure()

        assert not (temp_dir / "nodockerapp" / "docker").exists()

    def test_docker_enabled_creates_docker_dir(self, temp_dir):
        """Test docker=True creates docker directory."""
        gen = AppGenerator(
            app_name="dockerapp",
            docker=True,
            output_dir=temp_dir
        )
        gen.create_structure()

        assert (temp_dir / "dockerapp" / "docker").exists()

    def test_generate_docker_files(self, temp_dir):
        """Test Docker file generation."""
        gen = AppGenerator(
            app_name="dockerapp",
            docker=True,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_docker()

        assert (temp_dir / "dockerapp" / "docker" / "Dockerfile.dockerapp").exists()


class TestAppGeneratorTests:
    """Test AppGenerator test generation."""

    def test_generate_api_tests(self, temp_dir):
        """Test API test file generation."""
        gen = AppGenerator(
            app_name="testapp",
            api_only=False,
            frontend_only=False,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_tests()

        tests_dir = temp_dir / "testapp" / "tests"
        assert (tests_dir / "test_api.py").exists()

    def test_generate_frontend_tests(self, temp_dir):
        """Test frontend test file generation."""
        gen = AppGenerator(
            app_name="testapp",
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_tests()

        tests_dir = temp_dir / "testapp" / "tests"
        assert (tests_dir / "test_frontend.py").exists()

    def test_no_api_tests_when_frontend_only(self, temp_dir):
        """Test no API tests for frontend-only apps."""
        gen = AppGenerator(
            app_name="frontendapp",
            frontend_only=True,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_tests()

        tests_dir = temp_dir / "frontendapp" / "tests"
        assert not (tests_dir / "test_api.py").exists()

    def test_no_frontend_tests_when_api_only(self, temp_dir):
        """Test no frontend tests for API-only apps."""
        gen = AppGenerator(
            app_name="apiapp",
            api_only=True,
            output_dir=temp_dir
        )
        gen.create_structure()
        gen.generate_tests()

        tests_dir = temp_dir / "apiapp" / "tests"
        assert not (tests_dir / "test_frontend.py").exists()


class TestAppGeneratorAuthRequired:
    """Test AppGenerator auth_required option."""

    def test_auth_required_in_context(self, temp_dir):
        """Test auth_required flag in context."""
        gen = AppGenerator(
            app_name="authapp",
            auth_required=True,
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["auth_required"] is True

    def test_no_auth_required(self, temp_dir):
        """Test auth_required=False in context."""
        gen = AppGenerator(
            app_name="noauthapp",
            auth_required=False,
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert ctx["auth_required"] is False


class TestAppGeneratorModelName:
    """Test AppGenerator model name variants."""

    def test_model_name_variants_in_context(self, temp_dir):
        """Test model name variants in context."""
        gen = AppGenerator(
            app_name="jobs",
            model_name="JobPosting",
            output_dir=temp_dir
        )
        ctx = gen.get_context()

        assert ctx["model_name"] == "JobPosting"
        assert ctx["model_name_snake"] == "job_posting"
        assert ctx["model_name_plural"] == "JobPostings"
        assert ctx["model_name_kebab"] == "job-posting"

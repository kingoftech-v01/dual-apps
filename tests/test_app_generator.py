"""
Tests for AppGenerator class.
"""

import pytest
from pathlib import Path
from dual_apps.generators.app_generator import AppGenerator


class TestAppGeneratorInit:
    """Test AppGenerator initialization."""

    def test_default_model_name(self, temp_dir):
        """Test default model name is derived from app name with Model suffix."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        assert gen.model_name == "JobsModel"

    def test_custom_model_name(self, temp_dir):
        """Test custom model name."""
        gen = AppGenerator(app_name="jobs", model_name="JobPosting", output_dir=temp_dir)
        assert gen.model_name == "JobPosting"

    def test_app_name_normalization(self, temp_dir):
        """Test app name is normalized to snake_case."""
        gen = AppGenerator(app_name="MyApp", output_dir=temp_dir)
        assert gen.app_name == "my_app"

    def test_default_docker_true(self, temp_dir):
        """Test Docker is enabled by default."""
        gen = AppGenerator(app_name="test", output_dir=temp_dir)
        assert gen.docker is True


class TestAppGeneratorContext:
    """Test AppGenerator context generation."""

    def test_context_has_app_name(self, temp_dir):
        """Test context contains app name."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        ctx = gen.get_context()
        assert ctx["app_name"] == "jobs"

    def test_context_has_model_name(self, temp_dir):
        """Test context contains model name."""
        gen = AppGenerator(app_name="jobs", model_name="JobPosting", output_dir=temp_dir)
        ctx = gen.get_context()
        assert ctx["model_name"] == "JobPosting"

    def test_context_has_name_variants(self, temp_dir):
        """Test context contains all name variants."""
        gen = AppGenerator(app_name="my_app", output_dir=temp_dir)
        ctx = gen.get_context()
        assert ctx["app_name"] == "my_app"
        assert ctx["app_name_pascal"] == "MyApp"
        assert ctx["app_name_title"] == "My App"
        assert ctx["app_name_kebab"] == "my-app"

    def test_context_has_fields(self, temp_dir):
        """Test context contains fields."""
        gen = AppGenerator(
            app_name="products",
            fields=[
                ("name", "CharField", {"max_length": 200}),
                ("price", "DecimalField", {"max_digits": 10, "decimal_places": 2}),
            ],
            output_dir=temp_dir
        )
        ctx = gen.get_context()
        assert "fields" in ctx
        assert len(ctx["fields"]) == 2

    def test_context_has_version(self, temp_dir):
        """Test context contains version."""
        gen = AppGenerator(app_name="test", output_dir=temp_dir)
        ctx = gen.get_context()
        assert "version" in ctx
        assert ctx["version"] == "3.1.0"


class TestAppGeneratorStructure:
    """Test AppGenerator directory structure creation."""

    def test_create_structure(self, temp_dir):
        """Test directory structure is created."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()

        app_dir = temp_dir / "jobs"
        assert app_dir.exists()
        assert (app_dir / "jobs").exists()
        assert (app_dir / "jobs" / "migrations").exists()
        # Templates are at app_root/templates/app_name, not app_root/app_name/templates
        assert (app_dir / "templates" / "jobs").exists()

    def test_create_structure_with_docker(self, temp_dir):
        """Test Docker directory is created when enabled."""
        gen = AppGenerator(app_name="jobs", docker=True, output_dir=temp_dir)
        gen.create_structure()

        assert (temp_dir / "jobs" / "docker").exists()

    def test_create_structure_without_docker(self, temp_dir):
        """Test Docker directory is not created when disabled."""
        gen = AppGenerator(app_name="jobs", docker=False, output_dir=temp_dir)
        gen.create_structure()

        assert not (temp_dir / "jobs" / "docker").exists()


class TestAppGeneratorFiles:
    """Test AppGenerator file generation."""

    def test_generate_django_files(self, temp_dir):
        """Test Django files are generated."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_django_files()

        app_dir = temp_dir / "jobs" / "jobs"
        assert (app_dir / "models.py").exists()
        assert (app_dir / "views_api.py").exists()
        assert (app_dir / "views_frontend.py").exists()
        assert (app_dir / "serializers.py").exists()
        assert (app_dir / "urls.py").exists()
        assert (app_dir / "permissions.py").exists()
        assert (app_dir / "admin.py").exists()

    def test_generate_tests(self, temp_dir):
        """Test test files are generated."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_tests()

        tests_dir = temp_dir / "jobs" / "tests"
        assert tests_dir.exists()
        assert (tests_dir / "conftest.py").exists()
        assert (tests_dir / "test_models.py").exists()
        assert (tests_dir / "test_api.py").exists()

    def test_generate_docs(self, temp_dir):
        """Test documentation files are generated."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_docs()

        app_dir = temp_dir / "jobs"
        assert (app_dir / "README.md").exists()
        assert (app_dir / "CHANGELOG.md").exists()


class TestAppGeneratorContent:
    """Test generated file content."""

    def test_model_has_uuid_pk(self, temp_dir):
        """Test generated model has UUID primary key."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_django_files()

        models_file = temp_dir / "jobs" / "jobs" / "models.py"
        content = models_file.read_text()
        assert "UUIDField" in content
        assert "primary_key=True" in content

    def test_model_has_timestamps(self, temp_dir):
        """Test generated model has timestamps."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_django_files()

        models_file = temp_dir / "jobs" / "jobs" / "models.py"
        content = models_file.read_text()
        assert "created_at" in content
        assert "updated_at" in content

    def test_model_has_owner(self, temp_dir):
        """Test generated model has owner field."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_django_files()

        models_file = temp_dir / "jobs" / "jobs" / "models.py"
        content = models_file.read_text()
        assert "owner" in content
        assert "ForeignKey" in content

    def test_permissions_has_is_owner_or_readonly(self, temp_dir):
        """Test permissions file has IsOwnerOrReadOnly."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_django_files()

        perms_file = temp_dir / "jobs" / "jobs" / "permissions.py"
        content = perms_file.read_text()
        assert "IsOwnerOrReadOnly" in content

    def test_api_views_use_viewset(self, temp_dir):
        """Test API views use ModelViewSet."""
        gen = AppGenerator(app_name="jobs", output_dir=temp_dir)
        gen.create_structure()
        gen.generate_django_files()

        views_file = temp_dir / "jobs" / "jobs" / "views_api.py"
        content = views_file.read_text()
        assert "ModelViewSet" in content


class TestAppGeneratorFullGeneration:
    """Test full app generation."""

    def test_full_generation(self, temp_dir):
        """Test complete app generation."""
        gen = AppGenerator(
            app_name="products",
            model_name="Product",
            fields=[
                ("name", "CharField", {"max_length": 200}),
                ("price", "DecimalField", {"max_digits": 10, "decimal_places": 2}),
                ("active", "BooleanField", {"default": True}),
            ],
            docker=True,
            output_dir=temp_dir,
        )

        gen.create_structure()
        gen.generate_django_files()
        gen.generate_tests()
        gen.generate_docs()
        gen.finalize()

        app_dir = temp_dir / "products"

        # Check structure
        assert app_dir.exists()
        assert (app_dir / "products").exists()
        assert (app_dir / "tests").exists()
        assert (app_dir / "docker").exists()

        # Check key files
        assert (app_dir / "products" / "models.py").exists()
        assert (app_dir / "products" / "views_api.py").exists()
        assert (app_dir / "pyproject.toml").exists()
        assert (app_dir / "README.md").exists()

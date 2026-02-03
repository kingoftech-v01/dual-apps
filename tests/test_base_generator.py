"""
Tests for BaseGenerator class.
"""

import pytest
from pathlib import Path
from dual_apps.generators.base import BaseGenerator


class TestBaseGeneratorInit:
    """Test BaseGenerator initialization."""

    def test_default_output_dir(self):
        """Test default output directory."""
        gen = BaseGenerator()
        assert gen.output_dir == Path(".")

    def test_custom_output_dir(self, temp_dir):
        """Test custom output directory."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen.output_dir == temp_dir

    def test_jinja_env_created(self):
        """Test Jinja2 environment is created."""
        gen = BaseGenerator()
        assert gen.env is not None


class TestNameConversions:
    """Test name conversion utilities."""

    def test_to_snake_case(self):
        """Test snake_case conversion."""
        gen = BaseGenerator()
        assert gen._to_snake_case("MyApp") == "my_app"
        assert gen._to_snake_case("myApp") == "my_app"
        assert gen._to_snake_case("my_app") == "my_app"
        assert gen._to_snake_case("MyAppName") == "my_app_name"

    def test_to_pascal_case(self):
        """Test PascalCase conversion."""
        gen = BaseGenerator()
        assert gen._to_pascal_case("my_app") == "MyApp"
        assert gen._to_pascal_case("myapp") == "Myapp"
        assert gen._to_pascal_case("my_app_name") == "MyAppName"

    def test_to_kebab_case(self):
        """Test kebab-case conversion."""
        gen = BaseGenerator()
        assert gen._to_kebab_case("my_app") == "my-app"
        assert gen._to_kebab_case("MyApp") == "my-app"
        assert gen._to_kebab_case("my_app_name") == "my-app-name"

    def test_to_title_case(self):
        """Test Title Case conversion."""
        gen = BaseGenerator()
        assert gen._to_title_case("my_app") == "My App"
        assert gen._to_title_case("myapp") == "Myapp"
        assert gen._to_title_case("my_app_name") == "My App Name"


class TestFieldParsing:
    """Test field parsing utilities.

    Note: Field parsing is handled by AppGenerator, not BaseGenerator.
    These tests verify that default fields are properly structured.
    """

    def test_default_fields_structure(self):
        """Test that AppGenerator has properly structured default fields."""
        from dual_apps.generators.app_generator import AppGenerator
        gen = AppGenerator(app_name="test")
        fields = gen.fields
        assert len(fields) >= 1
        # Each field should be a tuple of (name, type, options)
        for field in fields:
            assert len(field) == 3
            assert isinstance(field[0], str)  # field name
            assert isinstance(field[1], str)  # field type
            assert isinstance(field[2], dict)  # options

    def test_fields_have_required_attributes(self):
        """Test fields have required attributes."""
        from dual_apps.generators.app_generator import AppGenerator
        gen = AppGenerator(app_name="test")
        # Default fields should include common fields
        field_names = [f[0] for f in gen.fields]
        assert "title" in field_names

    def test_custom_fields(self):
        """Test custom fields can be passed."""
        from dual_apps.generators.app_generator import AppGenerator
        custom_fields = [
            ("name", "CharField", {"max_length": 100}),
            ("price", "DecimalField", {"max_digits": 10, "decimal_places": 2}),
        ]
        gen = AppGenerator(app_name="test", fields=custom_fields)
        assert gen.fields == custom_fields

    def test_fields_in_context(self):
        """Test fields are included in context."""
        from dual_apps.generators.app_generator import AppGenerator
        gen = AppGenerator(app_name="test")
        ctx = gen.get_context()
        assert "fields" in ctx
        assert len(ctx["fields"]) >= 1

    def test_field_types_supported(self):
        """Test various Django field types can be used."""
        from dual_apps.generators.app_generator import AppGenerator
        fields = [
            ("text_field", "CharField", {"max_length": 200}),
            ("big_text", "TextField", {}),
            ("number", "IntegerField", {}),
            ("decimal", "DecimalField", {"max_digits": 10, "decimal_places": 2}),
            ("flag", "BooleanField", {"default": False}),
        ]
        gen = AppGenerator(app_name="test", fields=fields)
        assert len(gen.fields) == 5


class TestDirectoryCreation:
    """Test directory creation utilities."""

    def test_create_directory(self, temp_dir):
        """Test creating a directory."""
        gen = BaseGenerator(output_dir=temp_dir)
        new_dir = temp_dir / "subdir"
        gen.create_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_nested_directory(self, temp_dir):
        """Test creating nested directories."""
        gen = BaseGenerator(output_dir=temp_dir)
        new_dir = temp_dir / "level1" / "level2" / "level3"
        gen.create_directory(new_dir)
        assert new_dir.exists()

    def test_create_existing_directory(self, temp_dir):
        """Test creating already existing directory."""
        gen = BaseGenerator(output_dir=temp_dir)
        new_dir = temp_dir / "existing"
        new_dir.mkdir()
        # Should not raise error
        gen.create_directory(new_dir)
        assert new_dir.exists()


class TestTemplateRendering:
    """Test template rendering."""

    def test_get_base_context(self):
        """Test base context contains required keys."""
        gen = BaseGenerator()
        ctx = gen.get_base_context()
        assert "version" in ctx
        assert "date" in ctx
        assert "year" in ctx
        assert "generator" in ctx

    def test_version_in_context(self):
        """Test version is correct in context."""
        gen = BaseGenerator()
        ctx = gen.get_base_context()
        assert ctx["version"] == "3.1.0"


class TestJinjaFilters:
    """Test custom Jinja2 filters."""

    def test_snake_case_filter(self):
        """Test snake_case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | snake_case }}")
        result = template.render(name="MyApp")
        assert result == "my_app"

    def test_pascal_case_filter(self):
        """Test pascal_case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | pascal_case }}")
        result = template.render(name="my_app")
        assert result == "MyApp"

    def test_kebab_case_filter(self):
        """Test kebab_case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | kebab_case }}")
        result = template.render(name="my_app")
        assert result == "my-app"

    def test_title_case_filter(self):
        """Test title_case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | title_case }}")
        result = template.render(name="my_app")
        assert result == "My App"

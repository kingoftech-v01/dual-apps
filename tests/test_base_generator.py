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
    """Test field parsing utilities."""

    def test_parse_empty_fields(self):
        """Test parsing empty fields string."""
        gen = BaseGenerator()
        result = gen._parse_fields("")
        assert result == []

    def test_parse_none_fields(self):
        """Test parsing None fields."""
        gen = BaseGenerator()
        result = gen._parse_fields(None)
        assert result == []

    def test_parse_single_field(self):
        """Test parsing single field."""
        gen = BaseGenerator()
        result = gen._parse_fields("title:str")
        assert len(result) == 1
        assert result[0]["name"] == "title"
        assert result[0]["type"] == "str"

    def test_parse_multiple_fields(self):
        """Test parsing multiple fields."""
        gen = BaseGenerator()
        result = gen._parse_fields("title:str,price:decimal,active:bool")
        assert len(result) == 3
        assert result[0]["name"] == "title"
        assert result[1]["name"] == "price"
        assert result[2]["name"] == "active"

    def test_parse_field_types(self):
        """Test all supported field types."""
        gen = BaseGenerator()
        fields = "a:str,b:text,c:int,d:decimal,e:bool,f:date,g:datetime,h:uuid,i:email,j:url"
        result = gen._parse_fields(fields)
        assert len(result) == 10
        assert result[0]["type"] == "str"
        assert result[1]["type"] == "text"
        assert result[2]["type"] == "int"
        assert result[3]["type"] == "decimal"
        assert result[4]["type"] == "bool"


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
        assert "timestamp" in ctx
        assert "python_version" in ctx

    def test_version_in_context(self):
        """Test version is correct in context."""
        gen = BaseGenerator()
        ctx = gen.get_base_context()
        assert ctx["version"] == "3.1.0"


class TestJinjaFilters:
    """Test custom Jinja2 filters."""

    def test_snake_filter(self):
        """Test snake_case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | snake }}")
        result = template.render(name="MyApp")
        assert result == "my_app"

    def test_pascal_filter(self):
        """Test pascal_case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | pascal }}")
        result = template.render(name="my_app")
        assert result == "MyApp"

    def test_kebab_filter(self):
        """Test kebab-case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | kebab }}")
        result = template.render(name="my_app")
        assert result == "my-app"

    def test_title_filter(self):
        """Test title case filter in templates."""
        gen = BaseGenerator()
        template = gen.env.from_string("{{ name | title_case }}")
        result = template.render(name="my_app")
        assert result == "My App"

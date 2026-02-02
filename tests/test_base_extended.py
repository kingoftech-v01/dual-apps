"""
Extended tests for BaseGenerator to achieve 95%+ coverage.
"""

import pytest
from pathlib import Path
from dual_apps.generators.base import BaseGenerator


class TestBaseGeneratorExtended:
    """Extended tests for BaseGenerator."""

    def test_copy_static_file(self, temp_dir):
        """Test copying static file from templates."""
        gen = BaseGenerator(output_dir=temp_dir)
        # Copy a template file
        gen.copy_static_file("app/__init__.py.j2", Path("test/__init__.py"))

        output_file = temp_dir / "test" / "__init__.py"
        assert output_file.exists()

    def test_get_stats(self, temp_dir):
        """Test getting generation statistics."""
        gen = BaseGenerator(output_dir=temp_dir)

        # Create some files and dirs
        gen.create_directory(Path("testdir"))
        gen.write_file(Path("testdir/test.txt"), "content")

        stats = gen.get_stats()
        assert stats["files_created"] == 1
        assert stats["dirs_created"] == 1

    def test_template_exists_true(self, temp_dir):
        """Test template_exists returns True for existing templates."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen.template_exists("app/__init__.py.j2") is True

    def test_template_exists_false(self, temp_dir):
        """Test template_exists returns False for non-existing templates."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen.template_exists("nonexistent/template.j2") is False

    def test_write_executable_file(self, temp_dir):
        """Test writing executable file."""
        import os
        import stat

        gen = BaseGenerator(output_dir=temp_dir)
        gen.write_file(Path("script.sh"), "#!/bin/bash\necho hello", executable=True)

        file_path = temp_dir / "script.sh"
        assert file_path.exists()

        # Check executable permission
        mode = os.stat(file_path).st_mode
        assert mode & stat.S_IXUSR  # User execute permission

    def test_render_template_with_context(self, temp_dir):
        """Test rendering template with custom context."""
        gen = BaseGenerator(output_dir=temp_dir)
        content = gen.render_template(
            "app/__init__.py.j2",
            {"app_name": "testapp", "app_name_title": "TestApp"}
        )
        assert content is not None

    def test_render_and_write_executable(self, temp_dir):
        """Test render and write with executable flag."""
        import os
        import stat

        gen = BaseGenerator(output_dir=temp_dir)
        gen.render_and_write(
            "app/__init__.py.j2",
            Path("exec_file.py"),
            {"app_name": "test"},
            executable=True
        )

        file_path = temp_dir / "exec_file.py"
        assert file_path.exists()
        mode = os.stat(file_path).st_mode
        assert mode & stat.S_IXUSR

    def test_create_nested_directory_structure(self, temp_dir):
        """Test creating deeply nested directories."""
        gen = BaseGenerator(output_dir=temp_dir)
        gen.create_directory(Path("a/b/c/d/e"))

        assert (temp_dir / "a" / "b" / "c" / "d" / "e").exists()

    def test_write_file_creates_parent_dirs(self, temp_dir):
        """Test write_file creates parent directories."""
        gen = BaseGenerator(output_dir=temp_dir)
        gen.write_file(Path("deep/nested/dir/file.txt"), "content")

        assert (temp_dir / "deep" / "nested" / "dir" / "file.txt").exists()


class TestNameConversionsExtended:
    """Extended tests for name conversions."""

    def test_snake_case_with_numbers(self, temp_dir):
        """Test snake_case with numbers."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen._to_snake_case("API2Client") == "api2_client"

    def test_pascal_case_from_kebab(self, temp_dir):
        """Test pascal_case from kebab-case."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen._to_pascal_case("my-app-name") == "MyAppName"

    def test_title_case_with_dashes(self, temp_dir):
        """Test title_case with dashes."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen._to_title_case("my-app-name") == "My App Name"

    def test_kebab_case_complex(self, temp_dir):
        """Test kebab_case with complex input."""
        gen = BaseGenerator(output_dir=temp_dir)
        assert gen._to_kebab_case("MyAppName") == "my-app-name"

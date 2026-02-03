"""
Base generator class with common functionality.

Provides shared methods for file generation, template rendering,
and directory management used by both AppGenerator and ProjectGenerator.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import os

from jinja2 import Environment, PackageLoader, select_autoescape


class BaseGenerator:
    """
    Base class for all generators.

    Provides:
    - Jinja2 template rendering
    - Directory creation
    - File writing with proper permissions
    - Common context variables
    """

    def __init__(self, output_dir: Path = Path(".")):
        self.output_dir = Path(output_dir)
        self.created_files: list = []
        self.created_dirs: list = []

        # Setup Jinja2 environment
        self.env = Environment(
            loader=PackageLoader("dual_apps", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Register custom filters
        self.env.filters["snake_case"] = self._to_snake_case
        self.env.filters["pascal_case"] = self._to_pascal_case
        self.env.filters["kebab_case"] = self._to_kebab_case
        self.env.filters["title_case"] = self._to_title_case

    def _to_snake_case(self, value: str) -> str:
        """Convert string to snake_case."""
        import re
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower().replace("-", "_")

    def _to_pascal_case(self, value: str) -> str:
        """Convert string to PascalCase."""
        return "".join(word.capitalize() for word in value.replace("-", "_").split("_"))

    def _to_kebab_case(self, value: str) -> str:
        """Convert string to kebab-case."""
        return self._to_snake_case(value).replace("_", "-")

    def _to_title_case(self, value: str) -> str:
        """Convert string to Title Case."""
        return value.replace("-", " ").replace("_", " ").title()

    def get_base_context(self) -> Dict[str, Any]:
        """Get base context variables for all templates."""
        return {
            "version": "3.1.0",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "year": datetime.now().year,
            "generator": "dual-apps",
        }

    def create_directory(self, path: Path) -> None:
        """Create a directory if it doesn't exist."""
        full_path = self.output_dir / path
        full_path.mkdir(parents=True, exist_ok=True)
        self.created_dirs.append(full_path)

    def write_file(
        self,
        path: Path,
        content: str,
        executable: bool = False,
    ) -> None:
        """
        Write content to a file.

        Args:
            path: Relative path from output_dir
            content: File content
            executable: Make file executable
        """
        full_path = self.output_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        if executable:
            os.chmod(full_path, 0o755)

        self.created_files.append(full_path)

    def render_template(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a Jinja2 template.

        Args:
            template_name: Template path relative to templates/
            context: Variables to pass to template

        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_name)
        full_context = self.get_base_context()
        if context:
            full_context.update(context)
        return template.render(**full_context)

    def render_and_write(
        self,
        template_name: str,
        output_path: Path,
        context: Optional[Dict[str, Any]] = None,
        executable: bool = False,
    ) -> None:
        """Render template and write to file."""
        content = self.render_template(template_name, context)
        self.write_file(output_path, content, executable)

    def copy_static_file(self, src_template: str, dest_path: Path) -> None:
        """Copy a static file from templates."""
        content = self.render_template(src_template)
        self.write_file(dest_path, content)

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists."""
        try:
            self.env.get_template(template_name)
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get generation statistics."""
        return {
            "files_created": len(self.created_files),
            "dirs_created": len(self.created_dirs),
        }

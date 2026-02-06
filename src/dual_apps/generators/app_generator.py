"""
Generates standalone Django apps with dual-layer architecture.

Can create apps either as standalone packages or within a project.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dual_apps.generators.base import BaseGenerator


class AppGenerator(BaseGenerator):
    """Generate a Django app with dual-layer architecture (Frontend + API)."""

    def __init__(
        self,
        app_name: str,
        model_name: Optional[str] = None,
        fields: Optional[List[Tuple[str, str, Dict]]] = None,
        api_only: bool = False,
        frontend_only: bool = False,
        docker: bool = True,
        i18n: bool = False,
        celery: bool = False,
        auth_required: bool = True,
        output_dir: Path = Path("."),
        app_full_name: Optional[str] = None,
        standalone: bool = True,
    ):
        super().__init__(output_dir)

        self.app_name = self._to_snake_case(app_name)
        self.model_name = model_name or f"{self._to_pascal_case(app_name)}Model"
        self.fields = fields or self._get_default_fields()
        self.api_only = api_only
        self.frontend_only = frontend_only
        self.docker = docker
        self.i18n = i18n
        self.celery = celery
        self.auth_required = auth_required
        # Used for Django AppConfig.name when app lives in apps/ directory
        self.app_full_name = app_full_name
        # Standalone apps get package structure (app_name/app_name/), project apps are flat
        self.standalone = standalone
        self.app_root = Path(self.app_name)

    def _get_default_fields(self) -> List[Tuple[str, str, Dict]]:
        """Get default model fields."""
        return [
            ("title", "CharField", {"max_length": 200}),
            ("description", "TextField", {"blank": True}),
            ("status", "CharField", {
                "max_length": 20,
                "choices": [
                    ("draft", "Draft"),
                    ("active", "Active"),
                    ("archived", "Archived"),
                ],
                "default": "draft",
            }),
            ("is_active", "BooleanField", {"default": True}),
        ]

    def get_context(self) -> Dict[str, Any]:
        """Get template context for app generation."""
        ctx = {
            **self.get_base_context(),
            "app_name": self.app_name,
            "app_name_title": self._to_title_case(self.app_name),
            "app_name_pascal": self._to_pascal_case(self.app_name),
            "app_name_kebab": self._to_kebab_case(self.app_name),
            "model_name": self.model_name,
            "model_name_snake": self._to_snake_case(self.model_name),
            "model_name_plural": f"{self.model_name}s",
            "model_name_kebab": self._to_kebab_case(self.model_name),
            "fields": self.fields,
            "api_only": self.api_only,
            "frontend_only": self.frontend_only,
            "docker": self.docker,
            "i18n": self.i18n,
            "celery": self.celery,
            "auth_required": self.auth_required,
            "has_frontend": not self.api_only,
            "has_api": not self.frontend_only,
        }
        if self.app_full_name:
            ctx["app_full_name"] = self.app_full_name
        return ctx

    def create_structure(self) -> None:
        """Create app directory structure."""
        ctx = self.get_context()

        if self.standalone:
            # Standalone apps are installable packages: myapp/myapp/models.py
            dirs = [
                self.app_root,
                self.app_root / self.app_name,
                self.app_root / self.app_name / "migrations",
                self.app_root / self.app_name / "management",
                self.app_root / self.app_name / "management" / "commands",
                self.app_root / "tests",
                self.app_root / "docs",
            ]

            if ctx["has_frontend"]:
                dirs.extend([
                    self.app_root / "templates" / self.app_name,
                    self.app_root / "static" / self.app_name / "css",
                    self.app_root / "static" / self.app_name / "js",
                ])

            if self.docker:
                dirs.append(self.app_root / "docker")

            if self.i18n:
                dirs.append(self.app_root / "locale")
        else:
            # Project apps live in apps/: apps/myapp/models.py
            dirs = [
                self.app_root,
                self.app_root / "migrations",
                self.app_root / "management",
                self.app_root / "management" / "commands",
                self.app_root / "tests",
            ]

            # Frontend directories
            if ctx["has_frontend"]:
                dirs.extend([
                    self.app_root / "templates" / self.app_name,
                ])

        for d in dirs:
            self.create_directory(d)

    def generate_django_files(self) -> None:
        """Generate all Django app files."""
        ctx = self.get_context()
        app_dir = self.app_root / self.app_name if self.standalone else self.app_root

        self.render_and_write("app/__init__.py.j2", app_dir / "__init__.py", ctx)
        self.render_and_write("app/apps.py.j2", app_dir / "apps.py", ctx)
        self.render_and_write("app/models.py.j2", app_dir / "models.py", ctx)
        self.render_and_write("app/admin.py.j2", app_dir / "admin.py", ctx)
        self.render_and_write("app/forms.py.j2", app_dir / "forms.py", ctx)
        self.render_and_write("app/urls.py.j2", app_dir / "urls.py", ctx)
        self.render_and_write("app/permissions.py.j2", app_dir / "permissions.py", ctx)

        self.render_and_write(
            "app/migrations/__init__.py.j2",
            app_dir / "migrations" / "__init__.py",
            ctx,
        )

        self.render_and_write(
            "app/management/__init__.py.j2",
            app_dir / "management" / "__init__.py",
            ctx,
        )
        self.render_and_write(
            "app/management/commands/__init__.py.j2",
            app_dir / "management" / "commands" / "__init__.py",
            ctx,
        )
        self.render_and_write(
            "app/management/commands/demo_data.py.j2",
            app_dir / "management" / "commands" / f"demo_{self.app_name}.py",
            ctx,
        )

        if ctx["has_api"]:
            self.render_and_write("app/views_api.py.j2", app_dir / "views_api.py", ctx)
            self.render_and_write("app/serializers.py.j2", app_dir / "serializers.py", ctx)

        if ctx["has_frontend"]:
            self.render_and_write("app/views_frontend.py.j2", app_dir / "views_frontend.py", ctx)
            self._generate_templates(ctx)
            if self.standalone:
                self._generate_static_files(ctx)

        if self.celery:
            self.render_and_write("app/tasks.py.j2", app_dir / "tasks.py", ctx)

    def _generate_templates(self, ctx: Dict[str, Any]) -> None:
        """Generate HTML templates."""
        templates_dir = self.app_root / "templates" / self.app_name

        templates = [
            "base.html",
            "list.html",
            "detail.html",
            "form.html",
            "confirm_delete.html",
            "partials/item_row.html",
        ]

        for template in templates:
            self.render_and_write(
                f"app/templates/{template}.j2",
                templates_dir / template,
                ctx,
            )

    def _generate_static_files(self, ctx: Dict[str, Any]) -> None:
        """Generate static CSS and JS files."""
        static_dir = self.app_root / "static" / self.app_name

        self.render_and_write("app/static/css/style.css.j2", static_dir / "css" / "style.css", ctx)
        self.render_and_write("app/static/js/app.js.j2", static_dir / "js" / "app.js", ctx)

    def generate_tests(self) -> None:
        """Generate test files."""
        ctx = self.get_context()
        tests_dir = self.app_root / "tests"

        self.render_and_write("tests/__init__.py.j2", tests_dir / "__init__.py", ctx)
        self.render_and_write("tests/conftest.py.j2", tests_dir / "conftest.py", ctx)
        self.render_and_write("tests/test_models.py.j2", tests_dir / "test_models.py", ctx)

        if ctx["has_api"]:
            self.render_and_write("tests/test_api.py.j2", tests_dir / "test_api.py", ctx)

        if ctx["has_frontend"]:
            self.render_and_write("tests/test_frontend.py.j2", tests_dir / "test_frontend.py", ctx)

        self.render_and_write("tests/test_permissions.py.j2", tests_dir / "test_permissions.py", ctx)

    def generate_docker(self) -> None:
        """Generate Docker configuration."""
        ctx = self.get_context()
        docker_dir = self.app_root / "docker"

        self.render_and_write(
            "docker/Dockerfile.app.j2",
            docker_dir / f"Dockerfile.{self.app_name}",
            ctx,
        )

    def generate_docs(self) -> None:
        """Generate documentation files."""
        ctx = self.get_context()

        docs = [
            ("docs/README.md.j2", "README.md"),
            ("docs/CHANGELOG.md.j2", "CHANGELOG.md"),
            ("docs/CONTRIBUTING.md.j2", "CONTRIBUTING.md"),
            ("docs/TODO.md.j2", "TODO.md"),
            ("docs/SECURITY.md.j2", "SECURITY.md"),
            ("docs/COVERAGE.md.j2", "COVERAGE.md"),
            ("docs/ARCHITECTURE.md.j2", "ARCHITECTURE.md"),
            ("docs/LICENSE.j2", "LICENSE"),
        ]

        for template, output in docs:
            self.render_and_write(template, self.app_root / output, ctx)

        self.render_and_write(
            "docs/API.md.j2",
            self.app_root / "docs" / f"API-{self.app_name}.md",
            ctx,
        )

    def finalize(self) -> None:
        """Generate package config files (pyproject.toml, .gitignore, etc.)."""
        ctx = self.get_context()

        self.render_and_write("app/pyproject.toml.j2", self.app_root / "pyproject.toml", ctx)
        self.render_and_write("app/pytest.ini.j2", self.app_root / "pytest.ini", ctx)
        self.render_and_write("app/.gitignore.j2", self.app_root / ".gitignore", ctx)
        self.render_and_write("app/.env.example.j2", self.app_root / ".env.example", ctx)
        self.render_and_write(
            "app/.pre-commit-config.yaml.j2",
            self.app_root / ".pre-commit-config.yaml",
            ctx,
        )

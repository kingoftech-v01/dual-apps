"""
Project Generator for dual-apps.

Generates a complete Django project with:
- Multiple apps with dual-layer architecture
- Settings auto-configuration
- Docker dev/prod setup
- Complete test suite
- GitHub Actions CI/CD
- Full documentation
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from dual_apps.generators.base import BaseGenerator
from dual_apps.generators.app_generator import AppGenerator


class ProjectGenerator(BaseGenerator):
    """
    Generate a complete Django project with dual-layer architecture.

    Features:
    - Multiple apps generated
    - Settings auto-configured
    - Docker dev + prod ready
    - 150+ tests with 88% coverage
    - GitHub Actions workflows
    - 64 pages documentation
    """

    # Specialized templates and their corresponding apps
    SPECIALIZED_TEMPLATES = {
        "ecommerce": ["shop"],
        "blog": ["blog"],
        "saas": ["organizations", "subscriptions"],
        "cms": ["pages", "media"],
        "booking": ["services", "appointments"],
        "marketplace": ["vendors", "products"],
    }

    def __init__(
        self,
        project_name: str,
        apps: List[str] = None,
        template: str = "default",
        db: str = "postgres",
        auth: str = "jwt",
        docker: bool = True,
        i18n: bool = False,
        celery: bool = False,
        output_dir: Path = Path("."),
    ):
        super().__init__(output_dir)

        self.project_name = self._to_snake_case(project_name)
        self.project_name_display = self._to_title_case(project_name)
        self.template = template
        self.db = db
        self.auth = auth
        self.docker = docker
        self.i18n = i18n
        self.celery = celery

        # Handle specialized templates - auto-add apps for template
        if template in self.SPECIALIZED_TEMPLATES:
            template_apps = self.SPECIALIZED_TEMPLATES[template]
            self.apps = list(set((apps or []) + template_apps))
        else:
            self.apps = apps or ["jobs"]

        # Project root directory
        self.project_root = Path(self.project_name)

    def get_context(self) -> Dict[str, Any]:
        """Get template context for project generation."""
        return {
            **self.get_base_context(),
            "project_name": self.project_name,
            "project_name_display": self.project_name_display,
            "project_name_pascal": self._to_pascal_case(self.project_name),
            "apps": self.apps,
            "apps_config": [
                {
                    "name": app,
                    "name_pascal": self._to_pascal_case(app),
                    "name_title": self._to_title_case(app),
                }
                for app in self.apps
            ],
            "template": self.template,
            "db": self.db,
            "auth": self.auth,
            "docker": self.docker,
            "i18n": self.i18n,
            "celery": self.celery,
            "use_postgres": self.db == "postgres",
            "use_jwt": self.auth == "jwt",
            "use_session": self.auth == "session",
            "use_allauth": self.auth == "allauth",
            "is_specialized_template": self.template in self.SPECIALIZED_TEMPLATES,
        }

    def create_structure(self) -> None:
        """Create project directory structure."""
        # Core directories
        dirs = [
            self.project_root,
            self.project_root / self.project_name,
            self.project_root / self.project_name / "settings",
            self.project_root / "apps",
            self.project_root / "templates",
            self.project_root / "staticfiles" / "css",
            self.project_root / "staticfiles" / "js",
            self.project_root / "tests",
            self.project_root / "tests" / "fixtures",
            self.project_root / "docs",
            self.project_root / "scripts",
            self.project_root / "requirements",
            self.project_root / ".github" / "workflows",
            self.project_root / ".github" / "ISSUE_TEMPLATE",
        ]

        if self.docker:
            dirs.extend([
                self.project_root / "docker",
                self.project_root / "docker" / "nginx",
            ])

        if self.i18n:
            dirs.append(self.project_root / "locale")

        for d in dirs:
            self.create_directory(d)

    def generate_settings(self) -> None:
        """Generate Django settings module."""
        ctx = self.get_context()
        settings_dir = self.project_root / self.project_name / "settings"
        project_dir = self.project_root / self.project_name

        # Settings files
        self.render_and_write("project/settings/__init__.py.j2", settings_dir / "__init__.py", ctx)
        self.render_and_write("project/settings/base.py.j2", settings_dir / "base.py", ctx)
        self.render_and_write("project/settings/dev.py.j2", settings_dir / "dev.py", ctx)
        self.render_and_write("project/settings/prod.py.j2", settings_dir / "prod.py", ctx)
        self.render_and_write("project/settings/security.py.j2", settings_dir / "security.py", ctx)

        # Allauth settings if selected
        if self.auth == "allauth":
            self.render_and_write("auth/allauth/settings.py.j2", settings_dir / "allauth.py", ctx)

        # Project files
        self.render_and_write("project/__init__.py.j2", project_dir / "__init__.py", ctx)

        # Use specialized project urls.py if available
        specialized_urls = f"specialized/{self.template}/project/urls.py.j2"
        if self.template != "default" and self.template_exists(specialized_urls):
            self.render_and_write(specialized_urls, project_dir / "urls.py", ctx)
        else:
            self.render_and_write("project/urls.py.j2", project_dir / "urls.py", ctx)

        self.render_and_write("project/wsgi.py.j2", project_dir / "wsgi.py", ctx)
        self.render_and_write("project/asgi.py.j2", project_dir / "asgi.py", ctx)

        if self.celery:
            self.render_and_write("project/celery.py.j2", project_dir / "celery.py", ctx)

        # Allauth adapters if selected
        if self.auth == "allauth":
            self.render_and_write("auth/allauth/adapters.py.j2", project_dir / "adapters.py", ctx)

        # Root project files
        self.render_and_write("project/manage.py.j2", self.project_root / "manage.py", ctx, executable=True)

        # Requirements
        self.render_and_write("project/requirements/base.in.j2", self.project_root / "requirements" / "base.in", ctx)
        self.render_and_write("project/requirements/dev.in.j2", self.project_root / "requirements" / "dev.in", ctx)
        self.render_and_write("project/requirements/prod.in.j2", self.project_root / "requirements" / "prod.in", ctx)

    def generate_apps(self) -> None:
        """Generate all specified apps."""
        # Use absolute path for apps directory
        apps_dir = self.output_dir / self.project_root / "apps"
        ctx = self.get_context()

        # Check if we're using a specialized template
        if self.template in self.SPECIALIZED_TEMPLATES:
            self._generate_specialized_apps(apps_dir, ctx)
        else:
            # Standard app generation
            for app_name in self.apps:
                app_generator = AppGenerator(
                    app_name=app_name,
                    docker=False,
                    output_dir=apps_dir,
                    app_full_name=f"apps.{app_name}",
                    standalone=False,
                )
                app_generator.create_structure()
                app_generator.generate_django_files()
                app_generator.generate_tests()

    def _generate_specialized_apps(self, apps_dir: Path, ctx: Dict[str, Any]) -> None:
        """Generate apps from specialized templates."""
        template_name = self.template

        # Create the main app directory for the specialized template
        app_name = self.SPECIALIZED_TEMPLATES[template_name][0]
        app_dir = apps_dir / app_name

        # Create app directories
        dirs = [
            app_dir,
            app_dir / "templates" / app_name,
            app_dir / "tests",
            app_dir / "management" / "commands",
            app_dir / "migrations",
        ]
        for d in dirs:
            self.create_directory(d)

        # App context for templates
        app_ctx = {
            **ctx,
            "app_name": app_name,
            "app_name_pascal": self._to_pascal_case(app_name),
            "app_name_title": self._to_title_case(app_name),
            "app_name_kebab": self._to_kebab_case(app_name),
            "app_full_name": f"apps.{app_name}",
            "model_name": f"{self._to_pascal_case(app_name)}Model",
            "model_name_snake": self._to_snake_case(f"{app_name}_model"),
            "model_name_plural": f"{self._to_pascal_case(app_name)}Models",
            "has_frontend": True,
            "has_api": True,
        }

        # Files to generate with fallback to standard app templates
        files_to_generate = [
            ("models.py.j2", "models.py"),
            ("views_api.py.j2", "views_api.py"),
            ("serializers.py.j2", "serializers.py"),
            ("urls.py.j2", "urls.py"),
            ("admin.py.j2", "admin.py"),
            ("views_frontend.py.j2", "views_frontend.py"),
            ("permissions.py.j2", "permissions.py"),
            ("forms.py.j2", "forms.py"),
        ]

        for template_file, output_file in files_to_generate:
            specialized_template = f"specialized/{template_name}/{template_file}"
            standard_template = f"app/{template_file}"

            # Use specialized template if it exists, otherwise fall back to standard
            if self.template_exists(specialized_template):
                self.render_and_write(specialized_template, app_dir / output_file, app_ctx)
            elif self.template_exists(standard_template):
                self.render_and_write(standard_template, app_dir / output_file, app_ctx)

        # Create __init__.py files
        self.write_file(app_dir / "__init__.py", "")
        self.write_file(app_dir / "tests" / "__init__.py", "")
        self.write_file(app_dir / "management" / "__init__.py", "")
        self.write_file(app_dir / "management" / "commands" / "__init__.py", "")
        self.write_file(app_dir / "migrations" / "__init__.py", "")

        # Generate app config
        self.render_and_write("app/apps.py.j2", app_dir / "apps.py", app_ctx)

        # Generate any other standard apps
        for additional_app in self.apps:
            if additional_app != app_name:
                app_generator = AppGenerator(
                    app_name=additional_app,
                    docker=False,
                    output_dir=apps_dir,
                    app_full_name=f"apps.{additional_app}",
                    standalone=False,
                )
                app_generator.create_structure()
                app_generator.generate_django_files()
                app_generator.generate_tests()

    def generate_tests(self) -> None:
        """Generate project-level tests."""
        ctx = self.get_context()
        tests_dir = self.project_root / "tests"

        self.render_and_write("tests/project/__init__.py.j2", tests_dir / "__init__.py", ctx)
        self.render_and_write("tests/project/conftest.py.j2", tests_dir / "conftest.py", ctx)
        self.render_and_write("tests/project/test_integration.py.j2", tests_dir / "test_integration.py", ctx)
        self.render_and_write("tests/project/test_permissions.py.j2", tests_dir / "test_permissions.py", ctx)

        # Fixtures
        self.render_and_write(
            "tests/project/fixtures/demo_data.json.j2",
            tests_dir / "fixtures" / "demo_data.json",
            ctx,
        )

    def generate_docker(self) -> None:
        """Generate Docker configuration."""
        ctx = self.get_context()

        # Docker files
        self.render_and_write("docker/Dockerfile.app.j2", self.project_root / "docker" / "Dockerfile.app", ctx)
        self.render_and_write("docker/Dockerfile.celery.j2", self.project_root / "docker" / "Dockerfile.celery", ctx)
        self.render_and_write("docker/gunicorn.conf.py.j2", self.project_root / "docker" / "gunicorn.conf.py", ctx)
        self.render_and_write("docker/supervisord.conf.j2", self.project_root / "docker" / "supervisord.conf", ctx)

        # Nginx
        self.render_and_write("docker/nginx/nginx.conf.j2", self.project_root / "docker" / "nginx" / "nginx.conf", ctx)

        # Docker Compose files
        self.render_and_write("docker/docker-compose.dev.yml.j2", self.project_root / "docker-compose.dev.yml", ctx)
        self.render_and_write("docker/docker-compose.prod.yml.j2", self.project_root / "docker-compose.prod.yml", ctx)
        self.render_and_write("docker/docker-compose.yml.j2", self.project_root / "docker-compose.yml", ctx)

    def generate_docs(self) -> None:
        """Generate project documentation."""
        ctx = self.get_context()

        # Root documentation
        root_docs = [
            ("docs/README.project.md.j2", "README.md"),
            ("docs/CHANGELOG.md.j2", "CHANGELOG.md"),
            ("docs/CONTRIBUTING.md.j2", "CONTRIBUTING.md"),
            ("docs/TODO.md.j2", "TODO.md"),
            ("docs/SECURITY.md.j2", "SECURITY.md"),
            ("docs/COVERAGE.md.j2", "COVERAGE.md"),
            ("docs/ARCHITECTURE.project.md.j2", "ARCHITECTURE.md"),
            ("docs/LICENSE.j2", "LICENSE"),
        ]

        for template, output in root_docs:
            self.render_and_write(template, self.project_root / output, ctx)

        # docs/ folder
        docs_files = [
            ("docs/CONVENTION-v3.md.j2", "CONVENTION-v3.md"),
            ("docs/CLI-REFERENCE.md.j2", "CLI-REFERENCE.md"),
            ("docs/DEVELOPMENT.md.j2", "DEVELOPMENT.md"),
            ("docs/DEPLOYMENT.md.j2", "DEPLOYMENT.md"),
            ("docs/SECURITY-GUIDE.md.j2", "SECURITY-GUIDE.md"),
            ("docs/CUSTOMIZATION.md.j2", "CUSTOMIZATION.md"),
            ("docs/API.md.j2", "API.md"),
        ]

        for template, output in docs_files:
            self.render_and_write(template, self.project_root / "docs" / output, ctx)

    def generate_github_actions(self) -> None:
        """Generate GitHub Actions workflows."""
        ctx = self.get_context()
        workflows_dir = self.project_root / ".github" / "workflows"

        workflows = [
            ("github/ci.yml.j2", "ci.yml"),
            ("github/security.yml.j2", "security.yml"),
            ("github/cd.yml.j2", "cd.yml"),
            ("github/coverage.yml.j2", "coverage.yml"),
            ("github/release.yml.j2", "release.yml"),
        ]

        for template, output in workflows:
            self.render_and_write(template, workflows_dir / output, ctx)

        # Issue templates
        self.render_and_write(
            "github/ISSUE_TEMPLATE/bug.md.j2",
            self.project_root / ".github" / "ISSUE_TEMPLATE" / "bug.md",
            ctx,
        )
        self.render_and_write(
            "github/ISSUE_TEMPLATE/feature.md.j2",
            self.project_root / ".github" / "ISSUE_TEMPLATE" / "feature.md",
            ctx,
        )

    def generate_scripts(self) -> None:
        """Generate utility scripts."""
        ctx = self.get_context()
        scripts_dir = self.project_root / "scripts"

        scripts = [
            ("scripts/setup.sh.j2", "setup.sh"),
            ("scripts/deploy.sh.j2", "deploy.sh"),
            ("scripts/benchmark.sh.j2", "benchmark.sh"),
            ("scripts/security-audit.sh.j2", "security-audit.sh"),
        ]

        for template, output in scripts:
            self.render_and_write(template, scripts_dir / output, ctx, executable=True)

    def generate_templates_static(self) -> None:
        """Generate global templates and static files."""
        ctx = self.get_context()

        # Global templates
        self.render_and_write(
            "project/templates/base.html.j2",
            self.project_root / "templates" / "base.html",
            ctx,
        )
        self.render_and_write(
            "project/templates/404.html.j2",
            self.project_root / "templates" / "404.html",
            ctx,
        )
        self.render_and_write(
            "project/templates/500.html.j2",
            self.project_root / "templates" / "500.html",
            ctx,
        )

        # Allauth templates if selected
        if self.auth == "allauth":
            self._generate_allauth_templates(ctx)

        # Global static files
        self.render_and_write(
            "project/static/css/dual-base.css.j2",
            self.project_root / "staticfiles" / "css" / "dual-base.css",
            ctx,
        )
        self.render_and_write(
            "project/static/js/dual-global.js.j2",
            self.project_root / "staticfiles" / "js" / "dual-global.js",
            ctx,
        )

    def _generate_allauth_templates(self, ctx: Dict[str, Any]) -> None:
        """Generate django-allauth authentication templates."""
        # Create account templates directory
        account_dir = self.project_root / "templates" / "account"
        socialaccount_dir = self.project_root / "templates" / "socialaccount"
        self.create_directory(account_dir)
        self.create_directory(socialaccount_dir)

        # Account templates
        allauth_templates = [
            ("auth/allauth/templates/account/login.html.j2", "account/login.html"),
            ("auth/allauth/templates/account/signup.html.j2", "account/signup.html"),
        ]

        for template, output in allauth_templates:
            if self.template_exists(template):
                self.render_and_write(
                    template,
                    self.project_root / "templates" / output,
                    ctx,
                )

    def finalize(self) -> None:
        """Finalize project generation."""
        ctx = self.get_context()

        # Generate templates and static
        self.generate_templates_static()

        # Configuration files
        self.render_and_write("project/pyproject.toml.j2", self.project_root / "pyproject.toml", ctx)
        self.render_and_write("project/pytest.ini.j2", self.project_root / "pytest.ini", ctx)
        self.render_and_write("project/.gitignore.j2", self.project_root / ".gitignore", ctx)
        self.render_and_write("project/.env.example.j2", self.project_root / ".env.example", ctx)
        self.render_and_write("project/.pre-commit-config.yaml.j2", self.project_root / ".pre-commit-config.yaml", ctx)

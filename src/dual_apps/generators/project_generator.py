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
    - Security layer (SQL/XSS prevention, rate limiting)
    - Multiple project types (fullstack, backend, frontend)
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

    # Valid project types
    PROJECT_TYPES = ["fullstack", "backend", "frontend"]

    # Valid frontend choices
    FRONTEND_CHOICES = ["html", "htmx", "react", "none"]

    # Valid CSS frameworks
    CSS_FRAMEWORKS = ["bootstrap", "tailwind"]

    # Valid JWT storage options
    JWT_STORAGE_OPTIONS = ["httpOnly", "localStorage"]

    def __init__(
        self,
        project_name: str,
        project_type: str = "fullstack",
        apps: List[str] = None,
        template: str = "default",
        db: str = "postgres",
        auth: str = "jwt",
        jwt_storage: str = "httpOnly",
        docker: bool = True,
        i18n: bool = False,
        celery: bool = False,
        frontend: str = "htmx",
        css: str = "bootstrap",
        output_dir: Path = Path("."),
    ):
        super().__init__(output_dir)

        self.project_name = self._to_snake_case(project_name)
        self.project_name_display = self._to_title_case(project_name)
        self.project_type = project_type
        self.template = template
        self.db = db
        self.auth = auth
        self.jwt_storage = jwt_storage
        self.docker = docker
        self.i18n = i18n
        self.celery = celery
        self.frontend = frontend
        self.css = css

        # Adjust settings based on project type
        if project_type == "backend":
            self.frontend = "none"
            self.has_frontend = False
            self.has_api = True
        elif project_type == "frontend":
            self.has_frontend = True
            self.has_api = False
        else:  # fullstack
            self.has_frontend = True
            self.has_api = True

        # Handle specialized templates
        if template in self.SPECIALIZED_TEMPLATES:
            # If user provided apps, use those; otherwise use template defaults
            if apps:
                self.apps = apps
            else:
                self.apps = [self.SPECIALIZED_TEMPLATES[template][0]]
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
            # Project type
            "project_type": self.project_type,
            "is_fullstack": self.project_type == "fullstack",
            "is_backend_only": self.project_type == "backend",
            "is_frontend_only": self.project_type == "frontend",
            "has_frontend": self.has_frontend,
            "has_api": self.has_api,
            # Template
            "template": self.template,
            "is_specialized_template": self.template in self.SPECIALIZED_TEMPLATES,
            # Database
            "db": self.db,
            "use_postgres": self.db == "postgres",
            "use_mysql": self.db == "mysql",
            "use_sqlite": self.db == "sqlite",
            # Authentication
            "auth": self.auth,
            "use_jwt": self.auth == "jwt",
            "use_session": self.auth == "session",
            "use_allauth": self.auth == "allauth",
            "jwt_storage": self.jwt_storage,
            "use_httponly_jwt": self.jwt_storage == "httpOnly",
            "use_localstorage_jwt": self.jwt_storage == "localStorage",
            # Features
            "docker": self.docker,
            "i18n": self.i18n,
            "celery": self.celery,
            # Frontend
            "frontend": self.frontend,
            "use_html": self.frontend == "html",
            "use_htmx": self.frontend == "htmx",
            "use_react": self.frontend == "react",
            "no_frontend": self.frontend == "none",
            # CSS
            "css": self.css,
            "use_bootstrap": self.css == "bootstrap",
            "use_tailwind": self.css == "tailwind",
        }

    def create_structure(self) -> None:
        """Create project directory structure."""
        # Core directories
        dirs = [
            self.project_root,
            self.project_root / self.project_name,
            self.project_root / self.project_name / "settings",
            self.project_root / "apps",
            self.project_root / "apps" / "core",
            self.project_root / "apps" / "core" / "security",
            self.project_root / "tests",
            self.project_root / "tests" / "fixtures",
            self.project_root / "tests" / "security",
            self.project_root / "docs",
            self.project_root / "scripts",
            self.project_root / "requirements",
            self.project_root / ".github" / "workflows",
            self.project_root / ".github" / "ISSUE_TEMPLATE",
        ]

        # Add templates and static only if we have frontend
        if self.has_frontend:
            dirs.extend([
                self.project_root / "templates",
                self.project_root / "staticfiles" / "css",
                self.project_root / "staticfiles" / "js",
            ])

        if self.docker:
            dirs.extend([
                self.project_root / "docker",
                self.project_root / "docker" / "nginx",
            ])

        if self.i18n:
            dirs.append(self.project_root / "locale")

        # React frontend directory structure
        if self.frontend == "react":
            dirs.extend([
                self.project_root / "frontend",
                self.project_root / "frontend" / "src",
                self.project_root / "frontend" / "src" / "components",
                self.project_root / "frontend" / "src" / "components" / "common",
                self.project_root / "frontend" / "src" / "components" / "forms",
                self.project_root / "frontend" / "src" / "components" / "layout",
                self.project_root / "frontend" / "src" / "pages",
                self.project_root / "frontend" / "src" / "api",
                self.project_root / "frontend" / "src" / "auth",
                self.project_root / "frontend" / "src" / "hooks",
                self.project_root / "frontend" / "src" / "utils",
                self.project_root / "frontend" / "src" / "context",
                self.project_root / "frontend" / "public",
            ])

        # E2E tests directory
        dirs.append(self.project_root / "e2e")

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

        # Use the first app in self.apps for the specialized template
        app_name = self.apps[0]
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

        # Generate any other standard apps (excluding the one used for specialized template)
        for additional_app in self.apps[1:]:
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

        # Security tests
        security_tests_dir = tests_dir / "security"
        self.write_file(security_tests_dir / "__init__.py", "")
        self.render_and_write(
            "tests/security/test_validators.py.j2",
            security_tests_dir / "test_validators.py",
            ctx,
        )
        self.render_and_write(
            "tests/security/test_middleware.py.j2",
            security_tests_dir / "test_middleware.py",
            ctx,
        )
        self.render_and_write(
            "tests/security/test_throttling.py.j2",
            security_tests_dir / "test_throttling.py",
            ctx,
        )

    def generate_security_module(self) -> None:
        """Generate the core security module."""
        ctx = self.get_context()
        core_dir = self.project_root / "apps" / "core"
        security_dir = core_dir / "security"

        # Core app files
        self.write_file(core_dir / "__init__.py", "")
        self.render_and_write("core/apps.py.j2", core_dir / "apps.py", ctx)

        # Security module files
        self.write_file(security_dir / "__init__.py", '"""Security module for protection against common vulnerabilities."""\n')
        self.render_and_write("core/security/validators.py.j2", security_dir / "validators.py", ctx)
        self.render_and_write("core/security/middleware.py.j2", security_dir / "middleware.py", ctx)
        self.render_and_write("core/security/throttling.py.j2", security_dir / "throttling.py", ctx)
        self.render_and_write("core/security/mixins.py.j2", security_dir / "mixins.py", ctx)
        self.render_and_write("core/security/decorators.py.j2", security_dir / "decorators.py", ctx)
        self.render_and_write("core/security/utils.py.j2", security_dir / "utils.py", ctx)

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

        # Skip templates and static files for backend-only projects
        if not self.has_frontend:
            return

        # Use frontend-specific base template if available
        frontend_base = f"frontend/{self.frontend}/base.html.j2"
        if self.template_exists(frontend_base):
            self.render_and_write(frontend_base, self.project_root / "templates" / "base.html", ctx)
        else:
            self.render_and_write("project/templates/base.html.j2", self.project_root / "templates" / "base.html", ctx)

        # Error pages
        self.render_and_write("project/templates/404.html.j2", self.project_root / "templates" / "404.html", ctx)
        self.render_and_write("project/templates/500.html.j2", self.project_root / "templates" / "500.html", ctx)

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

        # Generate React frontend if selected
        if self.frontend == "react":
            self._generate_react_frontend(ctx)

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

    def _generate_react_frontend(self, ctx: Dict[str, Any]) -> None:
        """Generate React frontend files."""
        frontend_dir = self.project_root / "frontend"

        # React configuration files
        react_files = [
            ("frontend/react/package.json.j2", "package.json"),
            ("frontend/react/vite.config.js.j2", "vite.config.js"),
            ("frontend/react/index.html.j2", "index.html"),
            ("frontend/react/.gitignore.j2", ".gitignore"),
        ]

        for template, output in react_files:
            if self.template_exists(template):
                self.render_and_write(template, frontend_dir / output, ctx)

        # React source files
        react_src_files = [
            ("frontend/react/src/main.jsx.j2", "src/main.jsx"),
            ("frontend/react/src/App.jsx.j2", "src/App.jsx"),
            ("frontend/react/src/App.css.j2", "src/App.css"),
            ("frontend/react/src/index.css.j2", "src/index.css"),
            ("frontend/react/src/api/client.js.j2", "src/api/client.js"),
        ]

        for template, output in react_src_files:
            if self.template_exists(template):
                self.render_and_write(template, frontend_dir / output, ctx)

        # Generate components for each app
        for app_name in self.apps:
            app_ctx = {**ctx, "app_name": app_name, "app_name_pascal": self._to_pascal_case(app_name)}
            component_template = "frontend/react/src/components/ModelList.jsx.j2"
            if self.template_exists(component_template):
                self.render_and_write(
                    component_template,
                    frontend_dir / "src" / "components" / f"{self._to_pascal_case(app_name)}List.jsx",
                    app_ctx,
                )

    def finalize(self) -> None:
        """Finalize project generation."""
        ctx = self.get_context()

        # Generate security module
        self.generate_security_module()

        # Generate templates and static
        self.generate_templates_static()

        # Generate E2E test configuration
        self._generate_e2e_tests(ctx)

        # Configuration files
        self.render_and_write("project/pyproject.toml.j2", self.project_root / "pyproject.toml", ctx)
        self.render_and_write("project/pytest.ini.j2", self.project_root / "pytest.ini", ctx)
        self.render_and_write("project/.gitignore.j2", self.project_root / ".gitignore", ctx)
        self.render_and_write("project/.env.example.j2", self.project_root / ".env.example", ctx)
        self.render_and_write("project/.pre-commit-config.yaml.j2", self.project_root / ".pre-commit-config.yaml", ctx)

    def _generate_e2e_tests(self, ctx: Dict[str, Any]) -> None:
        """Generate E2E test configuration with Playwright."""
        e2e_dir = self.project_root / "e2e"

        # Playwright configuration
        self.render_and_write("e2e/playwright.config.js.j2", e2e_dir / "playwright.config.js", ctx)
        self.render_and_write("e2e/package.json.j2", e2e_dir / "package.json", ctx)

        # Test fixtures
        fixtures_dir = e2e_dir / "fixtures"
        self.create_directory(fixtures_dir)
        self.render_and_write("e2e/fixtures/auth.js.j2", fixtures_dir / "auth.js", ctx)

        # Base test file
        tests_dir = e2e_dir / "tests"
        self.create_directory(tests_dir)
        self.render_and_write("e2e/tests/base.spec.js.j2", tests_dir / "base.spec.js", ctx)

"""
Main CLI for dual-apps using Typer.

Provides commands for generating Django apps and projects with
dual-layer architecture (Frontend HTMX + API DRF).

Commands:
    dual_apps init app <name>      Generate a standalone Django app
    dual_apps init project <name>  Generate a complete Django project
    dual_apps add app <name>       Add app to existing project
    dual_apps config               Generate config file
    dual_apps version              Show version
"""

import typer
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint
import yaml
import json
import sys

# Valid choices for CLI options
PROJECT_TYPES = ["fullstack", "backend", "frontend"]
FRONTEND_CHOICES = ["html", "htmx", "react"]
CSS_FRAMEWORKS = ["bootstrap", "tailwind"]
JWT_STORAGE_OPTIONS = ["httpOnly", "localStorage"]
TEMPLATE_CHOICES = ["default", "ecommerce", "blog", "saas", "cms", "booking", "marketplace", "api"]
DB_CHOICES = ["postgres", "mysql", "sqlite"]
AUTH_CHOICES = ["jwt", "session", "allauth", "none"]

from dual_apps import __version__
from dual_apps.generators.app_generator import AppGenerator
from dual_apps.generators.project_generator import ProjectGenerator

# Initialize Typer app
app = typer.Typer(
    name="dual_apps",
    help="Django App & Project Generator with Dual-Layer Architecture",
    add_completion=False,
    rich_markup_mode="rich",
)

# Sub-commands
init_app = typer.Typer(help="Initialize a new app or project")
add_app = typer.Typer(help="Add components to existing project")
app.add_typer(init_app, name="init")
app.add_typer(add_app, name="add")

console = Console()


# =============================================================================
# Utility Functions
# =============================================================================

def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold green]dual-apps[/] version [cyan]{__version__}[/]")
        raise typer.Exit()


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML or JSON file."""
    if not config_path.exists():
        return {}

    with open(config_path) as f:
        if config_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f) or {}
        elif config_path.suffix == '.json':
            return json.load(f)
    return {}


def _parse_fields(fields_str: str) -> list:
    """
    Parse fields string into list of tuples.

    Input: "title:CharField,status:CharField(choices)"
    Output: [("title", "CharField", {}), ("status", "CharField", {"choices": True})]
    """
    if not fields_str:
        return []

    fields = []
    for field in fields_str.split(","):
        field = field.strip()
        if ":" not in field:
            continue

        name, field_type = field.split(":", 1)
        name = name.strip()
        field_type = field_type.strip()

        # Parse field options
        options = {}
        if "(" in field_type:
            base_type = field_type[:field_type.index("(")]
            opts = field_type[field_type.index("(")+1:field_type.rindex(")")]
            options = {"options": opts}
            field_type = base_type

        fields.append((name, field_type, options))

    return fields


# =============================================================================
# Interactive Mode
# =============================================================================

def interactive_app_setup() -> dict:
    """Interactive wizard for app generation."""
    console.print("\n[bold cyan]🧙 Interactive App Generator[/]\n")

    config = {}

    # App name
    config['name'] = Prompt.ask(
        "[yellow]App name[/] (snake_case)",
        default="myapp"
    )

    # Model name
    default_model = config['name'].replace('_', ' ').title().replace(' ', '')
    config['model'] = Prompt.ask(
        "[yellow]Main model name[/]",
        default=default_model
    )

    # Fields
    console.print("\n[dim]Enter model fields (comma-separated, format: name:type)[/]")
    console.print("[dim]Types: str, text, int, decimal, bool, date, datetime, uuid, email, url[/]")
    config['fields'] = Prompt.ask(
        "[yellow]Fields[/]",
        default="title:str,description:text,is_active:bool"
    )

    # Options
    console.print("\n[bold]Options:[/]")
    config['docker'] = Confirm.ask("[yellow]Include Docker files?[/]", default=True)
    config['celery'] = Confirm.ask("[yellow]Include Celery support?[/]", default=False)
    config['i18n'] = Confirm.ask("[yellow]Include i18n support?[/]", default=False)

    # API/Frontend
    console.print("\n[bold]Layer selection:[/]")
    layer = Prompt.ask(
        "[yellow]Generate[/]",
        choices=["both", "api-only", "frontend-only"],
        default="both"
    )
    config['api_only'] = layer == "api-only"
    config['frontend_only'] = layer == "frontend-only"

    return config


def interactive_project_setup() -> dict:
    """Interactive wizard for project generation."""
    console.print("\n[bold cyan]🧙 Interactive Project Generator[/]\n")

    config = {}

    # Project name
    config['name'] = Prompt.ask(
        "[yellow]Project name[/]",
        default="myproject"
    )

    # Project type
    console.print("\n[bold]Project Type:[/]")
    console.print("[dim]  fullstack - Full stack with API + Frontend (default)[/]")
    console.print("[dim]  backend   - API only (DRF ViewSets, no templates)[/]")
    console.print("[dim]  frontend  - Frontend only (no API processing)[/]")
    config['project_type'] = Prompt.ask(
        "[yellow]Project type[/]",
        choices=PROJECT_TYPES,
        default="fullstack"
    )

    # Template
    config['template'] = Prompt.ask(
        "[yellow]Project template[/]",
        choices=TEMPLATE_CHOICES,
        default="default"
    )

    # Apps
    console.print("\n[dim]Enter apps to generate (comma-separated)[/]")
    apps_str = Prompt.ask(
        "[yellow]Apps[/]",
        default="jobs,users"
    )
    config['apps'] = [a.strip() for a in apps_str.split(",")]

    # Database
    config['db'] = Prompt.ask(
        "[yellow]Database[/]",
        choices=DB_CHOICES,
        default="postgres"
    )

    # Authentication
    config['auth'] = Prompt.ask(
        "[yellow]Authentication[/]",
        choices=AUTH_CHOICES,
        default="jwt"
    )

    # JWT Storage (only if using JWT)
    if config['auth'] == 'jwt':
        console.print("\n[bold]JWT Token Storage:[/]")
        console.print("[dim]  httpOnly     - Secure httpOnly cookies (recommended)[/]")
        console.print("[dim]  localStorage - Browser localStorage (simpler)[/]")
        config['jwt_storage'] = Prompt.ask(
            "[yellow]JWT storage method[/]",
            choices=JWT_STORAGE_OPTIONS,
            default="httpOnly"
        )

    # Frontend framework (only if not backend-only)
    if config['project_type'] != 'backend':
        console.print("\n[bold]Frontend Framework:[/]")
        console.print("[dim]  html  - Basic Django templates, server-side rendering[/]")
        console.print("[dim]  htmx  - HTMX dynamic templates, SPA-like feel[/]")
        console.print("[dim]  react - React SPA with Vite, full client-side[/]")
        config['frontend'] = Prompt.ask(
            "[yellow]Frontend framework[/]",
            choices=FRONTEND_CHOICES,
            default="htmx"
        )

        # CSS Framework
        console.print("\n[bold]CSS Framework:[/]")
        config['css'] = Prompt.ask(
            "[yellow]CSS framework[/]",
            choices=CSS_FRAMEWORKS,
            default="bootstrap"
        )

    # Options
    console.print("\n[bold]Options:[/]")
    config['docker'] = Confirm.ask("[yellow]Include Docker files?[/]", default=True)
    config['celery'] = Confirm.ask("[yellow]Include Celery support?[/]", default=False)
    config['i18n'] = Confirm.ask("[yellow]Include i18n support?[/]", default=False)

    return config


# =============================================================================
# Main App Callback
# =============================================================================

@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    [bold green]dual-apps[/] - Django App & Project Generator

    Generate production-ready Django apps and projects with:
    - [cyan]Dual layer architecture[/] (Frontend + API)
    - [cyan]Zero configuration[/] setup
    - [cyan]88% test coverage[/] out of the box
    - [cyan]Docker[/] dev/prod ready
    - [cyan]OWASP security[/] headers

    Quick Start:
        dual_apps init app jobs --model=JobPosting
        dual_apps init project myproject --apps=jobs,users
    """
    pass


# =============================================================================
# Init App Command
# =============================================================================

@init_app.command("app")
def init_app_command(
    name: str = typer.Argument(
        None,
        help="App name (snake_case, e.g., 'jobs' or 'user_profiles')",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Main model name (e.g., 'JobPosting'). Default: '{Name}Model'",
    ),
    fields: str = typer.Option(
        None,
        "--fields",
        "-f",
        help="Model fields CSV: 'title:str,status:str,price:decimal'",
    ),
    api_only: bool = typer.Option(
        False,
        "--api-only",
        help="Generate API only (skip frontend templates)",
    ),
    frontend_only: bool = typer.Option(
        False,
        "--frontend-only",
        help="Generate frontend only (skip API)",
    ),
    docker: bool = typer.Option(
        True,
        "--docker/--no-docker",
        help="Generate Docker files",
    ),
    i18n: bool = typer.Option(
        False,
        "--i18n",
        help="Add internationalization support",
    ),
    celery: bool = typer.Option(
        False,
        "--celery",
        help="Add Celery async tasks support",
    ),
    auth_required: bool = typer.Option(
        True,
        "--auth/--no-auth",
        help="Require authentication for views",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Interactive setup wizard",
    ),
    config: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Load configuration from YAML/JSON file",
    ),
    output_dir: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory",
    ),
):
    """
    Generate a standalone Django app with dual-layer architecture.

    Examples:
        dual_apps init app jobs --model=JobPosting
        dual_apps init app products --fields="name:str,price:decimal"
        dual_apps init app myapp --interactive
        dual_apps init app myapp --config=dual-apps.yaml
    """
    # Interactive mode
    if interactive or name is None:
        cfg = interactive_app_setup()
        name = cfg.get('name', name)
        model = cfg.get('model', model)
        fields = cfg.get('fields', fields)
        docker = cfg.get('docker', docker)
        celery = cfg.get('celery', celery)
        i18n = cfg.get('i18n', i18n)
        api_only = cfg.get('api_only', api_only)
        frontend_only = cfg.get('frontend_only', frontend_only)

    # Config file
    if config:
        file_config = load_config(config)
        if 'app' in file_config:
            cfg = file_config['app']
            name = cfg.get('name', name)
            model = cfg.get('model', model)
            fields = cfg.get('fields', fields)
            docker = cfg.get('docker', docker)
            celery = cfg.get('celery', celery)
            i18n = cfg.get('i18n', i18n)

    if not name:
        console.print("[red]Error: App name is required[/]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold green]Creating Django App:[/] [cyan]{name}[/]",
        title="dual-apps",
        border_style="green",
    ))

    # Parse fields if provided
    parsed_fields = _parse_fields(fields) if fields else None

    # Set default model name
    if not model:
        model = f"{name.replace('_', ' ').title().replace(' ', '')}"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Generating...", total=6)

        generator = AppGenerator(
            app_name=name,
            model_name=model,
            fields=parsed_fields,
            api_only=api_only,
            frontend_only=frontend_only,
            docker=docker,
            i18n=i18n,
            celery=celery,
            auth_required=auth_required,
            output_dir=output_dir,
        )

        progress.update(task, advance=1, description="Creating directories...")
        generator.create_structure()

        progress.update(task, advance=1, description="Generating Django files...")
        generator.generate_django_files()

        progress.update(task, advance=1, description="Generating tests...")
        generator.generate_tests()

        if docker:
            progress.update(task, advance=1, description="Generating Docker files...")
            generator.generate_docker()
        else:
            progress.update(task, advance=1)

        progress.update(task, advance=1, description="Generating documentation...")
        generator.generate_docs()

        progress.update(task, advance=1, description="Finalizing...")
        generator.finalize()

    _print_success_app(name, output_dir)


# =============================================================================
# Init Project Command
# =============================================================================

@init_app.command("project")
def init_project_command(
    name: str = typer.Argument(
        None,
        help="Project name (e.g., 'myproject' or 'saas-platform')",
    ),
    project_type: str = typer.Option(
        "fullstack",
        "--type",
        help="Project type: 'fullstack' (both API + Frontend), 'backend' (API only), 'frontend' (Frontend only)",
    ),
    apps: str = typer.Option(
        "jobs",
        "--apps",
        "-a",
        help="Apps to generate (comma-separated): 'jobs,users,payments'",
    ),
    template: str = typer.Option(
        "default",
        "--template",
        "-t",
        help="Project template: 'default', 'ecommerce', 'blog', 'saas', 'cms', 'booking', 'marketplace', 'api'",
    ),
    db: str = typer.Option(
        "postgres",
        "--db",
        help="Database: 'postgres', 'mysql', or 'sqlite'",
    ),
    auth: str = typer.Option(
        "jwt",
        "--auth",
        help="Authentication: 'jwt', 'session', 'allauth', or 'none'",
    ),
    jwt_storage: str = typer.Option(
        None,
        "--jwt-storage",
        help="JWT token storage: 'httpOnly' (secure cookies) or 'localStorage'",
    ),
    docker: bool = typer.Option(
        True,
        "--docker/--no-docker",
        help="Generate Docker files",
    ),
    i18n: bool = typer.Option(
        False,
        "--i18n",
        help="Add internationalization support",
    ),
    celery: bool = typer.Option(
        False,
        "--celery",
        help="Add Celery async tasks",
    ),
    frontend: str = typer.Option(
        "htmx",
        "--frontend",
        "-f",
        help="Frontend framework: 'html' (basic), 'htmx' (dynamic), 'react' (SPA)",
    ),
    css: str = typer.Option(
        "bootstrap",
        "--css",
        help="CSS framework: 'bootstrap' or 'tailwind'",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Interactive setup wizard",
    ),
    config: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Load configuration from YAML/JSON file",
    ),
    output_dir: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory",
    ),
):
    """
    Generate a complete Django project with dual-layer architecture.

    Examples:
        dual_apps init project myproject --apps=jobs,users
        dual_apps init project myproject --type backend --template ecommerce
        dual_apps init project myproject --frontend react --css tailwind
        dual_apps init project myproject --auth jwt --jwt-storage httpOnly
        dual_apps init project myproject --interactive
        dual_apps init project myproject --config=dual-apps.yaml
    """
    # Interactive mode
    if interactive or name is None:
        cfg = interactive_project_setup()
        name = cfg.get('name', name)
        project_type = cfg.get('project_type', project_type)
        apps = ",".join(cfg.get('apps', [apps]))
        template = cfg.get('template', template)
        db = cfg.get('db', db)
        auth = cfg.get('auth', auth)
        jwt_storage = cfg.get('jwt_storage', jwt_storage)
        docker = cfg.get('docker', docker)
        celery = cfg.get('celery', celery)
        i18n = cfg.get('i18n', i18n)
        frontend = cfg.get('frontend', frontend)
        css = cfg.get('css', css)

    # Config file
    if config:
        file_config = load_config(config)
        if 'project' in file_config:
            cfg = file_config['project']
            name = cfg.get('name', name)
            project_type = cfg.get('type', cfg.get('project_type', project_type))
            if 'apps' in cfg:
                apps = ",".join(cfg['apps']) if isinstance(cfg['apps'], list) else cfg['apps']
            template = cfg.get('template', template)
            db = cfg.get('db', db)
            auth = cfg.get('auth', auth)
            jwt_storage = cfg.get('jwt_storage', jwt_storage)
            docker = cfg.get('docker', docker)
            celery = cfg.get('celery', celery)
            i18n = cfg.get('i18n', i18n)
            frontend = cfg.get('frontend', frontend)
            css = cfg.get('css', css)

    if not name:
        console.print("[red]Error: Project name is required[/]")
        raise typer.Exit(1)

    # Validate options
    if project_type not in PROJECT_TYPES:
        console.print(f"[red]Error: Invalid project type '{project_type}'. Choose from: {', '.join(PROJECT_TYPES)}[/]")
        raise typer.Exit(1)

    if frontend not in FRONTEND_CHOICES:
        console.print(f"[red]Error: Invalid frontend '{frontend}'. Choose from: {', '.join(FRONTEND_CHOICES)}[/]")
        raise typer.Exit(1)

    if css not in CSS_FRAMEWORKS:
        console.print(f"[red]Error: Invalid CSS framework '{css}'. Choose from: {', '.join(CSS_FRAMEWORKS)}[/]")
        raise typer.Exit(1)

    # Default jwt_storage if not specified (don't prompt - just use default)
    if jwt_storage is None:
        jwt_storage = "httpOnly"

    # Adjust settings based on project type
    if project_type == "backend":
        frontend = "none"  # No frontend for backend-only
    elif project_type == "frontend":
        auth = "none"  # No auth processing for frontend-only (connects to external API)

    console.print(Panel.fit(
        f"[bold green]Creating Django Project:[/] [cyan]{name}[/]",
        title="dual-apps",
        border_style="green",
    ))

    # Parse apps list
    apps_list = [a.strip() for a in apps.split(",") if a.strip()]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Generating...", total=9)

        generator = ProjectGenerator(
            project_name=name,
            project_type=project_type,
            apps=apps_list,
            template=template,
            db=db,
            auth=auth,
            jwt_storage=jwt_storage,
            docker=docker,
            i18n=i18n,
            celery=celery,
            frontend=frontend,
            css=css,
            output_dir=output_dir,
        )

        progress.update(task, advance=1, description="Creating project structure...")
        generator.create_structure()

        progress.update(task, advance=1, description="Generating Django settings...")
        generator.generate_settings()

        progress.update(task, advance=1, description="Generating apps...")
        generator.generate_apps()

        progress.update(task, advance=1, description="Generating tests...")
        generator.generate_tests()

        if docker:
            progress.update(task, advance=1, description="Generating Docker files...")
            generator.generate_docker()
        else:
            progress.update(task, advance=1)

        progress.update(task, advance=1, description="Generating documentation...")
        generator.generate_docs()

        progress.update(task, advance=1, description="Generating GitHub Actions...")
        generator.generate_github_actions()

        progress.update(task, advance=1, description="Generating scripts...")
        generator.generate_scripts()

        progress.update(task, advance=1, description="Finalizing...")
        generator.finalize()

    _print_success_project(name, apps_list, output_dir, auth)


# =============================================================================
# Add App Command
# =============================================================================

@add_app.command("app")
def add_app_command(
    name: str = typer.Argument(
        ...,
        help="App name to add",
    ),
    to: Path = typer.Option(
        Path("."),
        "--to",
        "-t",
        help="Project directory to add app to",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Main model name",
    ),
    fields: str = typer.Option(
        None,
        "--fields",
        "-f",
        help="Model fields",
    ),
):
    """
    Add a new app to an existing project.

    Example:
        dual_apps add app products --to=myproject
    """
    apps_dir = to / "apps"

    if not apps_dir.exists():
        console.print(f"[red]Error: apps/ directory not found in {to}[/]")
        console.print("[dim]Make sure you're in a dual-apps generated project[/]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold green]Adding App:[/] [cyan]{name}[/] to [cyan]{to}[/]",
        title="dual-apps",
        border_style="green",
    ))

    if not model:
        model = f"{name.replace('_', ' ').title().replace(' ', '')}"

    parsed_fields = _parse_fields(fields) if fields else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Adding app...", total=None)

        generator = AppGenerator(
            app_name=name,
            model_name=model,
            fields=parsed_fields,
            docker=False,
            output_dir=apps_dir,
        )

        progress.update(task, description="Creating app structure...")
        generator.create_structure()

        progress.update(task, description="Generating Django files...")
        generator.generate_django_files()

        progress.update(task, description="Generating tests...")
        generator.generate_tests()

        progress.update(task, description="Generating docs...")
        generator.generate_docs()

    console.print(f"\n[green]✓[/] App [cyan]{name}[/] added successfully!")
    console.print(f"\n[bold]Next steps:[/]")
    console.print(f"1. Add [cyan]'apps.{name}'[/] to INSTALLED_APPS in settings")
    console.print(f"2. Add URL: [cyan]path('{name}/', include('apps.{name}.urls'))[/]")
    console.print(f"3. Run: [yellow]python manage.py makemigrations {name}[/]")
    console.print(f"4. Run: [yellow]python manage.py migrate[/]")


# =============================================================================
# Config Command
# =============================================================================

@app.command("config")
def config_command(
    output: Path = typer.Option(
        Path("dual-apps.yaml"),
        "--output",
        "-o",
        help="Output file path",
    ),
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Output format: yaml or json",
    ),
):
    """
    Generate a sample configuration file.

    Example:
        dual_apps config --output=dual-apps.yaml
    """
    sample_config = {
        "project": {
            "name": "myproject",
            "version": "1.0.0",
            "apps": ["jobs", "users", "products"],
            "template": "default",
            "db": "postgres",
            "docker": True,
            "celery": False,
            "i18n": False,
        },
        "apps": {
            "jobs": {
                "model": "JobPosting",
                "fields": [
                    {"name": "title", "type": "str"},
                    {"name": "description", "type": "text"},
                    {"name": "salary", "type": "decimal"},
                    {"name": "is_remote", "type": "bool"},
                ],
            },
            "users": {
                "model": "UserProfile",
                "fields": [
                    {"name": "bio", "type": "text"},
                    {"name": "avatar", "type": "str"},
                ],
            },
        },
        "options": {
            "auth": "jwt",
            "docker": True,
            "celery": False,
            "i18n": False,
        },
    }

    with open(output, 'w') as f:
        if format == 'yaml':
            yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(sample_config, f, indent=2)

    console.print(f"[green]✓[/] Configuration file created: [cyan]{output}[/]")
    console.print(f"\n[bold]Usage:[/]")
    console.print(f"  dual_apps init project myproject --config={output}")


# =============================================================================
# Info Command
# =============================================================================

@app.command("info")
def info_command():
    """
    Show information about dual-apps.
    """
    table = Table(title="dual-apps Information", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Version", __version__)
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Documentation", "https://dual-apps.github.io/dual-apps/")
    table.add_row("GitHub", "https://github.com/dual-apps/dual-apps")
    table.add_row("PyPI", "https://pypi.org/project/dual-apps/")

    console.print(table)

    console.print("\n[bold]Features:[/]")
    features = [
        "✓ Dual-layer architecture (Frontend HTMX + API DRF)",
        "✓ 88% test coverage out of the box",
        "✓ Docker dev/prod configurations",
        "✓ OWASP security headers",
        "✓ GitHub Actions CI/CD",
        "✓ OpenAPI/Swagger documentation",
        "✓ JWT/Session authentication",
    ]
    for feature in features:
        console.print(f"  [green]{feature}[/]")


# =============================================================================
# Help Command
# =============================================================================

@app.command("help")
def help_command(
    topic: Optional[str] = typer.Argument(
        None,
        help="Help topic: commands, templates, quickstart, config, examples"
    )
):
    """
    Show detailed documentation and usage examples.

    Examples:
        dual-apps help              Show all help topics
        dual-apps help commands     List all commands with examples
        dual-apps help templates    Show available project templates
        dual-apps help quickstart   Quick start guide
        dual-apps help examples     Show usage examples
    """
    if topic is None:
        _show_help_overview()
    elif topic.lower() == "commands":
        _show_help_commands()
    elif topic.lower() == "templates":
        _show_help_templates()
    elif topic.lower() in ("quickstart", "quick", "start"):
        _show_help_quickstart()
    elif topic.lower() in ("config", "configuration"):
        _show_help_config()
    elif topic.lower() == "examples":
        _show_help_examples()
    else:
        console.print(f"[yellow]Unknown topic: {topic}[/]")
        console.print("Available topics: [cyan]commands, templates, quickstart, config, examples[/]")


def _show_help_overview():
    """Show help overview with all topics."""
    console.print(Panel(
        """[bold cyan]dual-apps[/] - Django App & Project Generator

Generate production-ready Django apps and projects with dual-layer architecture
(Frontend HTMX + REST API with Django REST Framework).

[bold]Help Topics:[/]
  [cyan]dual-apps help commands[/]     List all available commands
  [cyan]dual-apps help templates[/]    Show project templates (ecommerce, blog, saas, etc.)
  [cyan]dual-apps help quickstart[/]   Quick start guide
  [cyan]dual-apps help config[/]       Configuration file reference
  [cyan]dual-apps help examples[/]     Usage examples

[bold]Quick Commands:[/]
  [green]dual-apps init app myapp[/]              Create a standalone app
  [green]dual-apps init project mysite[/]         Create a full project
  [green]dual-apps init project shop -t ecommerce[/]  E-commerce project
  [green]dual-apps init project app -f react[/]   React SPA frontend
  [green]dual-apps config[/]                      Generate config file

[bold]More Info:[/]
  [cyan]dual-apps info[/]              Show version and links
  [cyan]dual-apps --help[/]            Show command-line options
  [cyan]dual-apps init app --help[/]   Show app creation options
  [cyan]dual-apps init project --help[/] Show project creation options""",
        title="[bold green]dual-apps Help[/]",
        border_style="cyan",
    ))


def _show_help_commands():
    """Show all available commands."""
    console.print("\n[bold cyan]Available Commands[/]\n")

    # Init commands
    console.print("[bold]Initialize new app or project:[/]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Command", style="green")
    table.add_column("Description")
    table.add_column("Example", style="dim")

    table.add_row(
        "init app <name>",
        "Create a standalone Django app",
        "dual-apps init app blog"
    )
    table.add_row(
        "init project <name>",
        "Create a complete Django project",
        "dual-apps init project mysite"
    )
    console.print(table)

    # Add commands
    console.print("\n[bold]Add to existing project:[/]")
    table2 = Table(show_header=True, header_style="bold")
    table2.add_column("Command", style="green")
    table2.add_column("Description")
    table2.add_column("Example", style="dim")

    table2.add_row(
        "add app <name>",
        "Add an app to existing project",
        "dual-apps add app payments"
    )
    console.print(table2)

    # Utility commands
    console.print("\n[bold]Utility commands:[/]")
    table3 = Table(show_header=True, header_style="bold")
    table3.add_column("Command", style="green")
    table3.add_column("Description")

    table3.add_row("config", "Generate a sample configuration file")
    table3.add_row("info", "Show version and project information")
    table3.add_row("help [topic]", "Show help and documentation")
    table3.add_row("--version, -v", "Show version number")
    console.print(table3)

    console.print("\n[dim]Use --help with any command for detailed options:[/]")
    console.print("  [cyan]dual-apps init project --help[/]")


def _show_help_templates():
    """Show available project templates."""
    console.print("\n[bold cyan]Project Templates[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Template", style="green")
    table.add_column("Description")
    table.add_column("Models Included")

    table.add_row(
        "default",
        "Basic project structure",
        "Custom model with CRUD"
    )
    table.add_row(
        "ecommerce",
        "E-commerce / Online store",
        "Product, Category, Cart, Order, Review"
    )
    table.add_row(
        "blog",
        "Blog / Content platform",
        "Post, Category, Comment, Tag, Newsletter"
    )
    table.add_row(
        "saas",
        "SaaS / Multi-tenant app",
        "Organization, Member, Plan, Subscription, Invoice"
    )
    table.add_row(
        "cms",
        "Content Management System",
        "Page, Block, Menu, Media, Form"
    )
    table.add_row(
        "booking",
        "Appointment / Reservation system",
        "Service, Staff, Booking, Availability, Review"
    )
    table.add_row(
        "marketplace",
        "Multi-vendor marketplace",
        "Vendor, Product, Order, Review, Payout"
    )
    table.add_row(
        "api",
        "API-only project",
        "Custom models, no frontend templates"
    )
    console.print(table)

    console.print("\n[bold]Usage:[/]")
    console.print("  [green]dual-apps init project myshop --template ecommerce[/]")
    console.print("  [green]dual-apps init project myblog -t blog[/]")
    console.print("  [green]dual-apps init project mysaas -t saas --apps orgs[/]")

    # Frontend options
    console.print("\n[bold cyan]Frontend Frameworks[/]\n")

    frontend_table = Table(show_header=True, header_style="bold")
    frontend_table.add_column("Frontend", style="green")
    frontend_table.add_column("Description")
    frontend_table.add_column("Features")

    frontend_table.add_row(
        "html",
        "Basic Django templates",
        "Server-side rendering, forms, no JS required"
    )
    frontend_table.add_row(
        "htmx",
        "HTMX dynamic templates (default)",
        "Partial page updates, minimal JS, SPA-like feel"
    )
    frontend_table.add_row(
        "react",
        "React SPA",
        "Separate frontend, Vite build, API-driven"
    )
    console.print(frontend_table)

    console.print("\n[bold]Frontend Usage:[/]")
    console.print("  [green]dual-apps init project mysite --frontend html[/]      [dim]# Basic HTML[/]")
    console.print("  [green]dual-apps init project mysite --frontend htmx[/]      [dim]# HTMX (default)[/]")
    console.print("  [green]dual-apps init project mysite --frontend react[/]     [dim]# React SPA[/]")


def _show_help_quickstart():
    """Show quick start guide."""
    console.print(Panel(
        """[bold]1. Create a new project[/]
   [green]dual-apps init project myproject[/]

[bold]2. Enter the project directory[/]
   [green]cd myproject[/]

[bold]3. Set up the environment[/]
   [green]python -m venv .venv[/]
   [green]source .venv/bin/activate[/]  [dim]# On Windows: .venv\\Scripts\\activate[/]
   [green]pip install -r requirements/dev.in[/]

[bold]4. Configure the database[/]
   [green]cp .env.example .env[/]
   [dim]# Edit .env with your database settings[/]

[bold]5. Run migrations[/]
   [green]python manage.py migrate[/]
   [green]python manage.py createsuperuser[/]

[bold]6. Start the development server[/]
   [green]python manage.py runserver[/]

[bold]7. Access your application[/]
   Frontend: [cyan]http://localhost:8000/[/]
   Admin:    [cyan]http://localhost:8000/admin/[/]
   API:      [cyan]http://localhost:8000/api/v1/[/]
   API Docs: [cyan]http://localhost:8000/api/docs/[/]

[bold]Alternative: Use Docker[/]
   [green]./scripts/setup.sh[/]  [dim]# One-command setup[/]
   [green]docker-compose up[/]   [dim]# Start all services[/]""",
        title="[bold green]Quick Start Guide[/]",
        border_style="green",
    ))


def _show_help_config():
    """Show configuration file reference."""
    console.print("\n[bold cyan]Configuration File Reference[/]\n")

    console.print("[bold]Generate a config file:[/]")
    console.print("  [green]dual-apps config > dual-apps.yaml[/]\n")

    console.print("[bold]Use with project creation:[/]")
    console.print("  [green]dual-apps init project myproject --config dual-apps.yaml[/]\n")

    console.print("[bold]Configuration options:[/]")

    config_example = """[dim]# dual-apps.yaml[/]
[cyan]project_name[/]: myproject
[cyan]apps[/]:
  - users
  - products
  - orders

[cyan]template[/]: ecommerce    [dim]# default, ecommerce, blog, saas, cms, booking, marketplace[/]
[cyan]database[/]: postgres     [dim]# postgres or sqlite[/]
[cyan]auth[/]: jwt              [dim]# jwt, session, allauth, or none[/]

[cyan]features[/]:
  [cyan]docker[/]: true          [dim]# Generate Docker files[/]
  [cyan]celery[/]: false         [dim]# Add Celery async tasks[/]
  [cyan]i18n[/]: false           [dim]# Add internationalization[/]

[cyan]model_fields[/]:          [dim]# Custom fields for default template[/]
  - title:CharField
  - status:CharField(choices)
  - created_at:DateTimeField"""

    console.print(config_example)


def _show_help_examples():
    """Show usage examples."""
    console.print("\n[bold cyan]Usage Examples[/]\n")

    examples = [
        (
            "Create a basic app",
            "dual-apps init app blog",
            "Creates a standalone blog app with models, views, serializers, and tests"
        ),
        (
            "Create app with custom model",
            "dual-apps init app jobs --model JobPosting --fields 'title:CharField,salary:DecimalField'",
            "Creates an app with a JobPosting model and specified fields"
        ),
        (
            "Create a basic project",
            "dual-apps init project mysite --apps jobs,users",
            "Creates a Django project with jobs and users apps"
        ),
        (
            "Create an e-commerce project",
            "dual-apps init project shop --template ecommerce --apps products",
            "Creates a full e-commerce project with product catalog"
        ),
        (
            "Create a SaaS project",
            "dual-apps init project saasapp -t saas --apps tenants --auth jwt",
            "Creates a multi-tenant SaaS application"
        ),
        (
            "Create with SQLite (no Docker)",
            "dual-apps init project quickstart --db sqlite --no-docker",
            "Creates a lightweight project for quick development"
        ),
        (
            "Create with allauth authentication",
            "dual-apps init project socialsite --auth allauth",
            "Creates project with social login (Google, GitHub)"
        ),
        (
            "Interactive mode",
            "dual-apps init project myproject --interactive",
            "Step-by-step wizard to configure your project"
        ),
        (
            "Use a config file",
            "dual-apps init project myproject --config dual-apps.yaml",
            "Load all settings from a YAML configuration file"
        ),
    ]

    for title, command, description in examples:
        console.print(f"[bold]{title}[/]")
        console.print(f"  [green]{command}[/]")
        console.print(f"  [dim]{description}[/]\n")


# =============================================================================
# Success Messages
# =============================================================================

def _print_success_app(name: str, output_dir: Path):
    """Print success message for app generation."""
    app_path = output_dir / name

    console.print()
    console.print(Panel(
        f"""[bold green]✓ App generated successfully![/]

[cyan]Location:[/] {app_path.absolute()}

[bold]Next steps:[/]

  [yellow]cd {name}[/]
  [yellow]pip install -e .[/]
  [yellow]pytest[/]  [dim]# Run tests (45 tests, 88% coverage)[/]

[bold]Add to existing project:[/]

  1. Copy [cyan]{name}/[/] to your [cyan]apps/[/] folder
  2. Add to INSTALLED_APPS: [cyan]'apps.{name}'[/]
  3. Add URL: [cyan]path('{name}/', include('apps.{name}.urls'))[/]
  4. Register in router: [cyan]router.register('{name}', {name.title()}ViewSet)[/]
  5. Run: [yellow]python manage.py migrate[/]

[bold]URLs generated:[/]
  Frontend: [green]/{name}/[/]
  API:      [green]/api/v1/{name}/[/]
  Docs:     [green]/api/docs/[/]""",
        title="[bold green]Success![/]",
        border_style="green",
    ))


def _print_success_project(name: str, apps: List[str], output_dir: Path, auth: str = "jwt"):
    """Print success message for project generation."""
    project_path = output_dir / name

    apps_str = ", ".join(apps)

    console.print()
    console.print(Panel(
        f"""[bold green]✓ Project generated successfully![/]

[cyan]Location:[/] {project_path.absolute()}
[cyan]Apps:[/] {apps_str}
[cyan]Auth:[/] {auth}

[bold]Quick Start (30 seconds):[/]

  [yellow]cd {name}[/]
  [yellow]./scripts/setup.sh[/]  [dim]# One-command setup[/]
  [yellow]docker-compose up[/]   [dim]# Start dev server[/]

[bold]Manual Setup:[/]

  [yellow]python -m venv .venv && source .venv/bin/activate[/]
  [yellow]pip install -r requirements/dev.in[/]
  [yellow]cp .env.example .env[/]
  [yellow]python manage.py migrate[/]
  [yellow]python manage.py createsuperuser[/]
  [yellow]python manage.py runserver[/]

[bold]Run Tests:[/]
  [yellow]pytest[/]  [dim]# 150+ tests, 88% coverage[/]

[bold]URLs ready:[/]
  Frontend: [green]http://localhost:8000/{apps[0]}/[/]
  API:      [green]http://localhost:8000/api/v1/{apps[0]}/[/]
  Admin:    [green]http://localhost:8000/admin/[/]
  API Docs: [green]http://localhost:8000/api/docs/[/]
  ReDoc:    [green]http://localhost:8000/api/redoc/[/]

[bold]Documentation:[/]
  [dim]See README.md and docs/ folder for complete documentation[/]""",
        title="[bold green]Success![/]",
        border_style="green",
    ))


if __name__ == "__main__":
    app()

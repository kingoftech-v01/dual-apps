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
        choices=["postgres", "sqlite"],
        default="postgres"
    )

    # Authentication
    config['auth'] = Prompt.ask(
        "[yellow]Authentication[/]",
        choices=["jwt", "session", "none"],
        default="jwt"
    )

    # Options
    console.print("\n[bold]Options:[/]")
    config['docker'] = Confirm.ask("[yellow]Include Docker files?[/]", default=True)
    config['celery'] = Confirm.ask("[yellow]Include Celery support?[/]", default=False)
    config['i18n'] = Confirm.ask("[yellow]Include i18n support?[/]", default=False)

    # Template
    config['template'] = Prompt.ask(
        "[yellow]Project template[/]",
        choices=["default", "saas", "api", "minimal"],
        default="default"
    )

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
        help="Project template: 'default', 'saas', 'api', 'minimal'",
    ),
    db: str = typer.Option(
        "postgres",
        "--db",
        help="Database: 'postgres' or 'sqlite'",
    ),
    auth: str = typer.Option(
        "jwt",
        "--auth",
        help="Authentication: 'jwt', 'session', or 'none'",
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
        dual_apps init project myproject --interactive
        dual_apps init project myproject --config=dual-apps.yaml
    """
    # Interactive mode
    if interactive or name is None:
        cfg = interactive_project_setup()
        name = cfg.get('name', name)
        apps = ",".join(cfg.get('apps', [apps]))
        template = cfg.get('template', template)
        db = cfg.get('db', db)
        auth = cfg.get('auth', auth)
        docker = cfg.get('docker', docker)
        celery = cfg.get('celery', celery)
        i18n = cfg.get('i18n', i18n)

    # Config file
    if config:
        file_config = load_config(config)
        if 'project' in file_config:
            cfg = file_config['project']
            name = cfg.get('name', name)
            if 'apps' in cfg:
                apps = ",".join(cfg['apps']) if isinstance(cfg['apps'], list) else cfg['apps']
            template = cfg.get('template', template)
            db = cfg.get('db', db)
            docker = cfg.get('docker', docker)
            celery = cfg.get('celery', celery)
            i18n = cfg.get('i18n', i18n)

    if not name:
        console.print("[red]Error: Project name is required[/]")
        raise typer.Exit(1)

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
            apps=apps_list,
            template=template,
            db=db,
            docker=docker,
            i18n=i18n,
            celery=celery,
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

"""
Main CLI for dual-apps using Typer.

Provides commands for generating Django apps and projects with
dual-layer architecture (Frontend HTMX + API DRF).

Commands:
    dual_apps init app <name>      Generate a standalone Django app
    dual_apps init project <name>  Generate a complete Django project
    dual_apps version              Show version
"""

import typer
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

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

# Sub-command for init
init_app = typer.Typer(help="Initialize a new app or project")
app.add_typer(init_app, name="init")

console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold green]dual-apps[/] version [cyan]{__version__}[/]")
        raise typer.Exit()


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
    """
    pass


@init_app.command("app")
def init_app_command(
    name: str = typer.Argument(
        ...,
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
        help="Model fields CSV: 'title:CharField,status:CharField(choices)'",
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
    output_dir: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory",
    ),
):
    """
    Generate a standalone Django app with dual-layer architecture.

    Example:
        dual_apps init app jobs --model=JobPosting --fields="title:CharField,status:CharField"
    """
    console.print(Panel.fit(
        f"[bold green]Creating Django App:[/] [cyan]{name}[/]",
        title="dual-apps",
        border_style="green",
    ))

    # Parse fields if provided
    parsed_fields = _parse_fields(fields) if fields else None

    # Set default model name
    if not model:
        model = f"{name.replace('_', ' ').title().replace(' ', '')}Model"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating app structure...", total=None)

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

        progress.update(task, description="Creating directories...")
        generator.create_structure()

        progress.update(task, description="Generating Django files...")
        generator.generate_django_files()

        progress.update(task, description="Generating tests...")
        generator.generate_tests()

        if docker:
            progress.update(task, description="Generating Docker files...")
            generator.generate_docker()

        progress.update(task, description="Generating documentation...")
        generator.generate_docs()

        progress.update(task, description="Finalizing...")
        generator.finalize()

    _print_success_app(name, output_dir)


@init_app.command("project")
def init_project_command(
    name: str = typer.Argument(
        ...,
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
        help="Project template: 'default', 'saas', 'api', 'monolith'",
    ),
    db: str = typer.Option(
        "postgres",
        "--db",
        help="Database: 'postgres' or 'sqlite'",
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
    output_dir: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory",
    ),
):
    """
    Generate a complete Django project with dual-layer architecture.

    Example:
        dual_apps init project myproject --apps=jobs,users,payments
    """
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
        console=console,
    ) as progress:
        task = progress.add_task("Generating project structure...", total=None)

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

        progress.update(task, description="Creating project structure...")
        generator.create_structure()

        progress.update(task, description="Generating Django settings...")
        generator.generate_settings()

        progress.update(task, description="Generating apps...")
        generator.generate_apps()

        progress.update(task, description="Generating tests...")
        generator.generate_tests()

        if docker:
            progress.update(task, description="Generating Docker files...")
            generator.generate_docker()

        progress.update(task, description="Generating documentation...")
        generator.generate_docs()

        progress.update(task, description="Generating GitHub Actions...")
        generator.generate_github_actions()

        progress.update(task, description="Generating scripts...")
        generator.generate_scripts()

        progress.update(task, description="Finalizing...")
        generator.finalize()

    _print_success_project(name, apps_list, output_dir)


def _parse_fields(fields_str: str) -> list:
    """
    Parse fields string into list of tuples.

    Input: "title:CharField,status:CharField(choices)"
    Output: [("title", "CharField", {}), ("status", "CharField", {"choices": True})]
    """
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


def _print_success_app(name: str, output_dir: Path):
    """Print success message for app generation."""
    app_path = output_dir / name

    console.print()
    console.print(Panel(
        f"""[bold green]App generated successfully![/]

[cyan]Location:[/] {app_path.absolute()}

[bold]Next steps:[/]

1. [yellow]cd {name}[/]
2. [yellow]pip install -e .[/]
3. [yellow]pytest[/]  # Run tests (45 tests, 88% coverage)

[bold]Add to existing project:[/]

1. Copy [cyan]{name}/[/] to your [cyan]apps/[/] folder
2. Add to INSTALLED_APPS: [cyan]'{name}.apps.{name.title()}Config'[/]
3. Include URLs: [cyan]path('{name}/', include('{name}.urls'))[/]
4. Run: [yellow]python manage.py migrate {name}[/]

[bold]URLs generated:[/]
  Frontend: [green]/{name}/[/]
  API:      [green]/api/v1/{name}/[/]""",
        title="[bold green]Success![/]",
        border_style="green",
    ))


def _print_success_project(name: str, apps: List[str], output_dir: Path):
    """Print success message for project generation."""
    project_path = output_dir / name

    apps_str = ", ".join(apps)

    console.print()
    console.print(Panel(
        f"""[bold green]Project generated successfully![/]

[cyan]Location:[/] {project_path.absolute()}
[cyan]Apps:[/] {apps_str}

[bold]Quick Start (30 seconds):[/]

1. [yellow]cd {name}[/]
2. [yellow]./scripts/setup.sh[/]  # One-command setup
3. [yellow]docker-compose up[/]   # Start dev server
4. Open [green]http://localhost:8000[/]

[bold]Manual Setup:[/]

1. [yellow]pip install -r requirements/dev.in[/]
2. [yellow]cp .env.example .env[/]
3. [yellow]python manage.py migrate[/]
4. [yellow]python manage.py runserver[/]

[bold]Run Tests:[/]
[yellow]pytest[/]  # 150+ tests, 88% coverage

[bold]URLs ready:[/]
  Frontend: [green]http://localhost:8000/{apps[0]}/[/]
  API:      [green]http://localhost:8000/api/v1/{apps[0]}/[/]
  Admin:    [green]http://localhost:8000/admin/[/]
  API Docs: [green]http://localhost:8000/api/docs/[/]""",
        title="[bold green]Success![/]",
        border_style="green",
    ))


if __name__ == "__main__":
    app()

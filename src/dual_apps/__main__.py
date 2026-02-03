"""
Entry point for running dual_apps as a module.

Usage:
    python -m dual_apps init app jobs
    python -m dual_apps init project myproject
"""

from dual_apps.cli.main import app

if __name__ == "__main__":
    app()

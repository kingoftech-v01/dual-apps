"""
dual-apps: Django App & Project Generator with Dual-Layer Architecture.

Generate production-ready Django apps and projects with:
- Dual layer architecture (Frontend + API)
- Zero configuration setup
- 88% test coverage out of the box
- Docker dev/prod ready
- OWASP security headers
- Complete documentation

Usage:
    dual_apps init app jobs --model=JobPosting
    dual_apps init project myproject --apps=jobs,users

Author: dual-apps team
License: MIT
Version: 3.1.0
"""

__version__ = "3.1.0"
__author__ = "dual-apps team"
__license__ = "MIT"

from dual_apps.generators.app_generator import AppGenerator
from dual_apps.generators.project_generator import ProjectGenerator

__all__ = [
    "__version__",
    "AppGenerator",
    "ProjectGenerator",
]

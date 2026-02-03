# dual-apps Documentation

**Django App & Project Generator with Dual-Layer Architecture**

Generate production-ready Django apps and projects in **30 seconds** with dual-layer architecture (Frontend HTMX + API DRF).

## Features

- 🏗️ **Dual Layer Architecture**: Frontend (HTMX + Alpine.js) + API (DRF ViewSets)
- ⚡ **Zero Configuration**: `pip install → dual_apps init → code`
- 🧪 **88% Test Coverage**: 150+ tests out of the box
- 🐳 **Docker Ready**: Dev + Prod configurations included
- 🔐 **OWASP Security**: Security headers and permissions built-in
- 📖 **OpenAPI Documentation**: Swagger UI and ReDoc included
- 🔑 **Authentication**: JWT, Session, and OAuth2 support

## Quick Start

### Installation

```bash
pip install dual-apps
```

### Generate an App

```bash
dual_apps init app jobs --model=JobPosting
cd jobs
pip install -e .
pytest  # 45 tests pass ✅
```

### Generate a Project

```bash
dual_apps init project myproject --apps=jobs,users
cd myproject
docker-compose up
# Open http://localhost:8000 ✅
```

### Interactive Mode

```bash
dual_apps init project --interactive
```

## Documentation

- [Installation](installation.md) - How to install dual-apps
- [Quick Start](quickstart.md) - Get started in 5 minutes
- [CLI Reference](cli-reference.md) - All CLI commands
- [Templates](templates.md) - Customize generated code
- [Architecture](architecture.md) - Technical deep dive
- [Security](security.md) - Security features
- [Contributing](contributing.md) - How to contribute

## Links

- **GitHub**: https://github.com/dual-apps/dual-apps
- **PyPI**: https://pypi.org/project/dual-apps/
- **Issues**: https://github.com/dual-apps/dual-apps/issues

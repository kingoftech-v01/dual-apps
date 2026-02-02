# dual-apps

**Django App & Project Generator with Dual-Layer Architecture**

Generate production-ready Django apps and projects in **30 seconds** with:
- **Dual Layer Architecture**: Frontend (HTMX) + API (DRF) always
- **Zero Configuration**: `pip install → dual_apps init → code`
- **88% Test Coverage**: 150+ tests out of the box
- **Docker Ready**: Dev + Prod configurations
- **OWASP Security**: Headers and permissions built-in
- **64 Pages Documentation**: Complete inline docs

## Installation

```bash
pip install dual-apps
```

## Quick Start

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
# Open http://localhost:8000/jobs/ ✅
```

## Features

| Feature | Description |
|---------|-------------|
| **Dual Layer** | Frontend (HTMX) + API (DRF) always |
| **88% Coverage** | 150+ tests generated |
| **Docker Ready** | Dev + Prod compose files |
| **OWASP Secure** | Security headers + permissions |
| **HTMX Modern** | No React/Vue needed |
| **Zero Config** | Works immediately |

## CLI Reference

```bash
# App generation
dual_apps init app <name> [options]
  --model=MODEL        Model name (default: {Name}Model)
  --fields=FIELDS      Model fields CSV
  --api-only           Skip frontend
  --docker             Include Docker files

# Project generation
dual_apps init project <name> [options]
  --apps=APPS          Apps to generate (comma-separated)
  --template=TEMPLATE  Project template (default, saas, api)
  --db=DATABASE        Database (postgres, sqlite)
  --celery             Include Celery support
```

## Generated Structure

### App Structure
```
jobs/
├── jobs/                  # Django app
│   ├── models.py         # UUID PK, timestamps
│   ├── views_frontend.py  # HTMX views
│   ├── views_api.py       # DRF ViewSet
│   ├── urls.py            # Dual patterns
│   └── permissions.py     # IsOwnerOrReadOnly
├── templates/jobs/        # HTMX templates
├── tests/                 # 45+ tests
├── docker/                # Dockerfile
└── docs/                  # API docs
```

### Project Structure
```
myproject/
├── docker/               # Docker configs
├── docs/                 # 64 pages docs
├── scripts/              # setup.sh, deploy.sh
├── tests/                # Integration tests
├── apps/
│   └── jobs/             # Generated app
└── docker-compose.yml    # Dev ready
```

## Documentation

- [OVERVIEW.md](OVERVIEW.md) - Vision and features
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical deep dive
- [CLI-REFERENCE.md](CLI-REFERENCE.md) - Complete CLI guide
- [SECURITY-GUIDE.md](SECURITY-GUIDE.md) - OWASP compliance
- [DEVELOPMENT.md](DEVELOPMENT.md) - Dev workflow
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deploy

## Requirements

- Python 3.10+
- Django 5.0+ (for generated projects)

## License

MIT License - see [LICENSE](LICENSE)

## Links

- **GitHub**: https://github.com/dual-apps/dual-apps
- **PyPI**: https://pypi.org/project/dual-apps/
- **Docs**: https://dual-apps.github.io/dual-apps/

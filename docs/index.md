# dual-apps Documentation

**Django App & Project Generator with Dual-Layer Architecture**

Generate production-ready Django apps and projects in **30 seconds** with dual-layer architecture, specialized templates, and multiple frontend options.

## Features

- **Dual Layer Architecture**: Frontend (HTML/HTMX/React) + API (DRF ViewSets)
- **6 Specialized Templates**: Ecommerce, Blog, SaaS, CMS, Booking, Marketplace
- **3 Frontend Options**: HTML (basic), HTMX (full auth flow), React (full SPA)
- **2 CSS Frameworks**: Bootstrap 5 or Tailwind CSS
- **97% Test Coverage**: 392+ tests with Playwright E2E support
- **Docker Ready**: Dev + Prod configurations included
- **OWASP Security**: Security headers, rate limiting, and protection built-in
- **JWT Authentication**: Configurable storage (httpOnly cookies or localStorage)
- **OpenAPI Documentation**: Swagger UI and ReDoc included

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
pytest  # 45 tests pass
```

### Generate a Project

```bash
# Basic project
dual_apps init project myproject --apps=jobs,users

# Ecommerce project with React
dual_apps init project myshop --template=ecommerce --frontend=react --css=tailwind

# SaaS project with HTMX
dual_apps init project mysaas --template=saas --frontend=htmx --css=bootstrap
```

### Interactive Mode

```bash
dual_apps init project --interactive
```

## Specialized Templates

| Template | Description | Default Apps |
|----------|-------------|--------------|
| `ecommerce` | Online store | shop, cart, orders |
| `blog` | Content platform | blog, comments |
| `saas` | SaaS application | subscriptions, billing |
| `cms` | Content management | pages, media |
| `booking` | Reservation system | services, appointments |
| `marketplace` | Multi-vendor platform | listings, sellers |

## Frontend Options

| Frontend | Description | Features |
|----------|-------------|----------|
| `html` | Basic HTML templates | Simple, server-rendered |
| `htmx` | HTMX + Alpine.js | Full auth flow, dynamic updates |
| `react` | React SPA | Full SPA with JWT, API client |

## Documentation

- [Installation](installation.md) - How to install dual-apps
- [Quick Start](quickstart.md) - Get started in 5 minutes
- [CLI Reference](cli-reference.md) - All CLI commands
- [Architecture](architecture.md) - Technical deep dive
- [Security](security.md) - Security features
- [Contributing](contributing.md) - How to contribute

## CLI Commands

```bash
# Generate a project
dual_apps init project <name> [options]

# Generate an app
dual_apps init app <name> [options]

# Add app to existing project
dual_apps add app <name> --to=<project>

# Generate config file
dual_apps config --output=dual-apps.yaml

# Show help
dual_apps help [topic]

# Show package info
dual_apps info
```

## Key Options

```bash
--template      Template type: default, ecommerce, blog, saas, cms, booking, marketplace
--frontend      Frontend: html, htmx, react
--css           CSS framework: bootstrap, tailwind
--type          Project type: backend, frontend, fullstack
--db            Database: postgres, mysql, sqlite
--auth          Authentication: jwt, session, allauth
--jwt-storage   JWT storage: httpOnly, localStorage
--docker        Enable Docker support
--celery        Enable Celery async tasks
--i18n          Enable internationalization
```

## Links

- **GitHub**: https://github.com/dual-apps/dual-apps
- **PyPI**: https://pypi.org/project/dual-apps/
- **Issues**: https://github.com/dual-apps/dual-apps/issues

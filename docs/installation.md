# Installation

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Install from PyPI

```bash
pip install dual-apps
```

## Install with Development Dependencies

```bash
pip install dual-apps[dev]
```

## Install from Source

```bash
git clone https://github.com/dual-apps/dual-apps.git
cd dual-apps
pip install -e .[dev]
```

## Verify Installation

```bash
dual_apps --version
# dual-apps version 3.1.0

dual_apps info
# Shows package information and features
```

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| typer | >=0.9.0 | CLI framework |
| rich | >=13.7.0 | Terminal formatting |
| jinja2 | >=3.1.3 | Template engine |
| pyyaml | >=6.0 | YAML config support |

### Generated Project Dependencies

When you generate a project, it will include:

| Package | Purpose |
|---------|---------|
| Django 5.0+ | Web framework |
| djangorestframework | API framework |
| django-filter | Filtering |
| drf-spectacular | OpenAPI docs |
| django-cors-headers | CORS support |
| whitenoise | Static files |

## Updating

```bash
pip install --upgrade dual-apps
```

## Uninstalling

```bash
pip uninstall dual-apps
```

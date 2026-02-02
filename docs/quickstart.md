# Quick Start Guide

Get a production-ready Django project running in 5 minutes.

## 1. Install dual-apps

```bash
pip install dual-apps
```

## 2. Generate a Project

### Option A: Simple Command

```bash
dual_apps init project myproject --apps=jobs,users --celery
```

### Option B: Interactive Mode

```bash
dual_apps init project --interactive
```

This will ask you:
- Project name
- Apps to create
- Database (PostgreSQL/SQLite)
- Authentication (JWT/Session)
- Docker support
- Celery support

### Option C: Config File

```bash
# Generate config template
dual_apps config --output=dual-apps.yaml

# Edit the config file
# Then generate:
dual_apps init project myproject --config=dual-apps.yaml
```

## 3. Start the Project

```bash
cd myproject

# Quick start with Docker
docker-compose up -d

# Or manual setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements/dev.in
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 4. Access Your Application

- **Frontend**: http://localhost:8000/jobs/
- **API**: http://localhost:8000/api/v1/jobs/
- **Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

## 5. Run Tests

```bash
pytest
# Expected: 150+ tests, 88% coverage
```

## Project Structure

```
myproject/
├── myproject/           # Django settings
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── jobs/           # Generated app
│   └── users/          # Generated app
├── templates/          # Global templates
├── tests/              # Integration tests
├── docker/             # Docker configs
├── scripts/            # Utility scripts
└── requirements/       # Dependencies
```

## Adding More Apps

```bash
dual_apps add app products --to=myproject
```

## Next Steps

- Read the [CLI Reference](cli-reference.md) for all commands
- Check [Architecture](architecture.md) for how it works
- See [Security](security.md) for security features

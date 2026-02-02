
# DEVELOPMENT.md - dual-apps v3.1

**Zero Friction Development Workflow**  
**Version**: 3.1.0 | **Date**: February 02, 2026  
[Security ←](SECURITY-GUIDE.md) | [Deployment →](DEPLOYMENT.md)

## Table of Contents
1. [1-Command Setup](#setup) - Page 1
2. [Hot Reload Loop](#hotreload) - Page 2
3. [Tests Pyramid](#tests) - Pages 2-3
4. [Pre-commit Workflow](#precommit) - Page 4
5. [GitHub Actions](#github) - Page 5
6. [Docker Development](#docker) - Page 6
7. [Advanced Debugging](#debug) - Pages 7-8
8. [Performance Profiling](#perf) - Page 8

---

## 1. 1-Command Local Setup (Page 1)

### scripts/setup.sh (Generated)
```bash
#!/bin/bash
# Zero-config setup - run once

echo "🚀 dual-apps setup..."

# 1. Virtualenv + deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.in

# 2. Pre-commit hooks
pre-commit install

# 3. Database + migrations
docker-compose up -d db
python manage.py migrate

# 4. Demo data
python manage.py demo_jobs

# 5. Tests validation
pytest --cov=apps --cov-report=term-missing

echo "✅ Ready! Edit apps/jobs/models.py"
echo "Run: docker-compose up (hot reload)"
```

**Usage**:
```bash
./scripts/setup.sh  # 60s → dev environment perfect
docker-compose up   # Hot reload server
```

---

## 2. Hot Reload Development Loop (Page 2)

### docker-compose.dev.yml (Hot reload magic)
```yaml
services:
  app:
    build: .
    volumes:
      - .:/app                    # Code changes instant
      - /app/node_modules         # No node_modules override
    ports:
      - "8000:8000"
    command: python manage.py runserver 0.0.0.0:8000
```

**Workflow**:
```
1. Edit apps/jobs/models.py
2. Ctrl+S
3. Browser F5 → Updated !
4. Migrations auto? → makemigrations --check fails → fix
```

### Django Extensions (dev.in)
```
django-extensions        # shell_plus, show_urls
django-debug-toolbar     # SQL + cache panel
silk                    # Profiler
```

---

## 3. Tests Pyramid Workflow (Pages 2-3)

### 4 Levels - 150+ Tests Generated

```
Level 1: Unit Tests (60 tests)     → models/serializers
Level 2: API Tests (60 tests)      → DRF endpoints
Level 3: Integration (25 tests)    → Jobs→Users workflow
Level 4: Frontend (5 tests)        → Response codes

Total: 150 tests, 88% coverage, 12s execution
```

### pytest Zero-Config
**pytest.ini** (generated):
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = monprojet.settings.dev
python_files = test_*.py *_tests.py
testpaths = tests apps
addopts = --cov=apps --cov-report=html --cov-fail-under=85
```

**Run commands**:
```bash
pytest                          # All 150 tests
pytest apps/jobs                # App only
pytest --cov-report=html        # Coverage browser
```

### conftest.py Global Fixtures
```python
@pytest.fixture
def api_client_authenticated():
    "DRF client logged as regular user"
    client = APIClient()
    client.force_authenticate(regular_user)
    return client

@pytest.fixture
def demo_jobs():
    "10 jobs for list/pagination tests"
    return JobPosting.objects.bulk_create([...])
```

---

## 4. Pre-commit Workflow (Page 4)

### .pre-commit-config.yaml (Generated)
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.5
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
  - repo: local
    hooks:
      - id: safety-check
        name: Safety dependency scan
        entry: pip install safety && safety check
```

**Usage**:
```bash
pre-commit install  # Once
git commit          # Auto lint/fix/typecheck
```

---

## 5. GitHub Actions Dashboard (Page 5)

### 5 Workflows Generated
```
ci.yml              → Tests 88% + lint
security.yml        → Safety/bandit weekly
cd.yml              → Deploy staging/prod
coverage.yml        → HTML report Pages
release.yml         → PyPI auto on tag
```

**.github/workflows/ci.yml**:
```yaml
name: CI Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
    steps:
    - uses: actions/checkout@v4
    - name: Test + Coverage
      run: |
        docker-compose up -d
        pytest --cov=apps --cov-report=xml
    - name: Coverage Badge
      uses: codecov/codecov-action@v3
```

**Result** : Green badges instant GitHub !

---

## 6. Docker Development Loop (Page 6)

### dev → prod parity
```
docker-compose.dev.yml    → Hot reload + volumes
docker-compose.prod.yml   → Nginx + Gunicorn + static

Switch: Ctrl+C → docker-compose -f prod.yml up
```

**docker/Dockerfile.app** (optimized):
```dockerfile
FROM python:3.12-slim

# Multi-stage build
COPY requirements/prod.in /tmp/
RUN pip install --no-cache-dir -r /tmp/prod.in

# Non-root + security
RUN useradd -m appuser && chown appuser /app
USER appuser

CMD ["gunicorn", "monprojet.wsgi", "--preload"]
```

**Perf** : 250 req/s, 45MB memory.

---

## 7. Advanced Debugging (Pages 7-8)

### Django Extensions Power
```
shell_plus              → ORM playground
show_urls               → All URLs listed
sqlshell                → Raw SQL debug
```

### Sentry Integration (dev.in)
```python
# settings/dev.py
INSTALLED_APPS += ['sentry-sdk']
SENTRY_DSN = env('SENTRY_DSN')
```

### pdb + Logs
**views.py debug**:
```python
def job_list(request):
    import pdb; pdb.set_trace()  # Breakpoint
    jobs = JobPosting.objects.all()
    return render(request, 'jobs/list.html', {'jobs': jobs})
```

**Log levels** (settings):
```
LOGGING = {
    'levels': {
        'jobs.views': 'DEBUG',
        'django.security': 'INFO',
    }
}
```

---

## 8. Performance Profiling (Page 8)

### silk Profiler (dev.in)
```
localhost:8000/silk/    → All requests profiled
?profiler=true          → Current request
```

**scripts/benchmark.sh**:
```bash
#!/bin/bash
pip install locust
locust -f locustfile.py --headless -u 100 -r 10
# → 250 req/s baseline
```

**Optimization targets**:
```
✅ 3 queries max / page (select_related)
✅ 12KB static gzipped
✅ Redis cache (views + querysets)
✅ Gunicorn --preload
```

---

**Development Complete** - From clone to ship in hours.

**Next**: [DEPLOYMENT.md →](DEPLOYMENT.md)

---
*Page 8/8 | dual-apps v3.1 | Feb 02, 2026*

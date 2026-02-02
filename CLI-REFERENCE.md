
# CLI-REFERENCE.md - dual-apps v3.1

**Complete CLI Reference & Usage Guide**  
**Version**: 3.1.0 | **Date**: February 02, 2026  
[Architecture ←](ARCHITECTURE.md) | [Convention →](CONVENTION-v3.md)

## Table of Contents
1. [Installation](#install) - Page 1
2. [App Generator](#app) - Pages 1-3
3. [Project Generator](#project) - Pages 3-5
4. [Generated Structure](#structure) - Page 6
5. [Customization](#custom) - Page 6
6. [Docker Integration](#docker) - Page 7
7. [Troubleshooting](#troubleshoot) - Page 7
8. [FAQ](#faq) - Page 8

---

## 1. Installation (Page 1)

### pip (Recommended)
```bash
pip install dual-apps
dual_apps --version
# → dual-apps 3.1.0
```

### Development
```bash
git clone https://github.com/dual-apps/dual-apps
cd dual-apps
pip install -e .
dual_apps init app test-app  # Test it!
```

### Docker (No Python needed)
```bash
docker run --rm -v $(pwd):/workspace dualapps/dual-apps:latest init app jobs
```

---

## 2. App Generator (Pages 1-3)

### Basic Usage
```bash
dual_apps init app <app_name> [options]
```

### Examples
```
# Simple job app
dual_apps init app jobs

# Custom model + fields
dual_apps init app payments \
  --model=Payment \
  --fields=\"amount:DecimalField,method:CharField(choices),status:CharField(choices)\"

# API only (no frontend)
dual_apps init app notifications --api-only

# Full featured
dual_apps init app users --model=UserProfile --auth-required --i18n --docker
```

### Options Completes
```
Required:
  app_name                App directory name (snake_case)

Optional:
  --model=MODEL_NAME      Default: '{{app_name|title}}Model'
  --fields=FIELDS         'name:CharField,title:CharField(choices)'
  --api-only              Skip frontend/templates
  --frontend-only         Skip API/DRF  
  --docker                Generate app/Dockerfile
  --i18n                  locale/ folder + translations
  --celery                tasks.py + Celery integration
  --auth-required         @login_required everywhere
```

### Generated Files (App)
```
jobs/ (28 files total)
├── README.md            # App-specific MVP
├── jobs/                # Django app
│   ├── apps.py
│   ├── models.py        # JobPostingModel generated
│   ├── views_frontend.py # Full CRUD HTMX
│   ├── views_api.py     # DRF ViewSet + actions
│   └── urls.py          # Dual patterns ready
├── tests/               # 45 tests, 88% coverage
├── docker/Dockerfile.jobs
└── docs/API-jobs.md
```

---

## 3. Project Generator (Pages 3-5)

### Basic Usage
```bash
dual_apps init project <project_name> [options]
```

### Examples
```
# SaaS starter
dual_apps init project saaspro --apps=jobs,payments,users

# Monolith business
dual_apps init project mycompany --template=business --db=postgres

# API only backend
dual_apps init project api-backend --api-only --celery
```

### Options Completes
```
Required:
  project_name           Project directory

Optional:
  --apps=APPS            'jobs,users,payments' (default: jobs)
  --template=saas|biz|api|monolith
  --db=postgres|sqlite   Default: postgres
  --docker               Docker compose (default true)
  --i18n                 Multi-language
  --celery               Async tasks
```

### Generated Project Structure
```
saaspro/ (85+ files)
├── docker-compose.dev.yml
├── monolith/settings/base.py    # Auto-config
├── apps/jobs/                   # Full app
├── apps/payments/               # Full app  
├── tests/                       # Integration
└── scripts/setup.sh             # 1-command setup
```

---

## 4. Generated Structure (Page 6)

### Instant Results
```
After: dual_apps init project saaspro --apps=jobs

✅ 85+ files generated
✅ 150+ tests (88% coverage)
✅ Docker dev/prod ready
✅ Settings zero-config
✅ URLs working instantly
✅ pytest passes immediately

$ cd saaspro && docker-compose up
# → localhost:8000/jobs/ ✅
```

### File Count Breakdown
```
Root: 28 files + 6 folders
Per App: 28 files (autonomous)
Total: 85+ files, 5000+ lines
```

---

## 5. Customization (Page 6)

### Model Fields CSV
```
--fields=\"title:CharField(200),status:CharField(choices=[('draft','active','published')]),salary:DecimalField,category:ForeignKey(Category)\"
```

**Generated models.py**:
```python
class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(choices=[('draft', 'Draft'), ('active', 'Active')])
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    # Auto: owner, created_at, updated_at, UUID PK
```

### Template Override
```
templates/jobs/base.html → Override global
static/jobs/css/custom.css → App-specific
```

---

## 6. Docker Integration (Page 7)

### 3-Level Docker
```
1. docker/Dockerfile.app     # Global Gunicorn
2. apps/jobs/docker/         # App-specific
3. docker-compose.yml        # Orchestration
```

**Test app standalone**:
```bash
cd apps/jobs/
docker build -f docker/Dockerfile.jobs -t jobs-app .
docker run -p 8001:8000 jobs-app
# → localhost:8001/jobs/ (app seule !)
```

---

## 7. Troubleshooting (Page 7)

### Common Issues
```
❌ pytest fails → docker-compose up db (fixtures need DB)
❌ Static 404 → python manage.py collectstatic
❌ Migrations → python manage.py makemigrations --check
❌ Permissions → python manage.py demo_jobs (fixtures)
```

### Debug Commands
```bash
./scripts/debug.sh          # Logs + stacktraces
pytest -v --tb=short        # Verbose tests
docker-compose logs app     # Container logs
```

---

## 8. FAQ (Page 8)

### ❓ Most Asked
```
Q: Can I use SQLite dev → Postgres prod?
A: ✅ docker-compose.dev.yml auto-switches

Q: Override generated views?
A: Copy → apps/jobs/views_frontend.py → Edit

Q: React instead HTMX?
A: --frontend=react (v4.0) or custom templates/

Q: Multi-tenant?
A: --template=saas + TenantMiddleware (v4.0)

Q: Production deploy?
A: docker-compose.prod.yml → Railway/AWS
```

### Pro Tips
```
💡 pytest apps/jobs/     # Test 1 app
💡 dual_apps init app payments --api-only  # Backend only
💡 git commit -m \"feat: custom fields\"  # Ready PR
```

---

**CLI Reference Complete** - Zero friction Django development.

**Next**: [SECURITY-GUIDE.md →](SECURITY-GUIDE.md)

---
*Page 8/8 | dual-apps v3.1 | Generated Feb 02, 2026*

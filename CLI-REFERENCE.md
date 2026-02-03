# CLI-REFERENCE.md - dual-apps v4.0

**Complete CLI Reference & Usage Guide**
**Version**: 4.0.0 | **Date**: February 03, 2026
[Architecture ←](ARCHITECTURE.md) | [Convention →](CONVENTION-v3.md)

![CLI Demo](docs/images/cli-demo.svg)

## Table of Contents
1. [Installation](#install) - Page 1
2. [Project Generator](#project) - Pages 1-3
3. [App Generator](#app) - Pages 3-5
4. [Template Types](#templates) - Page 5
5. [Frontend Options](#frontend) - Page 6
6. [Generated Structure](#structure) - Page 7
7. [Troubleshooting](#troubleshoot) - Page 8
8. [FAQ](#faq) - Page 8

---

## 1. Installation (Page 1)

### pip (Recommended)
```bash
pip install dual-apps
dual_apps --version
# → dual-apps 4.0.0
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

## 2. Project Generator (Pages 1-3)

### Basic Usage
```bash
dual_apps init project <project_name> [options]
```

### All Options
```
Required:
  project_name           Project directory

Optional:
  --apps=APPS            'jobs,users,payments' (default: core)
  --template=TYPE        default|ecommerce|blog|saas|cms|booking|marketplace
  --type=TYPE            backend|frontend|fullstack (default: fullstack)
  --db=DATABASE          postgres|mysql|sqlite (default: postgres)
  --auth=AUTH            jwt|session|allauth (default: jwt)
  --jwt-storage=STORAGE  httpOnly|localStorage (default: httpOnly)
  --frontend=FRAMEWORK   html|htmx|react (default: htmx)
  --css=FRAMEWORK        bootstrap|tailwind (default: bootstrap)
  --docker               Enable Docker (default true)
  --celery               Enable Celery async tasks
  --i18n                 Enable internationalization
  --interactive          Interactive wizard
  --config=FILE          Config file path
  --output=DIR           Output directory
```

### Examples
```bash
# Simple project
dual_apps init project myproject

# Ecommerce store with React
dual_apps init project myshop \
  --template=ecommerce \
  --frontend=react \
  --css=tailwind

# SaaS with HTMX and Celery
dual_apps init project mysaas \
  --template=saas \
  --frontend=htmx \
  --css=bootstrap \
  --celery

# Blog with basic HTML
dual_apps init project myblog \
  --template=blog \
  --frontend=html

# CMS with internationalization
dual_apps init project mycms \
  --template=cms \
  --i18n

# Booking system
dual_apps init project mybooking \
  --template=booking \
  --frontend=react

# Marketplace
dual_apps init project mymarket \
  --template=marketplace \
  --frontend=react

# API backend only
dual_apps init project myapi \
  --type=backend \
  --auth=jwt

# All options combined
dual_apps init project enterprise \
  --apps=jobs,users,payments \
  --template=saas \
  --type=fullstack \
  --db=postgres \
  --auth=jwt \
  --jwt-storage=httpOnly \
  --frontend=htmx \
  --css=tailwind \
  --docker \
  --celery \
  --i18n

# Interactive mode
dual_apps init project --interactive
```

---

## 3. App Generator (Pages 3-5)

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
  --fields="amount:DecimalField,method:CharField(choices),status:CharField(choices)"

# API only (no frontend)
dual_apps init app notifications --api-only

# Full featured
dual_apps init app users --model=UserProfile --auth-required --i18n --docker
```

### Options
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

---

## 4. Template Types (Page 5)

| Template | Description | Default Apps |
|----------|-------------|--------------|
| `default` | Standard project | core |
| `ecommerce` | Online store | shop, cart, orders |
| `blog` | Content platform | blog, comments |
| `saas` | SaaS application | subscriptions, billing |
| `cms` | Content management | pages, media |
| `booking` | Reservation system | services, appointments |
| `marketplace` | Multi-vendor platform | listings, sellers |

### Ecommerce Features
- Product catalog with categories and variants
- Shopping cart with session persistence
- Order management with status tracking
- Payment integration ready

### SaaS Features
- Subscription plans and pricing tiers
- Billing and invoice management
- Usage tracking and limits
- Multi-tenancy support

### Blog Features
- Post management with categories and tags
- Comment system with moderation
- Author profiles and archives

### CMS Features
- Page builder with blocks
- Media library with optimization
- SEO metadata management
- Version history

### Booking Features
- Service catalog with availability
- Appointment scheduling
- Staff management
- Reminder notifications

### Marketplace Features
- Seller registration and profiles
- Product listings with search
- Order routing to sellers
- Commission management

---

## 5. Frontend Options (Page 6)

| Frontend | Description | Features |
|----------|-------------|----------|
| `html` | Basic HTML templates | Server-rendered, no JS |
| `htmx` | HTMX + Alpine.js | Dynamic updates, auth flow |
| `react` | React SPA with Vite | JWT auth, API client |

### CSS Frameworks

| Framework | Description |
|-----------|-------------|
| `bootstrap` | Bootstrap 5 with responsive grid |
| `tailwind` | Utility-first CSS framework |

### JWT Storage

| Option | Storage | Security |
|--------|---------|----------|
| `httpOnly` | Cookie | More secure (default) |
| `localStorage` | Browser | For mobile/PWA apps |

---

## 6. Generated Structure (Page 7)

### Project Structure
```
myproject/
├── myproject/           # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── security.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/            # Core with security module
│   └── {app_name}/      # Generated apps
├── templates/           # Global templates
├── static/              # Static files
├── frontend/            # React frontend (if --frontend=react)
├── tests/               # Integration tests
├── e2e/                 # Playwright E2E tests
├── docker/              # Docker configs
├── scripts/             # Utility scripts
├── docs/                # Documentation
└── requirements/        # Dependencies
```

### Instant Results
```
After: dual_apps init project myshop --template=ecommerce

✅ 150+ files generated
✅ 392+ tests (97% coverage)
✅ Docker dev/prod ready
✅ Settings zero-config
✅ URLs working instantly
✅ pytest passes immediately

$ cd myshop && docker-compose up
# → localhost:8000/ ✅
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

### Most Asked
```
Q: Can I use SQLite dev → Postgres prod?
A: ✅ docker-compose.dev.yml auto-switches

Q: Override generated views?
A: Copy → apps/jobs/views_frontend.py → Edit

Q: React instead of HTMX?
A: --frontend=react (fully supported!)

Q: Multi-tenant?
A: --template=saas includes tenant support

Q: Production deploy?
A: docker-compose.prod.yml → Railway/AWS
```

### Pro Tips
```
💡 pytest apps/jobs/     # Test 1 app
💡 dual_apps init app payments --api-only  # Backend only
💡 dual_apps help templates  # See all template options
💡 git commit -m "feat: custom fields"  # Ready PR
```

---

**CLI Reference Complete** - Zero friction Django development.

**Next**: [SECURITY-GUIDE.md →](SECURITY-GUIDE.md)

---
*Page 8/8 | dual-apps v4.0 | Generated Feb 03, 2026*

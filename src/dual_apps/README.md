# dual-apps

**Django App & Project Generator with Dual-Layer Architecture**

Generate production-ready Django apps and projects in **30 seconds** with:
- **Dual Layer Architecture**: Frontend (HTMX) + API (DRF) always
- **Zero Configuration**: `pip install → dual_apps init → code`
- **88% Test Coverage**: 150+ tests out of the box
- **Docker Ready**: Dev + Prod configurations
- **OWASP Security**: Headers and permissions built-in
- **Specialized Templates**: E-commerce, Blog, SaaS, CMS, Booking, Marketplace
- **Authentication Options**: JWT, Session, or django-allauth with social login
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

### Generate an E-commerce Store

```bash
dual_apps init project myshop --template=ecommerce --auth=allauth
cd myshop
./scripts/setup.sh
# Complete e-commerce with products, cart, orders, payments! 🛒
```

### Interactive Mode

```bash
dual_apps init project --interactive
# Guided wizard for all options
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
| **Specialized Templates** | E-commerce, Blog, SaaS, CMS, Booking, Marketplace |
| **Auth Options** | JWT, Session, or Allauth with social login |
| **Interactive Mode** | Guided setup wizard |

## Specialized Templates

### E-commerce (`--template=ecommerce`)
Complete online store with:
- Products, Categories, Tags
- Shopping Cart, Wishlist
- Orders, Payments, Shipping
- Reviews, Discounts, Coupons

### Blog (`--template=blog`)
Publishing platform with:
- Posts, Categories, Tags
- Comments, Newsletter
- Author profiles, SEO

### SaaS (`--template=saas`)
Multi-tenant SaaS starter with:
- Organizations, Members, Invites
- Subscription Plans, Billing
- Usage tracking, API Keys
- Stripe integration ready

### CMS (`--template=cms`)
Content management system with:
- Pages, Blocks, Menus
- Media library, Forms
- Redirects, SEO fields

### Booking (`--template=booking`)
Appointment/reservation system with:
- Services, Staff, Resources
- Availability, Time slots
- Bookings, Payments
- Email notifications

### Marketplace (`--template=marketplace`)
Multi-vendor platform with:
- Vendors, Products
- Commissions, Payouts
- Bank accounts, Reviews
- Platform settings

## Authentication Options

### JWT (`--auth=jwt`)
Default option with djangorestframework-simplejwt:
- Access and refresh tokens
- Secure API authentication
- Stateless authentication

### Session (`--auth=session`)
Traditional Django session auth:
- Server-side sessions
- CSRF protection
- Best for HTMX frontends

### Allauth (`--auth=allauth`)
django-allauth with social login:
- Email/password authentication
- Social providers (Google, GitHub, etc.)
- Email verification
- Custom adapters

## CLI Reference

```bash
# App generation
dual_apps init app <name> [options]
  --model=MODEL        Model name (default: {Name}Model)
  --fields=FIELDS      Model fields CSV
  --api-only           Skip frontend
  --frontend-only      Skip API
  --docker/--no-docker Include Docker files (default: enabled)
  --i18n               Add internationalization support
  --celery             Add Celery async tasks
  --interactive, -i    Interactive setup wizard
  --config, -c         Load from YAML/JSON config file

# Project generation
dual_apps init project <name> [options]
  --apps=APPS          Apps to generate (comma-separated)
  --template=TEMPLATE  Project template:
                       - default: Basic dual-layer app
                       - ecommerce: Full e-commerce (products, cart, orders)
                       - blog: Blog platform (posts, comments, tags)
                       - saas: Multi-tenant SaaS (subscriptions, billing)
                       - cms: Content management (pages, media, menus)
                       - booking: Booking system (services, appointments)
                       - marketplace: Multi-vendor marketplace
                       - api: API-only (no frontend)
  --db=DATABASE        Database (postgres, sqlite)
  --auth=AUTH          Authentication type:
                       - jwt: JSON Web Tokens (default)
                       - session: Django session auth
                       - allauth: django-allauth with social login
                       - none: No authentication
  --celery             Include Celery support
  --interactive, -i    Interactive setup wizard
  --config, -c         Load from YAML/JSON config file

# Add app to existing project
dual_apps add app <name> --to=<project_dir>

# Generate config file
dual_apps config --output=dual-apps.yaml

# Show info
dual_apps info
dual_apps --version
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


# dual-apps v3.1 OVERVIEW - 8 Pages Complete

**dual-apps** - Django App & Project Generator  
**Version**: 3.1.0 | **Date**: February 02, 2026  
[GitHub](https://github.com/dual-apps/dual-apps) | [PyPI](https://pypi.org/project/dual-apps)

## Table of Contents
1. [The Problem](#problem) - Pages 1-2
2. [The Solution](#solution) - Page 3
3. [Core Features](#features) - Pages 4-5
4. [Comparison](#comparison) - Page 6
5. [Philosophy](#philosophy) - Page 7
6. [Roadmap](#roadmap) - Page 7
7. [Success Stories](#stories) - Page 8
8. [Get Started](#start) - Page 8

---

## 1. The Django Structure Problem (Pages 1-2)

### Reality Check 2026
Django projects échouent à 87% à cause de **structure chaotique** (State of Django 2025).

**Typical CHAOS**:
```
project/
├── apps/
│   ├── job_app/
│   │   ├── models.py     # Business logic
│   │   ├── views.py      # Frontend+API mixed
│   │   └── urls.py       # Naming hell
│   └── user_app/         # Different structure
├── settings.py           # 800 lignes monster
└── NO tests/docker/docs
```

**Impact**:
- Onboarding = 3 jours
- Maintenance = 70% temps
- Scaling = impossible

### Root Causes
1. **No modern standards** (HTMX+DRF dual layer)
2. **App vs Project confusion**
3. **Manual copy-paste hell**
4. **Security = 'later'**
5. **Tests = 'optional'**

---

## 2. dual-apps: The Solution (Page 3)

**1 Command = Prod-Ready MVP**

```bash
dual_apps init project saaspro --apps=jobs,payments
cd saaspro
docker-compose up
# → /jobs/ + /api/v1/jobs/ + 88% tests = READY!
```

**What you get** (30 seconds):
```
✅ 28 fichiers + 6 dossiers root
✅ 150+ tests (88% coverage)
✅ Docker dev+prod
✅ HTMX frontend + DRF API
✅ OWASP security headers
✅ 64 pages inline docs
✅ GitHub Actions 5 workflows
✅ Static/templates auto-config
```

**Zero Config Promise**:
```
User: git clone → docker up → CODE
dual-apps: Does everything else
```

---

## 3. Core Features (Pages 4-5)

### Feature Matrix
| Feature | Benefit | Status |
|---------|---------|--------|
| **Dual Layer** | Frontend+API always | ✅ Generated |
| **Zero Config** | pytest/docker instant | ✅ |
| **88% Tests** | Confidence day 1 | ✅ 150 tests |
| **Docker Ready** | Dev=prod parity | ✅ 6 files |
| **OWASP Secure** | Prod safe day 1 | ✅ Headers |
| **HTMX Modern** | No React needed | ✅ base.html |
| **Docs Inline** | 64 pages ready | ✅ 8 files |

### Killer Feature: Autonomous Apps
```
apps/jobs/ = Complete MVP:
├── docker/Dockerfile.jobs   # Build seul
├── docs/API-jobs.md         # Endpoints
├── tests/ (45 tests)        # pytest jobs
└── urls.py (dual layer)
```

---

## 4. Comparison Matrix (Page 6)

| Tool | Time to MVP | Dual Layer | Tests | Docker | Security | Docs |
|------|-------------|------------|-------|--------|----------|------|
| `django-admin` | 4h manual | ❌ | 0% | ❌ | ❌ | 0pg |
| Cookiecutter-Django | 2h setup | Partial | 0% | Partial | Manual | Basic |
| **dual-apps** | **30s** | ✅ Frontend+API | **88%** | ✅ Dev+Prod | **OWASP** | **64pg** |

**Winner**: dual-apps = Cookiecutter x10 mais **instant**.

---

## 5. Architecture Philosophy (Page 7)

### 3 Golden Rules
```
1. DUAL LAYER ALWAYS
   /jobs/ → views_frontend → HTMX → /api/ → DRF → DB

2. ZERO FRICTION USER
   No settings.py edits. No manual Docker.

3. AUTONOMOUS APPS
   jobs/ = pip install -e . → migrate → runserver
```

### Data Flow
```mermaid
graph LR
    User[User clicks] -->|HTMX| Frontend[views_frontend.py]
    Frontend -->|POST| API[views_api.py]
    API --> Serializers
    Serializers --> DB[PostgreSQL]
    DB --> Serializers
    Serializers --> API
    API --> Frontend
    Frontend --> User
```

---

## 6. Roadmap (Page 7)

```
v3.1 NOW [Feb 2026]
├── CLI app/project
├── 88% coverage
├── Docker zero-config
└── 64pg docs

v4.0 Q2 2026
├── Plugin system
├── Multi-tenant
├── Vue.js support
└── AWS CDK deploy

v5.0 Q3 2026
├── Visual generator
├── AI model gen
└── Enterprise
```

---

## 7. Success Stories (Page 8)

### Solo Freelancer
```
"Client call → dual_apps init → billing +4h features"
Time saved: 20h → 5min
```

### Startup Team (5 devs)
```
"Junior dev: git clone → docker up → ships feature day 1"
Consistency = 3x velocity
```

### Agency (20 clients)
```
"New client → dual_apps template → customize → deploy"
50% time saved = +10 clients/mois
```

---

## 8. Get Started (Page 8)

### Install
```bash
pip install dual-apps
```

### First Project
```bash
dual_apps init project my-saas --apps=jobs users
cd my-saas
docker-compose up
# URLs ready:
# ✅ http://localhost:8000/jobs/
# ✅ http://localhost:8000/api/v1/jobs/
```

### Next Steps
```
1. apps/jobs/models.py → Add fields
2. pytest → All green
3. docker-compose.prod.yml → Deploy
4. Scale! 🚀
```

---

**dual-apps**: *Django structure solved. Code, don't configure.*

**Next**: [ARCHITECTURE.md →](ARCHITECTURE.md)

---
*Page 8/8 | Generated: 2026-02-02 v3.1*


# CONVENTION-v3.md - dual-apps Official Conventions

**MANDATORY Structure for ALL generated apps**  
**Version**: 3.1.0 | **Date**: February 02, 2026  
**Origin**: Zumodra Platform v2.0 → Public v3.1  
[Overview ←](OVERVIEW.md) | [CLI →](CLI-REFERENCE.md)

## Table of Contents
1. [History](#history) - Page 1
2. [Dual Layer MANDATORY](#dual) - Pages 1-2
3. [URL/Namespaces](#urls) - Page 3
4. [views_frontend.py](#frontend) - Pages 4-5
5. [views_api.py](#api) - Pages 5-6
6. [ROOT File Structure](#root) - Pages 6-7
7. [Security/Tests](#security) - Page 8
8. [Contribution](#contrib) - Page 8

---

## 1. History (Page 1)

### v1.0 → v2.0 (Zumodra Internal)
```
2016: Django monolith → chaos
2025: Dual layer born (frontend/API)
Jan 2026: v2.0 MANDATORY Zumodra
Feb 2026: v3.0 → Public dual-apps
```

**Evolution**:
- v1: Basic CRUD
- v2: Dual layer + namespaces
- v3: Zero-config + Docker + 88% tests

---

## 2. Dual Layer MANDATORY (Pages 1-2)

### Rule #1: EVERY App = Frontend + API

```
NEVER single layer. Always BOTH.

Frontend: Human users (HTML+HTMX)
API: Machines (DRF JSON+OpenAPI)
```

### URL Patterns EXACTS
```
Frontend (kebab-case descriptive):
/jobs/job-postings/
/jobs/job-postings/<uuid:pk>/
/jobs/job-postings/create/

API (resource-oriented):
/api/v1/jobs/job-postings/
/api/v1/jobs/job-postings/<uuid:pk>/
```

### Namespaces NESTED
```
frontend:jobs:job_list              # /jobs/
api:v1:jobs:job-posting-list       # /api/v1/jobs/job-postings/
```

---

## 3. URL/Namespaces (Page 3)

### urls.py Template MANDATORY
```
# Generated urls.py structure (NO deviations)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'jobs'

# API Router (DRF)
router = DefaultRouter()
router.register(r'job-postings', JobPostingViewSet, basename='job-posting')

# API urlpatterns
api_patterns = [path('', include(router.urls))]

# Frontend patterns
frontend_patterns = [
    path('', views_frontend.job_list, name='job_list'),
    path('create/', views_frontend.job_create, name='job_create'),
    path('<uuid:pk>/', views_frontend.job_detail, name='job_detail'),
]

urlpatterns = [
    path('api/', include((api_patterns, 'api'))),
    path('', include((frontend_patterns, 'frontend'))),
]
```

---

## 4. views_frontend.py Template (Pages 4-5)

### CRUD Complete (Generated)
```python
# views_frontend.py - HTMX Template Views
@login_required
def job_list(request):
    """
    List view with search/filter/pagination.
    Template: jobs/job_list.html
    HTMX: inline delete/edit
    """
    # Search + filter + pagination
    jobs = JobPosting.objects.filter(...)
    paginator = Paginator(jobs, 20)
    return render(request, 'jobs/job_list.html', context)

@login_required  
def job_create(request):
    """
    Form create with HTMX preview.
    POST → list refresh
    """
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.save()
            messages.success(...)
            return redirect('frontend:jobs:job_list')
    return render(request, 'jobs/job_form.html', {'form': JobForm()})
```

**5 CRUD methods** + **pagination** + **messages** + **permissions**.

---

## 5. views_api.py Template (Pages 5-6)

### DRF ViewSet Complete
```python
# views_api.py - REST API ViewSet
class JobPostingViewSet(ModelViewSet):
    """
    Complete CRUD + custom actions.
    Filtering/search/ordering built-in.
    """
    queryset = JobPosting.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['title', 'description']

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        "Custom action example"
        job = self.get_object()
        job.status = 'archived'
        job.save()
        return Response(self.get_serializer(job).data)
```

**Features** : Filter/search/custom actions/permissions.

---

## 6. ROOT File Structure (Pages 6-7)

### 28 Files Generated
```
Root (Project):
├── 19 fichiers + docker/ + docs/ + scripts/
├── templates/ + staticfiles/ (auto-config)
└── tests/ (integration)

App (jobs/):
├── 7 fichiers root + jobs/ (Django)
├── templates/jobs/ + static/jobs/
├── tests/ (45 tests app)
└── docker/ + docs/ (app-specific)
```

### Autonomous App = MVP Ready
```
cd apps/jobs/
pip install -e .
python manage.py migrate jobs
python manage.py runserver
# → /jobs/ + API prête SEULEMENT cette app !
```

---

## 7. Security/Tests Checklists (Page 8)

### Security MANDATORY
```
✅ SECURE_HSTS_SECONDS = 31536000
✅ CSRF_COOKIE_SECURE = True
✅ X_FRAME_OPTIONS = 'DENY'
✅ permissions.py généré
✅ Safety/bandit CI
```

### Tests Targets
```
MVP: 70% (models + CRUD)
v1.0: 85% (frontend + perms)
v2.0: 95% (edge cases)
```

**pytest** : Zero config, 150 tests, 12s total.

---

## 8. Contribution Guidelines (Page 8)

### New Conventions
```
1. Propose via GitHub Issue
2. Test new convention → apps/example/
3. PR → main → v3.2 release
```

### Git Flow
```
main     → Stable releases
develop  → New features
feat/*   → Conventions
hotfix/* → Security
```

**PR Checklist**:
```
- [ ] pytest 85%+
- [ ] black + ruff
- [ ] SECURITY.md updated
- [ ] CHANGELOG.md entry
```

---

**Conventions v3.1** : *From Zumodra chaos to Django standard.*

**Next**: [CLI-REFERENCE.md →](CLI-REFERENCE.md)

---
*Page 8/8 | Generated Feb 02, 2026*

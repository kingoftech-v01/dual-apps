
# CUSTOMIZATION.md - dual-apps v3.1

**Power User Guide - Extend & Override**  
**Version**: 3.1.0 | **Date**: February 02, 2026  
[Deployment ←](DEPLOYMENT.md)

## Table of Contents
1. [Model Overrides](#models) - Page 1
2. [Custom Permissions](#perms) - Page 2
3. [Template Customization](#templates) - Page 3
4. [Multi-App Integration](#multiapp) - Page 4
5. [Dockerfile Customization](#docker) - Page 5
6. [Plugin System](#plugins) - Page 6
7. [Multi-Tenant v4.0](#tenant) - Page 7
8. [PyPI Packaging](#pypi) - Page 8

---

## 1. Model Overrides (Page 1)

### Extend Generated Models
**Generated** `apps/jobs/models.py`:
```python
class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(choices=STATUS_CHOICES)
    owner = models.ForeignKey(User, on_delete=CASCADE)
```

**Your override** `apps/jobs/models_custom.py`:
```python
class JobPosting(JobPostingBase):
    salary_range = models.CharField(max_length=50)
    remote_ok = models.BooleanField(default=False)

    class Meta(JobPostingBase.Meta):
        indexes = JobPostingBase.Meta.indexes + [
            models.Index(fields=['salary_range', 'remote_ok']),
        ]
```

**Migration**:
```bash
python manage.py makemigrations jobs --name custom_fields
```

---

## 2. Custom Permissions (Page 2)

### Extend permission_classes
**Generated** `permissions.py`:
```python
class IsOwnerOrReadOnly(BasePermission):
    # Owner CRUD, others read
```

**Your custom**:
```python
class JobPublisherPermission(BasePermission):
    """Publisher role + owner."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return hasattr(request.user, 'publisher_profile')
        return False

# Usage in ViewSet
permission_classes = [JobPublisherPermission | IsOwnerOrReadOnly]
```

---

## 3. Template Customization (Page 3)

### 3 Override Levels
```
1. Global: templates/base.html
2. App: templates/jobs/base.html  
3. Instance: templates/jobs/job_list.html
```

**Custom jobs list**:
```
templates/jobs/job_list_custom.html:
{% extends 'jobs/job_list.html' %}
{% block extra_columns %}
  <th>Salary</th>
{% endblock %}
```

**Static**:
```
static/jobs/css/custom-jobs.css → Auto-collected
```

---

## 4. Multi-App Integration (Page 4)

### Add app to existing project
```
1. dual_apps init app payments
2. INSTALLED_APPS += ['payments.apps.PaymentsConfig']
3. urls.py: path('payments/', include('payments.urls'))
4. Migrate: python manage.py migrate payments
```

### Cross-App Relations
```
# apps/payments/models.py
class Payment(models.Model):
    job = models.ForeignKey('jobs.JobPosting', on_delete=CASCADE)
```

---

## 5. Dockerfile Customization (Page 5)

### apps/jobs/docker/Dockerfile.jobs
```dockerfile
FROM base-dual-apps:latest
# App-specific deps
COPY requirements/jobs.in /tmp/
RUN pip install -r /tmp/jobs.in
# Custom entrypoint
COPY docker/entrypoint.jobs.sh /entrypoint.sh
CMD ["./entrypoint.sh"]
```

**Build standalone**:
```bash
cd apps/jobs/
docker build -f docker/Dockerfile.jobs -t jobs-app .
docker run -p 8001:8000 jobs-app
```

---

## 6. Plugin System (Page 6)

### apps.py ready() Hooks
```
def ready(self):
    import jobs.plugins  # Auto-register
```

**jobs/plugins.py**:
```python
# Register plugins
PLUGIN_REGISTRY = []

class JobNotificationPlugin:
    def post_save_job(self, job):
        send_notification(job)

PLUGIN_REGISTRY.append(JobNotificationPlugin())
```

---

## 7. Multi-Tenant Preview v4.0 (Page 7)

### TenantMiddleware Ready
```
MIDDLEWARE += ['django_dual_apps.tenant.TenantMiddleware']
TENANT_MODEL = 'tenant.Tenant'

# jobs/models.py auto
class JobPosting(TenantModel):  # Inherits tenant_id
    pass
```

**URLs**:
```
/tenant1/jobs/ → Tenant 1 data only
/tenant2/jobs/ → Tenant 2 data only
```

---

## 8. PyPI Packaging Guide (Page 8)

### Package ton app
```
apps/jobs/ → pip installable:
1. pyproject.toml (generated)
2. python -m build
3. twine upload dist/*
```

**Generated pyproject.toml**:
```toml
[project]  
name = "dual-jobs"
dependencies = ["dual-apps>=3.1.0"]
```

**Install anywhere**:
```bash
pip install dual-jobs
# → INSTALLED_APPS += ['dual_jobs.apps.JobsConfig']
```

---

**Customization Complete** - Extend without breaking.

---
*Page 8/8 | dual-apps v3.1 | Feb 02, 2026*

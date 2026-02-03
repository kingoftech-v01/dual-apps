# Architecture

Technical deep dive into dual-apps architecture.

## Dual-Layer Architecture

Every generated app has two layers:

```
┌─────────────────────────────────────────────────────────┐
│                      Browser                            │
└─────────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
┌─────────────────────┐   ┌─────────────────────┐
│   Frontend Layer    │   │     API Layer       │
│   (HTMX Views)      │   │   (DRF ViewSets)    │
│                     │   │                     │
│   /{app}/           │   │   /api/v1/{app}/    │
│   - list.html       │   │   - GET (list)      │
│   - detail.html     │   │   - POST (create)   │
│   - form.html       │   │   - PUT (update)    │
│   - partials/       │   │   - DELETE          │
└─────────────────────┘   └─────────────────────┘
          │                           │
          └───────────┬───────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    Django ORM                           │
│                                                         │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │
│   │   Models    │   │ Serializers │   │    Forms    │  │
│   │  UUID PK    │   │  DRF        │   │  Django     │  │
│   │ Timestamps  │   │  Validation │   │  CSRF       │  │
│   │   Owner     │   │             │   │             │  │
│   └─────────────┘   └─────────────┘   └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Database                              │
│              PostgreSQL / SQLite                        │
└─────────────────────────────────────────────────────────┘
```

## Model Pattern

All models follow this pattern:

```python
class BaseModel(models.Model):
    # UUID for security and distributed systems
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Automatic timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Owner relationship
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # Soft delete support
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
```

## Permission Pattern

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - Read: Anyone
    - Write: Owner only
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

## Request Flow

### Frontend (HTMX)
```
Browser → HTMX Request → Django View → Template → HTML → Browser (swap)
```

### API (DRF)
```
Client → HTTP → DRF ViewSet → Serializer → JSON → Client
```

## File Structure

### App Structure
```
app_name/
├── app_name/
│   ├── __init__.py
│   ├── models.py           # UUID + timestamps + owner
│   ├── views_api.py        # DRF ViewSet
│   ├── views_frontend.py   # HTMX views
│   ├── serializers.py      # API serializers
│   ├── urls.py             # Dual URL patterns
│   ├── forms.py            # Django forms
│   ├── permissions.py      # IsOwnerOrReadOnly
│   ├── admin.py
│   ├── templates/app_name/ # HTMX templates
│   └── migrations/
├── tests/                   # 45+ tests
├── docs/
└── pyproject.toml
```

### Project Structure
```
project_name/
├── project_name/
│   ├── settings/
│   │   ├── base.py         # Common settings
│   │   ├── dev.py          # Development
│   │   ├── prod.py         # Production
│   │   └── security.py     # OWASP settings
│   ├── urls.py             # Root URLs
│   └── wsgi.py
├── apps/                    # All apps here
├── templates/               # Global templates
├── tests/                   # Integration tests
├── docker/                  # Docker configs
└── requirements/            # Dependencies
```

## Security Architecture

### OWASP Headers
```python
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
```

### Authentication
- JWT tokens for API
- Session for frontend
- OAuth2 for social auth

### Authorization
- Object-level permissions
- Owner-based access control
- Role-based for admin

## Scalability

### Horizontal Scaling
- Stateless application servers
- Redis for sessions/cache
- PostgreSQL with replicas

### Caching
- Redis for session storage
- WhiteNoise for static files
- Django cache framework

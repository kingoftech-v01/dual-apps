# Architecture

Technical deep dive into dual-apps architecture.

## Dual-Layer Architecture

Every generated app has two layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Browser                                    │
└─────────────────────────────────────────────────────────────────────┘
          │                    │                         │
          ▼                    ▼                         ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐
│  HTML Frontend  │  │  HTMX Frontend  │  │     React Frontend      │
│  (Basic)        │  │  (Dynamic)      │  │     (SPA)               │
│                 │  │                 │  │                         │
│  Server-side    │  │  Partial page   │  │  JWT Authentication     │
│  rendering      │  │  updates        │  │  API Client             │
│  No JavaScript  │  │  Alpine.js      │  │  Vite build             │
└─────────────────┘  └─────────────────┘  └─────────────────────────┘
          │                    │                         │
          └────────────────────┼─────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API Layer (DRF)                               │
│                                                                      │
│   /api/v1/{app}/                                                     │
│   - GET (list/retrieve)                                              │
│   - POST (create)                                                    │
│   - PUT/PATCH (update)                                               │
│   - DELETE                                                           │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Django ORM                                   │
│                                                                      │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│   │   Models    │   │ Serializers │   │    Forms    │              │
│   │  UUID PK    │   │  DRF        │   │  Django     │              │
│   │ Timestamps  │   │  Validation │   │  CSRF       │              │
│   │   Owner     │   │             │   │             │              │
│   └─────────────┘   └─────────────┘   └─────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Database                                     │
│                PostgreSQL / MySQL / SQLite                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Specialized Template Architecture

dual-apps provides 6 specialized templates, each with its own app structure:

### Ecommerce Template
```
myshop/
├── apps/
│   ├── shop/           # Products, categories, variants
│   ├── cart/           # Shopping cart, sessions
│   └── orders/         # Order management, payments
├── templates/
│   └── ecommerce/      # Store templates
└── frontend/           # React components (if react)
    └── components/
        ├── ProductCard.jsx
        ├── CartDrawer.jsx
        └── CheckoutForm.jsx
```

### SaaS Template
```
mysaas/
├── apps/
│   ├── subscriptions/  # Plans, pricing tiers
│   ├── billing/        # Invoices, payments
│   └── tenants/        # Multi-tenancy
├── templates/
│   └── saas/           # SaaS templates
└── frontend/
    └── components/
        └── PricingPage.jsx
```

### Blog Template
```
myblog/
├── apps/
│   ├── blog/           # Posts, categories, tags
│   └── comments/       # Comment system
├── templates/
│   └── blog/           # Blog templates
└── frontend/
    └── components/
        └── PostCard.jsx
```

### CMS Template
```
mycms/
├── apps/
│   ├── pages/          # Page builder, blocks
│   └── media/          # Media library
├── templates/
│   └── cms/            # CMS templates
└── frontend/
    └── components/
        └── PageEditor.jsx
```

### Booking Template
```
mybooking/
├── apps/
│   ├── services/       # Service catalog
│   └── appointments/   # Scheduling, calendar
├── templates/
│   └── booking/        # Booking templates
└── frontend/
    └── components/
        └── BookingCalendar.jsx
```

### Marketplace Template
```
mymarket/
├── apps/
│   ├── listings/       # Product listings
│   └── sellers/        # Seller profiles
├── templates/
│   └── marketplace/    # Marketplace templates
└── frontend/
    └── components/
        ├── ListingCard.jsx
        └── SellerProfile.jsx
```

## Frontend Architecture

### HTML Frontend (Basic)
Simple server-rendered templates with no JavaScript dependencies.

```
templates/
├── base.html           # Base template with CSS framework
├── components/
│   ├── navbar.html
│   └── footer.html
└── {app_name}/
    ├── list.html
    ├── detail.html
    └── form.html
```

### HTMX Frontend (Dynamic)
HTMX + Alpine.js for dynamic updates without full page reloads.

```
templates/
├── base.html           # HTMX + Alpine.js loaded
├── auth/
│   ├── login.html
│   ├── register.html
│   └── password_reset.html
├── partials/           # HTMX partial templates
│   ├── navbar.html
│   └── messages.html
└── {app_name}/
    ├── list.html
    ├── detail.html
    ├── form.html
    └── partials/
        ├── card.html
        └── table_row.html
```

### React Frontend (SPA)
Full single-page application with Vite.

```
frontend/
├── package.json        # Vite, React, dependencies
├── vite.config.js      # Vite configuration
├── index.html          # Entry point
└── src/
    ├── main.jsx        # React entry
    ├── App.jsx         # Router setup
    ├── App.css
    ├── api/
    │   └── client.js   # JWT API client
    ├── components/
    │   ├── common/
    │   └── {app_name}/
    ├── pages/
    │   ├── Login.jsx
    │   ├── Register.jsx
    │   └── Dashboard.jsx
    └── hooks/
        └── useAuth.js
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

## Authentication Architecture

### JWT Authentication (API)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Login     │ -> │  Validate   │ -> │ Issue JWT   │
│   Request   │    │  Credentials│    │  Tokens     │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   API       │ <- │  Validate   │ <- │   Store     │
│   Request   │    │   Token     │    │   Token     │
└─────────────┘    └─────────────┘    └─────────────┘
```

### JWT Storage Options

| Option | Storage | Security | Use Case |
|--------|---------|----------|----------|
| httpOnly | Cookie | High | Web apps (default) |
| localStorage | Browser | Medium | Mobile/PWA apps |

## Security Architecture

### Core Security Module
```
apps/core/security/
├── __init__.py
├── validators.py       # Input validation
├── middleware.py       # Security headers
├── throttling.py       # Rate limiting
├── mixins.py           # View mixins
└── decorators.py       # Security decorators
```

### OWASP Headers
```python
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
```

### Rate Limiting
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## Testing Architecture

### Test Pyramid
```
┌───────────────────┐
│   E2E Tests       │  (Playwright)
│   5%              │
├───────────────────┤
│   Integration     │  (pytest)
│   25%             │
├───────────────────┤
│   Unit Tests      │  (pytest)
│   70%             │
└───────────────────┘
```

### Coverage Targets
- **Overall**: 97%+
- **Models**: 100%
- **Views**: 95%
- **Serializers**: 95%

### E2E Test Structure
```
e2e/
├── playwright.config.js
├── package.json
├── fixtures/
│   └── auth.js
└── tests/
    ├── auth.spec.js
    ├── ecommerce.spec.js
    ├── saas.spec.js
    ├── booking.spec.js
    └── marketplace.spec.js
```

## Scalability

### Horizontal Scaling
- Stateless application servers
- Redis for sessions/cache
- PostgreSQL with replicas

### Caching
- Redis for session storage
- WhiteNoise for static files
- Django cache framework

### Async Tasks (Celery)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Request   │ -> │   Queue     │ -> │   Worker    │
│             │    │   (Redis)   │    │  (Celery)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

# Security Guide

dual-apps generates secure Django projects following OWASP best practices.

## Security Features

### 1. OWASP Headers

All generated projects include secure HTTP headers:

```python
# settings/security.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
```

### 2. CSRF Protection

- CSRF tokens required for all POST requests
- Secure cookie settings
- SameSite cookie policy

```python
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
```

### 3. Session Security

```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 86400  # 24 hours
```

### 4. Content Security Policy

```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.tailwindcss.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_FRAME_ANCESTORS = ("'none'",)
```

## Authentication

### JWT Authentication

```python
# Secure token configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Password Validation

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

## Rate Limiting

### API Throttling

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    }
}
```

### Login Rate Limiting

- 5 login attempts per minute
- 3 password reset requests per hour

## Permission Model

### IsOwnerOrReadOnly

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for owner
        return obj.owner == request.user
```

## SQL Injection Prevention

- Django ORM parameterizes all queries
- No raw SQL queries in generated code
- Input validation on all serializers

## XSS Prevention

- Template auto-escaping enabled
- Content Security Policy headers
- No unsafe HTML rendering

## Security Audit

Run security checks:

```bash
# Django security check
python manage.py check --deploy

# Check for vulnerable packages
pip-audit

# Run security audit script
./scripts/security-audit.sh
```

## Secrets Management

### Development
```bash
# .env file (never commit!)
SECRET_KEY=dev-secret-key
```

### Production
Use environment variables or secret management:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## Security Updates

1. Keep dependencies updated
2. Enable GitHub security alerts
3. Run `pip-audit` regularly
4. Subscribe to Django security announcements

## Reporting Vulnerabilities

If you discover a security vulnerability:
1. Do NOT open a public issue
2. Email security@dual-apps.dev
3. Include detailed reproduction steps

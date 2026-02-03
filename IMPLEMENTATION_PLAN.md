# Implementation Plan: Project Types + Template-Specific Frontends

## Overview

This document outlines the complete implementation plan for adding project types, template-specific frontends with full features, security layer, and comprehensive testing.

---

## 1. New CLI Options

### Command Structure
```bash
dual-apps init project <name> \
  --type fullstack|backend|frontend \
  --template default|ecommerce|blog|saas|cms|booking|marketplace \
  --frontend html|htmx|react \
  --css bootstrap|tailwind \
  --auth jwt|session|allauth \
  --jwt-storage localStorage|httpOnly \
  --db postgres|mysql|sqlite \
  --docker / --no-docker \
  --celery / --no-celery \
  --i18n / --no-i18n
```

### Interactive Prompts (when not specified)
```
? Select project type: (fullstack)
  ○ fullstack - Full stack with API + Frontend
  ○ backend - API only (DRF ViewSets, no templates)
  ○ frontend - Frontend only (no API processing)

? Select JWT storage method: (httpOnly)
  ○ httpOnly - Secure httpOnly cookies (recommended)
  ○ localStorage - Browser localStorage (simpler)
```

---

## 2. Project Types

### 2.1 Backend Only (`--type backend`)
- DRF ViewSets, Serializers, URLs
- API documentation (Swagger/ReDoc)
- No HTML templates
- No static files (except API docs)
- CORS configured for external frontends

**Generated Structure:**
```
project/
├── apps/
│   └── [app]/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py          # API ViewSets only
│       ├── urls.py           # API URLs only
│       ├── permissions.py
│       ├── filters.py
│       └── tests/
├── config/
│   └── settings/
│       └── base.py           # CORS, no template config
└── requirements/
```

### 2.2 Frontend Only (`--type frontend`)
- Django views serving templates OR React SPA
- No DRF, no API processing
- Connects to external API (configurable base URL)
- Static file serving

**Generated Structure (HTML/HTMX):**
```
project/
├── apps/
│   └── [app]/
│       ├── views.py          # TemplateViews only
│       ├── urls.py           # Frontend URLs only
│       └── forms.py          # Frontend forms
├── templates/
│   └── [app]/
└── static/
```

**Generated Structure (React):**
```
project/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── (minimal Django for serving)
```

### 2.3 Fullstack (`--type fullstack`) - Default
- Both API and Frontend
- Full Django + DRF + Templates/React
- Current behavior enhanced

---

## 3. Security Layer

### 3.1 Files to Generate

```
apps/core/
├── security/
│   ├── __init__.py
│   ├── middleware.py         # Security middleware
│   ├── validators.py         # Input validators with regex
│   ├── throttling.py         # DRF throttling classes
│   ├── mixins.py             # Security mixins for views
│   ├── decorators.py         # Security decorators
│   └── utils.py              # Security utilities
```

### 3.2 Security Features Implementation

#### 3.2.1 SQL Injection Prevention
```python
# validators.py
import re
from django.core.exceptions import ValidationError

class SQLInjectionValidator:
    """Validates input against SQL injection patterns."""

    DANGEROUS_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bAND\b\s+\d+\s*=\s*\d+)",
        r"(\'|\"|`)",
    ]

    def __init__(self, allow_quotes=False):
        self.allow_quotes = allow_quotes
        self.patterns = self.DANGEROUS_PATTERNS.copy()
        if allow_quotes:
            self.patterns = self.patterns[:-1]

    def __call__(self, value):
        for pattern in self.patterns:
            if re.search(pattern, str(value), re.IGNORECASE):
                raise ValidationError(
                    "Invalid characters detected in input.",
                    code="sql_injection_attempt"
                )
        return value
```

#### 3.2.2 XSS Prevention
```python
# validators.py
import re
import html
from django.utils.html import strip_tags

class XSSValidator:
    """Validates and sanitizes input against XSS attacks."""

    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"expression\s*\(",
        r"url\s*\(",
    ]

    def __init__(self, sanitize=True, strip=False):
        self.sanitize = sanitize
        self.strip = strip

    def __call__(self, value):
        str_value = str(value)

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, str_value, re.IGNORECASE | re.DOTALL):
                raise ValidationError(
                    "Potentially unsafe content detected.",
                    code="xss_attempt"
                )

        if self.strip:
            return strip_tags(str_value)
        if self.sanitize:
            return html.escape(str_value)
        return value
```

#### 3.2.3 Rate Limiting
```python
# throttling.py
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class BurstRateThrottle(AnonRateThrottle):
    """Limits burst requests from anonymous users."""
    scope = 'burst'
    rate = '60/min'

class SustainedRateThrottle(UserRateThrottle):
    """Limits sustained requests from authenticated users."""
    scope = 'sustained'
    rate = '1000/day'

class LoginRateThrottle(AnonRateThrottle):
    """Strict rate limiting for login attempts."""
    scope = 'login'
    rate = '5/min'

class PasswordResetThrottle(AnonRateThrottle):
    """Rate limiting for password reset requests."""
    scope = 'password_reset'
    rate = '3/hour'

class APIKeyThrottle(UserRateThrottle):
    """Rate limiting for API key authenticated requests."""
    scope = 'api_key'
    rate = '10000/day'
```

#### 3.2.4 Security Middleware
```python
# middleware.py
from django.conf import settings
from django.http import HttpResponseForbidden
import re

class SecurityHeadersMiddleware:
    """Adds security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-ancestors 'none'; "
            "form-action 'self';"
        )

        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=()'
        )

        if settings.DEBUG is False:
            response['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )

        return response

class BruteForceProtectionMiddleware:
    """Protects against brute force attacks."""

    # Track failed attempts per IP
    failed_attempts = {}
    MAX_ATTEMPTS = 5
    LOCKOUT_TIME = 900  # 15 minutes

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_locked_out(request):
            return HttpResponseForbidden(
                "Too many failed attempts. Please try again later."
            )
        return self.get_response(request)
```

#### 3.2.5 Input Validators
```python
# validators.py
import re
from django.core.validators import RegexValidator

# Email validator (strict)
email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message='Enter a valid email address.',
    code='invalid_email'
)

# Phone validator (international)
phone_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{1,14}$',
    message='Enter a valid phone number in E.164 format.',
    code='invalid_phone'
)

# Username validator
username_validator = RegexValidator(
    regex=r'^[a-zA-Z][a-zA-Z0-9_]{2,29}$',
    message='Username must start with a letter, contain only letters, numbers, and underscores, and be 3-30 characters.',
    code='invalid_username'
)

# Slug validator
slug_validator = RegexValidator(
    regex=r'^[a-z0-9]+(?:-[a-z0-9]+)*$',
    message='Enter a valid slug (lowercase letters, numbers, and hyphens only).',
    code='invalid_slug'
)

# Password validator (strong)
password_validator = RegexValidator(
    regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,128}$',
    message='Password must be 8-128 characters with at least one uppercase, lowercase, number, and special character.',
    code='weak_password'
)

# URL validator (safe)
safe_url_validator = RegexValidator(
    regex=r'^https?://[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+(/[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=-]*)?$',
    message='Enter a valid and safe URL.',
    code='invalid_url'
)

# Credit card validator (basic format)
credit_card_validator = RegexValidator(
    regex=r'^\d{13,19}$',
    message='Enter a valid credit card number.',
    code='invalid_card'
)

# Postal code validators
us_zip_validator = RegexValidator(
    regex=r'^\d{5}(-\d{4})?$',
    message='Enter a valid US ZIP code.',
    code='invalid_zip'
)

# UUID validator
uuid_validator = RegexValidator(
    regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    message='Enter a valid UUID.',
    code='invalid_uuid'
)

# Safe filename validator
filename_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9][-a-zA-Z0-9._]*[a-zA-Z0-9]$',
    message='Filename contains invalid characters.',
    code='invalid_filename'
)

# No HTML/Script validator
no_html_validator = RegexValidator(
    regex=r'^[^<>]*$',
    message='HTML tags are not allowed.',
    code='html_not_allowed'
)
```

#### 3.2.6 Security Decorators
```python
# decorators.py
from functools import wraps
from django.http import HttpResponseForbidden
from django_ratelimit.decorators import ratelimit

def require_https(view_func):
    """Requires HTTPS for the view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            return HttpResponseForbidden("HTTPS required")
        return view_func(request, *args, **kwargs)
    return wrapper

def validate_content_type(allowed_types):
    """Validates Content-Type header."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            content_type = request.content_type
            if content_type not in allowed_types:
                return HttpResponseForbidden("Invalid content type")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def sanitize_input(*fields):
    """Sanitizes specified input fields."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            for field in fields:
                if field in request.POST:
                    request.POST[field] = html.escape(request.POST[field])
                if field in request.GET:
                    request.GET[field] = html.escape(request.GET[field])
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 4. Template-Specific Frontends

### 4.1 Ecommerce Template

#### HTML Pages
```
templates/shop/
├── base_shop.html
├── product/
│   ├── list.html             # Product listing with filters
│   ├── detail.html           # Product detail with add to cart
│   ├── search.html           # Search results
│   └── category.html         # Category products
├── cart/
│   ├── view.html             # Cart view with quantities
│   ├── mini.html             # Mini cart (header dropdown)
│   └── empty.html            # Empty cart state
├── checkout/
│   ├── address.html          # Shipping address form
│   ├── payment.html          # Payment form
│   ├── review.html           # Order review
│   └── confirmation.html     # Order confirmation
├── order/
│   ├── list.html             # Order history
│   ├── detail.html           # Order detail
│   └── track.html            # Order tracking
├── wishlist/
│   └── list.html             # Wishlist items
├── account/
│   ├── login.html            # Login form
│   ├── register.html         # Registration form
│   ├── profile.html          # User profile
│   └── addresses.html        # Saved addresses
└── components/
    ├── product_card.html     # Reusable product card
    ├── pagination.html       # Pagination component
    ├── filters.html          # Filter sidebar
    └── breadcrumbs.html      # Breadcrumb navigation
```

#### HTMX Features
- Live cart updates without page reload
- Infinite scroll product listing
- Real-time search suggestions
- Add to cart with animation
- Quantity updates in cart
- Live stock checking
- Form validation feedback

#### React Components
```
frontend/src/
├── api/
│   ├── client.js
│   ├── products.js
│   ├── cart.js
│   ├── orders.js
│   └── auth.js
├── auth/
│   ├── AuthContext.jsx
│   ├── useAuth.js
│   ├── LoginForm.jsx
│   ├── RegisterForm.jsx
│   ├── ProtectedRoute.jsx
│   └── TokenService.js
├── cart/
│   ├── CartContext.jsx
│   ├── useCart.js
│   ├── Cart.jsx
│   ├── CartItem.jsx
│   ├── CartSummary.jsx
│   └── MiniCart.jsx
├── checkout/
│   ├── CheckoutContext.jsx
│   ├── AddressForm.jsx
│   ├── PaymentForm.jsx
│   ├── OrderReview.jsx
│   └── Confirmation.jsx
├── products/
│   ├── ProductList.jsx
│   ├── ProductCard.jsx
│   ├── ProductDetail.jsx
│   ├── ProductFilters.jsx
│   ├── ProductSearch.jsx
│   └── CategoryNav.jsx
├── orders/
│   ├── OrderList.jsx
│   ├── OrderDetail.jsx
│   └── OrderTracking.jsx
├── wishlist/
│   ├── WishlistContext.jsx
│   ├── Wishlist.jsx
│   └── WishlistButton.jsx
├── components/
│   ├── forms/
│   │   ├── Input.jsx
│   │   ├── Select.jsx
│   │   ├── Checkbox.jsx
│   │   ├── FormError.jsx
│   │   └── validators.js
│   ├── common/
│   │   ├── Loading.jsx
│   │   ├── Pagination.jsx
│   │   ├── Modal.jsx
│   │   ├── Alert.jsx
│   │   ├── Breadcrumbs.jsx
│   │   └── Rating.jsx
│   └── layout/
│       ├── Header.jsx
│       ├── Footer.jsx
│       ├── Sidebar.jsx
│       └── Layout.jsx
├── hooks/
│   ├── useApi.js
│   ├── useForm.js
│   ├── usePagination.js
│   └── useDebounce.js
├── utils/
│   ├── validators.js
│   ├── formatters.js
│   └── storage.js
├── pages/
│   ├── HomePage.jsx
│   ├── ProductsPage.jsx
│   ├── ProductPage.jsx
│   ├── CartPage.jsx
│   ├── CheckoutPage.jsx
│   ├── OrdersPage.jsx
│   ├── OrderPage.jsx
│   ├── WishlistPage.jsx
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   └── ProfilePage.jsx
├── App.jsx
├── main.jsx
└── routes.jsx
```

### 4.2 Blog Template

#### HTML Pages
```
templates/blog/
├── base_blog.html
├── post/
│   ├── list.html             # Post listing
│   ├── detail.html           # Post with comments
│   ├── create.html           # Create post (authors)
│   └── edit.html             # Edit post (authors)
├── category/
│   ├── list.html             # All categories
│   └── detail.html           # Category posts
├── tag/
│   └── detail.html           # Tag posts
├── author/
│   ├── list.html             # All authors
│   └── profile.html          # Author profile
├── search/
│   └── results.html          # Search results
├── comment/
│   ├── list.html             # Comment section
│   └── form.html             # Comment form
├── account/
│   ├── login.html
│   ├── register.html
│   └── profile.html
└── components/
    ├── post_card.html
    ├── sidebar.html
    ├── newsletter.html
    └── social_share.html
```

#### React Components
```
frontend/src/
├── api/
│   ├── posts.js
│   ├── categories.js
│   ├── comments.js
│   └── authors.js
├── posts/
│   ├── PostList.jsx
│   ├── PostCard.jsx
│   ├── PostDetail.jsx
│   ├── PostEditor.jsx
│   └── PostMeta.jsx
├── comments/
│   ├── CommentSection.jsx
│   ├── CommentForm.jsx
│   ├── Comment.jsx
│   └── CommentReply.jsx
├── categories/
│   ├── CategoryList.jsx
│   ├── CategoryNav.jsx
│   └── CategoryBadge.jsx
├── authors/
│   ├── AuthorProfile.jsx
│   ├── AuthorCard.jsx
│   └── AuthorPosts.jsx
├── search/
│   ├── SearchBar.jsx
│   └── SearchResults.jsx
└── pages/
    ├── HomePage.jsx
    ├── PostPage.jsx
    ├── CategoryPage.jsx
    ├── AuthorPage.jsx
    └── SearchPage.jsx
```

### 4.3 SaaS Template

#### HTML Pages
```
templates/saas/
├── base_saas.html
├── landing/
│   ├── home.html             # Landing page
│   ├── features.html         # Features page
│   └── pricing.html          # Pricing page
├── dashboard/
│   ├── index.html            # Main dashboard
│   ├── analytics.html        # Analytics view
│   └── activity.html         # Activity feed
├── organization/
│   ├── settings.html         # Org settings
│   ├── members.html          # Team members
│   ├── invitations.html      # Pending invites
│   └── roles.html            # Role management
├── billing/
│   ├── subscription.html     # Current subscription
│   ├── plans.html            # Available plans
│   ├── payment.html          # Payment method
│   ├── invoices.html         # Invoice history
│   └── upgrade.html          # Upgrade flow
├── account/
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── security.html         # 2FA, sessions
│   └── api_keys.html         # API key management
└── components/
    ├── sidebar.html
    ├── stats_card.html
    ├── chart.html
    └── member_row.html
```

#### React Components
```
frontend/src/
├── dashboard/
│   ├── Dashboard.jsx
│   ├── StatsCard.jsx
│   ├── ActivityFeed.jsx
│   ├── Analytics.jsx
│   └── Charts.jsx
├── organization/
│   ├── OrgContext.jsx
│   ├── OrgSettings.jsx
│   ├── MemberList.jsx
│   ├── MemberInvite.jsx
│   ├── RoleManager.jsx
│   └── OrgSwitcher.jsx
├── billing/
│   ├── BillingContext.jsx
│   ├── Subscription.jsx
│   ├── PricingTable.jsx
│   ├── PaymentForm.jsx
│   ├── InvoiceList.jsx
│   └── UpgradeModal.jsx
├── api-keys/
│   ├── ApiKeyList.jsx
│   ├── ApiKeyCreate.jsx
│   └── ApiKeyRow.jsx
└── pages/
    ├── LandingPage.jsx
    ├── DashboardPage.jsx
    ├── SettingsPage.jsx
    ├── BillingPage.jsx
    └── TeamPage.jsx
```

### 4.4 CMS Template

#### HTML Pages
```
templates/cms/
├── base_cms.html
├── page/
│   ├── view.html             # Dynamic page view
│   └── preview.html          # Page preview
├── navigation/
│   ├── menu.html             # Main menu
│   ├── breadcrumbs.html      # Breadcrumbs
│   └── footer_menu.html      # Footer menu
├── media/
│   ├── gallery.html          # Media gallery
│   └── detail.html           # Media detail
├── search/
│   └── results.html          # Site search
├── sitemap/
│   └── index.html            # HTML sitemap
└── components/
    ├── block_text.html       # Text block
    ├── block_image.html      # Image block
    ├── block_video.html      # Video block
    ├── block_gallery.html    # Gallery block
    └── block_form.html       # Form block
```

#### React Components
```
frontend/src/
├── pages/
│   ├── DynamicPage.jsx       # Renders CMS pages
│   └── PageBlocks.jsx        # Block renderer
├── blocks/
│   ├── TextBlock.jsx
│   ├── ImageBlock.jsx
│   ├── VideoBlock.jsx
│   ├── GalleryBlock.jsx
│   └── FormBlock.jsx
├── navigation/
│   ├── MainNav.jsx
│   ├── FooterNav.jsx
│   └── Breadcrumbs.jsx
├── media/
│   ├── MediaGallery.jsx
│   └── MediaViewer.jsx
└── search/
    ├── SiteSearch.jsx
    └── SearchResults.jsx
```

### 4.5 Booking Template

#### HTML Pages
```
templates/booking/
├── base_booking.html
├── service/
│   ├── list.html             # Service listing
│   ├── detail.html           # Service detail
│   └── category.html         # Service category
├── booking/
│   ├── calendar.html         # Calendar view
│   ├── form.html             # Booking form
│   ├── confirmation.html     # Booking confirmed
│   └── reschedule.html       # Reschedule form
├── staff/
│   ├── list.html             # Staff listing
│   └── profile.html          # Staff profile
├── customer/
│   ├── bookings.html         # My bookings
│   ├── history.html          # Booking history
│   └── profile.html          # Customer profile
├── account/
│   ├── login.html
│   ├── register.html
│   └── profile.html
└── components/
    ├── calendar.html         # Calendar widget
    ├── time_slots.html       # Time slot picker
    ├── service_card.html     # Service card
    └── booking_card.html     # Booking summary
```

#### React Components
```
frontend/src/
├── services/
│   ├── ServiceList.jsx
│   ├── ServiceCard.jsx
│   ├── ServiceDetail.jsx
│   └── ServiceCategory.jsx
├── booking/
│   ├── BookingContext.jsx
│   ├── BookingCalendar.jsx
│   ├── TimeSlotPicker.jsx
│   ├── BookingForm.jsx
│   ├── BookingConfirmation.jsx
│   └── RescheduleModal.jsx
├── staff/
│   ├── StaffList.jsx
│   ├── StaffCard.jsx
│   └── StaffProfile.jsx
├── customer/
│   ├── MyBookings.jsx
│   ├── BookingHistory.jsx
│   └── BookingCard.jsx
└── pages/
    ├── ServicesPage.jsx
    ├── BookingPage.jsx
    ├── MyBookingsPage.jsx
    └── StaffPage.jsx
```

### 4.6 Marketplace Template

#### HTML Pages
```
templates/marketplace/
├── base_marketplace.html
├── vendor/
│   ├── list.html             # Vendor listing
│   ├── detail.html           # Vendor store
│   ├── dashboard.html        # Vendor dashboard
│   ├── products.html         # Vendor products
│   ├── orders.html           # Vendor orders
│   └── settings.html         # Vendor settings
├── product/
│   ├── list.html             # All products
│   ├── detail.html           # Product detail
│   └── search.html           # Search results
├── cart/
│   ├── view.html             # Cart (multi-vendor)
│   └── checkout.html         # Checkout
├── order/
│   ├── list.html             # Order history
│   └── detail.html           # Order detail
├── review/
│   ├── list.html             # Product reviews
│   └── form.html             # Write review
├── account/
│   ├── login.html
│   ├── register.html
│   ├── become_vendor.html    # Vendor application
│   └── profile.html
└── components/
    ├── vendor_card.html
    ├── product_card.html
    ├── review_card.html
    └── rating.html
```

#### React Components
```
frontend/src/
├── vendors/
│   ├── VendorList.jsx
│   ├── VendorCard.jsx
│   ├── VendorStore.jsx
│   ├── VendorDashboard.jsx
│   ├── VendorProducts.jsx
│   ├── VendorOrders.jsx
│   └── VendorSettings.jsx
├── products/
│   ├── ProductList.jsx
│   ├── ProductCard.jsx
│   ├── ProductDetail.jsx
│   └── ProductSearch.jsx
├── cart/
│   ├── CartContext.jsx
│   ├── MultiVendorCart.jsx
│   └── Checkout.jsx
├── orders/
│   ├── OrderList.jsx
│   └── OrderDetail.jsx
├── reviews/
│   ├── ReviewList.jsx
│   ├── ReviewCard.jsx
│   ├── ReviewForm.jsx
│   └── Rating.jsx
└── pages/
    ├── HomePage.jsx
    ├── VendorsPage.jsx
    ├── VendorPage.jsx
    ├── ProductsPage.jsx
    ├── ProductPage.jsx
    ├── CartPage.jsx
    ├── VendorDashboardPage.jsx
    └── BecomeVendorPage.jsx
```

---

## 5. JWT Storage Options

### 5.1 localStorage (Simpler)

```javascript
// TokenService.js (localStorage version)
class TokenService {
  static ACCESS_TOKEN_KEY = 'access_token';
  static REFRESH_TOKEN_KEY = 'refresh_token';

  static getAccessToken() {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static setAccessToken(token) {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, token);
  }

  static getRefreshToken() {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setTokens(access, refresh) {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, access);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
  }

  static clearTokens() {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  static isAuthenticated() {
    const token = this.getAccessToken();
    if (!token) return false;

    // Check if token is expired
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }
}
```

### 5.2 httpOnly Cookies (Recommended/Secure)

```python
# Django view for httpOnly cookie auth
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings

class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('access'):
            response.set_cookie(
                key=settings.JWT_AUTH_COOKIE,
                value=response.data['access'],
                expires=settings.JWT_ACCESS_TOKEN_LIFETIME,
                secure=settings.JWT_AUTH_SECURE,
                httponly=True,
                samesite=settings.JWT_AUTH_SAMESITE,
            )
            del response.data['access']

        if response.data.get('refresh'):
            response.set_cookie(
                key=settings.JWT_AUTH_REFRESH_COOKIE,
                value=response.data['refresh'],
                expires=settings.JWT_REFRESH_TOKEN_LIFETIME,
                secure=settings.JWT_AUTH_SECURE,
                httponly=True,
                samesite=settings.JWT_AUTH_SAMESITE,
            )
            del response.data['refresh']

        return super().finalize_response(request, response, *args, **kwargs)
```

```javascript
// TokenService.js (httpOnly version)
class TokenService {
  // No token storage needed - cookies are automatic

  static async isAuthenticated() {
    try {
      const response = await fetch('/api/auth/verify/', {
        credentials: 'include',
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  static async refreshToken() {
    try {
      const response = await fetch('/api/auth/refresh/', {
        method: 'POST',
        credentials: 'include',
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  static async logout() {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      credentials: 'include',
    });
  }
}
```

---

## 6. CSS Framework Configuration

### 6.1 Bootstrap Configuration
```html
<!-- base.html (Bootstrap) -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ project_name }}{% endblock %}</title>

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 6.2 Tailwind Configuration
```html
<!-- base.html (Tailwind) -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ project_name }}{% endblock %}</title>

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3b82f6',
                        secondary: '#64748b',
                    }
                }
            }
        }
    </script>

    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50 min-h-screen">
    {% block content %}{% endblock %}
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```
tests/
├── test_security/
│   ├── test_validators.py        # Test all validators
│   ├── test_middleware.py        # Test security middleware
│   ├── test_throttling.py        # Test rate limiting
│   └── test_decorators.py        # Test security decorators
├── test_templates/
│   ├── test_ecommerce/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_serializers.py
│   │   ├── test_forms.py
│   │   └── test_api.py
│   ├── test_blog/
│   ├── test_saas/
│   ├── test_cms/
│   ├── test_booking/
│   └── test_marketplace/
├── test_frontend/
│   ├── test_html_generation.py
│   ├── test_htmx_generation.py
│   └── test_react_generation.py
└── test_project_types/
    ├── test_backend_only.py
    ├── test_frontend_only.py
    └── test_fullstack.py
```

### 7.2 E2E Tests with Playwright

```
e2e/
├── playwright.config.js
├── fixtures/
│   ├── auth.js               # Auth helpers
│   └── data.js               # Test data
├── ecommerce/
│   ├── product.spec.js       # Product CRUD
│   ├── cart.spec.js          # Cart operations
│   ├── checkout.spec.js      # Checkout flow
│   └── auth.spec.js          # Auth flow
├── blog/
│   ├── post.spec.js
│   ├── comment.spec.js
│   └── auth.spec.js
├── saas/
│   ├── dashboard.spec.js
│   ├── organization.spec.js
│   ├── billing.spec.js
│   └── auth.spec.js
├── cms/
│   ├── page.spec.js
│   └── navigation.spec.js
├── booking/
│   ├── service.spec.js
│   ├── booking.spec.js
│   └── auth.spec.js
└── marketplace/
    ├── vendor.spec.js
    ├── product.spec.js
    ├── cart.spec.js
    └── auth.spec.js
```

### 7.3 API Tests

```python
# test_api.py example for ecommerce
import pytest
from rest_framework.test import APIClient
from rest_framework import status

class TestProductAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    # CREATE
    def test_create_product_authenticated(self, auth_client, category):
        data = {
            'name': 'Test Product',
            'price': '99.99',
            'category': category.id,
            'description': 'Test description',
        }
        response = auth_client.post('/api/v1/products/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Product'

    def test_create_product_unauthenticated(self, client):
        response = client.post('/api/v1/products/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # READ
    def test_list_products(self, client, products):
        response = client.get('/api/v1/products/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(products)

    def test_retrieve_product(self, client, product):
        response = client.get(f'/api/v1/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id

    # UPDATE
    def test_update_product(self, auth_client, product):
        data = {'name': 'Updated Product'}
        response = auth_client.patch(f'/api/v1/products/{product.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Product'

    # DELETE
    def test_delete_product(self, auth_client, product):
        response = auth_client.delete(f'/api/v1/products/{product.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # SECURITY
    def test_sql_injection_prevention(self, client):
        response = client.get('/api/v1/products/?search=\'; DROP TABLE products; --')
        assert response.status_code == status.HTTP_200_OK  # Should not error
        # Verify table still exists
        response = client.get('/api/v1/products/')
        assert response.status_code == status.HTTP_200_OK

    def test_xss_prevention(self, auth_client, category):
        data = {
            'name': '<script>alert("xss")</script>',
            'price': '99.99',
            'category': category.id,
        }
        response = auth_client.post('/api/v1/products/', data)
        assert '<script>' not in response.data['name']
```

### 7.4 Form Tests

```python
# test_forms.py
import pytest
from django.core.exceptions import ValidationError

class TestProductForm:
    def test_valid_form(self, category):
        form = ProductForm(data={
            'name': 'Valid Product',
            'price': '99.99',
            'category': category.id,
            'description': 'Valid description',
        })
        assert form.is_valid()

    def test_xss_in_name(self, category):
        form = ProductForm(data={
            'name': '<script>alert("xss")</script>',
            'price': '99.99',
            'category': category.id,
        })
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_sql_injection_in_name(self, category):
        form = ProductForm(data={
            'name': "'; DROP TABLE products; --",
            'price': '99.99',
            'category': category.id,
        })
        assert not form.is_valid()

    def test_negative_price(self, category):
        form = ProductForm(data={
            'name': 'Product',
            'price': '-10.00',
            'category': category.id,
        })
        assert not form.is_valid()
        assert 'price' in form.errors
```

### 7.5 CRUD Action Tests

```python
# test_crud.py
import pytest

class TestProductCRUD:
    """Test full CRUD lifecycle for products."""

    def test_full_crud_lifecycle(self, auth_client, category):
        # CREATE
        create_data = {
            'name': 'CRUD Test Product',
            'price': '49.99',
            'category': category.id,
        }
        response = auth_client.post('/api/v1/products/', create_data)
        assert response.status_code == 201
        product_id = response.data['id']

        # READ
        response = auth_client.get(f'/api/v1/products/{product_id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'CRUD Test Product'

        # UPDATE
        update_data = {'name': 'Updated CRUD Product', 'price': '59.99'}
        response = auth_client.patch(f'/api/v1/products/{product_id}/', update_data)
        assert response.status_code == 200
        assert response.data['name'] == 'Updated CRUD Product'
        assert response.data['price'] == '59.99'

        # DELETE
        response = auth_client.delete(f'/api/v1/products/{product_id}/')
        assert response.status_code == 204

        # VERIFY DELETED
        response = auth_client.get(f'/api/v1/products/{product_id}/')
        assert response.status_code == 404
```

---

## 8. Implementation Phases (Detailed)

### Phase 1: Core Infrastructure
**Files: ~25**

1. Add CLI options (`--type`, `--css`, `--jwt-storage`)
2. Add interactive prompts for missing options
3. Create security module (validators, middleware, throttling)
4. Update project generator for project types
5. Add security tests

### Phase 2: Ecommerce Frontend
**Files: ~45**

1. HTML templates (15 files)
2. HTMX templates (15 files)
3. React components (15+ files)
4. Unit tests
5. E2E tests
6. API tests
7. Form tests

### Phase 3: Blog Frontend
**Files: ~35**

1. HTML templates (12 files)
2. HTMX templates (12 files)
3. React components (12+ files)
4. All tests

### Phase 4: SaaS Frontend
**Files: ~40**

1. HTML templates (14 files)
2. HTMX templates (14 files)
3. React components (14+ files)
4. All tests

### Phase 5: CMS Frontend
**Files: ~25**

1. HTML templates (8 files)
2. HTMX templates (8 files)
3. React components (10+ files)
4. All tests

### Phase 6: Booking Frontend
**Files: ~35**

1. HTML templates (12 files)
2. HTMX templates (12 files)
3. React components (12+ files)
4. All tests

### Phase 7: Marketplace Frontend
**Files: ~45**

1. HTML templates (15 files)
2. HTMX templates (15 files)
3. React components (15+ files)
4. All tests

### Phase 8: Integration & Documentation
**Files: ~20**

1. Cross-template integration tests
2. E2E test suite completion
3. Update help command
4. Update README
5. Final coverage report

---

## 9. File Count Summary

| Category | Files |
|----------|-------|
| Core Infrastructure | 25 |
| Ecommerce Frontend | 45 |
| Blog Frontend | 35 |
| SaaS Frontend | 40 |
| CMS Frontend | 25 |
| Booking Frontend | 35 |
| Marketplace Frontend | 45 |
| Tests & Documentation | 50 |
| **Total** | **~300 files** |

---

## 10. Success Criteria

1. All CLI options work correctly
2. All project types generate valid projects
3. All templates have html/htmx/react frontends
4. Security layer prevents SQL/XSS injection
5. Rate limiting works correctly
6. JWT storage options work correctly
7. All unit tests pass (95%+ coverage)
8. All E2E tests pass
9. All API CRUD tests pass
10. All form validation tests pass
11. Django check passes for all generated projects

---

**Ready to implement when approved.**

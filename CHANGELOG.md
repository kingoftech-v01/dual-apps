# Changelog

All notable changes to dual-apps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2026-02-03

### Added

#### Specialized Templates (6 new templates)
- **Ecommerce Template**: Complete online store with shop, cart, orders apps
  - Product catalog with categories and variants
  - Shopping cart with session/user persistence
  - Order management with status tracking
  - Payment integration ready
- **Blog Template**: Content platform with blog, comments apps
  - Post management with categories and tags
  - Comment system with moderation
  - Author profiles and archives
- **SaaS Template**: Software-as-a-Service with subscriptions, billing apps
  - Subscription plans and pricing tiers
  - Billing and invoice management
  - Usage tracking and limits
  - Tenant isolation support
- **CMS Template**: Content management with pages, media apps
  - Page editor with blocks/components
  - Media library with image optimization
  - SEO metadata management
  - Version history and drafts
- **Booking Template**: Reservation system with services, appointments apps
  - Service catalog with availability
  - Appointment scheduling with calendar
  - Staff management and assignments
  - Reminder notifications
- **Marketplace Template**: Multi-vendor platform with listings, sellers apps
  - Seller registration and profiles
  - Product listings with search/filters
  - Order routing to sellers
  - Commission and payout management

#### Frontend Options (3 options)
- **HTML Frontend**: Basic server-rendered HTML templates
  - Simple Django templates
  - Bootstrap 5 or Tailwind CSS
  - No JavaScript dependencies
- **HTMX Frontend**: Dynamic HTMX + Alpine.js templates
  - Full authentication flow (login, register, logout, password reset)
  - Real-time form validation
  - Partial page updates
  - CSRF protection built-in
- **React Frontend**: Full Single Page Application
  - Vite-powered React setup
  - JWT authentication with token refresh
  - API client with interceptors
  - Component library per app

#### CSS Framework Options
- **Bootstrap 5**: Full Bootstrap 5 integration with responsive layouts
- **Tailwind CSS**: Utility-first CSS with custom configuration

#### JWT Storage Options
- **httpOnly Cookies**: Secure cookie-based JWT storage (recommended)
- **localStorage**: Browser localStorage JWT storage (for specific use cases)

#### Project Type Options
- **Backend**: API-only project without frontend
- **Frontend**: Frontend-only project
- **Fullstack**: Complete frontend + backend project (default)

#### Testing Improvements
- **97% Test Coverage**: Increased from 88% to 97%
- **392+ Tests**: Comprehensive test suite
- **Playwright E2E Tests**: End-to-end test templates for all specialized templates
  - Authentication flow tests
  - Ecommerce checkout flow tests
  - SaaS subscription flow tests
  - Booking appointment flow tests
  - Marketplace listing flow tests
- **Integration Tests**: Frontend generation integration tests

#### Security Enhancements
- **Security Module**: Core security middleware and validators
- **Rate Limiting**: API throttling classes
- **CSRF Protection**: Enhanced CSRF handling for HTMX
- **JWT Security**: Configurable token expiration and refresh

### Changed
- Updated CLI with new options: `--template`, `--frontend`, `--css`, `--jwt-storage`, `--type`
- Improved project structure for specialized templates
- Enhanced documentation with examples for all templates
- Better error handling and validation

### Fixed
- Template rendering issues with complex nested structures
- JWT token refresh logic in React frontend
- HTMX CSRF token handling

---

## [3.2.0] - 2024-01-XX

### Added
- **Interactive Mode**: `dual_apps init project --interactive` wizard
- **Configuration File Support**: YAML/JSON config files
- **Authentication System**: JWT, Session, and OAuth2 templates
- **OpenAPI/Swagger Integration**: drf-spectacular with Swagger UI and ReDoc
- **Add Command**: `dual_apps add app <name>` to add apps to existing projects
- **Security Enhancements**:
  - Rate limiting middleware
  - API throttling classes
  - Security headers middleware
  - Request logging middleware
- **Package Documentation**: Complete docs/ folder with guides
- **Info Command**: `dual_apps info` shows package details

### Changed
- Improved post-generation success messages with next steps
- Updated CLI with progress bars
- Better error handling and validation

### Fixed
- Various template syntax issues
- Missing imports in generated files

---

## [3.1.0] - 2024-01-XX

### Added
- Initial release of dual-apps v3
- Dual-layer architecture (Frontend HTMX + API DRF)
- CLI with Typer
- Jinja2 templates for code generation
- Docker support (dev/prod)
- GitHub Actions workflows
- 88% test coverage target
- OWASP security headers

### Features
- `dual_apps init app <name>` - Generate standalone app
- `dual_apps init project <name>` - Generate complete project
- UUID primary keys
- Timestamps (created_at, updated_at)
- Owner-based permissions (IsOwnerOrReadOnly)
- HTMX + Alpine.js + Tailwind frontend
- DRF ViewSets with filtering, search, ordering

---

## [3.0.0] - 2024-01-XX

### Changed
- Complete rewrite with new architecture
- Zumodra Convention v3.0

---

## Versioning

- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

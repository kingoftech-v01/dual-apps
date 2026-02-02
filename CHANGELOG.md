# Changelog

All notable changes to dual-apps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [3.0.0] - 2024-01-XX

### Changed
- Complete rewrite with new architecture
- Zumodra Convention v3.0

---

## Versioning

- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

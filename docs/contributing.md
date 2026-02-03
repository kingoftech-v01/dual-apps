# Contributing to dual-apps

Thank you for your interest in contributing to dual-apps!

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/dual-apps.git
cd dual-apps
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e .[dev]
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Development Workflow

1. Create a branch:
```bash
git checkout -b feature/my-feature
```

2. Make your changes

3. Run tests:
```bash
pytest
```

4. Run linters:
```bash
black .
ruff check --fix .
mypy src/dual_apps
```

5. Commit your changes:
```bash
git commit -m "Add my feature"
```

6. Push and create a pull request

## Code Style

- Use Black for formatting (line length: 88)
- Use Ruff for linting
- Use type hints
- Write docstrings (Google style)

## Testing

- Write tests for new features
- Maintain 85%+ coverage
- Test both success and error cases

```bash
# Run tests with coverage
pytest --cov=src/dual_apps --cov-report=html

# Run specific tests
pytest tests/test_cli.py -v
```

## Adding Templates

Templates are in `src/dual_apps/templates/`. When adding new templates:

1. Use Jinja2 syntax
2. Include header comment with generator info
3. Follow existing naming conventions
4. Add corresponding tests

## Pull Request Guidelines

1. Update documentation if needed
2. Add tests for new features
3. Update CHANGELOG.md
4. Keep PRs focused and small
5. Reference related issues

## Release Process

1. Update version in `src/dual_apps/__init__.py`
2. Update CHANGELOG.md
3. Create a git tag
4. GitHub Actions will publish to PyPI

## Questions?

- Open an issue for bugs
- Start a discussion for questions
- Check existing issues first

Thank you for contributing! 🎉

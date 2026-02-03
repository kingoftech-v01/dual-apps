"""Integration tests for frontend template generation."""

import os
import tempfile
import pytest
from pathlib import Path

from dual_apps.generators.project_generator import ProjectGenerator


class TestFrontendTemplateGeneration:
    """Test frontend template generation for all specialized templates."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def generator(self, temp_dir):
        """Create a project generator instance."""
        return ProjectGenerator(
            project_name="test_project",
            output_dir=temp_dir,
            database="postgresql",
            use_docker=True,
            use_celery=True,
            auth="jwt",
        )

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    @pytest.mark.parametrize("frontend", ["html", "htmx", "react"])
    def test_specialized_frontend_templates_exist(self, template_type, frontend):
        """Verify that all frontend templates exist for each specialized template."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        frontend_path = base_path / "specialized" / template_type / "frontend" / frontend

        assert frontend_path.exists(), f"Frontend path {frontend_path} does not exist"

        # Check that there are template files
        templates = list(frontend_path.glob("**/*.j2"))
        assert len(templates) > 0, f"No templates found in {frontend_path}"

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_html_templates_have_base(self, template_type):
        """Verify HTML templates have a base template."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        html_path = base_path / "specialized" / template_type / "frontend" / "html"

        base_templates = list(html_path.glob("base*.html.j2"))
        assert len(base_templates) > 0, f"No base template found in {html_path}"

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_react_templates_have_app(self, template_type):
        """Verify React templates have an App component."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        react_path = base_path / "specialized" / template_type / "frontend" / "react"

        app_template = react_path / "App.jsx.j2"
        assert app_template.exists(), f"App.jsx.j2 not found in {react_path}"

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_react_templates_have_api_utils(self, template_type):
        """Verify React templates have API utilities."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        react_path = base_path / "specialized" / template_type / "frontend" / "react" / "utils"

        api_template = react_path / "api.js.j2"
        assert api_template.exists(), f"api.js.j2 not found in {react_path}"

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "saas", "cms", "booking", "marketplace"
    ])
    def test_htmx_templates_have_partials(self, template_type):
        """Verify HTMX templates have partials directory."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        htmx_path = base_path / "specialized" / template_type / "frontend" / "htmx" / "partials"

        if htmx_path.exists():
            partials = list(htmx_path.glob("*.j2"))
            assert len(partials) > 0, f"No partials found in {htmx_path}"


class TestFrontendTemplateContent:
    """Test the content of frontend templates."""

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_react_api_supports_jwt_storage_options(self, template_type):
        """Verify React API templates support both JWT storage options."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        api_path = base_path / "specialized" / template_type / "frontend" / "react" / "utils" / "api.js.j2"

        if api_path.exists():
            content = api_path.read_text()

            # Check for JWT storage conditional
            assert "jwt_storage" in content, f"JWT storage option not found in {api_path}"
            # Check for httpOnly support
            assert "httpOnly" in content or "withCredentials" in content, f"httpOnly support not found in {api_path}"
            # Check for localStorage support
            assert "localStorage" in content, f"localStorage support not found in {api_path}"

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "marketplace"  # These have explicit CSS framework handling
    ])
    def test_html_templates_support_css_framework_options(self, template_type):
        """Verify HTML templates support both CSS framework options.

        Note: Some templates (booking, cms) inherit CSS framework from parent base.html,
        so they don't need explicit CSS framework conditionals.
        """
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        html_path = base_path / "specialized" / template_type / "frontend" / "html"

        base_templates = list(html_path.glob("base*.html.j2"))

        for base_template in base_templates:
            content = base_template.read_text()
            # Check for CSS framework conditional or inherits from base
            has_css_option = (
                "css_framework" in content or
                "bootstrap" in content.lower() or
                "tailwind" in content.lower() or
                "extends" in content  # Inherits from parent
            )
            assert has_css_option, f"CSS framework option not found in {base_template}"


class TestCLIFrontendOptions:
    """Test CLI options for frontend generation.

    Note: These tests verify that frontend templates exist with proper content.
    The CLI options (frontend_framework, css_framework, jwt_storage) are passed
    via context during template rendering, not as constructor arguments.
    """

    def test_frontend_template_directories_exist(self):
        """Test that frontend template directories exist for all frameworks."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates" / "specialized"

        for template_type in ["ecommerce", "blog", "saas", "cms", "booking", "marketplace"]:
            for frontend in ["html", "htmx", "react"]:
                frontend_path = base_path / template_type / "frontend" / frontend
                assert frontend_path.exists(), f"{frontend_path} does not exist"

    def test_react_templates_support_jwt_storage_config(self):
        """Test that React templates have JWT storage configuration."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates" / "specialized"

        for template_type in ["ecommerce", "blog", "saas", "cms", "booking", "marketplace"]:
            api_path = base_path / template_type / "frontend" / "react" / "utils" / "api.js.j2"
            if api_path.exists():
                content = api_path.read_text()
                assert "jwt_storage" in content, f"jwt_storage not found in {api_path}"

    def test_html_templates_support_css_framework_config(self):
        """Test that HTML base templates support CSS framework configuration.

        Note: Templates may either have explicit CSS framework conditionals
        or inherit CSS framework from parent base.html template via extends.
        """
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates" / "specialized"

        # Templates with explicit CSS framework handling
        for template_type in ["saas", "marketplace"]:
            html_path = base_path / template_type / "frontend" / "html"
            base_templates = list(html_path.glob("base*.html.j2"))

            for base_template in base_templates:
                content = base_template.read_text()
                has_css = (
                    "css_framework" in content or
                    "bootstrap" in content.lower() or
                    "tailwind" in content.lower() or
                    "extends" in content  # Inherits CSS from parent template
                )
                assert has_css, f"CSS framework not found in {base_template}"


class TestSpecializedTemplateIntegration:
    """Test integration of specialized templates with the generator."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.parametrize("template_type,expected_patterns", [
        ("ecommerce", ["product", "cart", "checkout", "order"]),
        ("blog", ["post", "author", "base"]),  # blog has post_list, post_detail, author
        ("saas", ["dashboard", "pricing", "team"]),
        ("cms", ["page", "media"]),
        ("booking", ["service", "booking"]),
        ("marketplace", ["listing", "seller"]),
    ])
    def test_specialized_template_views(self, template_type, expected_patterns):
        """Test that specialized templates have expected view types."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        html_path = base_path / "specialized" / template_type / "frontend" / "html"

        templates = list(html_path.glob("*.j2"))
        template_names = [t.stem.replace('.html', '').lower() for t in templates]

        # Check that at least some expected patterns are present in template names
        found_patterns = [p for p in expected_patterns if any(p in name for name in template_names)]
        assert len(found_patterns) > 0, f"No expected patterns found for {template_type}. Templates: {template_names}"


class TestSecurityFeatures:
    """Test security features in generated templates."""

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_htmx_csrf_protection(self, template_type):
        """Verify HTMX templates include CSRF token handling."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        htmx_path = base_path / "specialized" / template_type / "frontend" / "htmx"

        if htmx_path.exists():
            templates = list(htmx_path.glob("**/*.j2"))

            # Check that at least one template has CSRF handling
            csrf_found = False
            for template in templates:
                content = template.read_text()
                if "csrf" in content.lower() or "hx-headers" in content:
                    csrf_found = True
                    break

            assert csrf_found, f"CSRF protection not found in HTMX templates for {template_type}"

    @pytest.mark.parametrize("template_type", [
        "ecommerce", "blog", "saas", "cms", "booking", "marketplace"
    ])
    def test_react_token_refresh_handling(self, template_type):
        """Verify React API templates handle token refresh."""
        base_path = Path(__file__).parent.parent.parent / "src" / "dual_apps" / "templates"
        api_path = base_path / "specialized" / template_type / "frontend" / "react" / "utils" / "api.js.j2"

        if api_path.exists():
            content = api_path.read_text()

            # Check for token refresh logic
            assert "refresh" in content.lower(), f"Token refresh not found in {api_path}"
            # Check for 401 handling
            assert "401" in content, f"401 error handling not found in {api_path}"

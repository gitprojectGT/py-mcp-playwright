"""
Example website UI tests demonstrating playwright-test-generator agent capabilities.
This test suite shows comprehensive web application testing patterns.
"""

import pytest
from playwright.sync_api import Page, expect


class TestExampleWebsite:
    """Comprehensive UI tests for web applications."""
    
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_homepage_loads(self, page_sync: Page):
        """Test that the homepage loads correctly."""
        page_sync.goto("https://example.com")
        
        # Verify page title
        expect(page_sync).to_have_title("Example Domain")
        
        # Verify main heading is visible
        heading = page_sync.get_by_role("heading", name="Example Domain")
        expect(heading).to_be_visible()
        
        # Verify page content
        content = page_sync.get_by_text("This domain is for use in illustrative examples")
        expect(content).to_be_visible()
    
    @pytest.mark.ui
    def test_navigation_links(self, page_sync: Page):
        """Test navigation links functionality."""
        page_sync.goto("https://example.com")
        
        # Find and verify "More information..." link
        info_link = page_sync.get_by_role("link", name="More information...")
        expect(info_link).to_be_visible()
        expect(info_link).to_have_attribute("href", "https://www.iana.org/domains/example")
    
    @pytest.mark.ui
    def test_page_accessibility(self, page_sync: Page):
        """Test basic accessibility features."""
        page_sync.goto("https://example.com")
        
        # Check for proper heading structure
        h1_heading = page_sync.locator("h1")
        expect(h1_heading).to_be_visible()
        
        # Verify page has proper lang attribute
        html_element = page_sync.locator("html")
        expect(html_element).to_have_attribute("lang")
    
    @pytest.mark.ui
    @pytest.mark.slow
    def test_page_performance(self, page_sync: Page):
        """Test page loading performance."""
        # Navigate and measure load time
        page_sync.goto("https://example.com")
        
        # Wait for network to be idle
        page_sync.wait_for_load_state("networkidle")
        
        # Verify page loaded successfully
        expect(page_sync).to_have_title("Example Domain")
        
        # Check that there are no console errors
        console_messages = []
        page_sync.on("console", lambda msg: console_messages.append(msg))
        
        # Reload to capture any console messages
        page_sync.reload()
        page_sync.wait_for_load_state("networkidle")
        
        # Filter for error messages
        error_messages = [msg for msg in console_messages if msg.type == "error"]
        assert len(error_messages) == 0, f"Console errors found: {error_messages}"
    
    @pytest.mark.ui
    def test_responsive_design(self, page_sync: Page):
        """Test responsive design on different viewport sizes."""
        # Test desktop viewport
        page_sync.set_viewport_size({"width": 1920, "height": 1080})
        page_sync.goto("https://example.com")
        
        heading = page_sync.get_by_role("heading", name="Example Domain")
        expect(heading).to_be_visible()
        
        # Test tablet viewport
        page_sync.set_viewport_size({"width": 768, "height": 1024})
        expect(heading).to_be_visible()
        
        # Test mobile viewport
        page_sync.set_viewport_size({"width": 375, "height": 667})
        expect(heading).to_be_visible()
    
    @pytest.mark.ui
    def test_page_screenshots(self, page_sync: Page):
        """Test screenshot functionality and visual regression."""
        page_sync.goto("https://example.com")
        page_sync.wait_for_load_state("networkidle")
        
        # Take full page screenshot
        screenshot_path = "test-results/screenshots/example_homepage.png"
        page_sync.screenshot(path=screenshot_path, full_page=True)
        
        # Take element screenshot
        heading = page_sync.get_by_role("heading", name="Example Domain")
        heading.screenshot(path="test-results/screenshots/example_heading.png")
        
        # Verify screenshots were created
        import os
        assert os.path.exists(screenshot_path)


class TestFormInteraction:
    """Tests for form interactions and user inputs."""
    
    @pytest.mark.ui
    def test_search_functionality(self, page_sync: Page):
        """Test search form if available on the page."""
        page_sync.goto("https://httpbin.org/forms/post")
        
        # Fill out form fields
        customer_name = page_sync.get_by_label("Customer name")
        customer_name.fill("Test Customer")
        
        telephone = page_sync.get_by_label("Telephone")
        telephone.fill("123-456-7890")
        
        email = page_sync.get_by_label("E-mail address")
        email.fill("test@example.com")
        
        # Select from dropdown
        size_select = page_sync.get_by_label("Pizza size")
        size_select.select_option("large")
        
        # Check checkboxes
        bacon_checkbox = page_sync.get_by_label("Bacon")
        bacon_checkbox.check()
        
        # Submit form
        submit_button = page_sync.get_by_role("button", name="Submit order")
        submit_button.click()
        
        # Verify form submission
        expect(page_sync).to_have_url("https://httpbin.org/post")
        
        # Verify form data in response
        response_text = page_sync.locator("pre").text_content()
        assert "Test Customer" in response_text
        assert "test@example.com" in response_text
"""
Example usage of the testing framework for UI testing.
This demonstrates how to use the UI testing components.
"""

from playwright.sync_api import sync_playwright
from src.test_helpers import UITestHelper, TestDataGenerator
from src.config import get_browser_config


def example_basic_ui_testing():
    """Example of basic UI testing."""
    print("=== Basic UI Testing Example ===")
    
    config = get_browser_config()
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(**config.get_launch_options())
        context = browser.new_context(**config.get_context_options())
        page = context.new_page()
        
        helper = UITestHelper(page)
        
        try:
            print("--- Testing basic page navigation ---")
            load_time = helper.measure_page_load_time("https://example.com")
            print(f"Page load time: {load_time:.3f}s")
            
            # Check page title
            title = page.title()
            print(f"Page title: {title}")
            
            # Take screenshot
            print("--- Taking screenshots ---")
            page.screenshot(path="test-results/screenshots/example_page.png")
            print("Screenshot saved to test-results/screenshots/example_page.png")
            
            # Test element interactions
            print("--- Testing element interactions ---")
            if helper.wait_for_element_visible("h1", timeout=5000):
                print("✅ Main heading found and visible")
                
                # Take element screenshot
                helper.take_element_screenshot("h1", "test-results/screenshots/heading.png")
                print("Heading screenshot saved")
            else:
                print("❌ Main heading not found")
            
            # Test accessibility
            print("--- Testing accessibility ---")
            accessibility_results = helper.check_accessibility()
            print("Accessibility check results:")
            for check, passed in accessibility_results.items():
                status = "✅" if passed else "❌"
                print(f"  {check}: {status}")
                
        finally:
            context.close()
            browser.close()


def example_form_testing():
    """Example of form testing."""
    print("\n=== Form Testing Example ===")
    
    config = get_browser_config()
    data_generator = TestDataGenerator()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**config.get_launch_options())
        context = browser.new_context(**config.get_context_options())
        page = context.new_page()
        
        helper = UITestHelper(page)
        
        try:
            # Navigate to a form page
            page.goto("https://httpbin.org/forms/post")
            
            print("--- Testing form filling ---")
            
            # Generate test data
            user_data = data_generator.generate_user_data()
            
            # Fill form using helper
            form_data = {
                "custname": f"{user_data['first_name']} {user_data['last_name']}",
                "custtel": user_data['phone'],
                "custemail": user_data['email']
            }
            
            helper.fill_form_data(form_data)
            print(f"Form filled with data: {form_data}")
            
            # Select dropdown option
            page.select_option("select[name='size']", "large")
            print("Selected 'large' from size dropdown")
            
            # Check checkboxes
            page.check("input[value='bacon']")
            page.check("input[value='cheese']")
            print("Checked bacon and cheese options")
            
            # Take screenshot before submission
            page.screenshot(path="test-results/screenshots/form_filled.png")
            
            # Submit form
            page.click("input[type='submit']")
            
            # Wait for response and verify
            page.wait_for_url("**/post")
            print("✅ Form submitted successfully")
            
            # Verify form data in response
            response_text = page.locator("pre").text_content()
            if user_data['first_name'] in response_text:
                print("✅ Form data verified in response")
            else:
                print("❌ Form data not found in response")
                
        finally:
            context.close()
            browser.close()


def example_responsive_testing():
    """Example of responsive design testing."""
    print("\n=== Responsive Design Testing Example ===")
    
    config = get_browser_config()
    viewports = [
        {"name": "Desktop", "width": 1920, "height": 1080},
        {"name": "Tablet", "width": 768, "height": 1024},
        {"name": "Mobile", "width": 375, "height": 667}
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**config.get_launch_options())
        
        for viewport in viewports:
            print(f"--- Testing {viewport['name']} viewport ({viewport['width']}x{viewport['height']}) ---")
            
            context = browser.new_context(
                viewport={"width": viewport['width'], "height": viewport['height']}
            )
            page = context.new_page()
            helper = UITestHelper(page)
            
            try:
                page.goto("https://example.com")
                
                # Check if main elements are visible
                if helper.wait_for_element_visible("h1", timeout=5000):
                    print(f"✅ Main heading visible on {viewport['name']}")
                else:
                    print(f"❌ Main heading not visible on {viewport['name']}")
                
                # Take viewport-specific screenshot
                screenshot_path = f"test-results/screenshots/example_{viewport['name'].lower()}.png"
                page.screenshot(path=screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
                
                # Check for horizontal scrollbars (indicator of layout issues)
                page_width = page.evaluate("document.documentElement.scrollWidth")
                viewport_width = viewport['width']
                
                if page_width <= viewport_width:
                    print(f"✅ No horizontal scroll on {viewport['name']}")
                else:
                    print(f"⚠️  Horizontal scroll detected on {viewport['name']} ({page_width}px content in {viewport_width}px viewport)")
                
            finally:
                context.close()
        
        browser.close()


def example_error_monitoring():
    """Example of monitoring console errors and network issues."""
    print("\n=== Error Monitoring Example ===")
    
    config = get_browser_config()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**config.get_launch_options())
        context = browser.new_context(**config.get_context_options())
        page = context.new_page()
        
        helper = UITestHelper(page)
        
        # Track console messages and network failures
        console_messages = []
        network_failures = []
        
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text
            })
        
        def handle_response(response):
            if response.status >= 400:
                network_failures.append({
                    "url": response.url,
                    "status": response.status
                })
        
        page.on("console", handle_console)
        page.on("response", handle_response)
        
        try:
            print("--- Monitoring errors during page load ---")
            page.goto("https://example.com")
            page.wait_for_load_state("networkidle")
            
            # Check for console errors
            error_messages = [msg for msg in console_messages if msg["type"] == "error"]
            if error_messages:
                print(f"❌ Found {len(error_messages)} console errors:")
                for error in error_messages:
                    print(f"  - {error['text']}")
            else:
                print("✅ No console errors found")
            
            # Check for network failures
            if network_failures:
                print(f"❌ Found {len(network_failures)} network failures:")
                for failure in network_failures:
                    print(f"  - {failure['url']}: {failure['status']}")
            else:
                print("✅ No network failures found")
            
            # Check for warnings
            warning_messages = [msg for msg in console_messages if msg["type"] == "warning"]
            if warning_messages:
                print(f"⚠️  Found {len(warning_messages)} console warnings:")
                for warning in warning_messages[:3]:  # Show first 3
                    print(f"  - {warning['text']}")
            
        finally:
            context.close()
            browser.close()


def example_performance_monitoring():
    """Example of performance monitoring."""
    print("\n=== Performance Monitoring Example ===")
    
    config = get_browser_config()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**config.get_launch_options())
        context = browser.new_context(**config.get_context_options())
        page = context.new_page()
        
        helper = UITestHelper(page)
        
        try:
            print("--- Measuring page performance ---")
            
            # Measure different loading stages
            import time
            
            start_time = time.time()
            page.goto("https://example.com")
            
            dom_loaded_time = time.time()
            page.wait_for_load_state("domcontentloaded")
            
            network_idle_time = time.time()
            page.wait_for_load_state("networkidle")
            
            total_time = network_idle_time - start_time
            dom_time = dom_loaded_time - start_time
            network_time = network_idle_time - dom_loaded_time
            
            print(f"DOM loaded: {dom_time:.3f}s")
            print(f"Network idle: {network_time:.3f}s")
            print(f"Total load time: {total_time:.3f}s")
            
            # Performance assertions
            if total_time < 5.0:
                print("✅ Page load time within acceptable limits")
            else:
                print("❌ Page load time too slow")
            
            # Measure JavaScript performance
            js_performance = page.evaluate("""
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    return {
                        dns_lookup: perfData.domainLookupEnd - perfData.domainLookupStart,
                        tcp_connect: perfData.connectEnd - perfData.connectStart,
                        server_response: perfData.responseEnd - perfData.requestStart,
                        dom_processing: perfData.domComplete - perfData.responseEnd
                    };
                }
            """)
            
            print("\nDetailed performance metrics:")
            for metric, value in js_performance.items():
                print(f"  {metric}: {value:.3f}ms")
                
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    # Ensure test-results directory exists
    import os
    os.makedirs("test-results/screenshots", exist_ok=True)
    
    # Run all examples
    example_basic_ui_testing()
    example_form_testing()
    example_responsive_testing()
    example_error_monitoring()
    example_performance_monitoring()
    
    print("\n=== All UI testing examples completed ===")
    print("Check test-results/screenshots/ for generated screenshots")
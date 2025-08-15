"""
Test helper utilities for Playwright testing framework.
"""

import json
import time
import uuid
import random
import string
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from faker import Faker
from playwright.sync_api import Page, APIRequestContext, Response
from playwright.async_api import Page as AsyncPage, APIRequestContext as AsyncAPIRequestContext

from .config import APIConfig, PerformanceConfig


class TestDataGenerator:
    """Generate test data for various testing scenarios."""
    
    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        
    def generate_user_data(self) -> Dict[str, Any]:
        """Generate realistic user data."""
        return {
            "id": self.fake.random_int(min=1, max=10000),
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "phone": self.fake.phone_number(),
            "address": {
                "street": self.fake.street_address(),
                "city": self.fake.city(),
                "state": self.fake.state(),
                "zip_code": self.fake.postcode(),
                "country": self.fake.country()
            },
            "date_of_birth": self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "created_at": self.fake.date_time_this_year().isoformat(),
            "is_active": self.fake.boolean(chance_of_getting_true=80)
        }
    
    def generate_post_data(self) -> Dict[str, Any]:
        """Generate blog post data."""
        return {
            "title": self.fake.sentence(nb_words=6),
            "body": self.fake.text(max_nb_chars=500),
            "userId": self.fake.random_int(min=1, max=100),
            "tags": [self.fake.word() for _ in range(self.fake.random_int(min=1, max=5))],
            "published": self.fake.boolean(chance_of_getting_true=70),
            "created_at": self.fake.date_time_this_month().isoformat()
        }
    
    def generate_product_data(self) -> Dict[str, Any]:
        """Generate e-commerce product data."""
        return {
            "name": self.fake.catch_phrase(),
            "description": self.fake.text(max_nb_chars=200),
            "price": round(self.fake.random.uniform(10.0, 1000.0), 2),
            "category": self.fake.word(),
            "sku": self.fake.bothify(text="??-####"),
            "stock_quantity": self.fake.random_int(min=0, max=1000),
            "weight": round(self.fake.random.uniform(0.1, 50.0), 2),
            "dimensions": {
                "length": round(self.fake.random.uniform(1.0, 100.0), 1),
                "width": round(self.fake.random.uniform(1.0, 100.0), 1),
                "height": round(self.fake.random.uniform(1.0, 100.0), 1)
            }
        }
    
    def generate_random_string(self, length: int = 10) -> str:
        """Generate random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def generate_uuid(self) -> str:
        """Generate UUID string."""
        return str(uuid.uuid4())
    
    def generate_invalid_data(self) -> Dict[str, Any]:
        """Generate intentionally invalid data for negative testing."""
        return {
            "empty_string": "",
            "null_value": None,
            "invalid_email": "not-an-email",
            "negative_number": -1,
            "very_long_string": "x" * 10000,
            "sql_injection": "'; DROP TABLE users; --",
            "xss_payload": "<script>alert('xss')</script>",
            "invalid_date": "not-a-date",
            "invalid_json": "invalid json content"
        }


class APITestHelper:
    """Helper class for API testing operations."""
    
    def __init__(self, api_context: Union[APIRequestContext, AsyncAPIRequestContext]):
        self.api_context = api_context
        self.config = APIConfig()
    
    def make_request_with_retry(self, method: str, url: str, **kwargs) -> Response:
        """Make API request with retry logic."""
        for attempt in range(self.config.retry_count):
            try:
                response = getattr(self.api_context, method.lower())(url, **kwargs)
                if response.status < 500:  # Don't retry client errors
                    return response
            except Exception as e:
                if attempt == self.config.retry_count - 1:
                    raise e
                time.sleep(self.config.retry_delay * (attempt + 1))
        
        return response
    
    def validate_response_schema(self, response: Response, expected_fields: List[str]) -> bool:
        """Validate that response contains expected fields."""
        try:
            data = response.json()
            if isinstance(data, list) and data:
                data = data[0]  # Check first item if it's a list
            
            for field in expected_fields:
                if field not in data:
                    return False
            return True
        except (json.JSONDecodeError, KeyError, IndexError):
            return False
    
    def validate_response_status(self, response: Response, expected_status: int) -> bool:
        """Validate response status code."""
        return response.status == expected_status
    
    def extract_response_data(self, response: Response) -> Any:
        """Safely extract JSON data from response."""
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text()
    
    def create_authenticated_headers(self, token: str, token_type: str = "Bearer") -> Dict[str, str]:
        """Create authentication headers."""
        headers = self.config.headers.copy()
        headers["Authorization"] = f"{token_type} {token}"
        return headers
    
    def measure_response_time(self, method: str, url: str, **kwargs) -> tuple[Response, float]:
        """Measure API response time."""
        start_time = time.time()
        response = getattr(self.api_context, method.lower())(url, **kwargs)
        end_time = time.time()
        response_time = end_time - start_time
        return response, response_time


class UITestHelper:
    """Helper class for UI testing operations."""
    
    def __init__(self, page: Union[Page, AsyncPage]):
        self.page = page
    
    def wait_for_element_visible(self, selector: str, timeout: int = 30000) -> bool:
        """Wait for element to be visible."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    def wait_for_element_hidden(self, selector: str, timeout: int = 30000) -> bool:
        """Wait for element to be hidden."""
        try:
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
            return True
        except Exception:
            return False
    
    def scroll_to_element(self, selector: str) -> None:
        """Scroll element into view."""
        element = self.page.locator(selector)
        element.scroll_into_view_if_needed()
    
    def take_element_screenshot(self, selector: str, path: str) -> None:
        """Take screenshot of specific element."""
        element = self.page.locator(selector)
        element.screenshot(path=path)
    
    def fill_form_data(self, form_data: Dict[str, str]) -> None:
        """Fill form with provided data."""
        for field_name, value in form_data.items():
            # Try different selector strategies
            selectors = [
                f"[name='{field_name}']",
                f"#{field_name}",
                f"[data-testid='{field_name}']"
            ]
            
            filled = False
            for selector in selectors:
                try:
                    element = self.page.locator(selector)
                    if element.count() > 0:
                        element.fill(value)
                        filled = True
                        break
                except Exception:
                    continue
            
            if not filled:
                # Try by label text
                try:
                    self.page.get_by_label(field_name).fill(value)
                except Exception:
                    pass
    
    def check_accessibility(self) -> Dict[str, Any]:
        """Basic accessibility checks."""
        results = {
            "has_title": bool(self.page.title()),
            "has_lang_attribute": bool(self.page.locator("html[lang]").count()),
            "has_main_heading": bool(self.page.locator("h1").count()),
            "images_have_alt": True,
            "links_have_text": True
        }
        
        # Check images have alt text
        images = self.page.locator("img")
        for i in range(images.count()):
            img = images.nth(i)
            if not img.get_attribute("alt"):
                results["images_have_alt"] = False
                break
        
        # Check links have accessible text
        links = self.page.locator("a")
        for i in range(links.count()):
            link = links.nth(i)
            if not link.text_content().strip() and not link.get_attribute("aria-label"):
                results["links_have_text"] = False
                break
        
        return results
    
    def measure_page_load_time(self, url: str) -> float:
        """Measure page load time."""
        start_time = time.time()
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        end_time = time.time()
        return end_time - start_time
    
    def get_console_errors(self) -> List[str]:
        """Capture console errors."""
        errors = []
        
        def handle_console_message(msg):
            if msg.type == "error":
                errors.append(msg.text)
        
        self.page.on("console", handle_console_message)
        return errors


class PerformanceHelper:
    """Helper class for performance testing."""
    
    def __init__(self):
        self.config = PerformanceConfig()
    
    def measure_multiple_requests(self, 
                                request_func, 
                                count: int = 10,
                                concurrent: bool = False) -> Dict[str, Any]:
        """Measure performance of multiple requests."""
        if concurrent:
            return self._measure_concurrent_requests(request_func, count)
        else:
            return self._measure_sequential_requests(request_func, count)
    
    def _measure_sequential_requests(self, request_func, count: int) -> Dict[str, Any]:
        """Measure sequential requests."""
        response_times = []
        errors = 0
        
        for _ in range(count):
            try:
                start_time = time.time()
                request_func()
                end_time = time.time()
                response_times.append(end_time - start_time)
            except Exception:
                errors += 1
        
        return {
            "total_requests": count,
            "successful_requests": count - errors,
            "error_count": errors,
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "response_times": response_times
        }
    
    def _measure_concurrent_requests(self, request_func, count: int) -> Dict[str, Any]:
        """Measure concurrent requests using threading."""
        import threading
        import queue
        
        result_queue = queue.Queue()
        threads = []
        
        def worker():
            try:
                start_time = time.time()
                request_func()
                end_time = time.time()
                result_queue.put(("success", end_time - start_time))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # Start threads
        for _ in range(count):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        response_times = []
        errors = 0
        
        while not result_queue.empty():
            result_type, value = result_queue.get()
            if result_type == "success":
                response_times.append(value)
            else:
                errors += 1
        
        return {
            "total_requests": count,
            "successful_requests": len(response_times),
            "error_count": errors,
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "response_times": response_times
        }
    
    def assert_performance_requirements(self, 
                                      response_time: float,
                                      max_response_time: Optional[float] = None) -> bool:
        """Assert performance requirements are met."""
        max_time = max_response_time or self.config.max_response_time
        return response_time <= max_time
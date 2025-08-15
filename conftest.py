import pytest
import os
import asyncio
from typing import Generator, AsyncGenerator
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright.sync_api import sync_playwright, Browser as SyncBrowser, BrowserContext as SyncBrowserContext, Page as SyncPage
try:
    from playwright_config import get_browser_config, get_context_config, PLAYWRIGHT_CONFIG
except ImportError:
    # Fallback configuration if playwright_config is not available
    PLAYWRIGHT_CONFIG = {
        "base_url": "http://localhost:3000",
        "headless": True,
        "timeout": 30000
    }
    
    def get_browser_config():
        return {"headless": True, "timeout": 30000}
    
    def get_context_config():
        return {"viewport": {"width": 1280, "height": 720}}

# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on file location."""
    for item in items:
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)

@pytest.fixture(scope="session")
def browser_config():
    """Browser configuration fixture."""
    return get_browser_config()

@pytest.fixture(scope="session")
def context_config():
    """Context configuration fixture."""
    return get_context_config()

# Sync fixtures
@pytest.fixture(scope="session")
def playwright_sync():
    """Sync Playwright instance."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser_sync(playwright_sync, browser_config) -> Generator[SyncBrowser, None, None]:
    """Sync browser instance."""
    browser = playwright_sync.chromium.launch(**browser_config)
    yield browser
    browser.close()

@pytest.fixture
def context_sync(browser_sync, context_config) -> Generator[SyncBrowserContext, None, None]:
    """Sync browser context."""
    context = browser_sync.new_context(**context_config)
    yield context
    context.close()

@pytest.fixture
def page_sync(context_sync) -> Generator[SyncPage, None, None]:
    """Sync page instance."""
    page = context_sync.new_page()
    yield page
    page.close()

# Async fixtures
@pytest.fixture(scope="session")
async def playwright_async():
    """Async Playwright instance."""
    async with async_playwright() as p:
        yield p

@pytest.fixture(scope="session")
async def browser_async(playwright_async, browser_config) -> AsyncGenerator[Browser, None]:
    """Async browser instance."""
    browser = await playwright_async.chromium.launch(**browser_config)
    yield browser
    await browser.close()

@pytest.fixture
async def context_async(browser_async, context_config) -> AsyncGenerator[BrowserContext, None]:
    """Async browser context."""
    context = await browser_async.new_context(**context_config)
    yield context
    await context.close()

@pytest.fixture
async def page_async(context_async) -> AsyncGenerator[Page, None]:
    """Async page instance."""
    page = await context_async.new_page()
    yield page
    await page.close()

# API testing fixtures
@pytest.fixture
def api_context_sync(playwright_sync):
    """API request context for sync tests."""
    context = playwright_sync.request.new_context(
        base_url=PLAYWRIGHT_CONFIG["base_url"],
        extra_http_headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    yield context
    context.dispose()

@pytest.fixture
async def api_context_async(playwright_async):
    """API request context for async tests."""
    context = await playwright_async.request.new_context(
        base_url=PLAYWRIGHT_CONFIG["base_url"],
        extra_http_headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    yield context
    await context.dispose()

# Utility fixtures
@pytest.fixture(scope="session")
def base_url():
    """Base URL for testing."""
    return PLAYWRIGHT_CONFIG["base_url"]

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    os.makedirs("test-results", exist_ok=True)
    os.makedirs("test-results/screenshots", exist_ok=True)
    os.makedirs("test-results/videos", exist_ok=True)
    os.makedirs("test-results/traces", exist_ok=True)
    yield
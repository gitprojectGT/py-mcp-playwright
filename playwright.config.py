from playwright.sync_api import Playwright
import os

def pytest_configure(config):
    """Configure pytest with Playwright settings."""
    pass

# Playwright configuration
PLAYWRIGHT_CONFIG = {
    "headless": os.getenv("HEADLESS", "true").lower() == "true",
    "slow_mo": int(os.getenv("SLOW_MO", "0")),
    "timeout": int(os.getenv("TIMEOUT", "30000")),
    "browser_timeout": int(os.getenv("BROWSER_TIMEOUT", "30000")),
    "browsers": ["chromium", "firefox", "webkit"],
    "base_url": os.getenv("BASE_URL", "http://localhost:3000"),
    "screenshot_on_failure": True,
    "video_on_failure": True,
    "trace_on_failure": True,
}

def get_browser_config():
    """Get browser configuration for Playwright."""
    return {
        "headless": PLAYWRIGHT_CONFIG["headless"],
        "slow_mo": PLAYWRIGHT_CONFIG["slow_mo"],
        "timeout": PLAYWRIGHT_CONFIG["browser_timeout"],
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content",
        ] if os.getenv("CI") else [],
    }

def get_context_config():
    """Get context configuration for Playwright."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "accept_downloads": True,
        "record_video_dir": "test-results/videos/" if PLAYWRIGHT_CONFIG.get("video_on_failure") else None,
        "record_har_path": "test-results/har/" if os.getenv("RECORD_HAR") else None,
    }
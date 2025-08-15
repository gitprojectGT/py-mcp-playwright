"""
Configuration classes for the testing framework.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


class TestConfig(BaseModel):
    """Main test configuration."""
    
    headless: bool = Field(default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true")
    slow_mo: int = Field(default_factory=lambda: int(os.getenv("SLOW_MO", "0")))
    timeout: int = Field(default_factory=lambda: int(os.getenv("TIMEOUT", "30000")))
    browser_timeout: int = Field(default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30000")))
    base_url: str = Field(default_factory=lambda: os.getenv("BASE_URL", "http://localhost:3000"))
    screenshot_on_failure: bool = True
    video_on_failure: bool = True
    trace_on_failure: bool = True
    parallel_workers: int = Field(default_factory=lambda: int(os.getenv("PYTEST_WORKERS", "4")))


class BrowserConfig(BaseModel):
    """Browser-specific configuration."""
    
    browsers: List[str] = ["chromium", "firefox", "webkit"]
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone: str = "UTC"
    accept_downloads: bool = True
    bypass_csp: bool = False
    java_script_enabled: bool = True
    
    def get_launch_options(self) -> Dict[str, Any]:
        """Get browser launch options."""
        return {
            "headless": TestConfig().headless,
            "slow_mo": TestConfig().slow_mo,
            "timeout": TestConfig().browser_timeout,
            "args": self._get_browser_args(),
        }
    
    def _get_browser_args(self) -> List[str]:
        """Get browser arguments."""
        args = []
        if os.getenv("CI"):
            args.extend([
                "--no-sandbox",
                "--disable-dev-shm-usage", 
                "--disable-gpu",
                "--disable-web-security",
                "--allow-running-insecure-content",
            ])
        return args
    
    def get_context_options(self) -> Dict[str, Any]:
        """Get browser context options."""
        config = TestConfig()
        return {
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "accept_downloads": self.accept_downloads,
            "user_agent": self.user_agent,
            "locale": self.locale,
            "timezone_id": self.timezone,
            "bypass_csp": self.bypass_csp,
            "java_script_enabled": self.java_script_enabled,
            "record_video_dir": "test-results/videos/" if config.video_on_failure else None,
            "record_har_path": "test-results/har/" if os.getenv("RECORD_HAR") else None,
        }


class APIConfig(BaseModel):
    """API testing configuration."""
    
    base_url: str = Field(default_factory=lambda: os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com"))
    timeout: int = Field(default_factory=lambda: int(os.getenv("API_TIMEOUT", "30000")))
    retry_count: int = 3
    retry_delay: float = 1.0
    headers: Dict[str, str] = Field(default_factory=lambda: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Playwright-Testing-Framework/0.1.0"
    })
    
    def get_request_context_options(self) -> Dict[str, Any]:
        """Get API request context options."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "extra_http_headers": self.headers,
        }


@dataclass
class PerformanceConfig:
    """Performance testing configuration."""
    
    max_response_time: float = 5.0
    max_memory_usage: int = 512  # MB
    concurrent_users: int = 10
    load_test_duration: int = 60  # seconds
    think_time: float = 1.0  # seconds between requests


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""
    
    environment: str = os.getenv("TEST_ENV", "development")
    debug_mode: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_ci(self) -> bool:
        """Check if running in CI environment."""
        return bool(os.getenv("CI"))


def get_test_config() -> TestConfig:
    """Get the main test configuration."""
    return TestConfig()


def get_browser_config() -> BrowserConfig:
    """Get browser configuration."""
    return BrowserConfig()


def get_api_config() -> APIConfig:
    """Get API configuration."""
    return APIConfig()


def get_performance_config() -> PerformanceConfig:
    """Get performance configuration."""
    return PerformanceConfig()


def get_environment_config() -> EnvironmentConfig:
    """Get environment configuration."""
    return EnvironmentConfig()
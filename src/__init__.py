"""
Python Playwright MCP Testing Framework

A comprehensive testing framework using Playwright with MCP integration
for automated web application and API testing.
"""

__version__ = "0.1.0"
__author__ = "Playwright Test Generator"
__email__ = "test@example.com"

from .test_helpers import (
    TestDataGenerator,
    APITestHelper,
    UITestHelper,
    PerformanceHelper,
)

from .config import (
    TestConfig,
    BrowserConfig,
    APIConfig,
)

__all__ = [
    "TestDataGenerator",
    "APITestHelper", 
    "UITestHelper",
    "PerformanceHelper",
    "TestConfig",
    "BrowserConfig",
    "APIConfig",
]
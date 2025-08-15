# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Playwright testing project that integrates with MCP (Model Context Protocol). The project is designed for automated testing of web applications and APIs using Playwright with Python.

## Development Environment

- **Python Version**: 3.13.5
- **Virtual Environment**: Located in `.venv/` directory
- **IDE**: PyCharm configuration included

## Activation Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate

# Install dependencies (when available)
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Specialized Agents

This repository includes three specialized Claude Code agents for Playwright testing:

1. **playwright-test-generator**: Creates comprehensive Playwright tests for web applications and APIs
2. **playwright-api-test-creator**: Generates tests for API endpoints with full CRUD operations
3. **playwright-api-explorer**: Explores APIs systematically and generates comprehensive test suites

These agents follow a systematic approach:
- Always explore applications using Playwright MCP tools before generating tests
- Create tests in the `tests/` directory
- Use proper Playwright best practices (role-based locators, auto-waiting, etc.)
- Execute tests iteratively until they pass

## Test Structure

- Tests should be saved in the `tests/` directory
- Use descriptive filenames and test titles
- Follow Python naming conventions (snake_case)
- Implement proper setup/teardown using fixtures
- Include both positive and negative test cases

## Testing Workflow

1. Use MCP tools to explore the target application
2. Generate comprehensive test coverage
3. Execute tests to ensure they pass
4. Iterate and refine as needed
5. Maintain test independence and reliability
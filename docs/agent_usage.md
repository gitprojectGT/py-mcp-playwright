# Claude Code Agent Usage Guide

This document explains how to use the specialized Playwright testing agents included in this project.

## Overview

The project includes three specialized Claude Code agents designed for different aspects of Playwright testing:

1. **playwright-test-generator**: General-purpose test generation
2. **playwright-api-test-creator**: API-focused test creation
3. **playwright-api-explorer**: Systematic API exploration and testing

## Agent Descriptions

### playwright-test-generator

**Purpose**: Generate comprehensive Playwright tests for web applications or APIs

**Best Used For**:
- Testing new application features
- Creating UI interaction tests
- Generating comprehensive test coverage for web applications

**Key Features**:
- Systematic exploration before test generation
- Role-based locators (getByRole, getByLabel, getByText)
- Auto-retrying assertions
- Comprehensive coverage including edge cases
- Proper test structure with setup/teardown

**Example Usage**:
```
User: "I need to test the user registration endpoint at /api/users"
Assistant: "I'll use the playwright-test-generator agent to explore the endpoint and create comprehensive tests"
```

### playwright-api-test-creator

**Purpose**: Create comprehensive Playwright tests for API endpoints with full CRUD operations

**Best Used For**:
- Testing REST APIs with multiple HTTP methods
- Creating comprehensive API test suites
- Testing CRUD operations (GET, POST, PUT, PATCH, DELETE)

**Key Features**:
- Full HTTP method coverage
- Error handling and validation testing
- Authentication and authorization scenarios
- Data-driven test approaches
- Concurrent request testing

**Example Usage**:
```
User: "I need to test the JSONPlaceholder API with all HTTP methods"
Assistant: "I'll use the playwright-api-test-creator agent to explore the API and generate comprehensive tests."
```

### playwright-api-explorer

**Purpose**: Systematically explore APIs and generate comprehensive test suites for CRUD operations

**Best Used For**:
- Exploring new APIs to understand their structure
- Creating comprehensive test coverage for REST APIs
- Testing APIs like JSONPlaceholder or similar services

**Key Features**:
- Systematic API resource discovery
- TypeScript test implementation
- Comprehensive endpoint testing
- Error condition testing
- Response validation and schema checking

**Example Usage**:
```
User: "I need to test the API at https://reqres.in/ - can you explore it and create comprehensive tests?"
Assistant: "I'll use the playwright-api-explorer agent to first explore the API endpoints and then generate comprehensive Playwright tests for all the key functionality."
```

## When to Use Each Agent

### Use playwright-test-generator when:
- You have a web application that needs comprehensive UI testing
- You want to test user interactions and workflows
- You need both positive and negative test scenarios
- You're testing a mix of UI and API functionality

### Use playwright-api-test-creator when:
- You have specific API endpoints that need thorough testing
- You need to test all CRUD operations systematically
- You want advanced API testing patterns (auth, concurrency, performance)
- You're working with well-defined API specifications

### Use playwright-api-explorer when:
- You're working with a new API and need to understand its structure
- You want to systematically explore all available endpoints
- You need comprehensive coverage of an unfamiliar API
- You want TypeScript-based test implementations

## Agent Workflow

All agents follow a similar systematic approach:

1. **Exploration Phase**:
   - Navigate to the specified URL using Playwright MCP tools
   - Systematically explore available resources and functionality
   - Document observed behavior and structure

2. **Planning Phase**:
   - Identify all testable scenarios
   - Plan test cases for different HTTP methods and conditions
   - Consider edge cases and error scenarios

3. **Implementation Phase**:
   - Generate test files in the appropriate directory structure
   - Use Playwright best practices and patterns
   - Include comprehensive assertions and error handling

4. **Validation Phase**:
   - Execute generated tests to ensure they pass
   - Iterate and refine based on test results
   - Ensure tests are maintainable and reliable

## Best Practices

### For All Agents:
- Always provide specific URLs or endpoints to test
- Be clear about the scope of testing required
- Specify any authentication requirements
- Mention any specific browsers or environments to target

### Agent-Specific Tips:

**playwright-test-generator**:
- Provide context about the application's main functionality
- Mention any specific user workflows to test
- Specify accessibility requirements if needed

**playwright-api-test-creator**:
- Provide API documentation URLs if available
- Mention authentication methods used
- Specify any rate limiting or special requirements

**playwright-api-explorer**:
- Provide the base API URL for exploration
- Mention any API keys or authentication needed
- Specify the desired output format (Python vs TypeScript)

## Example Commands

### Requesting API Testing:
```
"Use the playwright-api-test-creator agent to create comprehensive tests for the user management API at https://api.example.com/users"
```

### Requesting UI Testing:
```
"Use the playwright-test-generator agent to create tests for the shopping cart functionality on https://shop.example.com"
```

### Requesting API Exploration:
```
"Use the playwright-api-explorer agent to explore and test the JSONPlaceholder API at https://jsonplaceholder.typicode.com"
```

## Output and Results

### Generated Files:
- Test files are saved in the `tests/` directory
- Organized by type (api/, ui/, integration/)
- Follow Python naming conventions (snake_case)

### Test Structure:
- Descriptive test names and documentation
- Proper setup and teardown using fixtures
- Comprehensive assertions and error handling
- Grouped related tests using test classes or describe blocks

### Quality Assurance:
- Tests are executed immediately after generation
- Issues are identified and resolved iteratively
- Tests are designed to be deterministic and reliable
- Proper cleanup and resource management
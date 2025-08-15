# Python Playwright MCP Testing Framework Makefile

.PHONY: help install install-dev setup test test-api test-ui test-integration test-smoke test-parallel test-coverage clean lint format type-check pre-commit run-examples docker-build docker-test docker-dev docker-clean

# Default target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Local Development:"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  setup          - Full project setup (install + browsers)"
	@echo "  test           - Run all tests"
	@echo "  test-api       - Run API tests only"
	@echo "  test-ui        - Run UI tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-smoke     - Run smoke tests only"
	@echo "  test-parallel  - Run tests in parallel"
	@echo "  test-coverage  - Run tests with coverage"
	@echo "  quick-test     - Run quick smoke tests"
	@echo ""
	@echo "Docker Operations:"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-test    - Run tests in Docker"
	@echo "  docker-api     - Run API tests in Docker"
	@echo "  docker-ui      - Run UI tests in Docker"
	@echo "  docker-dev     - Start Docker development environment"
	@echo "  docker-shell   - Open shell in Docker container"
	@echo "  docker-clean   - Clean Docker resources"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code"
	@echo "  type-check     - Run type checking"
	@echo "  pre-commit     - Run pre-commit hooks"
	@echo ""
	@echo "Utilities:"
	@echo "  run-examples   - Run example scripts"
	@echo "  clean          - Clean up generated files"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

setup: install-dev
	playwright install
	mkdir -p test-results/screenshots test-results/videos test-results/traces test-results/reports

# Testing targets
test:
	pytest -v

test-api:
	pytest -m api -v

test-ui:
	pytest -m ui -v

test-integration:
	pytest -m integration -v

test-smoke:
	pytest -m smoke -v

test-parallel:
	pytest -n auto -v

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80 -v

# Code quality targets
lint:
	flake8 src tests utils examples

format:
	black src tests utils examples
	isort src tests utils examples

type-check:
	mypy src

pre-commit: format lint type-check
	@echo "All pre-commit checks passed"

# Example execution
run-examples:
	@echo "Running API usage examples..."
	python examples/example_api_usage.py
	@echo "Running UI usage examples..."
	python examples/example_ui_usage.py

# Quick testing
quick-test:
	./scripts/quick-test.sh

# Docker targets
docker-build:
	./scripts/docker-tests.sh build

docker-test:
	./scripts/docker-tests.sh test

docker-api:
	./scripts/docker-tests.sh api

docker-ui:
	./scripts/docker-tests.sh ui

docker-dev:
	./scripts/docker-tests.sh dev

docker-shell:
	./scripts/docker-tests.sh shell

docker-clean:
	./scripts/docker-tests.sh clean

# Cleanup
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf test-results/*
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
# NewsDigest Makefile
# Common development and build commands

.PHONY: help install install-dev install-all clean test lint format type-check \
        build build-wheel build-sdist build-zip build-exe package package-release \
        docker docker-build docker-up docker-down docker-logs \
        docs docs-serve setup-models venv version release-patch release-minor release-major

# Default target
.DEFAULT_GOAL := help

# Python and pip commands
PYTHON := python3
PIP := pip
VENV := .venv
VENV_BIN := $(VENV)/bin

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(BLUE)NewsDigest Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make venv          # Create virtual environment"
	@echo "  make install-dev   # Install with dev dependencies"
	@echo "  make test          # Run tests"
	@echo "  make docker-up     # Start Docker containers"

# =============================================================================
# Environment Setup
# =============================================================================

venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Virtual environment created at $(VENV)$(NC)"
	@echo ""
	@echo "Activate with:"
	@echo "  source $(VENV)/bin/activate  # Linux/macOS"
	@echo "  $(VENV)\\Scripts\\activate   # Windows"

install: ## Install core dependencies
	@echo "$(BLUE)Installing core dependencies...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	pre-commit install
	@echo "$(GREEN)Development environment ready!$(NC)"

install-all: ## Install all dependencies (including ML)
	@echo "$(BLUE)Installing all dependencies (this may take a while)...$(NC)"
	$(PIP) install -r requirements-all.txt
	$(PIP) install -e .
	pre-commit install

setup-models: ## Download spaCy language models
	@echo "$(BLUE)Downloading spaCy models...$(NC)"
	$(PYTHON) -m spacy download en_core_web_sm
	@echo "$(GREEN)Models downloaded!$(NC)"

setup: venv ## Complete development setup
	@echo "$(BLUE)Running complete setup...$(NC)"
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements-dev.txt
	$(VENV_BIN)/pip install -e .
	$(VENV_BIN)/python -m spacy download en_core_web_sm
	$(VENV_BIN)/pre-commit install
	@echo "$(GREEN)Setup complete! Activate venv with: source $(VENV)/bin/activate$(NC)"

# =============================================================================
# Development
# =============================================================================

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ -v --cov=src/newsdigest --cov-report=html --cov-report=term

lint: ## Run linter (ruff)
	@echo "$(BLUE)Running linter...$(NC)"
	ruff check src/ tests/

format: ## Format code (ruff)
	@echo "$(BLUE)Formatting code...$(NC)"
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Running type checker...$(NC)"
	mypy src/

security-scan: ## Run security vulnerability scan (bandit)
	@echo "$(BLUE)Running security scan...$(NC)"
	bandit -r src/ -c pyproject.toml

check: lint type-check security-scan test ## Run all checks (lint, type-check, security, test)
	@echo "$(GREEN)All checks passed!$(NC)"

check-ci: lint type-check security-scan ## Run CI checks (no tests)
	@echo "$(GREEN)CI checks passed!$(NC)"

# =============================================================================
# Build & Packaging
# =============================================================================

build: ## Build distribution packages (wheel + sdist)
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build

build-wheel: ## Build wheel package only
	@echo "$(BLUE)Building wheel package...$(NC)"
	$(PYTHON) -m build --wheel

build-sdist: ## Build source distribution only
	@echo "$(BLUE)Building source distribution...$(NC)"
	$(PYTHON) -m build --sdist

build-zip: ## Build zip archive for distribution
	@echo "$(BLUE)Building zip archive...$(NC)"
	./scripts/package.sh --zip

build-exe: ## Build standalone executable (requires PyInstaller)
	@echo "$(BLUE)Building standalone executable...$(NC)"
	./scripts/package.sh --exe

package: ## Build all distributable packages (wheel, sdist, zip, exe)
	@echo "$(BLUE)Building all distributable packages...$(NC)"
	./scripts/package.sh --all

package-release: clean build-wheel build-sdist build-zip ## Build release packages (wheel, sdist, zip)
	@echo "$(GREEN)Release packages built in dist/$(NC)"

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleaned!$(NC)"

# =============================================================================
# Docker
# =============================================================================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose -f docker/docker-compose.yml build

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d api
	@echo "$(GREEN)API running at http://localhost:8080$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## View Docker logs
	docker-compose -f docker/docker-compose.yml logs -f

docker-shell: ## Open shell in Docker container
	docker-compose -f docker/docker-compose.yml run --rm newsdigest /bin/bash

# =============================================================================
# Documentation
# =============================================================================

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	mkdocs build

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	mkdocs serve

# =============================================================================
# Release (Semantic Versioning)
# =============================================================================

version: ## Show current version
	@cat VERSION

release-patch: ## Bump patch version (0.0.x)
	@echo "$(BLUE)Bumping patch version...$(NC)"
	bump2version patch
	@echo "$(GREEN)New version: $$(cat VERSION)$(NC)"

release-minor: ## Bump minor version (0.x.0)
	@echo "$(BLUE)Bumping minor version...$(NC)"
	bump2version minor
	@echo "$(GREEN)New version: $$(cat VERSION)$(NC)"

release-major: ## Bump major version (x.0.0)
	@echo "$(BLUE)Bumping major version...$(NC)"
	bump2version major
	@echo "$(GREEN)New version: $$(cat VERSION)$(NC)"

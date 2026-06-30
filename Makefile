.PHONY: help install format lint test check all clean

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install development dependencies and setup pre-commit
	./scripts/bootstrap.sh

format: ## Format code using Ruff
	ruff format .
	ruff check --fix .

lint: ## Run linters and type checkers
	ruff check .
	mypy backend examples

test: ## Run unit tests with coverage
	PYTHONPATH=. pytest

check: format lint test ## Run format, lint, and tests

all: check ## Same as check

clean: ## Clean up build artifacts and cache directories
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/ .coverage

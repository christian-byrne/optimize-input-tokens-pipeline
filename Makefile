.PHONY: help setup test clean install run demo verbose format lint

# Default target
help:
	@echo "LLM Cost Optimization - Available Commands"
	@echo "========================================="
	@echo "make setup      - Create venv and install all dependencies"
	@echo "make test       - Run installation tests"
	@echo "make run        - Run the pipeline on example text"
	@echo "make demo       - Run the full demo"
	@echo "make verbose    - Run verbose demo with visual output"
	@echo "make format     - Format code with black"
	@echo "make lint       - Run linters"
	@echo "make clean      - Remove build artifacts and cache"
	@echo ""

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up environment..."
	@chmod +x setup_project.sh
	@./setup_project.sh

# Run installation test
test:
	@echo "Testing installation..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && python test_installation.py; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Install dependencies only (assumes venv exists)
install:
	@echo "Installing dependencies..."
	@. venv/bin/activate && pip install -r requirements.txt
	@. venv/bin/activate && python -m spacy download en_core_web_sm

# Run basic example
run:
	@echo "Running token optimizer..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && cd token-optimizer && \
		echo "Please could you help me understand the repository configuration?" | \
		python pipeline.py; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Run full demo
demo:
	@echo "Running demo..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && cd token-optimizer && ./demo.sh; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Run verbose demo
verbose:
	@echo "Running verbose demo..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && cd token-optimizer && ./demo_verbose.sh; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Format code
format:
	@echo "Formatting code..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && black token-optimizer/; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Run linters
lint:
	@echo "Running linters..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && flake8 token-optimizer/ --max-line-length=100; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@rm -rf .mypy_cache .pytest_cache .coverage htmlcov 2>/dev/null || true
	@rm -rf token-optimizer/verbose_demo.txt token-optimizer/optimized_example.txt 2>/dev/null || true
	@echo "Clean complete!"

# Development setup with extras
dev-setup: setup
	@echo "Installing development dependencies..."
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "Development setup complete!"

# CI commands
ci-format:
	@./scripts/ci_format.sh

ci-lint:
	@./scripts/ci_lint.sh

ci-typecheck:
	@./scripts/ci_typecheck.sh

ci-test:
	@./scripts/ci_test.sh

ci: ci-all
ci-all:
	@./scripts/ci_all.sh

# Quick check before commit
check: format lint test
	@echo "✅ All checks passed! Ready to commit."
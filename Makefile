# Python Formatter and Linter Makefile
# =====================================
# Run 'make format' to format code, 'make lint' to check code quality

.PHONY: help format format-check lint test clean install

help:
	@echo "Nays Python Formatter Commands"
	@echo "=============================="
	@echo "make format       - Format code with black + isort"
	@echo "make format-check - Check formatting without changes"
	@echo "make lint         - Run linter (ruff)"
	@echo "make lint-flake8  - Run flake8 linter"
	@echo "make test         - Run tests (if available)"
	@echo "make clean        - Remove build artifacts"
	@echo "make install      - Install dev dependencies"
	@echo "make all          - Format + lint"

# Format code with black and isort
format:
	@echo "🎨 Formatting Python code..."
	python -m black nays test
	python -m isort nays test
	@echo "✅ Formatting complete!"

# Check formatting without making changes
format-check:
	@echo "🔍 Checking Python code formatting..."
	python -m black --check nays test
	python -m isort --check-only nays test

# Run linter
lint:
	@echo "🔬 Linting Python code with ruff..."
	python -m ruff check nays test

# Run flake8 linter
lint-flake8:
	@echo "🔬 Linting Python code with flake8..."
	python -m flake8 nays test

# Run all formatters and linters
all: format lint
	@echo "✅ All formatting and linting complete!"

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest test/ -v

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	@echo "✅ Clean complete!"

# Install development dependencies
install:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt
	@echo "✅ Installation complete!"

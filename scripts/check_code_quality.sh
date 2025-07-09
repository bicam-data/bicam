#!/bin/bash
# Code quality check script

set -e

echo "Running code quality checks..."
echo "=============================="

# Run ruff linting and formatting
echo "1. Running ruff linting and formatting..."
uv run ruff check bicam/ tests/ scripts/*.py
uv run ruff format --check bicam/ tests/ scripts/*.py

# Run mypy type checking
echo "2. Running mypy type checking..."
uv run mypy bicam/

# Run tests
echo "3. Running tests..."
uv run pytest tests/ -x

echo ""
echo "✅ All code quality checks passed!"

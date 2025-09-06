#!/bin/bash
# Pre-commit hook for code quality checks

echo "Running pre-commit checks..."

# Run linting
echo "🔍 Running flake8..."
python -m flake8 src/ --max-line-length=100 --ignore=E203,W503

# Run type checking
echo "🔍 Running mypy..."
python -m mypy src/ --ignore-missing-imports

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -q

echo "✅ Pre-commit checks completed"

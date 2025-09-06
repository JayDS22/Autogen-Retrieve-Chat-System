#!/bin/bash

# AutoGen RetrieveChat System - Environment Setup Script
# Author: Jay Guwalani

set -e

echo "Setting up AutoGen RetrieveChat System environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/sample_docs
mkdir -p data/test_datasets
mkdir -p logs
mkdir -p models
mkdir -p chroma_db

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

# Set up Git hooks (if .git exists)
if [ -d ".git" ]; then
    echo "Setting up Git hooks..."
    cp scripts/pre-commit.sh .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
fi

# Run tests to verify installation
echo "Running tests to verify installation..."
python -m pytest tests/ -v --tb=short

echo "✅ Environment setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python src/main.py"
echo ""
echo "For API server: python -m flask --app src.api.app run --host=0.0.0.0 --port=8000"
echo "For development: python examples/basic_qa.py"

#!/usr/bin/env bash

set -e

echo "=> Bootstrapping Neural Constitution Engine development environment..."

# 1. Ensure Python 3.12+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3.12+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.12" | bc -l) -eq 1 ]]; then
    echo "Error: Python 3.12+ is required. Found $PYTHON_VERSION"
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "=> Creating virtual environment..."
    python3 -m venv .venv
fi

echo "=> Activating virtual environment..."
source .venv/bin/activate

# 3. Upgrade pip and install dependencies
echo "=> Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# 4. Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "=> Installing pre-commit hooks..."
    pre-commit install
else
    echo "Warning: pre-commit not found in PATH."
fi

echo "=> Bootstrap complete!"
echo ""
echo "Run 'source .venv/bin/activate' to activate the environment."
echo "Run 'make help' to see available commands."

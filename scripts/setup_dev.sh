#!/bin/bash
# Development environment setup script

set -e

echo "Setting up BICAM development environment with uv..."
echo "=============================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install package in editable mode with dev dependencies
echo "Installing BICAM in development mode..."
uv pip install -e ".[dev]"

# Install pre-commit hooks if available
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Installing pre-commit hooks..."
    uv pip install pre-commit
    pre-commit install
fi

# Run initial tests
echo ""
echo "Running initial tests..."
uv run pytest tests/ -v --tb=short || true

echo ""
echo "✓ Development environment ready!"
echo ""
echo "Next steps:"
echo "1. Activate the environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Set up AWS credentials:"
echo "   cp env.example .env"
echo "   # Edit .env file with your configuration"
echo ""
echo "3. Build credentials file:"
echo "   python scripts/credentials/3_build_credentials.py"
echo ""
echo "4. Run tests:"
echo "   uv run pytest"
echo ""
echo "5. See available commands:"
echo "   make help"

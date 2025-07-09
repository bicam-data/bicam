#!/bin/bash
# Simplified build and publish script for GitHub Actions

set -e  # Exit on error

echo "BICAM Simple Build and Publish Script"
echo "====================================="

# Debug environment variables
echo "Environment variables check:"
echo "  BICAM_SECRET_KEY: ${BICAM_SECRET_KEY:+SET}"
echo "  BICAM_CREDENTIAL_ENDPOINT: ${BICAM_CREDENTIAL_ENDPOINT:+SET}"
echo "  PYPI_API_TOKEN: ${PYPI_API_TOKEN:+SET}"

# Check if we have the required environment variables
if [ -z "${BICAM_CREDENTIAL_ENDPOINT:-}" ] || [ -z "${BICAM_SECRET_KEY:-}" ]; then
    echo "Error: Missing required environment variables"
    echo "  BICAM_CREDENTIAL_ENDPOINT: ${BICAM_CREDENTIAL_ENDPOINT:+SET}"
    echo "  BICAM_SECRET_KEY: ${BICAM_SECRET_KEY:+SET}"
    exit 1
fi

if [ "$1" == "--publish" ] && [ -z "${PYPI_API_TOKEN:-}" ]; then
    echo "Error: Missing PYPI_API_TOKEN for publishing"
    exit 1
fi

# Generate credentials file
echo "Generating credentials file..."
python scripts/credentials/3_build_credentials.py

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Run tests
echo "Running tests..."
uv run pytest tests/ -v || {
    echo "Tests failed! Fix issues before publishing."
    rm -f bicam/_auth.py
    exit 1
}

# Build package with uv
echo "Building package with uv..."
uv build

# Display built files
echo ""
echo "Built distributions:"
ls -la dist/

# Verify the wheel
echo ""
echo "Verifying wheel..."
uv venv test-wheel-env
uv pip install --find-links dist/ bicam
uv run python -c "import bicam; print(f'✓ Successfully imported bicam {bicam.__version__}')"
rm -rf test-wheel-env

# Publish to PyPI
if [ "$1" == "--publish" ]; then
    echo ""
    echo "Publishing to PyPI..."
    echo "Using PyPI token: ${PYPI_API_TOKEN:0:10}..."
    uv publish --token "$PYPI_API_TOKEN"
    echo "✓ Package published successfully!"
else
    echo ""
    echo "Build complete! To publish:"
    echo "  ./scripts/build_and_publish_simple.sh --publish"
fi

# Clean up credentials file for security
echo ""
echo "Cleaning up credentials file..."
rm -f bicam/_auth.py
echo "✓ Done!"

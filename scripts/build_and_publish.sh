#!/bin/bash
# Build and publish script using uv

set -e  # Exit on error

echo "BICAM Build and Publish Script"
echo "=============================="

# Check for root .env file (for PyPI tokens)
if [ ! -f ".env" ]; then
    echo "Error: .env file not found in project root"
    echo "Create .env file with PyPI tokens:"
    echo "  PYPI_API_TOKEN=your-pypi-token-here"
    exit 1
fi

# Load environment from root .env file (for PyPI tokens)
export $(grep -v '^#' .env | xargs)

# Check for credential server .env file
CREDENTIALS_ENV="scripts/credentials/.env"
if [ ! -f "$CREDENTIALS_ENV" ]; then
    echo "Error: Credential server .env file not found at $CREDENTIALS_ENV"
    echo "Run ./scripts/credentials/setup_credential_server.sh to create and configure it"
    exit 1
fi

# Load credential server environment variables
export $(grep -v '^#' "$CREDENTIALS_ENV" | xargs)

# Check for required credential server environment variables
if [ -z "$BICAM_CREDENTIAL_ENDPOINT" ] || [ -z "$BICAM_SECRET_KEY" ]; then
    echo "Error: BICAM_CREDENTIAL_ENDPOINT and BICAM_SECRET_KEY must be set in $CREDENTIALS_ENV"
    echo ""
    echo "To deploy the credential server first:"
    echo "  ./scripts/credentials/setup_credential_server.sh"
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

    # Check for PyPI token
    if [ -z "$PYPI_API_TOKEN" ]; then
        echo "Error: Set PYPI_API_TOKEN environment variable"
        echo "Get your token from: https://pypi.org/manage/account/token/"
        rm -f bicam/_auth.py
        exit 1
    fi

    # Publish with uv
    uv publish

    echo "✓ Package published successfully!"

elif [ "$1" == "--test-publish" ]; then
    echo ""
    echo "Publishing to TestPyPI..."

    # Check for TestPyPI token
    if [ -z "$PYPI_API_TOKEN_TEST" ]; then
        echo "Error: Set PYPI_API_TOKEN_TEST environment variable"
        echo "Get your token from: https://test.pypi.org/manage/account/token/"
        rm -f bicam/_auth.py
        exit 1
    fi

    # Set the token for uv publish
    export PYPI_API_TOKEN="$PYPI_API_TOKEN_TEST"

    # Publish to TestPyPI
    uv publish --publish-url https://test.pypi.org/legacy/

    echo "✓ Package published to TestPyPI!"
    echo ""
    echo "Test installation with:"
    echo "  uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ bicam"

else
    echo ""
    echo "Build complete! To publish:"
    echo "  - To PyPI:     ./scripts/build_and_publish.sh --publish"
    echo "  - To TestPyPI: ./scripts/build_and_publish.sh --test-publish"
    echo ""
    echo "Make sure to set the appropriate token in your .env file:"
    echo "  PYPI_API_TOKEN=pypi-... (for PyPI)"
    echo "  PYPI_API_TOKEN_TEST=pypi-... (for TestPyPI)"
fi

# Clean up credentials file for security
echo ""
echo "Cleaning up credentials file..."
rm -f bicam/_auth.py
echo "✓ Done!"

#!/bin/bash
# Build and publish script using uv

set -e  # Exit on error

echo "BICAM Build and Publish Script"
echo "=============================="

# Function to check if environment variables are set
check_env_vars() {
    local missing_vars=()

    if [ -z "$BICAM_CREDENTIAL_ENDPOINT" ]; then
        missing_vars+=("BICAM_CREDENTIAL_ENDPOINT")
    fi

    if [ -z "$BICAM_SECRET_KEY" ]; then
        missing_vars+=("BICAM_SECRET_KEY")
    fi

    if [ "$1" == "--publish" ] && [ -z "$PYPI_API_TOKEN" ]; then
        missing_vars+=("PYPI_API_TOKEN")
    fi

    if [ "$1" == "--test-publish" ] && [ -z "$PYPI_API_TOKEN_TEST" ]; then
        missing_vars+=("PYPI_API_TOKEN_TEST")
    fi

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi

    return 0
}

# Try to load from root .env file if it exists (for CI compatibility)
if [ -f ".env" ]; then
    echo "Loading environment from root .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Try to load from credential server .env file if it exists
CREDENTIALS_ENV="scripts/credentials/.env"
if [ -f "$CREDENTIALS_ENV" ]; then
    echo "Loading environment from $CREDENTIALS_ENV..."
    export $(grep -v '^#' "$CREDENTIALS_ENV" | xargs)
fi

# Check if we have the required environment variables
if ! check_env_vars "$1"; then
    echo ""
    echo "Environment variables can be set in several ways:"
    echo "1. Directly in the shell environment"
    echo "2. In a root .env file"
    echo "3. In scripts/credentials/.env file"
    echo ""
    echo "Required variables:"
    echo "  BICAM_CREDENTIAL_ENDPOINT=your_api_endpoint_here"
    echo "  BICAM_SECRET_KEY=your_secret_key_here"
    if [ "$1" == "--publish" ]; then
        echo "  PYPI_API_TOKEN=your_pypi_token_here"
    elif [ "$1" == "--test-publish" ]; then
        echo "  PYPI_API_TOKEN_TEST=your_test_pypi_token_here"
    fi
    echo ""
    echo "For local development, you can run:"
    echo "  ./scripts/credentials/setup_credential_server.sh"
    exit 1
fi

# Generate credentials file if we have the required variables
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
    echo "Make sure to set the appropriate token in your environment:"
    echo "  PYPI_API_TOKEN=pypi-... (for PyPI)"
    echo "  PYPI_API_TOKEN_TEST=pypi-... (for TestPyPI)"
fi

# Clean up credentials file for security
echo ""
echo "Cleaning up credentials file..."
rm -f bicam/_auth.py
echo "✓ Done!"

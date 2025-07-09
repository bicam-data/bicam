#!/bin/bash
# PyPI Setup Script for BICAM

set -e

echo "BICAM PyPI Setup Script"
echo "======================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "Please edit .env and add your credentials:"
    echo "1. BICAM_SECRET_KEY and BICAM_CREDENTIAL_ENDPOINT in .env file"
    echo "2. UV_PUBLISH_TOKEN and UV_PUBLISH_TOKEN_TEST"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Check for required environment variables
echo "Checking environment variables..."
echo ""

# Load environment from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs 2>/dev/null || true)
fi

# AWS credentials
if [ -z "$BICAM_SECRET_KEY" ] || [ -z "$BICAM_CREDENTIAL_ENDPOINT" ]; then
    echo "⚠️  AWS credentials not configured in .env file"
    echo "   Set BICAM_SECRET_KEY and BICAM_CREDENTIAL_ENDPOINT in .env"
else
    echo "✓ AWS credentials configured in .env file"
fi

# PyPI tokens
if [ -z "$UV_PUBLISH_TOKEN" ]; then
    echo "⚠️  PyPI token not set"
    echo "   Set UV_PUBLISH_TOKEN for publishing to PyPI"
else
    echo "✓ PyPI token configured"
fi

if [ -z "$UV_PUBLISH_TOKEN_TEST" ]; then
    echo "⚠️  TestPyPI token not set"
    echo "   Set UV_PUBLISH_TOKEN_TEST for testing on TestPyPI"
else
    echo "✓ TestPyPI token configured"
fi

echo ""
echo "Next steps:"
echo "1. Get PyPI API tokens from:"
echo "   - https://pypi.org/manage/account/token/"
echo "   - https://test.pypi.org/manage/account/token/"
echo ""
echo "2. Add tokens to .env file:"
echo "   UV_PUBLISH_TOKEN=pypi-your-token"
echo "   UV_PUBLISH_TOKEN_TEST=pypi-your-test-token"
echo ""
echo "3. Test build:"
echo "   make build"
echo ""
echo "4. Test on TestPyPI:"
echo "   make publish-test"
echo ""
echo "5. Publish to PyPI:"
echo "   make publish"
echo ""
echo "For detailed instructions, see: docs/pypi-integration.md"

#!/bin/bash
# Complete setup script for BICAM credential server using .env file

set -e

echo "BICAM Credential Server Setup"
echo "============================="
echo ""
echo "This script will guide you through setting up the credential server"
echo "from scratch using a .env file for configuration."
echo ""

# Step 1: Create .env file if it doesn't exist
echo "Step 1: Create .env file"
echo "------------------------"
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# BICAM Credential Server Configuration
# Generate a secret key with: openssl rand -hex 32
BICAM_SECRET_KEY=$(openssl rand -hex 32)

# This will be set automatically after deployment
BICAM_CREDENTIAL_ENDPOINT=

# Optional: Customize these if needed
# BICAM_ROLE_ARN=arn:aws:iam::your-account:role/YourCustomRole
# BICAM_BUCKET_NAME=your-custom-bucket
# BICAM_STACK_NAME=your-custom-stack-name
EOF
    echo "✓ Created .env file with generated secret key"
    echo "  Secret key: $(grep BICAM_SECRET_KEY .env | cut -d'=' -f2 | head -c 8)..."
    echo ""
else
    echo "✓ .env file already exists"
    if grep -q "BICAM_SECRET_KEY=" .env; then
        echo "  Secret key: $(grep BICAM_SECRET_KEY .env | cut -d'=' -f2 | head -c 8)..."
    else
        echo "  Adding secret key to .env file..."
        echo "BICAM_SECRET_KEY=$(openssl rand -hex 32)" >> .env
        echo "  Secret key: $(tail -1 .env | cut -d'=' -f2 | head -c 8)..."
    fi
    echo ""
fi

# Step 2: Create IAM Role
echo "Step 2: Create IAM Role"
echo "----------------------"
echo "Creating the IAM role that the Lambda function will assume..."
./1_create_iam_role.sh
echo ""

# Step 3: Deploy Credential Server
echo "Step 3: Deploy Credential Server"
echo "-------------------------------"
echo "Deploying the Lambda function and API Gateway..."
./2_deploy_credentials_server.sh

# Get the API endpoint from .env file
API_URL=$(grep BICAM_CREDENTIAL_ENDPOINT .env | cut -d'=' -f2)

if [ -n "$API_URL" ]; then
    echo ""
    echo "✓ Credential server deployed successfully!"
    echo "  API Endpoint: $API_URL"
    echo ""
else
    echo ""
    echo "❌ Failed to get API endpoint. Check the deployment output above."
    exit 1
fi

# Step 4: Build Package
echo "Step 4: Build Package"
echo "--------------------"
echo "Building the package with credential server configuration..."
python 3_build_credentials.py
echo ""

# Step 5: Test the System
echo "Step 5: Test the System"
echo "----------------------"
echo "Testing the complete authentication system..."
if ./4_test_credentials.py; then
    echo ""
    echo "🎉 SUCCESS! Your credential server is working!"
    echo ""
    echo "Summary:"
    echo "  Secret Key: $(grep BICAM_SECRET_KEY .env | cut -d'=' -f2 | head -c 8)..."
    echo "  API Endpoint: $API_URL"
    echo "  Package: Built and tested successfully"
    echo ""
    echo "Configuration saved in: .env"
    echo ""
    echo "You can now build and publish your package:"
    echo "  make build"
    echo ""
else
    echo ""
    echo "❌ Tests failed. Check the output above for errors."
    echo ""
    echo "Troubleshooting:"
    echo "1. Check that the IAM role exists and is assumable"
    echo "2. Verify the secret key in .env matches the server"
    echo "3. Check CloudWatch logs for Lambda function errors"
    exit 1
fi

echo "Setup complete! 🎉"

#!/bin/bash
# Deploy BICAM credential server infrastructure using .env file

set -e

echo "BICAM Credential Server Deployment"
echo "=================================="

# Load environment variables from .env file
if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    echo "Create a .env file with the following variables:"
    echo "  BICAM_SECRET_KEY=your_secret_key_here"
    echo "  BICAM_CREDENTIAL_ENDPOINT=your_api_endpoint_here (will be set after deployment)"
    exit 1
fi

# Source the .env file
export $(grep -v '^#' .env | xargs)

# Check for required environment variables
if [ -z "$BICAM_SECRET_KEY" ]; then
    echo "Error: BICAM_SECRET_KEY not set in .env file"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

if [ -z "$AWS_PROFILE" ] && [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Error: Set AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY"
    exit 1
fi

# Optional parameters with defaults
ROLE_ARN=${BICAM_ROLE_ARN:-"arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/BICAMReadOnlyRole"}
BUCKET_NAME=${BICAM_BUCKET_NAME:-"bicam-datasets"}
STACK_NAME=${BICAM_STACK_NAME:-"bicam-credential-server"}

echo "Deploying with configuration:"
echo "  Stack Name: $STACK_NAME"
echo "  Role ARN: $ROLE_ARN"
echo "  Bucket Name: $BUCKET_NAME"
echo "  Secret Key: ${BICAM_SECRET_KEY:0:8}..."
echo ""

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file _cloudformation.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        SecretKey="$BICAM_SECRET_KEY" \
        RoleArn="$ROLE_ARN" \
        BucketName="$BUCKET_NAME" \
    --capabilities CAPABILITY_NAMED_IAM \
    --no-fail-on-empty-changeset

# Get the API URL
echo ""
echo "Getting API endpoint..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

if [ -z "$API_URL" ]; then
    echo "Error: Failed to get API URL from CloudFormation stack"
    exit 1
fi

echo "✓ Credential server deployed successfully!"
echo ""
echo "API Endpoint: $API_URL"
echo ""
echo "Updating .env file with the new endpoint..."
# Update existing endpoint or add new one
# Remove all existing BICAM_CREDENTIAL_ENDPOINT lines and add a single new one
sed -i.bak '/^BICAM_CREDENTIAL_ENDPOINT=/d' .env
echo "BICAM_CREDENTIAL_ENDPOINT=$API_URL" >> .env
rm -f .env.bak
fi
echo "✓ Updated .env file with API endpoint"
echo ""
echo "To test the endpoint:"
echo "  ./4_test_credentials.py"
echo ""
echo "To delete the stack:"
echo "  aws cloudformation delete-stack --stack-name \"$STACK_NAME\""

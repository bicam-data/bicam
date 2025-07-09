# BICAM Credential Server Setup Guide

This guide walks you through setting up the BICAM credential server system step by step.

## Overview

The credential server is an AWS Lambda function that provides temporary AWS credentials to authenticated BICAM package requests. This replaces the old system of embedding AWS keys directly in the package.

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.9+
- `python-dotenv` package installed (`pip install python-dotenv`)

## Quick Start (Recommended)

For most users, run the automated setup:

```bash
# From the project root
./scripts/credentials/setup_credential_server.sh
```

This single command will:

1. Create `.env` file with configuration
2. Create IAM role
3. Deploy credential server
4. Build and test the package

## Manual Setup (Step by Step)

If you prefer to understand each step or need to customize the setup:

### Step 1: Create Configuration File

```bash
# Copy the example configuration
cp env.example .env

# Edit .env file with your values
# BICAM_SECRET_KEY=your_secret_key_here
# BICAM_CREDENTIAL_ENDPOINT= (will be set after deployment)
```

### Step 2: Generate Secret Key

```bash
# Generate a secure random key
openssl rand -hex 32
```

Add this to your `.env` file as `BICAM_SECRET_KEY`.

### Step 3: Create IAM Role

```bash
# Create the IAM role that Lambda will assume
./scripts/credentials/create_iam_role.sh
```

This creates:

- `BICAMReadOnlyRole` - Role with S3 read permissions
- Trust policy allowing Lambda to assume the role

### Step 4: Deploy Credential Server

```bash
# Deploy Lambda function and API Gateway
./scripts/credentials/deploy_credentials_server.sh
```

This creates:

- Lambda function for credential validation
- API Gateway for HTTP access
- CloudFormation stack: `bicam-credential-server`

### Step 5: Build Package

```bash
# Build package with credential server configuration
python scripts/credentials/build_credentials.py
```

This generates `bicam/_auth.py` from the template.

### Step 6: Test the System

```bash
# Test the complete authentication system
./scripts/credentials/4_test_credentials.py
```

## Script Reference

### Core Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `setup_credential_server.sh` | Complete automated setup | First time setup |
| `create_iam_role.sh` | Create IAM role | Before deployment |
| `deploy_credentials_server.sh` | Deploy Lambda + API Gateway | After IAM role creation |
| `3_build_credentials.py` | Build auth module | After deployment |
| `test_credentials.py` | Test the system | After building |

### Infrastructure Files

| File | Purpose |
|------|---------|
| `credentials_server.py` | Lambda function code |
| `cloudformation.yaml` | Infrastructure template |

### Configuration

| File | Purpose |
|------|---------|
| `.env` | Configuration (secret key, endpoint) |
| `env.example` | Example configuration template |
| `bicam/_auth.py.template` | Auth module template |

## Configuration Options

### Required Variables

```bash
# Secret key for package token validation
BICAM_SECRET_KEY=your_secret_key_here

# API endpoint (set automatically after deployment)
BICAM_CREDENTIAL_ENDPOINT=https://your-api-gateway-url.amazonaws.com/prod/get-credentials
```

### Optional Variables

```bash
# Custom IAM role ARN (defaults to BICAMReadOnlyRole)
BICAM_ROLE_ARN=arn:aws:iam::your-account:role/YourCustomRole

# Custom S3 bucket name (defaults to bicam-data)
BICAM_BUCKET_NAME=your-custom-bucket

# Custom CloudFormation stack name (defaults to bicam-credential-server)
BICAM_STACK_NAME=your-custom-stack-name
```

## Troubleshooting

### Common Issues

1. **"Invalid package token"**
   - Check that secret key in `.env` matches deployed server
   - Verify package version is correct

2. **"Failed to generate credentials"**
   - Check IAM role exists and is assumable
   - Verify Lambda function has correct permissions
   - Check CloudWatch logs for detailed errors

3. **"Missing required parameters"**
   - Ensure all required fields are sent in request
   - Check API Gateway configuration

### Debugging Commands

```bash
# Check Lambda logs
aws logs tail /aws/lambda/bicam-credential-server --follow

# Test Lambda directly
aws lambda invoke \
  --function-name bicam-credential-server \
  --payload '{"package_token":"test","version":"1.0.0"}' \
  response.json

# Verify IAM role
aws iam get-role --role-name BICAMReadOnlyRole
aws iam list-attached-role-policies --role-name BICAMReadOnlyRole

# Check CloudFormation stack
aws cloudformation describe-stacks --stack-name bicam-credential-server
```

## Security

### Secret Key Management

- **Generation**: Use `openssl rand -hex 32` for secure random keys
- **Storage**: Store in `.env` file (never commit to version control)
- **Rotation**: Rarely needed unless compromised
- **Scope**: Used only for package token validation

### IAM Permissions

The Lambda function assumes a role with minimal S3 read permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bicam-data",
        "arn:aws:s3:::bicam-data/*"
      ]
    }
  ]
}
```

## Maintenance

### Updating the Secret Key

1. Generate a new secret key
2. Update the `.env` file
3. Redeploy the credential server
4. Rebuild the package

### Updating the Lambda Function

1. Modify the Lambda code in `credentials_server.py`
2. Redeploy with `./scripts/credentials/deploy_credentials_server.sh`

### Monitoring

- **CloudWatch Logs**: Monitor Lambda function execution
- **API Gateway Metrics**: Track API usage and errors
- **IAM Access Analyzer**: Review role permissions regularly

## Cost Considerations

- **Lambda**: ~$0.20 per million requests
- **API Gateway**: ~$3.50 per million requests
- **CloudWatch**: Minimal cost for logs
- **IAM**: No additional cost

For typical usage, costs are negligible (< $1/month).

## Migration from Old System

If you're migrating from the old embedded credentials system:

```bash
./scripts/credentials/migrate_to_credential_server.sh
```

This will:

- Remove old credential files
- Set up the new system
- Test the migration

## Support

For issues with the credential server:

1. Check CloudWatch logs
2. Verify `.env` configuration
3. Test the API endpoint directly
4. Review IAM permissions

For detailed documentation, see: `docs/credential-server.md`

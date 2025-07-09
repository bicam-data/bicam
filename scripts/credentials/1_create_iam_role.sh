#!/bin/bash
# Create IAM role for BICAM credential server

set -e

echo "Creating IAM role for BICAM credential server..."

# Create the role
aws iam create-role \
    --role-name BICAMReadOnlyRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::'"$(aws sts get-caller-identity --query Account --output text)"':role/BICAMCredentialServerRole"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' \
    --description "Role for BICAM credential server Lambda function" || echo "Role may already exist"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name BICAMReadOnlyRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole || echo "Policy may already be attached"

# Create policy for S3 access
aws iam put-role-policy \
    --role-name BICAMReadOnlyRole \
    --policy-name BICAMS3Access \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::bicam-datasets",
                    "arn:aws:s3:::bicam-datasets/*"
                ]
            }
        ]
    }' || echo "Policy may already exist"

echo "✓ IAM role created successfully!"
echo "Role ARN: arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/BICAMReadOnlyRole"

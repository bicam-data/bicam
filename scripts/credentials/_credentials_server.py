#!/usr/bin/env python3
"""Lambda function for BICAM credential validation and temporary credential generation."""

import hashlib
import json
import os
from typing import Any, Dict

import boto3


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for credential requests.

    Expected event structure:
    {
        "package_token": "hash_of_version_and_secret",
        "version": "package_version",
        "user_agent": "optional_user_agent"
    }
    """

    # Get configuration from environment
    secret_key = os.environ.get("BICAM_SECRET_KEY")
    role_arn = os.environ.get(
        "BICAM_ROLE_ARN", "arn:aws:iam::123456789:role/BICAMReadOnlyRole"
    )
    bucket_name = os.environ.get("BICAM_BUCKET_NAME", "bicam-data")

    if not secret_key:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Server configuration error"}),
        }

    # Extract request parameters
    package_token = event.get("package_token")
    package_version = event.get("version")
    user_agent = event.get("user_agent", "unknown")

    if not package_token or not package_version:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required parameters"}),
        }

    # Validate package token
    expected_token = hashlib.sha256(
        f"{package_version}-{secret_key}".encode()
    ).hexdigest()

    if package_token != expected_token:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "Invalid package token"}),
        }

    try:
        # Generate temporary credentials
        sts = boto3.client("sts")
        assumed_role = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=f"bicam-{package_version}-{hashlib.md5(user_agent.encode()).hexdigest()[:8]}",
            DurationSeconds=3600,  # 1 hour
            Policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["s3:GetObject", "s3:ListBucket"],
                            "Resource": [
                                f"arn:aws:s3:::{bucket_name}",
                                f"arn:aws:s3:::{bucket_name}/*",
                            ],
                        }
                    ],
                }
            ),
        )

        # Log the request (optional, for monitoring)
        print(f"Credential request: version={package_version}, user_agent={user_agent}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
            },
            "body": json.dumps(
                {
                    "credentials": {
                        "access_key": assumed_role["Credentials"]["AccessKeyId"],
                        "secret_key": assumed_role["Credentials"]["SecretAccessKey"],
                        "session_token": assumed_role["Credentials"]["SessionToken"],
                        "expiration": assumed_role["Credentials"][
                            "Expiration"
                        ].isoformat(),
                    },
                    "bucket": bucket_name,
                    "region": "us-east-1",
                }
            ),
        }

    except Exception as e:
        print(f"Error generating credentials: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to generate credentials"}),
        }


def handle_cors(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle CORS preflight requests."""
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        },
        "body": "",
    }

#!/usr/bin/env python3
"""Test script for the new credential server authentication system using .env file."""

import hashlib
import json
import logging
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_env_file():
    """Load environment variables from .env file."""
    # Look for .env file in the credentials directory first, then project root
    credentials_env_path = Path(__file__).parent / ".env"
    project_env_path = project_root.parent / ".env"

    env_path = None
    if credentials_env_path.exists():
        env_path = credentials_env_path
    elif project_env_path.exists():
        env_path = project_env_path
    else:
        logger.error(
            f"Error: .env file not found in {credentials_env_path} or {project_env_path}"
        )
        logger.info("Create a .env file with the following variables:")
        logger.info("  BICAM_SECRET_KEY=your_secret_key_here")
        logger.info("  BICAM_CREDENTIAL_ENDPOINT=your_api_endpoint_here")
        return False

    # Load the .env file
    load_dotenv(env_path)
    logger.info(f"Loaded .env file from: {env_path}")
    return True


def test_credential_server():
    """Test the credential server endpoint."""

    # Load environment from .env file
    if not load_env_file():
        return False

    endpoint = os.getenv("BICAM_CREDENTIAL_ENDPOINT")
    secret_key = os.getenv("BICAM_SECRET_KEY")

    if not endpoint or not secret_key:
        logger.error(
            "Error: BICAM_CREDENTIAL_ENDPOINT and BICAM_SECRET_KEY must be set in .env file"
        )
        return False

    # Get package version
    from bicam.__version__ import __version__

    # Generate package token
    package_token = hashlib.sha256(f"{__version__}-{secret_key}".encode()).hexdigest()

    logger.info("Testing credential server...")
    logger.info(f"  Endpoint: {endpoint}")
    logger.info(f"  Version: {__version__}")
    logger.info(f"  Package token: {package_token[:16]}...")
    logger.info("")

    try:
        response = requests.post(
            endpoint,
            json={
                "package_token": package_token,
                "version": __version__,
                "user_agent": f"bicam/{__version__}",
            },
            timeout=10,
        )

        logger.info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            credentials = data["credentials"]

            logger.info("✓ Credential server working!")
            logger.info(f"  Access Key: {credentials['access_key'][:10]}...")
            logger.info(
                f"  Secret Key: {'*' * (len(credentials['secret_key']) - 4)}{credentials['secret_key'][-4:]}"
            )
            logger.info(f"  Session Token: {credentials['session_token'][:20]}...")
            logger.info(f"  Expiration: {credentials['expiration']}")
            logger.info(f"  Bucket: {data.get('bucket', 'N/A')}")
            logger.info(f"  Region: {data.get('region', 'N/A')}")

            return True
        else:
            logger.error(f"✗ Credential server error: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"  Error: {error_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                logger.error(f"  Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Connection error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {str(e)}")
        return False


def test_auth_module():
    """Test the auth module with the new system."""

    logger.info("\nTesting auth module...")

    try:
        # Import and test the auth module
        from bicam import _auth

        # Test package token generation
        token = _auth.get_package_token()
        logger.info(f"  Package token: {token[:16]}...")

        # Test S3 client creation
        s3_client = _auth.get_s3_client()
        logger.info(f"  S3 client created: {type(s3_client).__name__}")

        # Test bucket name
        bucket = _auth.get_bucket_name()
        logger.info(f"  Bucket name: {bucket}")

        logger.info("✓ Auth module working!")
        return True

    except Exception as e:
        logger.error(f"✗ Auth module error: {str(e)}")
        return False


def main():
    """Run all tests."""
    logger.info("BICAM Credential Server Test")
    logger.info("============================")

    # Test credential server
    server_ok = test_credential_server()

    # Test auth module
    auth_ok = test_auth_module()

    logger.info("\n" + "=" * 50)
    if server_ok and auth_ok:
        logger.info("✓ All tests passed! The new authentication system is working.")
        return 0
    else:
        logger.error("✗ Some tests failed. Check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

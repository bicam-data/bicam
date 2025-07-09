#!/usr/bin/env python3
"""Script to build auth file with credential server configuration from .env file."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        logger.error(f"Error: .env file not found at {env_path}")
        logger.info("Create a .env file with the following variables:")
        logger.info("  BICAM_SECRET_KEY=your_secret_key_here")
        logger.info("  BICAM_CREDENTIAL_ENDPOINT=your_api_endpoint_here")
        sys.exit(1)

    # Load the .env file
    load_dotenv(env_path)
    return env_path


def build_auth_file():
    """Build the _auth.py file with credential server configuration."""

    # Load environment from .env file
    env_path = load_env_file()

    # Get configuration from .env file
    credential_endpoint = os.getenv("BICAM_CREDENTIAL_ENDPOINT")
    secret_key = os.getenv("BICAM_SECRET_KEY")

    if not credential_endpoint:
        logger.error("Error: BICAM_CREDENTIAL_ENDPOINT not set in .env file")
        logger.info("This should be the URL of your deployed credential server")
        logger.info(
            "Example: https://abc123.execute-api.us-east-1.amazonaws.com/prod/get-credentials"
        )
        sys.exit(1)

    if not secret_key:
        logger.error("Error: BICAM_SECRET_KEY not set in .env file")
        logger.info(
            "This should be the same secret key used to deploy the credential server"
        )
        sys.exit(1)

    # Read template
    template_path = Path(__file__).parent.parent.parent / "bicam" / "_auth.py.template"
    if not template_path.exists():
        logger.error(f"Error: Template file not found at {template_path}")
        sys.exit(1)

    template_content = template_path.read_text()

    # Replace placeholders
    auth_content = template_content.replace(
        "{{CREDENTIAL_ENDPOINT}}", credential_endpoint
    )
    auth_content = auth_content.replace("{{SECRET_KEY}}", secret_key)

    # Write file
    auth_path = Path(__file__).parent.parent.parent / "bicam" / "_auth.py"
    auth_path.write_text(auth_content)

    logger.info(f"✓ Generated {auth_path}")
    logger.info(f"  Credential endpoint: {credential_endpoint}")
    logger.info(f"  Secret key: {'*' * (len(secret_key) - 4)}{secret_key[-4:]}")
    logger.info(f"  Source: {env_path}")


if __name__ == "__main__":
    build_auth_file()

#!/usr/bin/env python3
"""Script to build auth file with credential server configuration from environment or .env file."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        # Load the .env file
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
        return env_path
    else:
        logger.info("No .env file found, using environment variables directly")
        return None


def build_auth_file():
    """Build the _auth.py file with credential server configuration."""

    # Debug: Print environment variables (without values for security)
    logger.info("Environment variables check:")
    logger.info(
        f"  BICAM_CREDENTIAL_ENDPOINT: {'SET' if os.getenv('BICAM_CREDENTIAL_ENDPOINT') else 'NOT SET'}"
    )
    logger.info(
        f"  BICAM_SECRET_KEY: {'SET' if os.getenv('BICAM_SECRET_KEY') else 'NOT SET'}"
    )

    # Get configuration from environment variables
    credential_endpoint = os.getenv("BICAM_CREDENTIAL_ENDPOINT")
    secret_key = os.getenv("BICAM_SECRET_KEY")

    env_path = load_env_file() if not credential_endpoint or not secret_key else None

    if not credential_endpoint:
        logger.error("Error: BICAM_CREDENTIAL_ENDPOINT not set")
        logger.info("This should be the URL of your deployed credential server")
        logger.info(
            "Example: https://abc123.execute-api.us-east-1.amazonaws.com/prod/get-credentials"
        )
        if env_path:
            logger.info(f"Check your .env file at {env_path}")
        else:
            logger.info("Set the environment variable or create a .env file")
        sys.exit(1)

    if not secret_key:
        logger.error("Error: BICAM_SECRET_KEY not set")
        logger.info(
            "This should be the same secret key used to deploy the credential server"
        )
        if env_path:
            logger.info(f"Check your .env file at {env_path}")
        else:
            logger.info("Set the environment variable or create a .env file")
        sys.exit(1)

    # Read template
    template_path = Path(__file__).parent.parent.parent / "bicam" / "_auth.py.template"
    logger.info(f"Looking for template at: {template_path}")
    if not template_path.exists():
        logger.error(f"Error: Template file not found at {template_path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Script location: {Path(__file__).parent}")
        sys.exit(1)
    logger.info(f"✓ Found template at {template_path}")

    template_content = template_path.read_text()

    # Replace placeholders
    auth_content = template_content.replace(
        "{{CREDENTIAL_ENDPOINT}}", credential_endpoint
    )
    auth_content = auth_content.replace("{{SECRET_KEY}}", secret_key)

    # Write file
    auth_path = Path(__file__).parent.parent.parent / "bicam" / "_auth.py"
    logger.info(f"Writing auth file to: {auth_path}")
    auth_path.write_text(auth_content)
    logger.info(f"✓ Successfully wrote {auth_path}")

    logger.info(f"✓ Generated {auth_path}")
    logger.info(f"  Credential endpoint: {credential_endpoint}")
    logger.info(f"  Secret key: {'*' * (len(secret_key) - 4)}{secret_key[-4:]}")
    if env_path:
        logger.info(f"  Source: {env_path}")
    else:
        logger.info("  Source: Environment variables")


if __name__ == "__main__":
    build_auth_file()

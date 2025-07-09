#!/usr/bin/env python3
"""Test script to verify environment variable handling."""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


def test_auth_import():
    """Test that _auth.py can be imported and uses environment variables."""
    print("Testing _auth.py import and environment variable handling...")

    # Set test environment variables
    os.environ["BICAM_SECRET_KEY"] = "test_secret_key"
    os.environ["BICAM_CREDENTIAL_ENDPOINT"] = "https://test.example.com/get-credentials"

    try:
        from bicam._auth import SECRET_KEY, CREDENTIAL_ENDPOINT

        print(f"✓ SECRET_KEY: {SECRET_KEY}")
        print(f"✓ CREDENTIAL_ENDPOINT: {CREDENTIAL_ENDPOINT}")

        if (
            SECRET_KEY == "test_secret_key"
            and CREDENTIAL_ENDPOINT == "https://test.example.com/get-credentials"
        ):
            print("✓ Environment variables are being read correctly")
            return True
        else:
            print("✗ Environment variables are not being read correctly")
            return False
    except ImportError as e:
        print(f"✗ Failed to import _auth: {e}")
        return False


def test_build_credentials():
    """Test that the build credentials script works with environment variables."""
    print("\nTesting build credentials script...")

    # Set test environment variables
    os.environ["BICAM_SECRET_KEY"] = "test_secret_key"
    os.environ["BICAM_CREDENTIAL_ENDPOINT"] = "https://test.example.com/get-credentials"

    try:
        # Import and run the build script
        sys.path.insert(0, str(Path(__file__).parent / "scripts" / "credentials"))
        import importlib.util

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "build_credentials",
            Path(__file__).parent
            / "scripts"
            / "credentials"
            / "3_build_credentials.py",
        )
        build_credentials = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_credentials)

        # Run the build
        build_credentials.build_auth_file()

        # Check if the file was created
        auth_file = Path(__file__).parent / "bicam" / "_auth.py"
        if auth_file.exists():
            content = auth_file.read_text()
            if (
                "test_secret_key" in content
                and "https://test.example.com/get-credentials" in content
            ):
                print("✓ Build credentials script works with environment variables")
                # Clean up
                auth_file.unlink()
                return True
            else:
                print(
                    "✗ Build credentials script did not use environment variables correctly"
                )
                auth_file.unlink()
                return False
        else:
            print("✗ Build credentials script did not create _auth.py file")
            return False
    except Exception as e:
        print(f"✗ Build credentials script failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing environment variable handling...")
    print("=" * 50)

    success = True
    success &= test_auth_import()
    success &= test_build_credentials()

    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)

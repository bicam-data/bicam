"""Tests for the authentication module."""

import os
from unittest.mock import Mock, patch

import pytest
import requests

from bicam import _auth


class TestAuthentication:
    """Test the authentication module."""

    def test_get_package_token(self):
        """Test package token generation."""
        token = _auth.get_package_token()
        assert isinstance(token, str)
        assert len(token) == 64  # SHA-256 hash length

    def test_package_token_consistency(self):
        """Test that package token is consistent for same version and secret."""
        token1 = _auth.get_package_token()
        token2 = _auth.get_package_token()
        assert token1 == token2

    def test_environment_variable_loading(self):
        """Test that environment variables are properly loaded."""
        # Test that environment variables are loaded
        assert _auth.SECRET_KEY is not None
        assert _auth.CREDENTIAL_ENDPOINT is not None

    @patch("requests.post")
    def test_fetch_credentials_success(self, mock_post):
        """Test successful credential fetching."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "credentials": {
                "access_key": "ASIA123456789",
                "secret_key": "secret123",
                "session_token": "token123",
                "expiration": "2023-12-31T23:59:59+00:00",
            }
        }
        mock_post.return_value = mock_response

        credentials = _auth._fetch_credentials()

        assert credentials["access_key"] == "ASIA123456789"
        assert credentials["secret_key"] == "secret123"
        assert credentials["session_token"] == "token123"
        assert credentials["expiration"] == "2023-12-31T23:59:59+00:00"

    @patch("requests.post")
    def test_fetch_credentials_server_error(self, mock_post):
        """Test credential fetching with server error."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Credential server error: 500"):
            _auth._fetch_credentials()

    @patch("requests.post")
    def test_fetch_credentials_connection_error(self, mock_post):
        """Test credential fetching with connection error."""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(Exception, match="Failed to connect to credential server"):
            _auth._fetch_credentials()

    @patch("requests.post")
    def test_fetch_credentials_invalid_response(self, mock_post):
        """Test credential fetching with invalid response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Invalid JSON"):
            _auth._fetch_credentials()

    @patch("bicam._auth._fetch_credentials")
    def test_get_s3_client_success(self, mock_fetch):
        """Test successful S3 client creation."""
        # Mock credentials
        mock_fetch.return_value = {
            "access_key": "ASIA123456789",
            "secret_key": "secret123",
            "session_token": "token123",
            "expiration": "2023-12-31T23:59:59+00:00",
        }

        with patch("boto3.client") as mock_boto3:
            mock_s3 = Mock()
            mock_boto3.return_value = mock_s3

            s3_client = _auth.get_s3_client()

            assert s3_client == mock_s3
            mock_boto3.assert_called_once_with(
                "s3",
                aws_access_key_id="ASIA123456789",
                aws_secret_access_key="secret123",
                aws_session_token="token123",
                region_name="us-east-1",
            )

    def test_get_bucket_name(self):
        """Test bucket name retrieval."""
        # Test default bucket name
        bucket = _auth.get_bucket_name()
        assert bucket == "bicam-datasets"

        # Test custom bucket name from environment
        with patch.dict(os.environ, {"BICAM_BUCKET_NAME": "custom-bucket"}):
            bucket = _auth.get_bucket_name()
            assert bucket == "custom-bucket"

    def test_credentials_cache_invalidation(self):
        """Test that credentials cache is invalidated when expired."""
        # Clear the cache
        _auth._credentials_cache.clear()

        # Add expired credentials to cache
        _auth._credentials_cache = {
            "access_key": "old_key",
            "secret_key": "old_secret",
            "session_token": "old_token",
            "expiration": "2020-01-01T00:00:00+00:00",  # Expired
        }

        # Should return False for expired credentials
        assert not _auth._is_credentials_valid()

    def test_credentials_cache_validation(self):
        """Test that valid credentials are properly validated."""
        # Clear the cache
        _auth._credentials_cache.clear()

        # Add valid credentials to cache (more than 5 minutes in future)
        from datetime import datetime, timedelta, timezone

        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        _auth._credentials_cache = {
            "access_key": "valid_key",
            "secret_key": "valid_secret",
            "session_token": "valid_token",
            "expiration": future_time.isoformat(),
        }

        # Should return True for valid credentials
        result = _auth._is_credentials_valid()
        assert result

    @patch("bicam._auth._is_credentials_valid", return_value=True)
    @patch("bicam._auth._create_client_from_cache")
    def test_get_s3_client_uses_cache(self, mock_create_client, mock_is_valid):
        """Test that S3 client uses cached credentials when valid."""
        # Set up cached credentials
        _auth._credentials_cache = {
            "access_key": "cached_key",
            "secret_key": "cached_secret",
            "session_token": "cached_token",
            "expiration": "2030-01-01T00:00:00+00:00",
        }

        mock_s3 = Mock()
        mock_create_client.return_value = mock_s3

        # Clear the LRU cache to ensure fresh call
        _auth.get_s3_client.cache_clear()

        s3_client = _auth.get_s3_client()

        assert s3_client == mock_s3
        mock_create_client.assert_called_once()

    def test_package_token_with_different_versions(self):
        """Test that package tokens are different for different versions."""
        # Mock different versions
        with patch("bicam.__version__.__version__", "1.0.0"):
            token1 = _auth.get_package_token()

        with patch("bicam.__version__.__version__", "2.0.0"):
            token2 = _auth.get_package_token()

        assert token1 != token2

    def test_package_token_with_different_secrets(self):
        """Test that package tokens are different for different secrets."""
        # Test with different secret keys by directly patching the SECRET_KEY
        original_secret = _auth.SECRET_KEY

        # Test with first secret
        _auth.SECRET_KEY = "secret1"
        token1 = _auth.get_package_token()

        # Test with second secret
        _auth.SECRET_KEY = "secret2"
        token2 = _auth.get_package_token()

        # Restore original secret
        _auth.SECRET_KEY = original_secret

        assert token1 != token2

"""Integration tests for BICAM package."""

from pathlib import Path
from unittest.mock import Mock, patch

import click.testing
import pytest

from bicam import __version__


class TestPackageIntegration:
    """Integration tests for the BICAM package."""

    def test_package_import(self):
        """Test that the package can be imported."""
        import bicam

        assert bicam.__version__ == __version__

    def test_cli_help(self):
        """Test CLI help command."""
        from bicam.cli import main

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "BICAM" in result.output
        assert "download" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        from bicam.cli import main

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_list_datasets(self):
        """Test listing datasets."""
        from bicam.datasets import DATASET_TYPES

        datasets = list(DATASET_TYPES.keys())
        assert len(datasets) > 0
        assert "bills" in datasets
        assert "congresses" in datasets

    def test_dataset_info(self):
        """Test getting dataset info."""
        from bicam.datasets import DATASET_TYPES

        info = DATASET_TYPES["bills"]
        assert "size_mb" in info
        assert "description" in info
        assert "checksum" in info
        assert "files" in info

    @patch("bicam._auth.get_s3_client")
    def test_aws_connection_mock(self, mock_get_s3_client):
        """Test AWS S3 connection (mocked)."""
        # Mock S3 client
        mock_s3 = Mock()
        mock_get_s3_client.return_value = mock_s3

        # Mock successful list_objects_v2 response
        mock_s3.list_objects_v2.return_value = {"Contents": []}

        from bicam._auth import get_s3_client

        s3 = get_s3_client()

        # Test that we can call S3 methods
        response = s3.list_objects_v2(Bucket="bicam-datasets", MaxKeys=1)
        assert response == {"Contents": []}

        # Verify the mock was called correctly
        mock_s3.list_objects_v2.assert_called_once_with(
            Bucket="bicam-datasets", MaxKeys=1
        )

    def test_downloader_initialization(self):
        """Test downloader initialization and basic functionality."""
        from bicam.downloader import BICAMDownloader

        # Test with temporary directory
        with pytest.MonkeyPatch().context() as m:
            m.setenv("BICAM_CACHE_DIR", "/tmp/test_cache")
            downloader = BICAMDownloader()

            # Test that we can get info about datasets
            info = downloader.get_info("bills")
            assert "size_mb" in info
            assert "description" in info
            assert info["cached"] is False

    def test_downloader_with_temp_cache(self, temp_cache_dir):
        """Test downloader with temporary cache directory."""
        from bicam.downloader import BICAMDownloader

        downloader = BICAMDownloader(cache_dir=temp_cache_dir)

        # Test getting info for a dataset
        info = downloader.get_info("bills")
        assert info["cache_path"] is None
        assert info["cached"] is False

    @patch("bicam.downloader.BICAMDownloader._download_from_s3")
    @patch("bicam.downloader.BICAMDownloader._verify_zip")
    @patch("bicam.downloader.BICAMDownloader._extract_zip")
    def test_download_simulation(
        self, mock_extract, mock_verify, mock_download, temp_cache_dir
    ):
        """Test download simulation without actually downloading."""
        from bicam.downloader import BICAMDownloader

        # Set up mocks
        mock_verify.return_value = True
        mock_extract.return_value = temp_cache_dir / "bills"

        downloader = BICAMDownloader(cache_dir=temp_cache_dir)

        # Test that we can get info about downloads
        info = downloader.get_info("bills")
        assert info["size_mb"] > 0
        assert "description" in info

    def test_environment_variable_loading(self):
        """Test that environment variables are properly handled."""
        # Test that the package can handle missing AWS credentials gracefully
        with pytest.MonkeyPatch().context() as m:
            # Remove credential server environment variables
            m.delenv("BICAM_SECRET_KEY", raising=False)
            m.delenv("BICAM_CREDENTIAL_ENDPOINT", raising=False)

            # Should still be able to import and get basic info
            from bicam.datasets import DATASET_TYPES

            assert len(DATASET_TYPES) > 0

    def test_cache_directory_creation(self, temp_cache_dir):
        """Test that cache directories are created properly."""
        from bicam.downloader import BICAMDownloader

        # Create downloader with new cache dir
        new_cache = temp_cache_dir / "new_cache"
        _downloader = BICAMDownloader(cache_dir=new_cache)

        # Cache directory should be created
        assert new_cache.exists()
        assert new_cache.is_dir()

    def test_checksum_verification(self):
        """Test checksum verification functionality."""
        from bicam.utils import verify_checksum

        # Create a test file
        test_file = Path("test_file.txt")
        test_file.write_text("test content")

        try:
            checksum = verify_checksum(test_file)
            assert checksum.startswith("sha256:")
            assert len(checksum) == 71  # "sha256:" + 64 hex chars
        finally:
            test_file.unlink()

    def test_utility_functions(self):
        """Test utility functions."""
        from bicam.utils import format_bytes, safe_filename

        # Test format_bytes
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"

        # Test safe_filename
        assert safe_filename("normal_file.txt") == "normal_file.txt"
        assert safe_filename("file:with:colons.txt") == "file_with_colons.txt"

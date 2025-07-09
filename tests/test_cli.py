"""Tests for the CLI module."""

from pathlib import Path
from unittest.mock import patch

import click.testing

from bicam.cli import main


class TestCLI:
    """Test the CLI functionality."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "BICAM" in result.output
        assert "download" in result.output
        assert "list" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output

    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.get_cache_size")
    def test_list_datasets(self, mock_get_cache_size, mock_list_datasets):
        """Test listing datasets."""
        mock_list_datasets.return_value = ["bills", "members"]
        mock_get_cache_size.return_value = {"total": "1.0 MB"}

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["list-datasets"])

        assert result.exit_code == 0
        assert "bills" in result.output
        assert "members" in result.output

    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.get_cache_size")
    @patch("bicam.cli.get_dataset_info")
    def test_list_datasets_verbose(
        self, mock_get_dataset_info, mock_get_cache_size, mock_list_datasets
    ):
        """Test listing datasets with verbose output."""
        mock_list_datasets.return_value = ["bills"]
        mock_get_cache_size.return_value = {"total": "1.0 MB"}
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["list-datasets", "--detailed"])

        assert result.exit_code == 0
        assert "Test description" in result.output
        assert "Format: CSV" in result.output

    @patch("bicam.cli.get_dataset_info")
    def test_info_dataset(self, mock_get_dataset_info):
        """Test getting dataset info."""
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
            "cached_zip": False,
            "files": ["test.txt", "data.csv"],
        }

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["info", "bills"])

        assert result.exit_code == 0
        assert "bills" in result.output
        assert "Description" in result.output

    @patch("bicam.cli.get_dataset_info")
    def test_info_invalid_dataset(self, mock_get_dataset_info):
        """Test getting info for invalid dataset."""
        mock_get_dataset_info.side_effect = ValueError(
            "Unknown dataset type: invalid_dataset"
        )

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["info", "invalid_dataset"])

        assert result.exit_code != 0

    @patch("bicam.cli.download_dataset")
    @patch("bicam.cli.get_dataset_info")
    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.check_disk_space")
    def test_download_success(
        self,
        mock_check_disk_space,
        mock_list_datasets,
        mock_get_dataset_info,
        mock_download_dataset,
    ):
        """Test successful download."""
        mock_list_datasets.return_value = ["bills"]
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }
        mock_check_disk_space.return_value = True
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["download", "bills"])

        assert result.exit_code == 0
        assert "Dataset downloaded to" in result.output
        mock_download_dataset.assert_called_once_with(
            "bills", force_download=False, cache_dir=None, confirm=False, quiet=False
        )

    @patch("bicam.cli.download_dataset")
    @patch("bicam.cli.get_dataset_info")
    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.check_disk_space")
    def test_download_force(
        self,
        mock_check_disk_space,
        mock_list_datasets,
        mock_get_dataset_info,
        mock_download_dataset,
    ):
        """Test download with force flag."""
        mock_list_datasets.return_value = ["bills"]
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }
        mock_check_disk_space.return_value = True
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["download", "bills", "--force"])

        assert result.exit_code == 0
        mock_download_dataset.assert_called_once_with(
            "bills", force_download=True, cache_dir=None, confirm=False, quiet=False
        )

    @patch("bicam.cli.download_dataset")
    @patch("bicam.cli.get_dataset_info")
    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.check_disk_space")
    def test_download_with_cache_dir(
        self,
        mock_check_disk_space,
        mock_list_datasets,
        mock_get_dataset_info,
        mock_download_dataset,
    ):
        """Test download with custom cache directory."""
        mock_list_datasets.return_value = ["bills"]
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }
        mock_check_disk_space.return_value = True
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        runner = click.testing.CliRunner()
        result = runner.invoke(
            main, ["download", "bills", "--cache-dir", "/custom/cache"]
        )

        assert result.exit_code == 0
        mock_download_dataset.assert_called_once_with(
            "bills",
            force_download=False,
            cache_dir="/custom/cache",
            confirm=False,
            quiet=False,
        )

    @patch("bicam.cli.list_datasets")
    def test_download_invalid_dataset(self, mock_list_datasets):
        """Test download with invalid dataset."""
        mock_list_datasets.return_value = ["bills"]

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["download", "invalid_dataset"])

        assert result.exit_code != 0
        assert "Unknown dataset" in result.output

    @patch("bicam.cli.download_dataset")
    @patch("bicam.cli.get_dataset_info")
    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.check_disk_space")
    def test_download_network_error(
        self,
        mock_check_disk_space,
        mock_list_datasets,
        mock_get_dataset_info,
        mock_download_dataset,
    ):
        """Test download with network error."""
        mock_list_datasets.return_value = ["bills"]
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }
        mock_check_disk_space.return_value = True
        mock_download_dataset.side_effect = Exception("Network error")

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["download", "bills"])

        assert result.exit_code != 0
        assert "Error: Network error" in result.output

    @patch("bicam.cli.download_dataset")
    @patch("bicam.cli.get_dataset_info")
    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.check_disk_space")
    def test_download_quiet(
        self,
        mock_check_disk_space,
        mock_list_datasets,
        mock_get_dataset_info,
        mock_download_dataset,
    ):
        """Test download with quiet flag."""
        mock_list_datasets.return_value = ["bills"]
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }
        mock_check_disk_space.return_value = True
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["download", "bills", "--quiet"])

        assert result.exit_code == 0
        mock_download_dataset.assert_called_once_with(
            "bills", force_download=False, cache_dir=None, confirm=False, quiet=True
        )

    @patch("bicam.cli.download_dataset")
    @patch("bicam.cli.get_dataset_info")
    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.check_disk_space")
    def test_download_confirm(
        self,
        mock_check_disk_space,
        mock_list_datasets,
        mock_get_dataset_info,
        mock_download_dataset,
    ):
        """Test download with --confirm flag bypasses prompt for large datasets."""
        mock_list_datasets.return_value = ["amendments"]
        mock_get_dataset_info.return_value = {
            "description": "Large dataset",
            "size_mb": 2048,  # 2GB
            "extracted_size_mb": 4096,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
        }
        mock_check_disk_space.return_value = True
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["download", "amendments", "--confirm"])

        assert result.exit_code == 0
        # Should not prompt for confirmation, should call download_dataset with confirm=True
        mock_download_dataset.assert_called_once_with(
            "amendments",
            force_download=False,
            cache_dir=None,
            confirm=True,
            quiet=False,
        )

    @patch("bicam.cli.list_datasets")
    @patch("bicam.cli.get_cache_size")
    def test_list_datasets_quiet(self, mock_get_cache_size, mock_list_datasets):
        """Test list-datasets with --quiet flag suppresses output."""
        mock_list_datasets.return_value = ["bills", "members"]
        mock_get_cache_size.return_value = {"total": "1.0 MB"}

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["list-datasets", "--quiet"])

        assert result.exit_code == 0
        assert result.output.strip() == ""

    @patch("bicam.cli.get_dataset_info")
    def test_info_quiet(self, mock_get_dataset_info):
        """Test info with --quiet flag suppresses output."""
        mock_get_dataset_info.return_value = {
            "description": "Test description",
            "size_mb": 100,
            "extracted_size_mb": 200,
            "format": "CSV",
            "congress_range": "93-118",
            "cached": False,
            "cached_zip": False,
            "files": ["test.txt", "data.csv"],
        }
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["info", "bills", "--quiet"])
        assert result.exit_code == 0
        assert result.output.strip() == ""

    @patch("bicam.cli.clear_cache")
    @patch("bicam.cli.get_dataset_info")
    def test_clear_quiet(self, mock_get_dataset_info, mock_clear_cache):
        """Test clear with --quiet flag suppresses output."""
        mock_get_dataset_info.return_value = {"cached": True}
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["clear", "bills", "--yes", "--quiet"])
        assert result.exit_code == 0
        assert result.output.strip() == ""
        mock_clear_cache.assert_called_once_with("bills")

    @patch("bicam.cli.get_cache_size")
    def test_cache_quiet(self, mock_get_cache_size):
        """Test cache with --quiet flag suppresses output."""
        mock_get_cache_size.return_value = {
            "total": "1.0 MB",
            "total_bytes": 1000000,
            "datasets": {"bills": "500 KB", "members": "500 KB"},
        }
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["cache", "--quiet"])
        assert result.exit_code == 0
        assert result.output.strip() == ""

    @patch("bicam.cli.clear_cache")
    @patch("bicam.cli.get_cache_size")
    def test_clear_cache_all(self, mock_get_cache_size, mock_clear_cache):
        mock_get_cache_size.return_value = {"total": "1.0 MB"}
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["clear", "--all", "--yes"])
        assert result.exit_code == 0
        assert "Cleared all cached data" in result.output
        mock_clear_cache.assert_called_once_with()

    @patch("bicam.cli.get_cache_size")
    def test_cache_info(self, mock_get_cache_size):
        """Test cache info command."""
        mock_get_cache_size.return_value = {
            "total": "1.0 MB",
            "total_bytes": 1000000,
            "datasets": {"bills": "500 KB", "members": "500 KB"},
        }

        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["cache"])

        assert result.exit_code == 0
        assert "1.0 MB" in result.output

    def test_no_arguments(self):
        """Test CLI with no arguments."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code == 2  # Click shows help and exits with 2
        assert "Usage" in result.output

    def test_invalid_command(self):
        """Test invalid command."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["invalid_command"])

        assert result.exit_code != 0
        assert "No such command" in result.output

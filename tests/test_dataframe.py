"""Tests for the load_dataframe function."""

from pathlib import Path
from unittest.mock import ANY, patch

import pandas as pd
import pytest

from bicam import DATASET_TYPES, load_dataframe


class TestLoadDataframe:
    """Test the load_dataframe functionality."""

    @patch("bicam.download_dataset")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_with_download(self, mock_exists, mock_download_dataset):
        """Test loading dataframe with download=True."""
        # Simulate: dataset dir does not exist, then file exists after download
        mock_exists.side_effect = [False, True]
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        # Mock pandas read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
            mock_read_csv.return_value = mock_df

            result = load_dataframe("bills", "bills.csv", download=True)

            # Should call download_dataset with auto-confirm for large datasets
            mock_download_dataset.assert_called_once_with(
                "bills", force_download=False, cache_dir=ANY, confirm=True, quiet=False
            )

            # Should return the dataframe
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3

    @patch("bicam.download_dataset")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_with_download_small_dataset(
        self, mock_exists, mock_download_dataset
    ):
        """Test loading dataframe with download=True for small dataset (should not auto-confirm)."""
        mock_exists.side_effect = [False, True]
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        # Mock pandas read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_read_csv.return_value = mock_df

            result = load_dataframe("members", "members.csv", download=True)

            # Should call download_dataset without auto-confirm for small datasets
            mock_download_dataset.assert_called_once_with(
                "members",
                force_download=False,
                cache_dir=ANY,
                confirm=False,
                quiet=False,
            )

            # Should return the dataframe
            assert isinstance(result, pd.DataFrame)

    @patch("bicam.download_dataset")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_with_download_confirm_false(
        self, mock_exists, mock_download_dataset
    ):
        """Test loading dataframe with download=True and confirm=False."""
        mock_exists.side_effect = [False, True]
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        # Mock pandas read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_read_csv.return_value = mock_df

            result = load_dataframe("bills", "bills.csv", download=True, confirm=False)

            # Should call download_dataset with confirm=False (user override)
            mock_download_dataset.assert_called_once_with(
                "bills", force_download=False, cache_dir=ANY, confirm=False, quiet=False
            )

            # Should return the dataframe
            assert isinstance(result, pd.DataFrame)

    @patch("bicam.download_dataset")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_with_download_confirm_true(
        self, mock_exists, mock_download_dataset
    ):
        """Test loading dataframe with download=True and confirm=True."""
        mock_exists.side_effect = [False, True]
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        # Mock pandas read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_read_csv.return_value = mock_df

            result = load_dataframe("bills", "bills.csv", download=True, confirm=True)

            # Should call download_dataset with confirm=True (user override)
            mock_download_dataset.assert_called_once_with(
                "bills", force_download=False, cache_dir=ANY, confirm=True, quiet=False
            )

            # Should return the dataframe
            assert isinstance(result, pd.DataFrame)

    @patch("pathlib.Path.exists")
    def test_load_dataframe_not_cached_no_download(self, mock_exists):
        """Test loading dataframe when not cached and download=False."""
        # Mock that dataset doesn't exist
        mock_exists.return_value = False

        with pytest.raises(
            ValueError, match=r"Dataset 'bills' is not cached.*Set download=True"
        ):
            load_dataframe("bills", "bills.csv", download=False)

    @patch("pathlib.Path.exists")
    def test_load_dataframe_invalid_dataset(self, mock_exists):
        """Test loading dataframe with invalid dataset type."""
        with pytest.raises(
            ValueError, match=r"Unknown dataset type: invalid_dataset.*Available types:"
        ):
            load_dataframe("invalid_dataset", "test.csv")

    @patch("pathlib.Path.exists")
    def test_load_dataframe_invalid_file(self, mock_exists):
        """Test loading dataframe with invalid file name."""
        # Mock that dataset exists
        mock_exists.return_value = True

        with pytest.raises(
            ValueError,
            match=r"File 'invalid_file\.csv' not found in dataset 'bills'.*Available files:",
        ):
            load_dataframe("bills", "invalid_file.csv")

        # The match parameter above ensures the error message is as expected.

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_file_not_found(self, mock_exists, mock_read_csv):
        """Test loading dataframe when file doesn't exist on disk."""
        # Simulate: dataset dir exists, file does not exist
        mock_exists.side_effect = [True, False]
        with pytest.raises(FileNotFoundError) as exc_info:
            load_dataframe("bills", "bills.csv")
        assert "File not found" in str(exc_info.value)

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_load_error(self, mock_exists, mock_read_csv):
        """Test loading dataframe when pandas read_csv fails."""
        # Mock that dataset and file exist
        mock_exists.return_value = True
        mock_read_csv.side_effect = Exception("CSV parsing error")

        with pytest.raises(ValueError, match=r"Error loading.*CSV parsing error"):
            load_dataframe("bills", "bills.csv")

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_no_file_specified(self, mock_exists, mock_read_csv):
        """Test loading dataframe without specifying file_name."""
        # Mock that dataset exists
        mock_exists.return_value = True

        # Mock pandas read_csv
        mock_df = pd.DataFrame({"col1": [1, 2, 3]})
        mock_read_csv.return_value = mock_df

        result = load_dataframe("bills")

        # Should load the first CSV file (bills_metadata.csv)
        # Use the actual path that would be constructed
        from bicam.config import DEFAULT_CACHE_DIR

        expected_file = Path(DEFAULT_CACHE_DIR) / "bills" / "bills.csv"
        mock_read_csv.assert_called_once_with(expected_file)

        # Should return the dataframe
        assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_no_csv_files(self, mock_exists, mock_read_csv):
        """Test loading dataframe when no CSV files are available."""
        # Mock that dataset exists
        mock_exists.return_value = True

        # Temporarily modify DATASET_TYPES to have no CSV files
        original_files = DATASET_TYPES["bills"]["files"]
        DATASET_TYPES["bills"]["files"] = ["data.json", "metadata.txt"]

        try:
            with pytest.raises(
                ValueError, match=r"No CSV files available in dataset 'bills'"
            ):
                load_dataframe("bills")

        finally:
            # Restore original files
            DATASET_TYPES["bills"]["files"] = original_files

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_with_cache_dir(self, mock_exists, mock_read_csv):
        """Test loading dataframe with custom cache directory."""
        # Mock that dataset exists
        mock_exists.return_value = True

        # Mock pandas read_csv
        mock_df = pd.DataFrame({"col1": [1, 2, 3]})
        mock_read_csv.return_value = mock_df

        result = load_dataframe("bills", "bills.csv", cache_dir="/custom/cache")

        # Should use custom cache directory
        expected_file = Path("/custom/cache/bills/bills.csv")
        mock_read_csv.assert_called_once_with(expected_file)
        assert isinstance(result, pd.DataFrame)

    @patch("bicam.download_dataset")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_with_quiet(self, mock_exists, mock_download_dataset):
        """Test loading dataframe with quiet flag."""
        mock_exists.side_effect = [False, True]
        mock_download_dataset.return_value = Path("/tmp/test_dataset")

        # Mock pandas read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_read_csv.return_value = mock_df

            result = load_dataframe("bills", "bills.csv", download=True, quiet=True)

            # Should call download_dataset with quiet=True
            mock_download_dataset.assert_called_once_with(
                "bills", force_download=False, cache_dir=ANY, confirm=True, quiet=True
            )

            # Should return the dataframe
            assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_successful_load(self, mock_exists, mock_read_csv):
        """Test successful dataframe loading."""
        # Mock that dataset exists
        mock_exists.return_value = True

        # Mock pandas read_csv
        mock_df = pd.DataFrame(
            {
                "bill_id": ["HR1", "HR2", "HR3"],
                "title": ["Test Bill 1", "Test Bill 2", "Test Bill 3"],
                "congress": [116, 116, 117],
            }
        )
        mock_read_csv.return_value = mock_df

        result = load_dataframe("bills", "bills.csv")

        # Should return the dataframe with correct data
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ["bill_id", "title", "congress"]
        assert result["bill_id"].iloc[0] == "HR1"

    @patch("pathlib.Path.exists")
    def test_load_dataframe_invalid_engine(self, mock_exists):
        """Test loading dataframe with invalid df_engine."""
        # Mock that dataset exists
        mock_exists.return_value = True

        with pytest.raises(
            ValueError, match=r"Invalid df_engine: invalid_engine.*Available engines:"
        ):
            load_dataframe("bills", "bills.csv", df_engine="invalid_engine")

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_polars_engine(self, mock_exists, mock_read_csv):
        """Test loading dataframe with polars engine."""
        mock_exists.return_value = True
        import sys
        from types import ModuleType

        # Fake polars module if not present
        if "polars" not in sys.modules:
            polars_mod = ModuleType("polars")
            polars_mod.read_csv = lambda *a, **kw: pd.DataFrame({"col1": [1, 2, 3]})
            sys.modules["polars"] = polars_mod
        with patch("polars.read_csv") as mock_polars_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_polars_read_csv.return_value = mock_df
            result = load_dataframe("bills", "bills.csv", df_engine="polars")
            mock_polars_read_csv.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_dataframe_dask_engine_installed(self, mock_exists, mock_read_csv):
        """Test loading dataframe with dask engine when installed."""
        mock_exists.return_value = True
        import sys
        from types import ModuleType

        # Fake dask.dataframe module if not present
        if "dask" not in sys.modules:
            dask_mod = ModuleType("dask")
            dask_df_mod = ModuleType("dask.dataframe")
            dask_df_mod.read_csv = lambda *a, **kw: pd.DataFrame({"col1": [1, 2, 3]})
            sys.modules["dask"] = dask_mod
            sys.modules["dask.dataframe"] = dask_df_mod
        with patch("dask.dataframe.read_csv") as mock_dask_read_csv:
            mock_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_dask_read_csv.return_value = mock_df
            result = load_dataframe("bills", "bills.csv", df_engine="dask")
            mock_dask_read_csv.assert_called_once()
            assert isinstance(result, pd.DataFrame)

    @patch("pathlib.Path.exists")
    def test_load_dataframe_spark_engine_not_installed(self, mock_exists):
        """Test loading dataframe with spark engine when not installed."""
        # Mock that dataset exists
        mock_exists.return_value = True

        # Mock that pyspark is not available
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'pyspark'")
        ):
            with pytest.raises(ImportError) as exc_info:
                load_dataframe("bills", "bills.csv", df_engine="spark")

            assert "pyspark is not installed" in str(exc_info.value)
            assert "pip install pyspark" in str(exc_info.value)

    @patch("pathlib.Path.exists")
    def test_load_dataframe_duckdb_engine_not_installed(self, mock_exists):
        """Test loading dataframe with duckdb engine when not installed."""
        # Mock that dataset exists
        mock_exists.return_value = True

        # Mock that duckdb is not available
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'duckdb'")
        ):
            with pytest.raises(ImportError) as exc_info:
                load_dataframe("bills", "bills.csv", df_engine="duckdb")

            assert "duckdb is not installed" in str(exc_info.value)
            assert "pip install duckdb" in str(exc_info.value)

"""BICAM - Congressional and Legislative Data Downloader"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .__version__ import __version__
from .datasets import DATASET_TYPES
from .downloader import BICAMDownloader

# Main API
_downloader = BICAMDownloader()


# User-facing functions
def download_dataset(
    dataset_type: str,
    force_download: bool = False,
    cache_dir: Optional[Union[str, Path]] = None,
    confirm: bool = False,
    quiet: bool = False,
) -> Path:
    """
    Download and load a BICAM dataset.

    Parameters
    ----------
    dataset_type : str
        Type of dataset to download. Options: 'bills', 'amendments', 'members',
        'nominations', 'committees', 'committeereports', 'committeemeetings',
        'committeeprints', 'hearings', 'treaties', 'congresses', 'complete'
    force_download : bool, optional
        Force re-download even if cached. Default: False
    cache_dir : str or Path, optional
        Custom cache directory. Default: ~/.bicam/
    confirm : bool, optional
        Skip confirmation prompts for large datasets (>1GB). Default: False
    quiet : bool, optional
        Suppress log outputs. Default: False

    Returns
    -------
    Path
        Path to the extracted dataset directory

    Examples
    --------
    >>> import bicam
    >>> bills_path = bicam.download_dataset('bills')
    >>> print(f"Bills data available at: {bills_path}")
    """
    cache_dir_path = Path(cache_dir) if cache_dir else None
    return _downloader.download(
        dataset_type, force_download, cache_dir_path, confirm, quiet
    )


def load_dataframe(
    dataset_type: str,
    file_name: Optional[str] = None,
    download: bool = False,
    cache_dir: Optional[Union[str, Path]] = None,
    confirm: Optional[bool] = None,
    quiet: bool = False,
    df_engine: str = "pandas",
) -> Any:
    """
    Load a BICAM dataset directly into a pandas DataFrame.

    Parameters
    ----------
    dataset_type : str
        Type of dataset to load. Options: 'bills', 'amendments', 'members',
        'nominations', 'committees', 'committeereports', 'committeemeetings',
        'committeeprints', 'hearings', 'treaties', 'congresses', 'complete'
    file_name : str, optional
        Specific CSV file to load. If None, loads the first available CSV file.
        For example: 'bills_metadata.csv', 'members_current.csv'
    download : bool, optional
        If True, download the dataset if not cached. If False (default),
        raise an error if dataset is not cached. Default: False
    cache_dir : str or Path, optional
        Custom cache directory. Default: ~/.bicam/
    confirm : bool, optional
        Skip confirmation prompts for large datasets (>1GB).
        If None (default) and download=True, automatically confirms for large datasets.
        If False, will prompt for confirmation even for large datasets.
        Default: None
    quiet : bool, optional
        Suppress log outputs. Default: False
    df_engine : str, optional
        DataFrame engine to use. Options: 'pandas' (default), 'polars', 'dask', 'spark', 'duckdb'.
        Note: dask, spark, and duckdb require the respective packages to be installed.

    Returns
    -------
    DataFrame
        Loaded dataset as a DataFrame in the specified engine format

    Raises
    ------
    ValueError
        If dataset is not cached and download=False, or if file_name is invalid
    FileNotFoundError
        If the specified file doesn't exist in the dataset
    ImportError
        If the specified df_engine is not available

    Examples
    --------
    >>> import bicam
    >>> # Load bills metadata (will download if not cached, auto-confirm for large datasets)
    >>> bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', download=True)
    >>> print(f"Loaded {len(bills_df)} bills")

    >>> # Load members data (will raise error if not cached)
    >>> try:
    ...     members_df = bicam.load_dataframe('members', 'members_current.csv')
    ... except ValueError as e:
    ...     print(f"Dataset not cached: {e}")

    >>> # Force confirmation prompt even for large datasets
    >>> bills_df = bicam.load_dataframe('bills', download=True, confirm=False)

    >>> # Suppress all output during download
    >>> bills_df = bicam.load_dataframe('bills', download=True, quiet=True)

    >>> # Use polars engine
    >>> bills_df = bicam.load_dataframe('bills', df_engine='polars')

    >>> # Use dask engine (requires dask installed)
    >>> bills_df = bicam.load_dataframe('bills', df_engine='dask')
    """

    # Validate dataset type
    if dataset_type not in DATASET_TYPES:
        available = ", ".join(DATASET_TYPES.keys())
        raise ValueError(
            f"Unknown dataset type: {dataset_type}. Available types: {available}"
        )

    # Validate df_engine
    valid_engines = ["pandas", "polars", "dask", "spark", "duckdb"]
    if df_engine not in valid_engines:
        raise ValueError(
            f"Invalid df_engine: {df_engine}. Available engines: {', '.join(valid_engines)}"
        )

    dataset_info = DATASET_TYPES[dataset_type]
    cache_dir_path = Path(cache_dir) if cache_dir else _downloader.cache_dir
    dataset_path = cache_dir_path / dataset_type

    # Check if dataset is cached
    if not dataset_path.exists():
        if download:
            # Determine confirm value for large datasets
            if confirm is None:
                # Auto-confirm for large datasets when download=True
                size_gb = dataset_info["size_mb"] / 1024
                confirm = size_gb > 1

            # Download the dataset
            dataset_path = download_dataset(
                dataset_type,
                force_download=False,
                cache_dir=cache_dir,
                confirm=confirm,
                quiet=quiet,
            )
        else:
            # Raise informative error
            size_gb = dataset_info["size_mb"] / 1024
            raise ValueError(
                f"Dataset '{dataset_type}' is not cached. "
                f"Set download=True to download it ({size_gb:.1f}GB). "
                f"Example: load_dataframe('{dataset_type}', download=True)"
            )

    # Determine which file to load
    available_files = dataset_info["files"]

    if file_name is None:
        # Load the first CSV file
        csv_files = [f for f in available_files if f.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"No CSV files available in dataset '{dataset_type}'")
        file_name = csv_files[0]
    else:
        # Validate file name
        if file_name not in available_files:
            raise ValueError(
                f"File '{file_name}' not found in dataset '{dataset_type}'. "
                f"Available files: {', '.join(available_files)}"
            )

    # Load the file
    file_path = dataset_path / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        return _load_with_engine(file_path, df_engine)
    except ImportError:
        # Re-raise ImportError as-is (for missing engines)
        raise
    except Exception as e:
        raise ValueError(f"Error loading {file_path} with {df_engine}: {e}") from e


def _load_with_engine(file_path: Path, df_engine: str) -> Any:
    """
    Load a CSV file using the specified DataFrame engine.

    Parameters
    ----------
    file_path : Path
        Path to the CSV file
    df_engine : str
        DataFrame engine to use

    Returns
    -------
    DataFrame
        Loaded data in the specified engine format
    """

    if df_engine == "pandas":
        import pandas as pd

        return pd.read_csv(file_path)

    elif df_engine == "polars":
        import polars as pl

        return pl.read_csv(file_path)

    elif df_engine == "dask":
        try:
            import dask.dataframe as dd

            return dd.read_csv(file_path)
        except ImportError as e:
            raise ImportError(
                "dask is not installed. Install it with: pip install dask[dataframe]"
            ) from e

    elif df_engine == "spark":
        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()
            return spark.read.csv(str(file_path), header=True, inferSchema=True)
        except ImportError as e:
            raise ImportError(
                "pyspark is not installed. Install it with: pip install pyspark"
            ) from e

    elif df_engine == "duckdb":
        try:
            import duckdb

            return duckdb.read_csv(str(file_path))
        except ImportError as e:
            raise ImportError(
                "duckdb is not installed. Install it with: pip install duckdb"
            ) from e

    else:
        raise ValueError(f"Unsupported df_engine: {df_engine}")


def list_datasets() -> List[str]:
    """List all available dataset types."""
    return list(DATASET_TYPES.keys())


def get_dataset_info(dataset_type: str) -> Dict[str, Any]:
    """Get information about a specific dataset."""
    return _downloader.get_info(dataset_type)


def clear_cache(dataset_type: Optional[str] = None) -> None:
    """Clear cached data."""
    return _downloader.clear_cache(dataset_type)


def get_cache_size() -> Dict[str, Any]:
    """Get cache size information."""
    return _downloader.get_cache_size()


__all__ = [
    "download_dataset",
    "load_dataframe",
    "list_datasets",
    "get_dataset_info",
    "clear_cache",
    "get_cache_size",
    "__version__",
]

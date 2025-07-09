API Reference
=============

This page provides detailed documentation for the BICAM Python API.

Main Functions
-------------

.. automodule:: bicam
   :members:
   :undoc-members:
   :show-inheritance:

Downloader Class
---------------

.. automodule:: bicam.downloader
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

.. automodule:: bicam.config
   :members:
   :undoc-members:
   :show-inheritance:

Datasets
--------

.. automodule:: bicam.datasets
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

.. automodule:: bicam.utils
   :members:
   :undoc-members:
   :show-inheritance:

Command Line Interface
---------------------

The BICAM command-line interface provides easy access to all functionality.

**Main Commands**

.. code-block:: bash

   bicam --help                    # Show help
   bicam --version                 # Show version
   bicam list-datasets             # List datasets
   bicam download <dataset>        # Download dataset
   bicam info <dataset>            # Show dataset info
   bicam cache                     # Show cache info
   bicam clear <dataset>           # Clear cache

**Download Options**

.. code-block:: bash

   bicam download <dataset> [OPTIONS]

   Options:
     --force, -f              Force re-download
     --cache-dir PATH         Custom cache directory
     --no-extract             Download only, do not extract
     --confirm                Skip confirmation for large datasets
     --quiet, -q              Suppress log outputs

**List Options**

.. code-block:: bash

   bicam list-datasets [OPTIONS]

   Options:
     --detailed, -d           Show detailed information
     --quiet, -q              Suppress log outputs

**Info Options**

.. code-block:: bash

   bicam info <dataset> [OPTIONS]

   Options:
     --quiet, -q              Suppress log outputs

**Cache Options**

.. code-block:: bash

   bicam cache [OPTIONS]

   Options:
     --quiet, -q              Suppress log outputs

**Clear Options**

.. code-block:: bash

   bicam clear [OPTIONS] [DATASET]

   Options:
     --all                    Clear all cached data
     --yes                    Confirm cache clear without prompt
     --quiet, -q              Suppress log outputs

Function Reference
-----------------

download_dataset
~~~~~~~~~~~~~~~

.. function:: bicam.download_dataset(dataset_type, force_download=False, cache_dir=None, confirm=False, quiet=False)

   Download and load a BICAM dataset.

   **Parameters:**

   * **dataset_type** (str) -- Type of dataset to download. Options: 'bills', 'amendments', 'members', 'nominations', 'committees', 'committeereports', 'committeemeetings', 'committeeprints', 'hearings', 'treaties', 'congresses', 'complete'
   * **force_download** (bool, optional) -- Force re-download even if cached. Default: False
   * **cache_dir** (str or Path, optional) -- Custom cache directory. Default: ~/.bicam/
   * **confirm** (bool, optional) -- Skip confirmation prompts for large datasets (>1GB). Default: False
   * **quiet** (bool, optional) -- Suppress log outputs. Default: False

   **Returns:**

   * **Path** -- Path to the extracted dataset directory

   **Examples:**

   .. code-block:: python

      import bicam
      bills_path = bicam.download_dataset('bills')
      print(f"Bills data available at: {bills_path}")

load_dataframe
~~~~~~~~~~~~~

.. function:: bicam.load_dataframe(dataset_type, file_name=None, download=False, cache_dir=None, confirm=None, quiet=False, df_engine="pandas")

   Load a BICAM dataset directly into a pandas DataFrame.

   **Parameters:**

   * **dataset_type** (str) -- Type of dataset to load. Options: 'bills', 'amendments', 'members', 'nominations', 'committees', 'committeereports', 'committeemeetings', 'committeeprints', 'hearings', 'treaties', 'congresses', 'complete'
   * **file_name** (str, optional) -- Specific CSV file to load. If None, loads the first available CSV file. For example: 'bills_metadata.csv', 'members_current.csv'
   * **download** (bool, optional) -- If True, download the dataset if not cached. If False (default), raise an error if dataset is not cached. Default: False
   * **cache_dir** (str or Path, optional) -- Custom cache directory. Default: ~/.bicam/
   * **confirm** (bool, optional) -- Skip confirmation prompts for large datasets (>1GB). If None (default) and download=True, automatically confirms for large datasets. If False, will prompt for confirmation even for large datasets. Default: None
   * **quiet** (bool, optional) -- Suppress log outputs. Default: False
   * **df_engine** (str, optional) -- DataFrame engine to use. Options: 'pandas' (default), 'polars', 'dask', 'spark', 'duckdb'. Note: dask, spark, and duckdb require the respective packages to be installed. Default: "pandas"

   **Returns:**

   * **DataFrame** -- Loaded dataset as a DataFrame in the specified engine format

   **Raises:**

   * **ValueError** -- If dataset is not cached and download=False, or if file_name is invalid
   * **FileNotFoundError** -- If the specified file doesn't exist in the dataset
   * **ImportError** -- If the specified df_engine is not available

   **Examples:**

   .. code-block:: python

      import bicam

      # Load bills metadata (will download if not cached, auto-confirm for large datasets)
      bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', download=True)
      print(f"Loaded {len(bills_df)} bills")

      # Load members data (will raise error if not cached)
      try:
          members_df = bicam.load_dataframe('members', 'members_current.csv')
      except ValueError as e:
          print(f"Dataset not cached: {e}")

      # Force confirmation prompt even for large datasets
      bills_df = bicam.load_dataframe('bills', download=True, confirm=False)

      # Suppress all output during download
      bills_df = bicam.load_dataframe('bills', download=True, quiet=True)

      # Use polars engine (included by default)
      bills_df = bicam.load_dataframe('bills', df_engine='polars')

      # Use dask engine (requires dask installed)
      bills_df = bicam.load_dataframe('bills', df_engine='dask')

      # Use spark engine (requires pyspark installed)
      bills_df = bicam.load_dataframe('bills', df_engine='spark')

      # Use duckdb engine (requires duckdb installed)
      bills_df = bicam.load_dataframe('bills', df_engine='duckdb')

      # Load first available CSV file
      df = bicam.load_dataframe('bills', download=True)

list_datasets
~~~~~~~~~~~~

.. function:: bicam.list_datasets()

   List all available dataset types.

   **Returns:**

   * **list** -- List of available dataset names

   **Examples:**

   .. code-block:: python

      import bicam
      datasets = bicam.list_datasets()
      print(f"Available datasets: {datasets}")

get_dataset_info
~~~~~~~~~~~~~~~

.. function:: bicam.get_dataset_info(dataset_type)

   Get information about a specific dataset.

   **Parameters:**

   * **dataset_type** (str) -- Name of the dataset

   **Returns:**

   * **dict** -- Dataset information including size, description, and file list

   **Examples:**

   .. code-block:: python

      import bicam
      info = bicam.get_dataset_info('bills')
      print(f"Size: {info['size_mb']} MB")
      print(f"Files: {info['files']}")

clear_cache
~~~~~~~~~~

.. function:: bicam.clear_cache(dataset_type=None)

   Clear cached data.

   **Parameters:**

   * **dataset_type** (str, optional) -- Specific dataset to clear. If None, clears all cached data.

   **Examples:**

   .. code-block:: python

      import bicam

      # Clear specific dataset
      bicam.clear_cache('bills')

      # Clear all cached data
      bicam.clear_cache()

get_cache_size
~~~~~~~~~~~~~

.. function:: bicam.get_cache_size()

   Get cache size information.

   **Returns:**

   * **dict** -- Cache size information including total size and per-dataset breakdown

   **Examples:**

   .. code-block:: python

      import bicam
      cache_info = bicam.get_cache_size()
      print(f"Total cache size: {cache_info['total']}")

BICAMDownloader Class
--------------------

The main downloader class for BICAM datasets.

.. class:: bicam.downloader.BICAMDownloader(cache_dir=None)

   **Parameters:**

   * **cache_dir** (Path, optional) -- Custom cache directory

   **Methods:**

   .. method:: download(dataset_type, force_download=False, cache_dir=None, confirm=False, quiet=False)

      Download and extract a dataset.

      **Parameters:**

      * **dataset_type** (str) -- Type of dataset to download
      * **force_download** (bool) -- Force re-download even if cached
      * **cache_dir** (str) -- Custom cache directory
      * **confirm** (bool) -- Skip confirmation for large datasets
      * **quiet** (bool) -- Suppress log outputs

      **Returns:**

      * **Path** -- Path to the extracted dataset directory

   .. method:: get_info(dataset_type)

      Get information about a dataset.

      **Parameters:**

      * **dataset_type** (str) -- Name of the dataset

      **Returns:**

      * **dict** -- Dataset information

   .. method:: clear_cache(dataset_type=None)

      Clear cached data.

      **Parameters:**

      * **dataset_type** (str, optional) -- Specific dataset to clear

   .. method:: get_cache_size()

      Get cache size information.

      **Returns:**

      * **dict** -- Cache size information

Configuration
------------

.. data:: bicam.config.DEFAULT_CACHE_DIR

   Default cache directory path.

.. data:: bicam.config.MAX_RETRIES

   Maximum number of retry attempts for downloads.

.. data:: bicam.config.RETRY_DELAY

   Delay between retry attempts in seconds.

Utility Functions
----------------

.. function:: bicam.utils.format_bytes(bytes_value)

   Format bytes into human-readable string.

   **Parameters:**

   * **bytes_value** (int) -- Number of bytes

   **Returns:**

   * **str** -- Formatted string (e.g., "1.5 MB")

.. function:: bicam.utils.estimate_download_time(size_mb, speed_mbps=10)

   Estimate download time for a dataset.

   **Parameters:**

   * **size_mb** (float) -- Size in megabytes
   * **speed_mbps** (float) -- Download speed in Mbps

   **Returns:**

   * **str** -- Estimated time string

.. function:: bicam.utils.check_disk_space(path, required_mb)

   Check if sufficient disk space is available.

   **Parameters:**

   * **path** (Path) -- Path to check
   * **required_mb** (float) -- Required space in MB

   **Returns:**

   * **bool** -- True if sufficient space available

.. function:: bicam.utils.verify_checksum(file_path, algorithm='sha256')

   Verify file checksum.

   **Parameters:**

   * **file_path** (Path) -- Path to file
   * **algorithm** (str) -- Hash algorithm

   **Returns:**

   * **str** -- Checksum string

Error Handling
-------------

BICAM functions may raise the following exceptions:

.. exception:: ValueError

   Raised when an invalid dataset type is provided or when dataset information is not found.

.. exception:: OSError

   Raised when there are file system or network issues.

.. exception:: Exception

   Raised for other errors such as authentication failures or corrupted downloads.

**Example Error Handling:**

.. code-block:: python

   import bicam

   try:
       bills_path = bicam.download_dataset('bills')
   except ValueError as e:
       print(f"Invalid dataset: {e}")
   except OSError as e:
       print(f"System error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Environment Variables
--------------------

BICAM recognizes the following environment variables:

* **BICAM_DATA** -- Custom cache directory path
* **BICAM_LOG_LEVEL** -- Logging level (DEBUG, INFO, WARNING, ERROR)
* **BICAM_CHECK_VERSION** -- Enable/disable version checking

**Example:**

.. code-block:: bash

   export BICAM_DATA=/custom/cache/path
   export BICAM_LOG_LEVEL=DEBUG
   python -c "import bicam; bicam.download_dataset('bills')"

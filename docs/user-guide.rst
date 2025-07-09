User Guide
==========

This guide covers how to use BICAM to download and work with congressional datasets.

Command Line Interface
---------------------

BICAM provides a simple command-line interface for downloading and managing datasets.

**List Available Datasets**
View all available datasets and their sizes:

.. code-block:: bash

   bicam list-datasets

For detailed information:

.. code-block:: bash

   bicam list-datasets --detailed

**Download a Dataset**
Download a specific dataset:

.. code-block:: bash

   bicam download bills

Download with options:

.. code-block:: bash

   # Force re-download
   bicam download bills --force

   # Use custom cache directory
   bicam download bills --cache-dir /path/to/cache

   # Skip confirmation for large (> 1GB) datasets
   bicam download complete --confirm

   # Suppress output
   bicam download bills --quiet

**Get Dataset Information**
View detailed information about a dataset:

.. code-block:: bash

   bicam info bills

**Manage Cache**
View cache information:

.. code-block:: bash

   bicam cache

Clear specific dataset:

.. code-block:: bash

   bicam clear bills

Clear all cached data:

.. code-block:: bash

   bicam clear --all

Python API
---------

BICAM also provides a Python API for programmatic access.

**Basic Usage**

.. code-block:: python

   import bicam

   # Download a dataset
   bills_path = bicam.download_dataset('bills')
   print(f"Bills data available at: {bills_path}")

**Loading Data as DataFrames**

The easiest way to work with BICAM data is using the `load_dataframe` function:

.. code-block:: python

   import bicam
   import pandas as pd

   # Load bills data directly into a DataFrame (downloads if needed, auto-confirms for large datasets)
   bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', download=True)
   print(f"Loaded {len(bills_df)} bills")

   # Load members data (will raise error if not cached)
   try:
       members_df = bicam.load_dataframe('members', 'members_current.csv')
   except ValueError as e:
       print(f"Dataset not cached: {e}")
       # Download it first
       members_df = bicam.load_dataframe('members', 'members_current.csv', download=True)

   # Load first available CSV file from a dataset
   df = bicam.load_dataframe('bills', download=True)

   # Force confirmation prompt for large datasets
   bills_df = bicam.load_dataframe('bills', download=True, confirm=False)

   # Suppress all output during download
   bills_df = bicam.load_dataframe('bills', download=True, quiet=True)

   # Use different DataFrame engines
   # Polars (included by default)
   bills_df = bicam.load_dataframe('bills', df_engine='polars')

   # Dask (requires dask installed)
   bills_df = bicam.load_dataframe('bills', df_engine='dask')

   # Spark (requires pyspark installed)
   bills_df = bicam.load_dataframe('bills', df_engine='spark')

   # DuckDB (requires duckdb installed)
   bills_df = bicam.load_dataframe('bills', df_engine='duckdb')

**Advanced Options**

.. code-block:: python

   # Force re-download
   bills_path = bicam.download_dataset('bills', force_download=True)

   # Custom cache directory
   bills_path = bicam.download_dataset('bills', cache_dir='/custom/path')

   # Skip confirmation for large (> 1GB) datasets
   bills_path = bicam.download_dataset('complete', confirm=True)

   # Suppress logging
   bills_path = bicam.download_dataset('bills', quiet=True)

**Dataset Information**

.. code-block:: python

   # List all datasets
   datasets = bicam.list_datasets()
   print(f"Available datasets: {datasets}")

   # Get info about a dataset
   info = bicam.get_dataset_info('bills')
   print(f"Size: {info['size_mb']} MB")
   print(f"Description: {info['description']}")

**Cache Management**

.. code-block:: python

   # Get cache size
   cache_info = bicam.get_cache_size()
   print(f"Total cache size: {cache_info['total']}")

   # Clear specific dataset
   bicam.clear_cache('bills')

   # Clear all cache
   bicam.clear_cache()

Working with Data
----------------

**Using pandas with load_dataframe**

.. code-block:: python

   import bicam
   import pandas as pd

   # Load bills data directly into DataFrame
   bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', download=True)

   # Basic analysis
   print(f"Total bills: {len(bills_df)}")
   print(f"Congress range: {bills_df['congress'].min()} - {bills_df['congress'].max()}")

   # Filter recent bills
   recent_bills = bills_df[bills_df['congress'] >= 115]
   print(f"Recent bills: {len(recent_bills)}")

**Using different DataFrame engines**

.. code-block:: python

   import bicam

   # Load with polars (faster for large datasets)
   bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', df_engine='polars')
   print(f"Loaded {len(bills_df)} bills with polars")

   # Load with dask (for out-of-memory processing)
   bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', df_engine='dask')
   print(f"Loaded bills with dask: {bills_df.npartitions} partitions")

   # Load with spark (for distributed processing)
   bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', df_engine='spark')
   print(f"Loaded bills with spark: {bills_df.count()} rows")

**Working with Multiple Datasets**

.. code-block:: python

   import bicam

   # Load multiple datasets as DataFrames
   bills_sponsors_df = bicam.load_dataframe('bills', 'bills_sponsors.csv', download=True)
   members_df = bicam.load_dataframe('members', 'members.csv', download=True)

   # Join data (example)
   # bills_with_sponsors_detailed = bills_sponsors_df.merge(members_df, left_on='bioguide_id')

**Data Exploration**

.. code-block:: python

   # Explore bills dataset
   bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', download=True)

   # View columns
   print(bills_df.columns.tolist())

   # Basic statistics
   print(bills_df.describe())

   # Value counts
   print(bills_df['congress'].value_counts().sort_index())

Best Practices
-------------

**Dataset Selection**

* Start with smaller datasets like ``congresses`` or ``members``
* Use ``bills`` for legislative analysis
* Download ``complete`` only if you need all data

**Performance Tips**

* Use ``--quiet`` for automated scripts
* Use ``--confirm`` to skip prompts in batch operations
* Monitor disk space before downloading large datasets
* Use ``df_engine='polars'`` for faster loading of large datasets
* Use ``df_engine='dask'`` for out-of-memory processing

**Data Management**

* Use ``bicam cache`` to monitor storage usage
* Clear unused datasets with ``bicam clear``
* Consider using custom cache directories for different projects

**Error Handling**

* Use try/except blocks to handle download or loading errors. For example:

    .. code-block:: python

       import bicam

       try:
           bills_df = bicam.load_dataframe('bills', download=True)
       except Exception as e:
           print(f"Download failed: {e}")
           # Handle error appropriately

Examples
--------

**Legislative Analysis**

.. code-block:: python

   import bicam

   # Load bills and amendments data
   bills_df = bicam.load_dataframe('bills', 'bills.csv', download=True)

   # Analyze bill types by congress
   bill_types = bills_df.groupby('congress')['bill_type'].value_counts()
   print("Number of different bill types by congress:")
   print(bill_types)

**Committee Analysis**

.. code-block:: python

   import bicam

   # Load committee and hearing-committee mapping data
   committees_df = bicam.load_dataframe('committees', 'committees.csv', download=True)
   hearings_committees_df = bicam.load_dataframe('hearings', 'hearings_committees.csv', download=True)

   # Join on 'committee_code' to find committees with hearings that are current
   merged = hearings_committees_df.merge(
       committees_df[['committee_code', 'is_current']],
       on='committee_code',
       how='inner'
   )

   # Filter for current committees
   current_committees_with_hearings = merged[merged['is_current'] == True]

   print("Committees with hearings where is_current is True:")
   print(current_committees_with_hearings['committee_code'].unique())

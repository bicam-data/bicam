Welcome to BICAM's documentation!
================================

BICAM is a Python package for downloading and working with the BICAM (Bulk Ingestion of Congressional Actions & Materials) dataset. It provides easy access to bills, amendments, members, committees, hearings, and more from official government sources.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user-guide
   datasets
   api-reference
   troubleshooting

Quick Start
----------

Install BICAM and start downloading datasets:

.. code-block:: bash

   pip install bicam
   bicam list
   bicam download congresses

Features
--------

* **12 Comprehensive Datasets**: Bills, amendments, members, committees, hearings, and more
* **Simple Format**: CSV files for easy analysis with pandas, R, or other data analysis tools
* **Automatic Caching**: Downloads are cached locally to avoid re-downloading
* **Command Line Interface**: Streamlined CLI for quick access
* **Python API**: Full programmatic access for analysis

Available Datasets
-----------------

* **bills** (~2.5GB) - Complete bills data with text and metadata
* **amendments** (~800MB) - All amendments with voting records
* **members** (~150MB) - Historical and current member information
* **nominations** (~400MB) - Presidential nominations data
* **committees** (~200MB) - Committee membership and metadata
* **committeereports** (~1.2GB) - Full text of committee reports
* **committeemeetings** (~600MB) - Committee meeting records
* **committeeprints** (~900MB) - Committee prints and documents
* **hearings** (~3.5GB) - Hearing transcripts and testimonies
* **treaties** (~300MB) - Treaty documents and ratification records
* **congresses** (~100MB) - Congressional session metadata
* **complete** (~12GB) - All datasets combined

Example Usage
------------

.. code-block:: python

   import bicam
   import pandas as pd

   # Download bills dataset
   bills_path = bicam.download_dataset('bills')

   # Load and analyze data using BICAM's loader
   bills_df = bicam.load_dataframe('bills', 'bills.csv')
   print(f"Total bills: {len(bills_df)}")

   # Filter by congress
   recent_bills = bills_df[bills_df['congress'] >= 115]
   print(f"Recent bills (115th+): {len(recent_bills)}")

Support
-------

* **Documentation**: Check the guides in this documentation
* **GitHub Issues**: `Report bugs <https://github.com/bicam-data/bicam/issues>`_
* **Email Support**: bicam.data@gmail.com
* **Feedback**: https://bicam.net/feedback

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

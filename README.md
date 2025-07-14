# BICAM - Comprehensive Congressional Data Downloader

[![PyPI version](https://badge.fury.io/py/bicam.svg)](https://badge.fury.io/py/bicam)
[![Python versions](https://img.shields.io/pypi/pyversions/bicam.svg)](https://pypi.org/project/bicam/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The BICAM package provides easy programmatic access to the Bulk Ingestion of Congressional Actions & Materials (BICAM) dataset, a comprehensive collection of congressional data including bills, amendments, committee reports, hearings, and more sourced from the official [congress.gov](https://congress.gov) and [GovInfo](https://govinfo.gov) APIs.

## Features

- 📦 **11 Dataset Types**: Access bills, amendments, members, committees, hearings, and more
- 🚀 **Fast Downloads**: Optimized S3 downloads with progress tracking
- 💾 **Smart Caching**: Automatic local caching to avoid re-downloads
- 🔧 **Simple API**: Both Python API and command-line interface
- ✅ **Data Integrity**: Automatic checksum verification
- 📊 **Large Scale**: Efficiently handles datasets from 100MB to 12GB+

## Installation

### From PyPI (Recommended)

```bash
# Using uv (faster, recommended)
uv pip install bicam

# Using pip (alternative)
pip install bicam
```

### From Source

```bash
# Clone and install in development mode
git clone https://github.com/bicam-data/bicam
cd bicam
uv pip install -e .
```

## Quick Start

### Python API

```python
import bicam

# Download a dataset
bills_path = bicam.download_dataset('bills')
print(f"Bills data available at: {bills_path}")

# Load data directly into a DataFrame (downloads if needed, auto-confirms for large datasets)
bills_df = bicam.load_dataframe('bills', 'bills.csv', download=True)
print(f"Loaded {len(bills_df)} bills")

# Load members data (will raise error if not cached)
try:
    members_df = bicam.load_dataframe('members', 'members.csv')
except ValueError as e:
    print(f"Dataset not cached: {e}")
    # Download it first
    members_df = bicam.load_dataframe('members', 'members.csv', download=True)

# Load first available CSV file from a dataset
df = bicam.load_dataframe('bills', download=True)

# Use different DataFrame engines
bills_df = bicam.load_dataframe('bills', 'bills.csv', df_engine='polars')  # Faster for large datasets
bills_df = bicam.load_dataframe('bills', 'bills.csv', df_engine='dask')    # Out-of-memory processing
bills_df = bicam.load_dataframe('bills', 'bills.csv', df_engine='spark')   # Distributed processing
bills_df = bicam.load_dataframe('bills', 'bills.csv', df_engine='duckdb')  # SQL-like queries

# List available datasets
datasets = bicam.list_datasets()
print(f"Available datasets: {datasets}")

# Get dataset information
info = bicam.get_dataset_info('bills')
print(f"Size: {info['size_mb']} MB")

# Advanced options
bills_path = bicam.download_dataset('bills', force_download=True)  # Force re-download
bills_path = bicam.download_dataset('bills', cache_dir='/custom/path')  # Custom cache directory
bills_path = bicam.download_dataset('complete', confirm=True)  # Skip confirmation for large datasets
bills_path = bicam.download_dataset('bills', quiet=True)  # Suppress logging

### Command Line Interface

```bash
# List all available datasets
bicam list-datasets

# List with detailed information
bicam list-datasets --detailed

# Download a specific dataset
bicam download bills

# Download with options
bicam download bills --force          # Force re-download
bicam download bills --cache-dir /path/to/cache  # Custom cache directory
bicam download complete --confirm     # Skip confirmation for large datasets
bicam download bills --quiet          # Suppress output

# Get detailed information about a dataset
bicam info bills

# Show cache usage
bicam cache

# Clear cached data
bicam clear bills        # Clear specific dataset
bicam clear --all       # Clear all cached data
```

## Available Datasets

**NOTE:** Ensure that you have extra disk space in order to properly unzip these datasets, as they are stored as .zip files and
automatically unzip into the cache directory. This may require space up to around 30 GB for larger datatypes, such as amendments.

| Dataset | Size | Description |
|---------|------|-------------|
| **bills** | ~1.8GB | Complete bills data including text, summaries, and related records |
| **amendments** | ~6.6GB | All amendments with amended items |
| **members** | ~1MB | Historical and current member information |
| **nominations** | ~21MB | Presidential nominations data |
| **committees** | ~17MB | Committee information, including history of committee names |
| **committeereports** | ~570MB | Committee reports, with full text and related information |
| **committeemeetings** | ~5MB | Committee meeting records |
| **committeeprints** | ~91MB | Committee prints, including full text and topics |
| **hearings** | ~1.7GB | Hearing information, such as address and transcripts |
| **treaties** | ~0MB | Treaty documents with actions, titles, and more |
| **congresses** | ~1MB | Congressional session metadata, like directories and session dates |
| **complete** | ~12GB | Complete BICAM dataset with all data types |

## Working with Data

### Basic Analysis

```python
import bicam
import pandas as pd

# Load bills data directly into DataFrame
bills_df = bicam.load_dataframe('bills', 'bills.csv', download=True)

# Basic analysis
print(f"Total bills: {len(bills_df)}")
print(f"Congress range: {bills_df['congress'].min()} - {bills_df['congress'].max()}")

# Filter recent bills
recent_bills = bills_df[bills_df['congress'] >= 115]
print(f"Recent bills: {len(recent_bills)}")
```

### Working with Multiple Datasets

```python
import bicam

# Load multiple datasets as DataFrames
bills_sponsors_df = bicam.load_dataframe('bills', 'bills_sponsors.csv', download=True)
members_df = bicam.load_dataframe('members', 'members.csv', download=True)

# Join data (example)
# bills_with_sponsors_detailed = bills_sponsors_df.merge(members_df, left_on='bioguide_id')
```

## Configuration

### Environment Variables

```bash
# Set custom cache directory (default: ~/.bicam)
export BICAM_DATA=/path/to/cache

# Control logging
export BICAM_LOG_LEVEL=DEBUG

# Disable version check
export BICAM_CHECK_VERSION=false
```

### Python Configuration

```python
import bicam

# Get current cache size
cache_info = bicam.get_cache_size()
print(f"Total cache size: {cache_info['total']}")

# Clear specific dataset cache
bicam.clear_cache('bills')

# Clear all cached data
bicam.clear_cache()
```

## Best Practices

### Dataset Selection

- Start with smaller datasets like `congresses` or `members`
- Use `bills` for legislative analysis
- Download `complete` only if you need all data

### Performance Tips

- Use `--quiet` for automated scripts
- Use `--confirm` to skip prompts in batch operations
- Monitor disk space before downloading large datasets
- Use `df_engine='polars'` for faster loading of large datasets
- Use `df_engine='dask'` for out-of-memory processing

### Data Management

- Use `bicam cache` to monitor storage usage
- Clear unused datasets with `bicam clear`
- Consider using custom cache directories for different projects

### Error Handling

```python
import bicam

try:
    bills_df = bicam.load_dataframe('bills', download=True)
except Exception as e:
    print(f"Download failed: {e}")
    # Handle error appropriately
```

## Contributing

We may welcome contributions in the future. For now, please visit <https://bicam.net/feedback> for suggestions, concerns, or data inaccuracies.

## Citation

If you use BICAM in your research, please cite:

{FUTURE CITATION GOES HERE}

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: <bicam.data@gmail.com>
- 🐛 Issues: [GitHub Issues](https://github.com/bicam-data/bicam/issues)
- 📖 Documentation: [Read the Docs](https://bicam.readthedocs.io)
- 💬 Feedback: [BICAM.net/feedback](https://bicam.net/feedback)

## Acknowledgments

- Congressional data provided by <https://api.congress.gov> and <https://api.govinfo.gov>
- Built with support from MIT and the [LobbyView](https://lobbyview.org) team.

---

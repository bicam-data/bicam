# BICAM - Comprehensive Congressional Data Downloader

[![PyPI version](https://badge.fury.io/py/bicam.svg)](https://badge.fury.io/py/bicam)
[![Python versions](https://img.shields.io/pypi/pyversions/bicam.svg)](https://pypi.org/project/bicam/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The BICAM package provides easy programmatic access to the Bulk Ingestion of Congressional Actions & Materials (BICAM) dataset, a comprehensive collection of congressional data including bills, amendments, committee reports, hearings, and more sourced from the official [congress.gov](https://congress.gov) and [GovInfo](https://govinfo.gov) APIs.

## Features

- 📦 **12 Dataset Types**: Access bills, amendments, members, committees, hearings, and more
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

# Load data directly into a DataFrame (downloads if needed)
bills_df = bicam.load_dataframe('bills', 'bills_metadata.csv', download=True)
print(f"Loaded {len(bills_df)} bills")

# List available datasets
datasets = bicam.list_datasets()
print(f"Available datasets: {datasets}")

# Get dataset information
info = bicam.get_dataset_info('bills')
print(f"Size: {info['size_mb']} MB")
```

### Command Line Interface

```bash
# List all available datasets
bicam list-datasets

# Download a specific dataset
bicam download bills

# Get detailed information about a dataset, such as size and file names
bicam info hearings

# Show cache usage
bicam cache

# Clear cached data
bicam clear bills        # Clear specific dataset
bicam clear --all       # Clear all cached data
```

## Available Datasets

| Dataset | Size | Description |
|---------|------|-------------|
| **bills** | ~2.5GB | Complete bills data including text, summaries, and related records  |
| **amendments** | ~800MB | All amendments with amended items |
| **members** | ~150MB | Historical and current member information |
| **nominations** | ~400MB | Presidential nominations data |
| **committees** | ~200MB | Committee information, including history of committee names |
| **committeereports** | ~1.2GB | Committee reports, with full text and related information |
| **committeemeetings** | ~600MB | Committee meeting records |
| **committeeprints** | ~900MB | Committee prints, including full text and topics |
| **hearings** | ~3.5GB | Hearing information, such as address and transcripts |
| **treaties** | ~300MB | Treaty documents with actions, titles, and more |
| **congresses** | ~100MB | Congressional session metadata, like directories and session dates |
| **complete** | ~12GB | Complete BICAM dataset with all data types |

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

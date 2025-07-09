"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from moto import mock_aws

from bicam.datasets import DATASET_TYPES


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_dataset_files(temp_cache_dir):
    """Create mock dataset files for testing."""

    def create_files(dataset_type):
        dataset_dir = temp_cache_dir / dataset_type
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Create expected files based on dataset type
        if dataset_type in DATASET_TYPES:
            for file in DATASET_TYPES[dataset_type]["files"]:
                if file != "All files from individual datasets":
                    (dataset_dir / file).touch()

        return dataset_dir

    return create_files


@pytest.fixture
@mock_aws
def mock_s3_bucket():
    """Create a mock S3 bucket with test data."""
    # Create mock S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="bicam-datasets")

    # Upload mock files for each dataset
    for _dataset_type, info in DATASET_TYPES.items():
        # Create a dummy zip file
        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
            # Write some data
            tmp.write(b"PK\x03\x04" + b"0" * 1000)  # Minimal zip header
            tmp.flush()

            # Upload to S3
            s3.upload_file(tmp.name, "bicam-datasets", info["key"])

    return s3


@pytest.fixture
def mock_auth(monkeypatch):
    """Mock authentication to avoid using real credentials."""
    mock_client = Mock()

    def mock_get_s3_client():
        return mock_client

    monkeypatch.setattr("bicam.downloader.get_s3_client", mock_get_s3_client)
    monkeypatch.setattr("bicam._auth.get_s3_client", mock_get_s3_client)

    return mock_client


@pytest.fixture
def mock_downloader(temp_cache_dir, mock_auth):
    """Create a mock downloader instance."""
    from bicam.downloader import BICAMDownloader

    return BICAMDownloader(cache_dir=temp_cache_dir)


@pytest.fixture
def sample_zip_file():
    """Create a sample zip file for testing."""
    import zipfile

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("test.txt", "test content")
            zf.writestr("data.csv", "col1,col2\n1,2\n3,4")

        yield Path(tmp.name)

    # Cleanup
    if Path(tmp.name).exists():
        Path(tmp.name).unlink()

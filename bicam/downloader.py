"""Main downloader functionality."""

import logging
import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from tqdm import tqdm

from ._auth import get_s3_client
from .config import (
    DEFAULT_CACHE_DIR,
    MAX_RETRIES,
    RETRY_DELAY,
    S3_BUCKET,
)
from .datasets import DATASET_TYPES
from .utils import format_bytes, get_directory_size, verify_checksum

logger = logging.getLogger(__name__)


class BICAMDownloader:
    """Downloader for BICAM datasets."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.s3_client = None
        self._download_history: Dict[str, Any] = {}

    def _get_s3_client(self) -> boto3.client:
        """Lazy load S3 client."""
        if self.s3_client is None:
            self.s3_client = get_s3_client()
        return self.s3_client

    def download(
        self,
        dataset_type: str,
        force_download: bool = False,
        cache_dir: Optional[Path] = None,
        confirm: bool = False,
        quiet: bool = False,
    ) -> Path:
        """Download and extract a dataset."""
        if dataset_type not in DATASET_TYPES:
            available = ", ".join(DATASET_TYPES.keys())
            raise ValueError(
                f"Unknown dataset type: {dataset_type}. Available types: {available}"
            )

        # Set up quiet mode
        if quiet:
            logger.setLevel(logging.ERROR)
            # Disable tqdm progress bars
            import os

            os.environ["TQDM_DISABLE"] = "1"

        # Use custom cache dir if provided
        cache_dir_path = cache_dir if cache_dir else self.cache_dir
        cache_dir_path.mkdir(parents=True, exist_ok=True)

        # Paths
        dataset_info = DATASET_TYPES[dataset_type]
        zip_path = cache_dir_path / f"{dataset_type}.zip"
        extract_path = cache_dir_path / dataset_type

        # Check if already extracted
        if extract_path.exists() and not force_download:
            if self._verify_extracted_files(extract_path, dataset_info):
                logger.info(f"Using cached dataset at {extract_path}")
                return extract_path
            else:
                logger.warning("Cached dataset appears incomplete, re-downloading...")
                shutil.rmtree(extract_path)

        # Check if zip exists and is valid
        if zip_path.exists() and not force_download:
            if self._verify_zip(zip_path, dataset_info["checksum"]):
                logger.info(f"Using cached zip file at {zip_path}")
                return self._extract_zip(zip_path, extract_path, dataset_info)
            else:
                logger.warning("Cached zip file is corrupted, re-downloading...")
                zip_path.unlink()

        # Download from S3
        logger.info(f"Downloading {dataset_type} dataset...")
        start_time = time.time()

        try:
            self._download_from_s3(
                dataset_info["key"], zip_path, dataset_info["size_mb"]
            )

            # Verify download
            if not self._verify_zip(zip_path, dataset_info["checksum"]):
                zip_path.unlink()
                raise ValueError("Downloaded file is corrupted")

            # Record download
            self._download_history[dataset_type] = {
                "timestamp": datetime.now(),
                "duration": time.time() - start_time,
                "size": zip_path.stat().st_size,
            }

            # Extract
            return self._extract_zip(zip_path, extract_path, dataset_info)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            if zip_path.exists():
                zip_path.unlink()
            raise

    def _download_from_s3(self, s3_key: str, local_path: Path, size_mb: float) -> None:
        """Download file from S3 with progress bar and retry logic."""
        s3 = self._get_s3_client()

        for attempt in range(MAX_RETRIES):
            try:
                # Get object size
                response = s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
                total_size = response["ContentLength"]

                # Download with progress
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Downloading {local_path.name}",
                ) as pbar:

                    def callback(bytes_amount: int) -> None:
                        pbar.update(bytes_amount)

                    s3.download_file(
                        S3_BUCKET,
                        s3_key,
                        str(local_path),
                        Callback=callback,
                        Config=TransferConfig(
                            multipart_threshold=1024 * 25,  # 25MB
                            max_concurrency=10,
                            multipart_chunksize=1024 * 25,
                            use_threads=True,
                        ),
                    )

                logger.info(f"Download complete: {format_bytes(total_size)}")
                break

            except ClientError as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                logger.warning(
                    f"Download failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}"
                )
                time.sleep(RETRY_DELAY * (attempt + 1))

    def _verify_zip(self, zip_path: Path, expected_checksum: str) -> bool:
        """Verify zip file integrity."""
        try:
            # Check if it's a valid zip
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                corrupt = zip_ref.testzip()
                if corrupt:
                    logger.error(f"Corrupt file in zip: {corrupt}")
                    return False

            # Verify checksum
            actual_checksum = verify_checksum(zip_path)
            return actual_checksum == expected_checksum

        except Exception as e:
            logger.error(f"Zip verification failed: {e}")
            return False

    def _extract_zip(
        self, zip_path: Path, extract_path: Path, dataset_info: Dict[str, Any]
    ) -> Path:
        """Extract zip file with progress."""
        logger.info(f"Extracting {zip_path.name}...")

        # Remove existing extraction
        if extract_path.exists():
            shutil.rmtree(extract_path)

        extract_path.mkdir(parents=True, exist_ok=True)

        # Extract with progress
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            members = zip_ref.namelist()

            with tqdm(total=len(members), desc="Extracting files") as pbar:
                for member in members:
                    zip_ref.extract(member, extract_path)
                    pbar.update(1)

        # Verify extraction
        if not self._verify_extracted_files(extract_path, dataset_info):
            shutil.rmtree(extract_path)
            raise ValueError("Extraction verification failed")

        logger.info(f"Dataset extracted to {extract_path}")
        return extract_path

    def _verify_extracted_files(
        self, extract_path: Path, dataset_info: Dict[str, Any]
    ) -> bool:
        """Verify that expected files exist after extraction."""
        expected_files = dataset_info.get("files", [])

        # Special handling for complete dataset
        if dataset_info.get("key", "").startswith("complete/"):
            return self._verify_complete_dataset(extract_path)

        # Regular validation for individual datasets
        for file_name in expected_files:
            if file_name == "All files from individual datasets":
                continue  # Skip placeholder for complete dataset

            file_path = extract_path / file_name
            if not file_path.exists():
                logger.error(f"Missing expected file: {file_name}")
                return False

        return True

    def _verify_complete_dataset(self, extract_path: Path) -> bool:
        """Verify complete dataset contains files from all individual datasets."""
        from .datasets import DATASET_TYPES

        # Get all expected files from individual datasets
        all_expected_files = []
        for dataset_type, dataset_info in DATASET_TYPES.items():
            if dataset_type != "complete":
                all_expected_files.extend(dataset_info["files"])

        # Check that all files exist
        missing_files = []
        for file_name in all_expected_files:
            file_path = extract_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        if missing_files:
            logger.error(
                f"Complete dataset missing {len(missing_files)} files: {missing_files[:5]}..."
            )
            if len(missing_files) <= 10:
                logger.error(f"Missing files: {missing_files}")
            return False

        logger.info(
            f"Complete dataset validation passed: {len(all_expected_files)} files found"
        )
        return True

    def get_info(self, dataset_type: str) -> Dict[str, Any]:
        """Get information about a dataset."""
        if dataset_type not in DATASET_TYPES:
            raise ValueError(f"Unknown dataset type: {dataset_type}")

        info = DATASET_TYPES[dataset_type].copy()

        # Check if cached
        extract_path = self.cache_dir / dataset_type
        zip_path = self.cache_dir / f"{dataset_type}.zip"

        info["cached"] = extract_path.exists()
        info["cached_zip"] = zip_path.exists()
        info["cache_path"] = str(extract_path) if info["cached"] else None

        if info["cached"]:
            info["cache_size"] = format_bytes(get_directory_size(extract_path))

        # Add download history if available
        if dataset_type in self._download_history:
            info["last_download"] = self._download_history[dataset_type]

        return info

    def clear_cache(self, dataset_type: Optional[str] = None) -> None:
        """Clear cached data."""
        if dataset_type:
            # Clear specific dataset
            if dataset_type not in DATASET_TYPES:
                raise ValueError(f"Unknown dataset type: {dataset_type}")

            paths = [
                self.cache_dir / f"{dataset_type}.zip",
                self.cache_dir / dataset_type,
            ]

            cleared_size = 0
            for path in paths:
                if path.exists():
                    if path.is_file():
                        cleared_size += path.stat().st_size
                        path.unlink()
                    else:
                        cleared_size += get_directory_size(path)
                        shutil.rmtree(path)

            logger.info(
                f"Cleared cache for {dataset_type} ({format_bytes(cleared_size)})"
            )
        else:
            # Clear all cache
            cleared_size = get_directory_size(self.cache_dir)
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cleared all cache ({format_bytes(cleared_size)})")

    def get_cache_size(self) -> Dict[str, Any]:
        """Get total size of cached datasets."""
        total_size = 0
        dataset_sizes = {}

        for dataset_type in DATASET_TYPES:
            extract_path = self.cache_dir / dataset_type
            zip_path = self.cache_dir / f"{dataset_type}.zip"

            dataset_size = 0
            if extract_path.exists():
                dataset_size += get_directory_size(extract_path)
            if zip_path.exists():
                dataset_size += zip_path.stat().st_size

            if dataset_size > 0:
                dataset_sizes[dataset_type] = dataset_size
                total_size += dataset_size

        return {
            "total": format_bytes(total_size),
            "total_bytes": total_size,
            "datasets": {k: format_bytes(v) for k, v in dataset_sizes.items()},
        }

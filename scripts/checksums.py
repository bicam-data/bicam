#!/usr/bin/env python3
"""Professional CLI tool for BICAM dataset checksums."""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

# Import project dataset definitions
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from bicam._auth import get_bucket_name, get_s3_client
    from bicam.datasets import DATASET_TYPES
except ImportError:
    DATASET_TYPES = {}
    get_s3_client = None
    get_bucket_name = None


def get_bucket() -> str:
    """Get the S3 bucket name for BICAM data."""
    if get_bucket_name is not None:
        return get_bucket_name()
    return "bicam-datasets"  # fallback


def calculate_s3_file_checksum(bucket: str, key: str, algorithm: str = "sha256") -> str:
    if get_s3_client is None:
        raise Exception("BICAM authentication not available")

    s3 = get_s3_client()
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        hash_func = getattr(hashlib, algorithm)()
        with open(tmp_file.name, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        os.unlink(tmp_file.name)
        return f"{algorithm}:{hash_func.hexdigest()}"


def get_s3_file_size(bucket: str, key: str) -> int:
    if get_s3_client is None:
        raise Exception("BICAM authentication not available")

    s3 = get_s3_client()
    response = s3.head_object(Bucket=bucket, Key=key)
    return response["ContentLength"]


def get_all_s3_checksums() -> Dict[str, Dict[str, Any]]:
    results = {}
    bucket = get_bucket()
    for dataset, info in DATASET_TYPES.items():
        key = info["key"]
        try:
            # Use BICAM authentication
            s3 = get_s3_client()
            s3.head_object(Bucket=bucket, Key=key)
            checksum = calculate_s3_file_checksum(bucket, key)
            size_bytes = get_s3_file_size(bucket, key)
            size_mb = size_bytes / (1024 * 1024)
            results[dataset] = {
                "key": key,
                "checksum": checksum,
                "size_bytes": size_bytes,
                "size_mb": size_mb,
            }
        except Exception as e:
            # Check if it's a credentials error and provide a more helpful message
            error_msg = str(e)
            if "Unable to locate credentials" in error_msg:
                error_msg = "Unable to locate credentials - check BICAM_SECRET_KEY and BICAM_CREDENTIAL_ENDPOINT"
            elif "BICAM authentication not available" in error_msg:
                error_msg = "BICAM authentication not available - check imports"
            results[dataset] = {"error": error_msg}
    return results


def print_checksums():
    results = get_all_s3_checksums()
    for dataset, info in results.items():
        if "error" in info:
            print(f"{dataset}: ERROR - {info['error']}")
        else:
            print(f"{dataset}: {info['checksum']} ({info['size_mb']:.1f} MB)")


def verify_checksums():
    results = get_all_s3_checksums()
    failed = False
    for dataset, info in results.items():
        if "error" in info:
            print(f"[FAIL] {dataset}: {info['error']}")
            failed = True
            continue
        expected = DATASET_TYPES[dataset]["checksum"]
        if info["checksum"] != expected:
            print(f"[FAIL] {dataset}: S3={info['checksum']} != datasets.py={expected}")
            failed = True
        else:
            print(f"[OK]   {dataset}: {info['checksum']}")
    if failed:
        sys.exit(1)
    print("All dataset checksums match.")


def print_update():
    results = get_all_s3_checksums()
    print("\nUpdated DATASET_TYPES for bicam/datasets.py:")
    print("-" * 60)
    for dataset, info in results.items():
        if "error" in info:
            print(f"# {dataset}: {info['error']}")
            continue
        print(f'    "{dataset}": {{')
        print(f'        "key": "{info["key"]}",')
        print(f'        "size_mb": {info["size_mb"]:.0f},')
        print(f'        "description": "Complete {dataset} data",')
        print(f'        "checksum": "{info["checksum"]}",')
        print(f'        "extracted_size_mb": {info["size_mb"] * 2:.0f},  # Estimate')
        print('        "files": ["..."],  # Update with actual files')
        print('        "format": "CSV and JSON files",')
        print('        "congress_range": "...",  # Update with actual range')
        print("    },")


def main():
    parser = argparse.ArgumentParser(description="BICAM dataset checksum utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("print", help="Print S3 checksums for all datasets")
    subparsers.add_parser("verify", help="Verify S3 checksums match bicam/datasets.py")
    subparsers.add_parser(
        "update", help="Print updated DATASET_TYPES for bicam/datasets.py"
    )

    args = parser.parse_args()
    if args.command == "print":
        print_checksums()
    elif args.command == "verify":
        verify_checksums()
    elif args.command == "update":
        print_update()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Professional CLI tool for BICAM dataset checksums."""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

import boto3

# Import project dataset definitions
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from bicam.datasets import DATASET_TYPES
except ImportError:
    DATASET_TYPES = {}

BUCKET = "bicam-datasets"


def calculate_s3_file_checksum(bucket: str, key: str, algorithm: str = "sha256") -> str:
    s3 = boto3.client("s3")
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        hash_func = getattr(hashlib, algorithm)()
        with open(tmp_file.name, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        os.unlink(tmp_file.name)
        return f"{algorithm}:{hash_func.hexdigest()}"


def get_s3_file_size(bucket: str, key: str) -> int:
    s3 = boto3.client("s3")
    response = s3.head_object(Bucket=bucket, Key=key)
    return response["ContentLength"]


def get_all_s3_checksums() -> Dict[str, Dict[str, Any]]:
    results = {}
    for dataset, info in DATASET_TYPES.items():
        key = info["key"]
        try:
            s3 = boto3.client("s3")
            s3.head_object(Bucket=BUCKET, Key=key)
            checksum = calculate_s3_file_checksum(BUCKET, key)
            size_bytes = get_s3_file_size(BUCKET, key)
            size_mb = size_bytes / (1024 * 1024)
            results[dataset] = {
                "key": key,
                "checksum": checksum,
                "size_bytes": size_bytes,
                "size_mb": size_mb,
            }
        except Exception as e:
            results[dataset] = {"error": str(e)}
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

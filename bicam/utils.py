"""Utility functions for BICAM."""

import hashlib
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Tuple


def format_bytes(size: float) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def verify_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """Calculate file checksum."""
    hash_func = getattr(hashlib, algorithm)()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return f"{algorithm}:{hash_func.hexdigest()}"


def get_directory_size(directory: Path) -> int:
    """Get total size of a directory in bytes."""
    total_size = 0

    for dirpath, _dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.islink(filepath):
                total_size += os.path.getsize(filepath)

    return total_size


def estimate_download_time(size_mb: float, speed_mbps: float = 10) -> str:
    """Estimate download time and return human-readable string."""
    seconds: float = (size_mb * 8) / speed_mbps

    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hours {minutes} minutes"


def parse_s3_url(url: str) -> Tuple[str, str]:
    """Parse S3 URL into bucket and key."""
    if url.startswith("s3://"):
        url = url[5:]
    parts = url.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid S3 URL: {url}")
    return parts[0], parts[1]


def safe_filename(filename: str) -> str:
    """Make filename safe for filesystem."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")
    return filename


def retry_with_backoff(
    func: Callable[[], Any], max_retries: int = 3, initial_delay: float = 1.0
) -> Any:
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception:
            if attempt == max_retries - 1:
                raise
            delay = initial_delay * (2**attempt)
            time.sleep(delay)


def check_disk_space(path: Path, required_mb: float) -> bool:
    """Check if there's enough disk space."""
    stat = os.statvfs(path)
    available_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
    return available_mb >= required_mb


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display."""
    now = datetime.now()
    diff = now - timestamp

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minutes ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hours ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} days ago"
    else:
        return timestamp.strftime("%Y-%m-%d")

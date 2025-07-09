"""Tests for utility functions."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from bicam.utils import (
    check_disk_space,
    estimate_download_time,
    format_bytes,
    format_timestamp,
    get_directory_size,
    parse_s3_url,
    retry_with_backoff,
    safe_filename,
    verify_checksum,
)


class TestUtils:
    """Test utility functions."""

    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        assert format_bytes(1536) == "1.5 KB"

    def test_verify_checksum(self):
        """Test checksum verification."""
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"test content")
            tmp.flush()

            checksum = verify_checksum(Path(tmp.name))
            assert checksum.startswith("sha256:")
            assert len(checksum) == 71  # "sha256:" + 64 hex chars

    def test_get_directory_size(self):
        """Test directory size calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test files
            (tmpdir / "file1.txt").write_bytes(b"0" * 1000)
            (tmpdir / "file2.txt").write_bytes(b"0" * 2000)

            subdir = tmpdir / "subdir"
            subdir.mkdir()
            (subdir / "file3.txt").write_bytes(b"0" * 3000)

            assert get_directory_size(tmpdir) == 6000

    def test_estimate_download_time(self):
        """Test download time estimation."""
        assert estimate_download_time(1, 10) == "0 seconds"
        assert estimate_download_time(10, 1) == "1 minutes"
        assert estimate_download_time(1000, 1) == "2 hours 13 minutes"

    def test_parse_s3_url(self):
        """Test S3 URL parsing."""
        bucket, key = parse_s3_url("s3://my-bucket/path/to/file.zip")
        assert bucket == "my-bucket"
        assert key == "path/to/file.zip"

        bucket, key = parse_s3_url("my-bucket/path/to/file.zip")
        assert bucket == "my-bucket"
        assert key == "path/to/file.zip"

        with pytest.raises(ValueError, match="Invalid S3 URL"):
            parse_s3_url("invalid-url")

    def test_safe_filename(self):
        """Test filename sanitization."""
        assert safe_filename("normal_file.txt") == "normal_file.txt"
        assert safe_filename("file:with:colons.txt") == "file_with_colons.txt"
        assert safe_filename("file<>with|pipes.txt") == "file__with_pipes.txt"

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        now = datetime.now()

        assert format_timestamp(now) == "just now"
        assert format_timestamp(now - timedelta(minutes=30)) == "30 minutes ago"
        assert format_timestamp(now - timedelta(hours=2)) == "2 hours ago"
        assert format_timestamp(now - timedelta(days=3)) == "3 days ago"

        old_date = now - timedelta(days=30)
        assert format_timestamp(old_date) == old_date.strftime("%Y-%m-%d")

    def test_format_bytes_edge_cases(self):
        """Test format_bytes with edge cases."""
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(1024**5) == "1.0 PB"
        assert format_bytes(-1024) == "-1024.0 B"  # Negative numbers stay as bytes

    def test_verify_checksum_with_different_algorithms(self):
        """Test verify_checksum with different hash algorithms."""
        test_file = Path("test_hash.txt")
        test_file.write_text("test content")

        try:
            sha256_hash = verify_checksum(test_file, "sha256")
            assert sha256_hash.startswith("sha256:")

            md5_hash = verify_checksum(test_file, "md5")
            assert md5_hash.startswith("md5:")

            sha1_hash = verify_checksum(test_file, "sha1")
            assert sha1_hash.startswith("sha1:")
        finally:
            test_file.unlink()

    def test_verify_checksum_with_invalid_algorithm(self):
        """Test verify_checksum with invalid hash algorithm."""
        test_file = Path("test_invalid_hash.txt")
        test_file.write_text("test content")

        try:
            with pytest.raises(AttributeError):
                verify_checksum(test_file, "invalid_algorithm")
        finally:
            test_file.unlink()

    def test_get_directory_size_with_symlinks(self, temp_cache_dir):
        """Test get_directory_size with symbolic links."""
        test_file = temp_cache_dir / "test.txt"
        test_file.write_text("test content")

        symlink_file = temp_cache_dir / "symlink.txt"
        symlink_file.symlink_to(test_file)

        subdir = temp_cache_dir / "subdir"
        subdir.mkdir()
        subdir_file = subdir / "subfile.txt"
        subdir_file.write_text("subdir content")

        size = get_directory_size(temp_cache_dir)
        expected_size = len("test content") + len("subdir content")
        assert size == expected_size

    def test_get_directory_size_with_permission_error(self, temp_cache_dir):
        """Test get_directory_size with permission errors."""
        test_file = temp_cache_dir / "test.txt"
        test_file.write_text("test content")

        with patch("os.walk") as mock_walk:
            mock_walk.side_effect = PermissionError("Permission denied")

            with pytest.raises(PermissionError):
                get_directory_size(temp_cache_dir)

    def test_retry_with_backoff_success_after_retries(self):
        """Test retry_with_backoff that succeeds after some failures."""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        with patch("time.sleep"):  # Speed up test
            result = retry_with_backoff(
                failing_function, max_retries=3, initial_delay=0.1
            )

        assert result == "success"
        assert call_count == 3

    def test_retry_with_backoff_max_retries_exceeded(self):
        """Test retry_with_backoff that fails after max retries."""

        def always_failing_function():
            raise ValueError("Always fails")

        with patch("time.sleep"), pytest.raises(ValueError, match="Always fails"):
            retry_with_backoff(
                always_failing_function, max_retries=2, initial_delay=0.1
            )

    def test_check_disk_space_with_insufficient_space(self, temp_cache_dir):
        """Test check_disk_space with insufficient space."""
        with patch("os.statvfs") as mock_statvfs:
            mock_statvfs.return_value.f_bavail = 100  # Very low available blocks
            mock_statvfs.return_value.f_frsize = 1024  # 1KB per block

            # Check for 1MB when only ~100KB available
            assert not check_disk_space(temp_cache_dir, required_mb=1)

    def test_check_disk_space_with_statvfs_error(self, temp_cache_dir):
        """Test check_disk_space with statvfs error."""
        with patch("os.statvfs") as mock_statvfs:
            mock_statvfs.side_effect = OSError("statvfs failed")

            with pytest.raises(OSError, match="statvfs failed"):
                check_disk_space(temp_cache_dir, required_mb=1)

    def test_safe_filename_with_various_characters(self):
        """Test safe_filename with various unsafe characters."""
        assert safe_filename("file<name>.txt") == "file_name_.txt"
        assert safe_filename("file:name|.txt") == "file_name_.txt"
        assert safe_filename("file?name*.txt") == "file_name_.txt"
        assert (
            safe_filename('file"name\\.txt') == "file_name\\.txt"
        )  # Backslash is not in unsafe_chars

        assert safe_filename("normal_file.txt") == "normal_file.txt"
        assert safe_filename("file-name.txt") == "file-name.txt"
        assert safe_filename("file_name.txt") == "file_name.txt"

    def test_parse_s3_url_with_various_formats(self):
        """Test parse_s3_url with various URL formats."""
        bucket, key = parse_s3_url("s3://my-bucket/path/to/file.txt")
        assert bucket == "my-bucket"
        assert key == "path/to/file.txt"

        bucket, key = parse_s3_url("my-bucket/path/to/file.txt")
        assert bucket == "my-bucket"
        assert key == "path/to/file.txt"

        bucket, key = parse_s3_url("s3://my-bucket/folder/subfolder/file.txt")
        assert bucket == "my-bucket"
        assert key == "folder/subfolder/file.txt"

    def test_parse_s3_url_with_invalid_format(self):
        """Test parse_s3_url with invalid URL format."""
        with pytest.raises(ValueError, match="Invalid S3 URL"):
            parse_s3_url("invalid-url")

        with pytest.raises(ValueError, match="Invalid S3 URL"):
            parse_s3_url("s3://bucket-only")

    def test_format_timestamp_with_future_date(self):
        """Test format_timestamp with future date."""
        future_time = datetime.now() + timedelta(days=1)
        result = format_timestamp(future_time)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_timestamp_with_very_old_date(self):
        """Test format_timestamp with very old date."""
        old_time = datetime.now() - timedelta(days=365)
        result = format_timestamp(old_time)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_estimate_download_time_with_zero_speed(self):
        """Test estimate_download_time with zero speed."""
        with pytest.raises(ZeroDivisionError):
            estimate_download_time(100, speed_mbps=0)

    def test_estimate_download_time_with_very_slow_speed(self):
        """Test estimate_download_time with very slow speed."""
        result = estimate_download_time(100, speed_mbps=0.001)
        assert "hours" in result or "minutes" in result

    def test_estimate_download_time_with_very_fast_speed(self):
        """Test estimate_download_time with very fast speed."""
        result = estimate_download_time(100, speed_mbps=1000)
        assert "seconds" in result

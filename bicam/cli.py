"""Command-line interface for BICAM."""

import logging
import sys
from pathlib import Path
from typing import Any, Optional

import click

from . import (
    __version__,
    clear_cache,
    download_dataset,
    get_cache_size,
    get_dataset_info,
    list_datasets,
)
from .config import CHECK_VERSION, VERSION_URL
from .utils import check_disk_space, estimate_download_time, format_bytes

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def check_for_updates() -> None:
    """Check if a newer version is available."""
    if not CHECK_VERSION:
        return

    try:
        import requests

        response = requests.get(VERSION_URL, timeout=2)
        if response.status_code == 200:
            latest = response.json()["tag_name"].lstrip("v")
            if latest > __version__:
                click.echo(
                    f"\nWARNING: New version available: {latest} "
                    f"(current: {__version__})\n"
                    f"   Update with: uv pip install --upgrade bicam\n",
                    err=True,
                )
    except Exception:
        pass  # Silently ignore version check failures


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """BICAM - Comprehensive Congressional Data Downloader"""
    check_for_updates()


@main.command()
@click.argument("dataset_type")
@click.option("--force", "-f", is_flag=True, help="Force re-download")
@click.option("--cache-dir", type=click.Path(), help="Custom cache directory")
@click.option("--no-extract", is_flag=True, help="Download only, do not extract")
@click.option(
    "--confirm", is_flag=True, help="Skip confirmation for large datasets (>1GB)"
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress log outputs")
def download(
    dataset_type: str,
    force: bool,
    cache_dir: Optional[str],
    no_extract: bool,
    confirm: bool,
    quiet: bool,
) -> None:
    """Download a BICAM dataset."""
    try:
        # Set up quiet mode
        if quiet:
            logging.getLogger().setLevel(logging.ERROR)
            # Disable tqdm progress bars
            import os

            os.environ["TQDM_DISABLE"] = "1"

        # Validate dataset type
        if dataset_type not in list_datasets():
            click.echo(f"Error: Unknown dataset '{dataset_type}'", err=True)
            click.echo(f"Available datasets: {', '.join(list_datasets())}")
            raise click.Abort()

        # Get dataset info
        info = get_dataset_info(dataset_type)

        # Check for large dataset confirmation
        size_gb = info["size_mb"] / 1024
        if size_gb > 1 and not confirm and not quiet:
            click.echo(
                f"WARNING: This dataset is {size_gb:.1f}GB. This may take a while."
            )
            if not click.confirm("Continue with download?"):
                click.echo("Download cancelled.")
                return

        # Check disk space
        required_mb = info["extracted_size_mb"] + info["size_mb"]
        from .config import DEFAULT_CACHE_DIR

        cache_path = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR

        if not check_disk_space(cache_path, required_mb):
            click.echo(
                f"WARNING: May not have enough disk space. "
                f"Need ~{format_bytes(required_mb * 1024 * 1024)}",
                err=True,
            )

        # Show download info (unless quiet)
        if not quiet:
            click.echo(f"Dataset: {dataset_type}")
            click.echo(f"Description: {info['description']}")
            click.echo(f"Download size: {format_bytes(info['size_mb'] * 1024 * 1024)}")
            click.echo(
                f"Extracted size: {format_bytes(info['extracted_size_mb'] * 1024 * 1024)}"
            )
            click.echo(f"Estimated time: {estimate_download_time(info['size_mb'])}")
            click.echo()

        # Download
        path = download_dataset(
            dataset_type,
            force_download=force,
            cache_dir=cache_dir,
            confirm=confirm,
            quiet=quiet,
        )

        if not quiet:
            click.echo(f"\n✓ Dataset downloaded to: {path}")

    except KeyboardInterrupt:
        click.echo("\nINTERRUPTED: Download cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed information")
@click.option("--quiet", "-q", is_flag=True, help="Suppress log outputs")
def list_datasets_cmd(detailed: bool, quiet: bool) -> None:
    """List available datasets."""
    # Set up quiet mode
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)

    datasets = list_datasets()
    cache_info = get_cache_size()

    if not quiet:
        click.echo("Available BICAM datasets:")
        click.echo()

    if detailed:
        # Detailed view
        for name in datasets:
            info = get_dataset_info(name)
            if not quiet:
                click.echo(f"{click.style(name, bold=True)}")
                click.echo(f"   {info['description']}")
                click.echo(
                    f"   Size: {format_bytes(info['size_mb'] * 1024 * 1024)} "
                    f"(extracts to {format_bytes(info['extracted_size_mb'] * 1024 * 1024)})"
                )
                click.echo(f"   Format: {info['format']}")
                click.echo(f"   Congress range: {info['congress_range']}")

                if info["cached"]:
                    click.echo(f"   Status: ✓ Cached at {info['cache_path']}")
                else:
                    click.echo("   Status: Not downloaded")
                click.echo()
    else:
        # Simple view
        for name in datasets:
            info = get_dataset_info(name)
            cached = "✓" if info["cached"] else " "
            size = format_bytes(info["size_mb"] * 1024 * 1024)
            if not quiet:
                click.echo(f"  [{cached}] {name:20} {size:>10} - {info['description']}")

    if not quiet:
        click.echo()
        click.echo(f"Total cache size: {cache_info['total']}")
        click.echo()
        click.echo("Use 'bicam download <dataset>' to download a dataset")
        click.echo("Use 'bicam list-datasets --detailed' for more information")


@main.command()
@click.argument("dataset_type", required=False)
@click.option("--all", is_flag=True, help="Clear all cached data.")
@click.option("--yes", is_flag=True, help="Confirm cache clear without prompt.")
@click.option("--quiet", "-q", is_flag=True, help="Suppress log outputs")
def clear(
    dataset_type: Optional[str] = None,
    all: bool = False,  # noqa: A002
    yes: bool = False,
    quiet: bool = False,
    **kwargs: Any,
) -> None:  # noqa: A002
    """Clear cached data for a dataset or all datasets."""
    # Set up quiet mode
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)

    if all:
        cache_info = get_cache_size()
        if not yes:
            click.confirm(
                f"Clear all cached data ({cache_info['total']})? This cannot be undone.",
                abort=True,
            )
        clear_cache()
        if not quiet:
            click.echo("✓ Cleared all cached data")
    elif dataset_type:
        info = get_dataset_info(dataset_type)
        if not info["cached"]:
            if not quiet:
                click.echo(f"Dataset '{dataset_type}' is not cached")
            return

        if not yes:
            click.confirm(
                f"Clear cache for {dataset_type}? This cannot be undone.", abort=True
            )
        clear_cache(dataset_type)
        if not quiet:
            click.echo(f"✓ Cleared cache for {dataset_type}")
    else:
        if not quiet:
            click.echo("Specify a dataset type or use --all")
            click.echo("Example: bicam clear bills")
            click.echo("         bicam clear --all")


@main.command()
@click.argument("dataset_type")
@click.option("--quiet", "-q", is_flag=True, help="Suppress log outputs")
def info(dataset_type: str, quiet: bool) -> None:
    """Show detailed information about a dataset."""
    # Set up quiet mode
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)

    try:
        info = get_dataset_info(dataset_type)

        if not quiet:
            click.echo(f"\nDataset: {click.style(dataset_type, bold=True)}")
            click.echo("=" * 50)
            click.echo(f"Description: {info['description']}")
            click.echo(f"Format: {info['format']}")
            click.echo(f"Congress range: {info['congress_range']}")
            click.echo(
                f"Compressed size: {format_bytes(info['size_mb'] * 1024 * 1024)}"
            )
            click.echo(
                f"Extracted size: {format_bytes(info['extracted_size_mb'] * 1024 * 1024)}"
            )
            click.echo(
                f"Estimated download time: {estimate_download_time(info['size_mb'])}"
            )

            click.echo("\nIncluded files:")
            for file in info["files"]:
                click.echo(f"  - {file}")

            click.echo("\nCache status:")
            if info["cached"]:
                click.echo("  ✓ Downloaded and extracted")
                click.echo(f"  Location: {info['cache_path']}")
                if "cache_size" in info:
                    click.echo(f"  Size on disk: {info['cache_size']}")
            else:
                click.echo("  ✗ Not downloaded")

            if info["cached_zip"]:
                click.echo("Zip file is cached")

            if "last_download" in info:
                last = info["last_download"]
                click.echo("\nLast download:")
                click.echo(f"  Time: {last['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                click.echo(f"  Duration: {last['duration']:.1f} seconds")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo(f"Available datasets: {', '.join(list_datasets())}")
        raise click.Abort() from e


@main.command()
@click.option("--quiet", "-q", is_flag=True, help="Suppress log outputs")
def cache(quiet: bool) -> None:
    """Show cache information and statistics."""
    # Set up quiet mode
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)

    cache_info = get_cache_size()

    if not quiet:
        click.echo("\nBICAM Cache Information")
        click.echo("=" * 50)
        click.echo(
            f"Total size: {cache_info['total']} ({cache_info['total_bytes']:,} bytes)"
        )

        if cache_info["datasets"]:
            click.echo("\nCached datasets:")
            for dataset, size in cache_info["datasets"].items():
                click.echo(f"  {dataset:20} {size:>10}")
        else:
            click.echo("\nNo datasets cached")

        from .config import DEFAULT_CACHE_DIR

        click.echo(f"\nCache location: {DEFAULT_CACHE_DIR}")
        click.echo("\nUse 'bicam clear <dataset>' to remove specific datasets")
        click.echo("Use 'bicam clear --all' to clear entire cache")


if __name__ == "__main__":
    main()

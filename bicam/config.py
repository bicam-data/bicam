"""Configuration for BICAM package."""

import logging
import os
import platform
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# Cache configuration - Windows compatible
def get_default_cache_dir() -> Path:
    """Get the default cache directory, ensuring Windows compatibility."""
    # Use environment variable if set
    env_data = os.environ.get("BICAM_DATA")
    if env_data:
        return Path(env_data)

    # Get home directory in a cross-platform way
    home_dir = Path.home()

    # On Windows, use AppData/Local for better compatibility
    if platform.system() == "Windows":
        cache_dir = home_dir / "AppData" / "Local" / "bicam"
    else:
        # Unix-like systems (macOS, Linux)
        cache_dir = home_dir / ".bicam"

    return cache_dir


DEFAULT_CACHE_DIR = get_default_cache_dir()
DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# S3 Configuration
S3_BUCKET = os.environ.get("BICAM_S3_BUCKET", "bicam-datasets")
S3_REGION = os.environ.get("BICAM_S3_REGION", "us-east-1")
S3_BASE_PATH = "data/v1"

# Download configuration
CHUNK_SIZE = 1024 * 1024  # 1MB chunks
MAX_RETRIES = 3
RETRY_DELAY = 1.0
TIMEOUT = 300  # 5 minutes

# Logging configuration
LOG_LEVEL = os.environ.get("BICAM_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Version check
CHECK_VERSION = os.environ.get("BICAM_CHECK_VERSION", "true").lower() == "true"
VERSION_URL = "https://api.github.com/repos/youruniversity/bicam/releases/latest"

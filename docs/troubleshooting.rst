Troubleshooting
==============

This page covers common issues and their solutions when using BICAM.

Installation Issues
------------------

**Permission Errors on Windows**

If you encounter permission errors when installing or running BICAM on Windows:

.. code-block:: bash

   # Run as administrator
   pip install bicam

   # Or use a different cache directory
   set BICAM_DATA=C:\Users\YourName\bicam_cache
   bicam download bills

**Python Version Issues**

BICAM requires Python 3.8 or higher:

.. code-block:: bash

   python --version

   # If using an older version, upgrade Python or use a virtual environment
   python3.11 -m pip install bicam
   python3.11 -m bicam list

**Missing Dependencies**

If you get import errors:

.. code-block:: bash

   # Reinstall with all dependencies
   pip install --upgrade bicam

   # Or install dependencies manually
   pip install boto3 requests tqdm click

Download Issues
--------------

**Network Connection Errors**

If downloads fail due to network issues:

.. code-block:: bash

   # Check your internet connection
   ping google.com

   # Try with verbose output
   bicam download bills --force

   # Check firewall settings
   # Ensure outbound HTTPS connections are allowed

**Insufficient Disk Space**

If you get disk space errors:

.. code-block:: bash

   # Check available disk space
   df -h  # Linux/macOS
   dir     # Windows

   # Clear existing cache
   bicam clear --all

   # Use a different cache directory with more space
   bicam download bills --cache-dir /path/with/more/space

**Download Interruptions**

If downloads are interrupted:

.. code-block:: bash

   # Resume download (BICAM will automatically retry)
   bicam download bills

   # Force re-download if corrupted
   bicam download bills --force

**Large Dataset Confirmation**

For datasets larger than 1GB, BICAM asks for confirmation:

.. code-block:: bash

   # Skip confirmation
   bicam download complete --confirm

   # Or use quiet mode
   bicam download complete --quiet

Authentication Issues
--------------------

**Credential Server Errors**

If you encounter authentication errors:

.. code-block:: bash

   # Check if you have the latest version
   pip install --upgrade bicam

   # Verify your internet connection
   curl https://api.github.com

   # Check if the credential server is accessible
   # (This is handled automatically by BICAM)

**Package Token Issues**

If there are package token validation errors:

.. code-block:: bash

   # Reinstall the package
   pip uninstall bicam
   pip install bicam

   # Check your package version
   bicam --version

Cache Issues
-----------

**Corrupted Cache**

If you suspect cache corruption:

.. code-block:: bash

   # Clear specific dataset
   bicam clear bills

   # Clear all cache
   bicam clear --all

   # Re-download
   bicam download bills

**Cache Location Issues**

If you can't find your cached data:

.. code-block:: bash

   # Check cache location
   bicam cache

   # Default locations:
   # Windows: %LOCALAPPDATA%\bicam
   # macOS/Linux: ~/.bicam

   # Use custom location
   export BICAM_DATA=/custom/path
   bicam download bills

**Cache Size Issues**

If cache is taking too much space:

.. code-block:: bash

   # Check cache size
   bicam cache

   # Clear unused datasets
   bicam clear bills
   bicam clear amendments

   # Clear all cache
   bicam clear --all

Performance Issues
-----------------

**Slow Downloads**

If downloads are slow:

.. code-block:: bash

   # Check your internet speed
   speedtest-cli

   # Use quiet mode to reduce overhead
   bicam download bills --quiet

   # Consider downloading during off-peak hours

**Memory Issues**

If you encounter memory errors:

.. code-block:: bash

   # Use smaller datasets first
   bicam download congresses
   bicam download members

   # Process data in chunks
   # Use pandas with chunking, or a different engine, for large files

**CPU Usage**

If BICAM uses too much CPU:

.. code-block:: bash

   # This is normal during extraction
   # Use quiet mode to reduce logging overhead
   bicam download bills --quiet

Platform-Specific Issues
-----------------------

**Windows Issues**

.. code-block:: bash

   # Path length issues
   # Use shorter cache paths
   set BICAM_DATA=C:\bicam

   # Permission issues
   # Run as administrator or use user directory
   set BICAM_DATA=%USERPROFILE%\bicam_cache

**macOS Issues**

.. code-block:: bash

   # Gatekeeper issues
   # Allow terminal access to files
   # Or use Homebrew Python
   brew install python
   python3 -m pip install bicam

**Linux Issues**

.. code-block:: bash

   # SELinux issues
   # Check SELinux status
   getenforce

   # If enforcing, allow file access
   setsebool -P httpd_can_network_connect 1

Command Line Issues
------------------

**Command Not Found**

If `bicam` command is not found:

.. code-block:: bash

   # Check if installed
   pip list | grep bicam

   # Reinstall
   pip install --upgrade bicam

   # Use Python module syntax
   python -m bicam list

**Permission Denied**

If you get permission errors:

.. code-block:: bash

   # Check file permissions
   ls -la ~/.bicam

   # Fix permissions
   chmod 755 ~/.bicam

   # Use custom cache directory
   export BICAM_DATA=/tmp/bicam_cache

**Invalid Dataset Names**

If you get "Unknown dataset" errors:

.. code-block:: bash

   # List available datasets
   bicam list

   # Check spelling
   bicam download bills  # not bill
   bicam download members  # not member

Python API Issues
----------------

**Import Errors**

If you can't import bicam:

.. code-block:: python

   # Check installation
   import sys
   print(sys.path)

   # Reinstall
   import subprocess
   subprocess.run(['pip', 'install', '--upgrade', 'bicam'])

**Function Errors**

If functions don't work as expected:

.. code-block:: python

   import bicam

   # Check available functions
   print(dir(bicam))

   # Use try-except for error handling
   try:
       bills_path = bicam.download_dataset('bills')
   except Exception as e:
       print(f"Error: {e}")

**Path Issues**

If you get path-related errors:

.. code-block:: python

   from pathlib import Path
   import bicam

   # Use Path objects
   cache_dir = Path('/custom/cache')
   bills_path = bicam.download_dataset('bills', cache_dir=str(cache_dir))

Getting Help
-----------

**Check Documentation**

.. code-block:: bash

   # View help
   bicam --help
   bicam download --help

   # Check version
   bicam --version

**Enable Debug Logging**

.. code-block:: bash

   # Set debug level
   export BICAM_LOG_LEVEL=DEBUG
   bicam download bills

**Report Issues**

If you encounter a bug:

1. Check this troubleshooting guide
2. Search existing issues on GitHub
3. Create a new issue with:
   * BICAM version (`bicam --version`)
   * Python version (`python --version`)
   * Operating system
   * Error message
   * Steps to reproduce
   -- OR --
   * Visit the feedback page at https://bicam.net/feedback
   * Select the issue type, data type, and provide a description

**Contact Support**

* **GitHub Issues**: https://github.com/bicam-data/bicam/issues
* **Email**: bicam.data@gmail.com

Common Error Messages
--------------------

**"Unknown dataset type"**
* Check available datasets with `bicam list`
* Verify spelling of dataset name

**"Insufficient disk space"**
* Check available space with `df -h` (Linux/macOS) or `dir` (Windows)
* Clear cache with `bicam clear --all`
* Use custom cache directory with `--cache-dir`

**"Network error"**
* Check internet connection
* Verify firewall settings
* Try again later

**"Permission denied"**
* Check file permissions
* Use custom cache directory
* Run as administrator (Windows)

**"Invalid checksum"**
* Clear cache and re-download
* Check for disk corruption
* Try with `--force` flag

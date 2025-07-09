Installation
===========

BICAM is available on PyPI and can be installed using pip.

Requirements
-----------

* Python 3.8 or higher
* 12GB+ free disk space (for the complete dataset)
* Internet connection for downloads

Basic Installation
-----------------

Install BICAM using pip:

.. code-block:: bash

   pip install bicam

For the latest development version:

.. code-block:: bash

   pip install git+https://github.com/bicam-data/bicam.git

Using uv (Recommended)
---------------------

If you use `uv <https://docs.astral.sh/uv/>`_ for Python package management:

.. code-block:: bash

   uv pip install bicam

Using conda
----------

BICAM is not yet available on conda-forge, but you can install it in a conda environment:

.. code-block:: bash

   conda create -n bicam python=3.11
   conda activate bicam
   pip install bicam

Verification
-----------

After installation, verify that BICAM is working:

.. code-block:: bash

   bicam --version
   bicam list

You should see the version number and a list of available datasets.

Configuration
------------

BICAM uses sensible defaults and requires no configuration. However, you can customize:

**Cache Directory**

By default, BICAM stores downloaded data in the following locations:

+-------------+-----------------------------------+
| Platform    | Default Cache Directory           |
+-------------+-----------------------------------+
| Windows     | %LOCALAPPDATA%\\bicam             |
+-------------+-----------------------------------+
| macOS/Linux | ~/.bicam                          |
+-------------+-----------------------------------+

To use a custom cache directory:

.. code-block:: bash

   export BICAM_DATA=/path/to/custom/cache
   bicam download bills

**Environment Variables**

+-------------------+---------------------------------------------------+
| Variable          | Description                                       |
+===================+===================================================+
| BICAM_DATA        | Custom cache directory                            |
+-------------------+---------------------------------------------------+
| BICAM_LOG_LEVEL   | Logging level (DEBUG, INFO, WARNING, ERROR)       |
+-------------------+---------------------------------------------------+

Troubleshooting
--------------

**Permission Errors**
If you encounter permission errors on Windows, try running as administrator or use a different cache directory.

**Disk Space**
Ensure you have sufficient disk space. The complete dataset requires ~12GB, and requires intermediate storage when downloading the data.

**Network Issues**
BICAM requires internet access to download datasets. Check your firewall settings if downloads fail.

**Python Version**
BICAM requires Python 3.8+. Check your version with:

.. code-block:: bash

   python --version

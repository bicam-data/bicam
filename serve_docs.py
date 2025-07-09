#!/usr/bin/env python3
"""
Convenience script to serve BICAM documentation locally.
This script runs the documentation server from the project root.
"""

import subprocess
import sys
from pathlib import Path


def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    docs_dir = project_root / "docs"

    # Check if docs directory exists
    if not docs_dir.exists():
        print("Error: docs directory not found!")
        sys.exit(1)

    # Check if the docs server script exists
    docs_server = docs_dir / "serve_docs.py"
    if not docs_server.exists():
        print("Error: docs/serve_docs.py not found!")
        print("Please ensure the documentation is properly set up.")
        sys.exit(1)

    # Change to docs directory and run the server
    try:
        subprocess.run([sys.executable, str(docs_server)], cwd=docs_dir)
    except KeyboardInterrupt:
        print("\nDocumentation server stopped.")
    except Exception as e:
        print(f"Error starting documentation server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

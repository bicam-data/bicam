#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run([sys.executable, "scripts/checksums.py", "verify"])
sys.exit(result.returncode)

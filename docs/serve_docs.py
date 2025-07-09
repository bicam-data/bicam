#!/usr/bin/env python3
"""
Simple HTTP server to serve BICAM documentation locally.
Run this script and open http://localhost:8000 in your browser.
"""

import http.server
import os
import socketserver
import sys
from pathlib import Path


def main():
    # Change to the docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)

    # Check if _build/html exists
    html_dir = docs_dir / "_build" / "html"
    if not html_dir.exists():
        print("Error: Documentation not built yet!")
        print("Please run 'make html' first to build the documentation.")
        sys.exit(1)

    # Change to the html directory
    os.chdir(html_dir)

    # Set up the server
    PORT = 8000

    # Try to find an available port
    for port in range(8000, 8010):
        try:
            with socketserver.TCPServer(
                ("", port), http.server.SimpleHTTPRequestHandler
            ) as httpd:
                print("BICAM Documentation Server")
                print("========================")
                print(f"Server running at: http://localhost:{port}")
                print(f"Serving from: {html_dir}")
                print("Press Ctrl+C to stop the server")
                print()

                # Open browser automatically (optional)
                try:
                    import webbrowser

                    webbrowser.open(f"http://localhost:{port}")
                    print("Browser opened automatically!")
                except:
                    print("Please open your browser and navigate to the URL above.")

                httpd.serve_forever()
        except OSError:
            continue

    print("Error: Could not find an available port between 8000-8009")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

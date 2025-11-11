#!/usr/bin/env python3
"""
Build script to fetch and extract MCP Inspector static assets.

This script:
1. Uses npm to install @modelcontextprotocol/inspector at a pinned version
2. Extracts the built static files (HTML, JS, CSS) from the package
3. Copies them to fastapi_mcp_inspector/static_ui/

This ensures we ship the inspector assets with our PyPI package without
inlining them in the repository.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Pin the inspector version
INSPECTOR_VERSION = "0.17.2"
INSPECTOR_PACKAGE = f"@modelcontextprotocol/inspector@{INSPECTOR_VERSION}"

def run_command(cmd, cwd=None):
    """Run a shell command and return its output."""
    # On Windows, npm is npm.cmd, so we need to adjust the command
    if sys.platform == "win32":
        if cmd[0] == "npm":
            cmd = ["npm.cmd"] + cmd[1:]
        elif cmd[0] == "node":
            cmd = ["node.exe"] + cmd[1:]

    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"STDOUT: {result.stdout}", file=sys.stderr)
        print(f"STDERR: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return result.stdout.strip()


def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    static_ui_dir = project_root / "fastapi_mcp_inspector" / "static_ui"

    print(f"Project root: {project_root}")
    print(f"Target static UI directory: {static_ui_dir}")

    # Create a temporary directory for npm operations
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        print(f"\nWorking in temporary directory: {tmpdir_path}")

        # Initialize a minimal package.json
        print("\nInitializing npm package...")
        package_json = {
            "name": "build-mcp-inspector",
            "version": "1.0.0",
            "private": True
        }

        package_json_path = tmpdir_path / "package.json"
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)

        # Install the inspector package
        print(f"\nInstalling {INSPECTOR_PACKAGE}...")
        run_command(
            ["npm", "install", "--no-save", INSPECTOR_PACKAGE],
            cwd=tmpdir_path
        )

        # Find the inspector package directory
        inspector_dir = tmpdir_path / "node_modules" / "@modelcontextprotocol" / "inspector"

        if not inspector_dir.exists():
            print(f"Error: Inspector package not found at {inspector_dir}", file=sys.stderr)
            sys.exit(1)

        print(f"\nInspector package found at: {inspector_dir}")

        # Look for the client/dist directory (where the built web UI is)
        dist_dir = inspector_dir / "client" / "dist"

        if not dist_dir.exists():
            print(f"Error: client/dist directory not found at {dist_dir}", file=sys.stderr)
            print("\nAvailable directories in inspector package:")
            for item in inspector_dir.iterdir():
                print(f"  - {item.name}")
            sys.exit(1)

        print(f"Found dist directory: {dist_dir}")

        # Remove existing static_ui directory if it exists
        if static_ui_dir.exists():
            print(f"\nRemoving existing static UI directory...")
            try:
                shutil.rmtree(static_ui_dir)
            except PermissionError as e:
                # On Windows, files might be locked - wait and retry
                print(f"Warning: Permission error removing directory, retrying...")
                import time
                time.sleep(1)
                shutil.rmtree(static_ui_dir)

        # Copy the dist directory to static_ui
        print(f"\nCopying static files to {static_ui_dir}...")
        shutil.copytree(dist_dir, static_ui_dir)

        print("\n✓ Successfully built MCP Inspector static assets!")
        print(f"  Version: {INSPECTOR_VERSION}")
        print(f"  Location: {static_ui_dir}")

        # Show what was copied
        print("\nCopied files:")
        for item in static_ui_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                rel_path = item.relative_to(static_ui_dir)
                print(f"  - {rel_path} ({size:,} bytes)")


if __name__ == "__main__":
    main()

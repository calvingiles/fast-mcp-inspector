# Build Process

This document describes how to build the `fastapi-mcp-inspector` package for PyPI distribution.

## Overview

The package includes static assets from the official MCP Inspector. Instead of checking these assets into version control, we fetch and build them during the package build process.

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm 7+

## Building Static Assets

The static assets are **not** checked into version control. You must build them before creating a distribution:

```bash
# Method 1: Using npm script
npm run build:assets

# Method 2: Using the shell script
./scripts/build.sh

# Method 3: Running Python directly
python3 scripts/build_assets.py
```

This will:
1. Download `@modelcontextprotocol/inspector@0.17.2` from npm
2. Extract the built static files
3. Copy them to `fastapi_mcp_inspector/static_ui/`

## Building the Python Package

After building the static assets, create the distribution:

```bash
# Install build dependencies
pip install build

# Build the package
python -m build
```

This creates wheel and source distributions in the `dist/` directory.

## Complete Build Pipeline

For a complete build from scratch:

```bash
# 1. Build static assets
npm run build:assets

# 2. Build Python package
python -m build

# 3. Check the package
pip install twine
twine check dist/*
```

## Publishing to PyPI

The GitHub Actions workflow `.github/workflows/publish.yml` handles this automatically:

1. Checks out the code
2. Sets up Node.js and Python
3. Runs `npm run build:assets` to fetch the inspector
4. Builds the package with `python -m build`
5. Publishes to PyPI

## Pinning the Inspector Version

The MCP Inspector version is pinned in two places:

1. **`package.json`**: `"@modelcontextprotocol/inspector": "0.17.2"`
2. **`scripts/build_assets.py`**: `INSPECTOR_VERSION = "0.17.2"`

To upgrade:
1. Update both files to the new version
2. Test locally with `npm run build:assets`
3. Verify the package builds correctly
4. Commit and push

## Troubleshooting

### "static_ui directory not found" error

Run the build script first:
```bash
npm run build:assets
```

### "npm: command not found"

Install Node.js and npm from https://nodejs.org/

### Build fails in CI/CD

Check that `.github/workflows/publish.yml` includes the asset build step before the Python build step.

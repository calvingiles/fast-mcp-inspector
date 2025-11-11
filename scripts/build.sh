#!/bin/bash
# Build script to fetch and build MCP Inspector static assets
# This script is run during the package build process

set -e

echo "Building MCP Inspector static assets..."
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "Error: npm is required but not found"
    exit 1
fi

# Run the build script
python3 scripts/build_assets.py

echo ""
echo "✓ Build complete!"

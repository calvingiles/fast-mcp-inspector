#!/bin/bash
# Claude Code Session Start Hook for fastapi-mcp-inspector
# This script runs automatically when a Claude Code session starts

set -e

echo "🚀 FastAPI MCP Inspector - Session Start Hook"
echo "=============================================="

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "⚠️  Not a git repository, skipping git hooks setup"
    exit 0
fi

# Install pre-commit if not available
if ! command -v pre-commit &> /dev/null; then
    echo "📥 pre-commit not found, installing..."
    if pip install pre-commit --quiet; then
        echo "✅ pre-commit installed successfully"
    else
        echo "⚠️  Failed to install pre-commit (non-fatal)"
        echo "   You can install manually with: pip install pre-commit"
    fi
fi

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit hooks..."
    if pre-commit install --install-hooks 2>/dev/null; then
        echo "✅ Pre-commit hooks installed successfully"
    else
        echo "⚠️  Failed to install pre-commit hooks (non-fatal)"
        echo "   Run manually: pre-commit install"
    fi
fi

# Check Python version
echo ""
echo "🐍 Python version:"
python --version || python3 --version

# Check if package is installed
echo ""
echo "📦 Package installation status:"
if python -c "import fastapi_mcp_inspector" 2>/dev/null; then
    VERSION=$(python -c "import fastapi_mcp_inspector; print(fastapi_mcp_inspector.__version__)")
    echo "✅ fastapi-mcp-inspector v${VERSION} is installed"
else
    echo "⚠️  Package not installed. Run: pip install -e ."
fi

# Show available development commands
echo ""
echo "🛠️  Development Commands:"
echo "  pytest tests/ -v              # Run tests"
echo "  pytest tests/ --cov           # Run with coverage"
echo "  ruff check .                  # Lint code"
echo "  black .                       # Format code"
echo "  python -m build               # Build package"
echo "  python examples/demo_app.py   # Run demo"
echo ""
echo "✨ Session ready! Happy coding!"
echo "=============================================="

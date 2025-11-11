# Contributing to FastAPI MCP Inspector Hub

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Node.js and npm (only if rebuilding MCP Inspector UI)

### Setting Up Your Development Environment

1. **Fork and clone the repository:**

```bash
git clone https://github.com/yourusername/fast-mcp-inspector.git
cd fast-mcp-inspector
```

2. **Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the package in editable mode with dev dependencies:**

```bash
pip install -e .
pip install -r requirements-dev.txt
```

4. **Install pre-commit hooks:**

```bash
pre-commit install
```

## Running Tests

### Full Test Suite

```bash
pytest tests/ -v
```

### With Coverage

```bash
pytest tests/ --cov=fastapi_mcp_inspector --cov-report=html --cov-report=term
```

### Specific Test File

```bash
pytest tests/test_inspector.py -v
```

### Specific Test

```bash
pytest tests/test_inspector.py::test_register_inspector_basic -v
```

## Code Quality

### Linting

We use `ruff` for linting:

```bash
ruff check fastapi_mcp_inspector/
```

To auto-fix issues:

```bash
ruff check fastapi_mcp_inspector/ --fix
```

### Formatting

We use `black` for code formatting:

```bash
black fastapi_mcp_inspector/ tests/
```

### Type Checking

We use `mypy` for type checking:

```bash
mypy fastapi_mcp_inspector/ --ignore-missing-imports
```

## Testing Your Changes

### Manual Testing

Run the example application to manually test your changes:

```bash
cd examples
python demo_app.py
```

Then visit http://localhost:8000/docs to see the Inspector Hub in action.

### Adding Tests

When adding new features, please include tests:

1. Add test functions to `tests/test_inspector.py`
2. Follow the existing test naming convention: `test_<feature_name>`
3. Include docstrings explaining what the test verifies
4. Aim for high test coverage (current: 90%+)

Example test structure:

```python
def test_new_feature():
    """Test description of what this verifies."""
    # Setup
    app = FastAPI(title="Test App")

    # Action
    result = some_function(app)

    # Assert
    assert result is not None
    assert expected_behavior
```

## Making Changes

### Branching Strategy

- `main` - Stable release branch
- `develop` - Development branch (if applicable)
- Feature branches: `feature/<feature-name>`
- Bug fixes: `fix/<bug-description>`

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

Example:

```
feat(discovery): Add support for WebSocket transport

- Implement WebSocket endpoint detection
- Add tests for WebSocket discovery
- Update documentation

Closes #123
```

## Pull Request Process

1. **Create a feature branch:**

```bash
git checkout -b feature/my-new-feature
```

2. **Make your changes and commit:**

```bash
git add .
git commit -m "feat: Add my new feature"
```

3. **Run tests locally:**

```bash
pytest tests/ -v
ruff check fastapi_mcp_inspector/
black --check fastapi_mcp_inspector/
```

4. **Push to your fork:**

```bash
git push origin feature/my-new-feature
```

5. **Create a Pull Request** on GitHub

### PR Checklist

Before submitting your PR, ensure:

- [ ] Tests pass locally (`pytest tests/`)
- [ ] Code is formatted (`black fastapi_mcp_inspector/`)
- [ ] Code is linted (`ruff check fastapi_mcp_inspector/`)
- [ ] Type hints are added where applicable
- [ ] Documentation is updated (if needed)
- [ ] Tests are added for new features
- [ ] Commit messages follow conventions
- [ ] PR description clearly explains the changes

### PR Review Process

1. CI checks must pass (tests, linting, building)
2. At least one maintainer review required
3. Address review feedback
4. Maintainer will merge when approved

## Project Structure

```
fast-mcp-inspector/
├── fastapi_mcp_inspector/     # Main package
│   ├── __init__.py           # Package exports
│   ├── inspector.py          # Core logic
│   ├── static_ui/            # MCP Inspector assets
│   └── py.typed              # Type hints marker
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_inspector.py     # Main tests
├── examples/                 # Example applications
│   ├── demo_app.py
│   └── README.md
├── .github/
│   └── workflows/            # CI/CD pipelines
├── pyproject.toml            # Package config
├── requirements-dev.txt      # Dev dependencies
└── README.md                 # Main documentation
```

## Key Design Principles

1. **Zero Configuration**: Features should work automatically without requiring manual setup
2. **FastAPI Standards**: Follow FastAPI conventions and best practices
3. **Type Safety**: Use type hints throughout the codebase
4. **Test Coverage**: Maintain high test coverage (90%+)
4. **Documentation**: Keep documentation clear and up-to-date

## Updating Static Assets

If you need to update the MCP Inspector UI:

1. **Clone the official inspector:**

```bash
cd /tmp
git clone https://github.com/modelcontextprotocol/inspector.git
cd inspector
```

2. **Build the UI:**

```bash
npm install
npm run build
```

3. **Copy to package:**

```bash
cp -r client/dist/* /path/to/fast-mcp-inspector/fastapi_mcp_inspector/static_ui/
```

4. **Test and commit the changes**

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- FastAPI version
- Operating system
- Minimal code example that reproduces the issue
- Expected vs actual behavior
- Full error traceback (if applicable)

### Feature Requests

When requesting features:

- Clear use case description
- Expected behavior
- Potential implementation approach (optional)
- Willingness to contribute (optional)

## Questions?

- Check the [README](README.md) for usage documentation
- Review [existing issues](https://github.com/calvingiles/fast-mcp-inspector/issues)
- Open a new issue for questions or discussions

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FastAPI MCP Inspector Hub! 🎉

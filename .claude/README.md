# Claude Code Configuration

This directory contains Claude Code configuration for the fastapi-mcp-inspector project.

## Session Start Hook

The `session_start.sh` script runs automatically when you open this project in Claude Code. It:

- ✅ Automatically installs pre-commit hooks if pre-commit is available
- 🐍 Shows your Python version
- 📦 Checks if the package is installed
- 🛠️ Displays helpful development commands

### Manual Hook Execution

You can manually run the session start hook:

```bash
./.claude/session_start.sh
```

## Pre-commit Hooks

The session start hook will attempt to install pre-commit hooks automatically. If it fails or pre-commit isn't installed:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

## Customization

You can customize the session start hook by editing `session_start.sh`. Common additions:

- Virtual environment activation
- Environment variable setup
- Dependency checks
- Custom tooling installation

## Troubleshooting

**Hook doesn't run:**
- Ensure the script is executable: `chmod +x .claude/session_start.sh`
- Check that Claude Code has permission to execute scripts

**Pre-commit installation fails:**
- Install pre-commit globally: `pip install --user pre-commit`
- Or in your virtual environment: `pip install pre-commit`

**Package not found:**
- Install in development mode: `pip install -e .`
- Or install dependencies: `pip install -r requirements-dev.txt`

## Learn More

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Pre-commit Hooks](https://pre-commit.com/)

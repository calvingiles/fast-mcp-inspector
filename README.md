# FastAPI MCP Inspector Hub

> **Swagger UI for MCP** - Integrate the official Model Context Protocol Inspector directly into your FastAPI applications

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)

## Overview

`fastapi-mcp-inspector` is a zero-configuration Python package that automatically discovers MCP servers mounted in your FastAPI application and provides one-click access to a visual debugging interface for each one. Think of it as "Swagger UI for MCP" - it seamlessly integrates the official [MCP Inspector](https://github.com/modelcontextprotocol/inspector) into your FastAPI documentation.

### Key Features

- **Zero Configuration**: Automatically discovers mounted MCP servers - no manual tagging required
- **Seamless Integration**: Adds Inspector links directly to your existing `/docs` page
- **One-Click Debugging**: Launch the MCP Inspector for any service with a single click
- **Multiple Transports**: Supports both `streamable-http` and `sse` transport protocols
- **Production Ready**: Built on standard FastAPI patterns and conventions

## Installation

```bash
pip install fastapi-mcp-inspector
```

## Quick Start

```python
from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi_mcp_inspector import register_inspector

# Create your main FastAPI app
app = FastAPI(title="My API")

# Create and mount your MCP servers
user_mcp = FastMCP("User Service")

@user_mcp.tool()
async def get_user(user_id: str) -> dict:
    """Get user by ID"""
    return {"id": user_id, "name": "John Doe"}

app.mount("/users", user_mcp.get_asgi_app())

# Register the inspector (should be last!)
register_inspector(app)

# That's it! Visit /docs to see the Inspector Hub
```

Now visit `http://localhost:8000/docs` and you'll see a new section:

```
🔬 MCP Inspector Hub

* User Service (/users)
  * Launch Inspector ➔
```

Click the link to open the MCP Inspector pre-connected to your service!

## How It Works

The package operates as a "Hub" that integrates with your FastAPI application:

1. **Discovery**: Scans your app's routing table to find mounted MCP servers
2. **Static Serving**: Serves the official MCP Inspector UI from a hidden route (`/_inspector_ui`)
3. **Documentation Injection**: Adds links to the Inspector in your OpenAPI/Swagger docs

```
┌─────────────────────────────────────┐
│      Your FastAPI App (/docs)      │
│  ┌───────────────────────────────┐ │
│  │  🔬 MCP Inspector Hub          │ │
│  │  • User Service    [Launch ➔] │ │
│  │  • Payment Service [Launch ➔] │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
               │
               │ (discovers)
               ▼
    ┌──────────────────────┐
    │  /users (MCP Server) │
    │  /payments (MCP)     │
    └──────────────────────┘
```

## Discovery Heuristics

The package automatically identifies MCP servers using these conventions:

| Detection Method | Condition | Result |
|-----------------|-----------|--------|
| **Transport Type** | Route path = `/mcp` | `streamable-http` |
| **Transport Type** | Route path = `/sse` | `sse` |
| **Server Name** | `sub_app.title` exists | Use title (e.g., "User Service") |
| **Server Name** | `sub_app.title` missing | Use mount name (e.g., "users") |

These are standard patterns from [fastmcp](https://github.com/modelcontextprotocol/python-sdk) and require no special configuration.

## API Reference

### `register_inspector(app, inspector_mount="/_inspector_ui", auto_discover=True)`

Register the MCP Inspector Hub with a FastAPI application.

**Parameters:**
- `app` (FastAPI): The FastAPI application to register with
- `inspector_mount` (str, optional): Path to mount the Inspector UI. Default: `"/_inspector_ui"`
- `auto_discover` (bool, optional): Whether to automatically discover MCP servers. Default: `True`

**Returns:**
- Dictionary with:
  - `discovered_servers`: List of `MCPServer` objects found
  - `inspector_url`: The URL where the Inspector UI is mounted

**Example:**
```python
result = register_inspector(app)
print(f"Found {len(result['discovered_servers'])} MCP servers")
print(f"Inspector UI at: {result['inspector_url']}")
```

## Advanced Usage

### Custom Inspector Mount Path

```python
register_inspector(app, inspector_mount="/debug/mcp")
```

### Manual Discovery

If you need more control:

```python
from fastapi_mcp_inspector import register_inspector, MCPServer

# Register without auto-discovery
result = register_inspector(app, auto_discover=False)

# Inspector UI is still available, but no servers are discovered
```

### Multiple Environments

```python
import os
from fastapi import FastAPI
from fastapi_mcp_inspector import register_inspector

app = FastAPI()

# Mount your MCP servers
app.mount("/users", user_mcp_app)

# Only enable inspector in development
if os.getenv("ENV") == "development":
    register_inspector(app)
```

## Requirements

- Python 3.8+
- FastAPI 0.68.0+
- Starlette 0.14.0+

## Architecture

The package follows FastAPI best practices:

- **Static Files**: Uses `StaticFiles` to serve the Inspector UI
- **Sub-applications**: Uses `app.mount()` pattern for mounting
- **OpenAPI Integration**: Extends `app.description` with Markdown
- **Type Safety**: Fully typed with `py.typed` marker

## Compatibility

### Works With

- ✅ [fastmcp](https://github.com/modelcontextprotocol/python-sdk) - Official Python SDK
- ✅ Any ASGI app that exposes `/mcp` or `/sse` endpoints
- ✅ Both `streamable-http` and `sse` transports

### Requirements

- Same origin (domain/port) for Inspector UI and MCP endpoints
- Sub-applications must expose a `.routes` attribute (standard in Starlette/FastAPI)

## Examples

See the [examples](./examples) directory for complete working demos:

- `demo_app.py` - Full example with multiple mock MCP servers
- `examples/README.md` - Instructions for running the examples

## Troubleshooting

### Inspector shows "Connection Failed"

- Ensure your MCP server is running on the same domain/port as the main app
- Check that the transport type matches (`streamable-http` vs `sse`)
- Verify the MCP endpoint path is correct (`/mcp` or `/sse`)

### Servers not discovered

- Ensure you call `register_inspector(app)` **after** mounting all MCP servers
- Verify your MCP servers expose routes at `/mcp` or `/sse`
- Check that mounted sub-apps are proper FastAPI/Starlette applications

### Static files not found

- Ensure the package is properly installed with `pip install fastapi-mcp-inspector`
- The `static_ui` directory must be included in the package distribution

## Contributing

Contributions are welcome! This package integrates:

- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - The UI
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Server SDK
- [FastAPI](https://github.com/tiangolo/fastapi) - Web framework

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built on the official [Model Context Protocol Inspector](https://github.com/modelcontextprotocol/inspector)
- Designed for use with [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
- Inspired by FastAPI's excellent developer experience

## Links

- **Repository**: https://github.com/calvingiles/fast-mcp-inspector
- **MCP Specification**: https://modelcontextprotocol.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **FastMCP Documentation**: https://github.com/modelcontextprotocol/python-sdk

---

Made with ❤️ for the MCP community

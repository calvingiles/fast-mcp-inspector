"""
FastAPI MCP Inspector Hub

A pluggable Python package that integrates the official Model Context Protocol (MCP)
Inspector directly into FastAPI applications. Acts as a "Swagger UI for MCP," providing
automatic discovery of mounted MCP servers and one-click access to visual debugging.

Example usage:
    ```python
    from fastapi import FastAPI
    from fastapi_mcp_inspector import register_inspector

    app = FastAPI(title="My API")

    # Mount your MCP servers
    app.mount("/users", user_mcp_app)
    app.mount("/payments", payment_mcp_app)

    # Register the inspector (should be last)
    register_inspector(app)
    ```
"""

from .inspector import register_inspector, MCPServer

__version__ = "0.1.0"
__all__ = ["register_inspector", "MCPServer"]

"""
Core logic for the FastAPI MCP Inspector Hub.

This module provides functionality to:
1. Discover mounted MCP servers in a FastAPI application
2. Serve the MCP Inspector UI as static files
3. Inject documentation links into the OpenAPI schema
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from urllib.parse import quote
import importlib.resources

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.routing import Mount
from starlette.routing import Route


class MCPServer:
    """Represents a discovered MCP server."""

    def __init__(
        self,
        name: str,
        mount_path: str,
        endpoint_path: str,
        transport: str
    ):
        self.name = name
        self.mount_path = mount_path
        self.endpoint_path = endpoint_path
        self.transport = transport
        self.full_url = f"{mount_path}{endpoint_path}"


def _discover_mcp_servers(app: FastAPI) -> List[MCPServer]:
    """
    Recursively scan the FastAPI app's routing table to discover MCP servers.

    Args:
        app: The FastAPI application to scan

    Returns:
        List of discovered MCP servers
    """
    discovered_servers = []

    for route in app.routes:
        # Check if this is a mounted sub-application
        if not isinstance(route, Mount):
            continue

        mount_path = route.path.rstrip('/')
        sub_app = route.app

        # Check if the sub-app has routes (standard for Starlette/FastAPI apps)
        if not hasattr(sub_app, 'routes'):
            continue

        # Scan the sub-app's routes for MCP endpoints
        transport = None
        endpoint_path = None

        for sub_route in sub_app.routes:
            if isinstance(sub_route, Route):
                # Check for MCP endpoint patterns
                if sub_route.path == '/mcp':
                    transport = 'streamable-http'
                    endpoint_path = '/mcp'
                    break
                elif sub_route.path == '/sse':
                    transport = 'sse'
                    endpoint_path = '/sse'
                    break

        # If we found an MCP endpoint, create a server entry
        if transport and endpoint_path:
            # Try to infer a name for this server
            name = None

            # Try to get the title from the sub-app (standard FastAPI attribute)
            if hasattr(sub_app, 'title'):
                name = sub_app.title

            # Fallback to the mount name
            if not name:
                name = route.name or mount_path.lstrip('/')

            discovered_servers.append(MCPServer(
                name=name,
                mount_path=mount_path,
                endpoint_path=endpoint_path,
                transport=transport
            ))

    return discovered_servers


def _inject_openapi_links(app: FastAPI, servers: List[MCPServer], inspector_mount: str) -> None:
    """
    Inject MCP Inspector Hub links into the OpenAPI description.

    Args:
        app: The FastAPI application
        servers: List of discovered MCP servers
        inspector_mount: The path where the inspector UI is mounted
    """
    if not servers:
        return

    # Build the hub section
    hub_section = "\n\n## \U0001F52C MCP Inspector Hub\n\n"

    for server in servers:
        # URL-encode the full path
        encoded_url = quote(server.full_url)
        inspector_link = f"{inspector_mount}?url={encoded_url}&transport={server.transport}"

        hub_section += f"* **{server.name}** (`{server.mount_path}`)\n"
        hub_section += f"  * [**Launch Inspector →**]({inspector_link})\n\n"

    # Append to existing description (or create new one)
    if app.description:
        app.description += hub_section
    else:
        app.description = hub_section.strip()


def _mount_inspector_ui(app: FastAPI, mount_path: str) -> None:
    """
    Mount the MCP Inspector UI static files.

    Args:
        app: The FastAPI application
        mount_path: The path to mount the inspector UI at
    """
    # Get the path to the static_ui directory using importlib.resources
    try:
        # Python 3.9+
        static_path = importlib.resources.files('fastapi_mcp_inspector').joinpath('static_ui')
    except AttributeError:
        # Python 3.7-3.8 fallback
        with importlib.resources.path('fastapi_mcp_inspector', 'static_ui') as p:
            static_path = p

    # Mount the static files
    app.mount(
        mount_path,
        StaticFiles(directory=str(static_path), html=True),
        name="mcp_inspector_ui"
    )


def register_inspector(
    app: FastAPI,
    inspector_mount: str = "/_inspector_ui",
    auto_discover: bool = True
) -> Dict[str, Any]:
    """
    Register the MCP Inspector Hub with a FastAPI application.

    This function should be called after all MCP servers have been mounted to the app.
    It will:
    1. Discover mounted MCP servers (if auto_discover is True)
    2. Mount the Inspector UI static files
    3. Inject documentation links into the OpenAPI schema

    Args:
        app: The FastAPI application to register with
        inspector_mount: The path to mount the inspector UI at (default: /_inspector_ui)
        auto_discover: Whether to automatically discover MCP servers (default: True)

    Returns:
        Dictionary containing:
        - discovered_servers: List of MCPServer objects that were discovered
        - inspector_url: The URL where the inspector UI is mounted

    Example:
        ```python
        from fastapi import FastAPI
        from fastapi_mcp_inspector import register_inspector

        app = FastAPI()

        # Mount your MCP servers
        app.mount("/users", user_mcp_app)
        app.mount("/payments", payment_mcp_app)

        # Register the inspector (should be last)
        register_inspector(app)
        ```
    """
    discovered_servers = []

    if auto_discover:
        # Discover MCP servers
        discovered_servers = _discover_mcp_servers(app)

    # Mount the inspector UI
    _mount_inspector_ui(app, inspector_mount)

    # Inject links into OpenAPI docs
    if discovered_servers:
        _inject_openapi_links(app, discovered_servers, inspector_mount)

    return {
        'discovered_servers': discovered_servers,
        'inspector_url': inspector_mount
    }

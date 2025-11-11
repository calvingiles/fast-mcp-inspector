"""
Unit tests for the FastAPI MCP Inspector Hub.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.routing import Route

from fastapi_mcp_inspector import register_inspector, MCPServer


def create_mock_mcp_app(name: str, transport: str = "streamable-http") -> FastAPI:
    """Create a mock MCP server application."""
    app = FastAPI(title=name)

    endpoint = "/mcp" if transport == "streamable-http" else "/sse"

    @app.get(endpoint)
    def mcp_endpoint():
        return {"status": "ok"}

    return app


def test_register_inspector_basic():
    """Test basic inspector registration."""
    app = FastAPI(title="Test App")

    # Mount a mock MCP server
    mcp_app = create_mock_mcp_app("Test Service")
    app.mount("/test", mcp_app)

    # Register the inspector
    result = register_inspector(app)

    # Verify result
    assert 'discovered_servers' in result
    assert 'inspector_url' in result
    assert result['inspector_url'] == '/_inspector_ui'
    assert len(result['discovered_servers']) == 1

    # Verify discovered server
    server = result['discovered_servers'][0]
    assert isinstance(server, MCPServer)
    assert server.name == "Test Service"
    assert server.mount_path == "/test"
    assert server.transport == "streamable-http"


def test_discover_multiple_servers():
    """Test discovery of multiple MCP servers."""
    app = FastAPI(title="Test App")

    # Mount multiple MCP servers
    app.mount("/users", create_mock_mcp_app("User Service", "streamable-http"))
    app.mount("/payments", create_mock_mcp_app("Payment Service", "streamable-http"))
    app.mount("/analytics", create_mock_mcp_app("Analytics", "sse"))

    # Register the inspector
    result = register_inspector(app)

    # Verify all servers were discovered
    assert len(result['discovered_servers']) == 3

    # Verify transports
    transports = {s.transport for s in result['discovered_servers']}
    assert "streamable-http" in transports
    assert "sse" in transports


def test_openapi_injection():
    """Test that inspector links are injected into OpenAPI description."""
    app = FastAPI(
        title="Test App",
        description="Original description"
    )

    # Mount a mock MCP server
    app.mount("/test", create_mock_mcp_app("Test Service"))

    # Register the inspector
    register_inspector(app)

    # Verify description was updated
    assert app.description is not None
    assert "Original description" in app.description
    assert "🔬 MCP Inspector Hub" in app.description
    assert "Test Service" in app.description
    assert "Launch Inspector" in app.description


def test_custom_inspector_mount():
    """Test custom inspector mount path."""
    app = FastAPI(title="Test App")
    app.mount("/test", create_mock_mcp_app("Test Service"))

    # Register with custom mount path
    result = register_inspector(app, inspector_mount="/debug/inspector")

    assert result['inspector_url'] == '/debug/inspector'


def test_no_autodiscover():
    """Test inspector without auto-discovery."""
    app = FastAPI(title="Test App")
    app.mount("/test", create_mock_mcp_app("Test Service"))

    # Register without auto-discovery
    result = register_inspector(app, auto_discover=False)

    # Should have no discovered servers
    assert len(result['discovered_servers']) == 0


def test_static_files_mounted():
    """Test that static files are accessible."""
    app = FastAPI(title="Test App")
    app.mount("/test", create_mock_mcp_app("Test Service"))

    register_inspector(app)

    # Create test client
    client = TestClient(app)

    # Test that inspector UI is accessible
    response = client.get("/_inspector_ui/")
    assert response.status_code == 200
    # Should return HTML content
    assert "html" in response.text.lower()


def test_mcp_server_class():
    """Test MCPServer class."""
    server = MCPServer(
        name="Test Server",
        mount_path="/test",
        endpoint_path="/mcp",
        transport="streamable-http"
    )

    assert server.name == "Test Server"
    assert server.mount_path == "/test"
    assert server.endpoint_path == "/mcp"
    assert server.transport == "streamable-http"
    assert server.full_url == "/test/mcp"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

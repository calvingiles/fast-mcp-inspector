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


def test_app_without_mcp_servers():
    """Test registering inspector on app with no MCP servers."""
    app = FastAPI(title="Test App", description="My API")

    # Register inspector on empty app
    result = register_inspector(app)

    # Should return empty list
    assert len(result['discovered_servers']) == 0

    # Description should not be modified
    assert app.description == "My API"


def test_server_name_fallback():
    """Test that server name falls back to mount name when title is missing."""
    app = FastAPI(title="Test App")

    # Create app without title (FastAPI has default title "FastAPI")
    mcp_app = FastAPI()

    @mcp_app.get("/mcp")
    def mcp_endpoint():
        return {"status": "ok"}

    # Mount with a specific name
    app.mount("/custom-service", mcp_app, name="custom_mount")

    result = register_inspector(app)

    # Should use the app's title (FastAPI has a default title)
    server = result['discovered_servers'][0]
    assert server.name in ["FastAPI", "custom_mount"]  # Either is acceptable


def test_non_mcp_mounts_ignored():
    """Test that non-MCP mounted apps are ignored."""
    app = FastAPI(title="Test App")

    # Mount a regular FastAPI app without MCP endpoints
    regular_app = FastAPI(title="Regular Service")

    @regular_app.get("/health")
    def health():
        return {"status": "ok"}

    app.mount("/regular", regular_app)

    # Mount an MCP app
    app.mount("/mcp-service", create_mock_mcp_app("MCP Service"))

    result = register_inspector(app)

    # Should only discover the MCP server
    assert len(result['discovered_servers']) == 1
    assert result['discovered_servers'][0].name == "MCP Service"


def test_url_encoding_in_links():
    """Test that URLs with special paths are handled in inspector links."""
    app = FastAPI(title="Test App")

    # Mount at a nested path
    app.mount("/api/v1/users", create_mock_mcp_app("User Service"))

    register_inspector(app)

    # Verify path is in description
    assert "/api/v1/users" in app.description
    # The URL encoding happens when the browser processes the link
    # In markdown, the path can remain unencoded
    assert "url=/api/v1/users/mcp" in app.description or "url=%2Fapi%2Fv1%2Fusers%2Fmcp" in app.description


def test_sse_transport_detection():
    """Test detection of SSE transport."""
    app = FastAPI(title="Test App")

    app.mount("/events", create_mock_mcp_app("Event Service", "sse"))

    result = register_inspector(app)

    server = result['discovered_servers'][0]
    assert server.transport == "sse"
    assert server.endpoint_path == "/sse"
    assert "transport=sse" in app.description


def test_inspector_link_format():
    """Test the format of inspector links in description."""
    app = FastAPI(title="Test App")

    app.mount("/users", create_mock_mcp_app("User Service"))

    result = register_inspector(app)

    # Verify markdown link format
    assert "* **User Service** (`/users`)" in app.description
    assert "[**Launch Inspector →**]" in app.description
    assert "/_inspector_ui?url=" in app.description


def test_multiple_inspector_registrations():
    """Test that multiple registrations don't cause issues."""
    app = FastAPI(title="Test App")

    app.mount("/test", create_mock_mcp_app("Test Service"))

    # Register twice
    result1 = register_inspector(app)
    result2 = register_inspector(app)

    # Both should succeed
    assert len(result1['discovered_servers']) == 1
    assert len(result2['discovered_servers']) == 1


def test_empty_description_handling():
    """Test handling of apps with no initial description."""
    app = FastAPI(title="Test App")  # No description

    app.mount("/test", create_mock_mcp_app("Test Service"))

    register_inspector(app)

    # Should create new description
    assert app.description is not None
    assert "🔬 MCP Inspector Hub" in app.description
    assert app.description.startswith("## 🔬")


def test_static_assets_exist():
    """Test that all expected static assets are available."""
    app = FastAPI(title="Test App")
    app.mount("/test", create_mock_mcp_app("Test Service"))

    register_inspector(app)

    client = TestClient(app)

    # Test index.html
    response = client.get("/_inspector_ui/")
    assert response.status_code == 200

    # Test that CSS and JS are referenced
    assert "assets/" in response.text or ".css" in response.text or ".js" in response.text


def test_endpoint_path_combinations():
    """Test various endpoint path configurations."""
    app = FastAPI(title="Test App")

    # Test /mcp endpoint
    mcp1 = create_mock_mcp_app("Service 1", "streamable-http")
    app.mount("/service1", mcp1)

    # Test /sse endpoint
    mcp2 = create_mock_mcp_app("Service 2", "sse")
    app.mount("/service2", mcp2)

    result = register_inspector(app)

    # Verify both were discovered with correct paths
    assert len(result['discovered_servers']) == 2

    paths = {s.endpoint_path for s in result['discovered_servers']}
    assert "/mcp" in paths
    assert "/sse" in paths


def test_mount_path_normalization():
    """Test that mount paths are normalized correctly."""
    app = FastAPI(title="Test App")

    # Mount with trailing slash
    app.mount("/test/", create_mock_mcp_app("Test Service"))

    result = register_inspector(app)

    # Path should be normalized (no trailing slash)
    server = result['discovered_servers'][0]
    assert server.mount_path == "/test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

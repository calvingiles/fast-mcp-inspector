"""
Demo application showing how to use fastapi-mcp-inspector.

This example creates a FastAPI application with multiple MCP servers
and demonstrates automatic discovery and integration of the Inspector Hub.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os

# Add the parent directory to the path so we can import our package during development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi_mcp_inspector import register_inspector


# Create mock MCP server applications
# In a real application, these would be created using fastmcp

def create_mock_mcp_app(name: str, transport: str = "streamable-http") -> FastAPI:
    """
    Create a mock MCP server application for demonstration.

    In a real application, you would use fastmcp to create these servers:

    from fastmcp import FastMCP

    mcp = FastMCP(name)

    @mcp.tool()
    async def my_tool():
        return "result"

    app = mcp.get_asgi_app()
    """
    app = FastAPI(title=name)

    # Add the MCP endpoint based on transport type
    endpoint = "/mcp" if transport == "streamable-http" else "/sse"

    @app.post(endpoint)
    @app.get(endpoint)
    async def mcp_endpoint():
        """Mock MCP endpoint"""
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": name,
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        })

    return app


# Create the main FastAPI application
app = FastAPI(
    title="MCP Demo API",
    description="Demo application showcasing FastAPI MCP Inspector Hub",
    version="1.0.0"
)


# Add a simple health check endpoint
@app.get("/")
async def root():
    return {
        "message": "MCP Demo API",
        "docs": "/docs",
        "inspector_hub": "See /docs for MCP Inspector links"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Mount MCP servers
# These would typically be created using fastmcp in a real application

user_service = create_mock_mcp_app("User Service", transport="streamable-http")
app.mount("/users", user_service)

payment_service = create_mock_mcp_app("Payment Service", transport="streamable-http")
app.mount("/payments", payment_service)

analytics_service = create_mock_mcp_app("Analytics Service", transport="sse")
app.mount("/analytics", analytics_service)


# Register the Inspector Hub (should be last!)
# This discovers all mounted MCP servers and adds them to the docs
result = register_inspector(app)

print(f"\n🔬 MCP Inspector Hub registered!")
print(f"   Inspector UI mounted at: {result['inspector_url']}")
print(f"   Discovered {len(result['discovered_servers'])} MCP servers:")
for server in result['discovered_servers']:
    print(f"   - {server.name} at {server.mount_path} ({server.transport})")
print(f"\n📚 Visit http://localhost:8000/docs to see the Inspector Hub\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

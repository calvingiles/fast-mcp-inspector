# Examples

This directory contains example applications demonstrating how to use `fastapi-mcp-inspector`.

## Demo Application

The `demo_app.py` file contains a complete working example with multiple mock MCP servers.

### Running the Demo

1. Install dependencies:
```bash
pip install -e ..
pip install -r requirements.txt
```

2. Run the application:
```bash
python demo_app.py
```

3. Open your browser:
   - API Docs: http://localhost:8000/docs
   - Look for the "🔬 MCP Inspector Hub" section
   - Click "Launch Inspector" for any service

### What the Demo Shows

- Three mock MCP services (Users, Payments, Analytics)
- Automatic discovery of mounted MCP servers
- Integration with FastAPI's OpenAPI documentation
- One-click access to the MCP Inspector UI for each service

## Real-World Usage

In a real application, you would use `fastmcp` to create your MCP servers:

```python
from fastapi import FastAPI
from fastmcp import FastMCP
from fastapi_mcp_inspector import register_inspector

# Create your main app
app = FastAPI(title="My API")

# Create an MCP server using fastmcp
mcp = FastMCP("My Service")

@mcp.tool()
async def my_tool(param: str) -> str:
    """A sample tool"""
    return f"Processed: {param}"

# Mount the MCP server
app.mount("/my-service", mcp.get_asgi_app())

# Register the inspector (should be last)
register_inspector(app)
```

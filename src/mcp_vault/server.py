from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
import os
import logging
from .tools import ToolHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-vault")
# TODO improve logging

vault_path = os.getenv("VAULT_PATH")
if not vault_path:
    raise ValueError(f"VAULT_PATH environment variable required. Working directory: {os.getcwd()}")

# Create server instance
app = Server("mcp-vault")

# Tools registry
tools_dict: dict[str, ToolHandler] = {}

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""

    return [handler.get_tool_description() for handler in tools_dict.values()]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name in tools_dict:
        handler = tools_dict[name]
        return handler.run_tool(arguments)

    err = f"Unknown tool: {name}";
    logger.error(err)
    raise ValueError(err)

async def main():
    """Run the server."""

    # Register tools
    global tools_dict
    from .tools import register_tools
    tools_dict = register_tools()

    # start the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


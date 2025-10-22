from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import logging
from pathlib import Path
from .tools import ToolHandler, ToolContext

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
        return await handler.run_tool(arguments)

    err = f"Unknown tool: {name}"
    logger.error(err)
    raise ValueError(err)

async def main():
    """Run the server."""

    # Create the tool context
    context = ToolContext(vault_path=Path(vault_path))

    # First, spawn mcp-obsidian as a subprocess
    obsidian_params = StdioServerParameters(
        command="uvx",
        args=["mcp-obsidian"],
        env={
            "OBSIDIAN_API_KEY": context.api_token,
            "OBSIDIAN_HOST": os.getenv("OBSIDIAN_HOST", "127.0.0.1"),
            "OBSIDIAN_PORT": os.getenv("OBSIDIAN_PORT", "27124"),
        }
    )

    # Connect to mcp-obsidian and keep the connection open
    async with stdio_client(obsidian_params) as (obs_read, obs_write):
        async with ClientSession(obs_read, obs_write) as obsidian_session:
            await obsidian_session.initialize()
            logger.info("Connected to mcp-obsidian")

            # Set obsidian session into context
            context.obsidian_session = obsidian_session

            # Register tools, passing the context to them
            global tools_dict
            from .tools import register_tools
            tools_dict = register_tools(context)

            # Start our own server
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await app.run(
                    read_stream,
                    write_stream,
                    app.create_initialization_options()
                )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


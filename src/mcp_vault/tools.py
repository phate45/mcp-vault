from collections.abc import Sequence
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import json
import os
from pathlib import Path
import urllib.parse
import ssl
import http.client

from . import implementation


def register_tools() -> dict['ToolHandler']:
    """Semi-automatic tool registrar.

    Each new tool needs to be added to the list below (for now).
    """

    tools = {}

    def add_tool(tool: ToolHandler):
        tools[tool.name] = tool

    add_tool(MoveFileTool())
    add_tool(ListHeadingsTool())
    add_tool(NailHeadingTool())

    return tools


class ToolHandler():
    """Base class, inspired by mcp-obsidian."""

    def __init__(self, tool_name: str):
        self.name = tool_name
        self.vault_path = Path(os.getenv("VAULT_PATH"))

    def get_tool_description(self) -> Tool:
        raise NotImplementedError()

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError()


class MoveFileTool(ToolHandler):
    def __init__(self):
        super().__init__("move_file")

    def get_tool_description(self) -> Tool:
        """Define the move_file tool."""

        return Tool(
            name=self.name,
            description="Move a file from one path to another",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_path": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "to_path": {
                        "type": "string",
                        "description": "Destination file path"
                    }
                },
                "required": ["from_path", "to_path"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle move_file tool calls."""

        config_path = ".obsidian/plugins/obsidian-local-rest-api/data.json"
        path_from = args['from_path']
        path_to = args['to_path']

        api_token = implementation.load_api_token(self.vault_path / config_path)

        # Encode paths for URLs
        path_encoded = urllib.parse.quote(path_from)
        dest_encoded = urllib.parse.quote(path_to)

        # Disable SSL verification (like curl -k)
        # This is because the plugin uses self-signed certificates for the https communication.
        context = ssl._create_unverified_context()

        conn = http.client.HTTPSConnection("localhost", 27124, context=context)
        # TODO make the connection details configurable

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Destination": dest_encoded,
        }

        conn.request("MOVE", f"/vault/{path_encoded}", headers=headers)
        response = conn.getresponse()

        res = f"Status: {response.status} {response.reason}"
        body = response.read().decode()
        if body:
            res += "\n" + body

        conn.close()

        return [TextContent(type="text", text=res)]


class ListHeadingsTool(ToolHandler):
    def __init__(self):
        super().__init__("list_headings")

    def get_tool_description(self) -> Tool:
        """Define the list_headings tool."""

        return Tool(
            name=self.name,
            description="List all headings in a markdown file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the markdown file"
                    }
                },
                "required": ["file_path"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle list_headings tool calls."""

        res = implementation.list_headings(self.vault_path / args['file_path'])
        formatted = "\n".join(f"{level} {title}" for level, title in res)
        return [TextContent(type="text", text=formatted)]


class NailHeadingTool(ToolHandler):
    def __init__(self):
        super().__init__("nail_heading")

    def get_tool_description(self) -> Tool:
        """Define the nail_heading tool."""
        return Tool(
            name=self.name,
            description="Nail a heading",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the markdown file"
                    },
                    "heading": {
                        "type": "string",
                        "description": "The heading to nail"
                    }
                },
                "required": ["file_path", "heading"]
            }
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle nail_heading tool calls."""

        res = implementation.nail_heading(self.vault_path / args['file_path'], args['heading'])
        return [TextContent(type="text", text=res)]


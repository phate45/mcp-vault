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


class ToolContext:
    """Context object passed to all tool handlers."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

        # Load API token for Obsidian Local REST API
        config_path = vault_path / ".obsidian/plugins/obsidian-local-rest-api/data.json"
        self.api_token = implementation.load_api_token(config_path)

        # Obsidian session - set later by server
        self.obsidian_session = None


def register_tools(context: ToolContext) -> dict['ToolHandler']:
    """Semi-automatic tool registrar.

    Each new tool needs to be added to the list below (for now).
    """

    tools = {}

    def add_tool(tool: ToolHandler):
        tools[tool.name] = tool

    add_tool(MoveFileTool(context))
    # add_tool(ListHeadingsTool(context))
    # add_tool(NailHeadingTool(context))
    add_tool(AppendToHeadingTool(context))
    add_tool(SimpleSearchTool(context))
    add_tool(ComplexSearchTool(context))
    add_tool(BatchGetFileContentsTool(context))
    add_tool(GetRecentChangesTool(context))
    add_tool(GetRecentDailiesTool(context))

    return tools


class ToolHandler():
    """Base class, inspired by mcp-obsidian."""

    def __init__(self, tool_name: str, context: ToolContext):
        self.name = tool_name
        self.context = context

    def get_tool_description(self) -> Tool:
        raise NotImplementedError()

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError()


class ObsidianProxyTool(ToolHandler):
    """Base class for tools that proxy calls to the obsidian session."""

    def __init__(self, tool_name: str, obsidian_tool_name: str, context: ToolContext):
        super().__init__(tool_name, context)
        self.obsidian_tool_name = obsidian_tool_name

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls by proxying to obsidian session."""
        result = await self.context.obsidian_session.call_tool(
            self.obsidian_tool_name,
            args
        )
        return result.content


class MoveFileTool(ToolHandler):
    def __init__(self, context: ToolContext):
        super().__init__("move_file", context)

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

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle move_file tool calls."""

        path_from = args['from_path']
        path_to = args['to_path']

        # Encode paths for URLs
        path_encoded = urllib.parse.quote(path_from)
        dest_encoded = urllib.parse.quote(path_to)

        # Disable SSL verification (like curl -k)
        # This is because the plugin uses self-signed certificates for the https communication.
        context = ssl._create_unverified_context()

        conn = http.client.HTTPSConnection("localhost", 27124, context=context)
        # TODO make the connection details configurable

        headers = {
            "Authorization": f"Bearer {self.context.api_token}",
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
    def __init__(self, context: ToolContext):
        super().__init__("list_headings", context)

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

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle list_headings tool calls."""

        res = implementation.list_headings(self.context.vault_path / args['file_path'])
        formatted = "\n".join(f"{level} {title}" for level, title in res)
        return [TextContent(type="text", text=formatted)]


class NailHeadingTool(ToolHandler):
    def __init__(self, context: ToolContext):
        super().__init__("nail_heading", context)

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

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle nail_heading tool calls."""

        res = implementation.nail_heading(self.context.vault_path / args['file_path'], args['heading'])
        return [TextContent(type="text", text=res)]


class AppendToHeadingTool(ToolHandler):
    def __init__(self, context: ToolContext):
        super().__init__("append_to_heading", context)

    def get_tool_description(self) -> Tool:
        """Define the append_to_heading tool."""
        return Tool(
            name=self.name,
            description="Append content to a specific heading in a markdown file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the markdown file"
                    },
                    "heading": {
                        "type": "string",
                        "description": "The heading to append content to"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to append"
                    }
                },
                "required": ["file_path", "heading", "content"]
            }
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle append_to_heading tool calls."""

        file_path = args['file_path']
        heading = args['heading']
        content = args['content']

        # 1. Use nail_heading to get the full hierarchical path
        heading_path = implementation.nail_heading(
            self.context.vault_path / file_path,
            heading
        )

        # 2. Call obsidian_patch_content via the obsidian session
        result = await self.context.obsidian_session.call_tool(
            "obsidian_patch_content",
            {
                "filepath": file_path,
                "operation": "append",
                "target_type": "heading",
                "target": heading_path,
                "content": content
            }
        )

        # 3. Return the result from obsidian
        return result.content


class SimpleSearchTool(ObsidianProxyTool):
    def __init__(self, context: ToolContext):
        super().__init__("simple_search", "obsidian_simple_search", context)

    def get_tool_description(self) -> Tool:
        """Define the simple_search tool."""
        return Tool(
            name=self.name,
            description="Simple search for documents matching a specified text query across all files in the vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for in the vault"
                    },
                    "context_length": {
                        "type": "integer",
                        "description": "How much context to return around the matching string (default: 100)"
                    }
                },
                "required": ["query"]
            }
        )


class ComplexSearchTool(ObsidianProxyTool):
    def __init__(self, context: ToolContext):
        super().__init__("complex_search", "obsidian_complex_search", context)

    def get_tool_description(self) -> Tool:
        """Define the complex_search tool."""
        return Tool(
            name=self.name,
            description="Complex search for documents using a JsonLogic query. Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "JsonLogic query object. Example: {\"in\": [\"tag-name\", {\"var\": \"tags\"}]} to search by tag"
                    }
                },
                "required": ["query"]
            }
        )


class BatchGetFileContentsTool(ObsidianProxyTool):
    def __init__(self, context: ToolContext):
        super().__init__("batch_get_file_contents", "obsidian_batch_get_file_contents", context)

    def get_tool_description(self) -> Tool:
        """Define the batch_get_file_contents tool."""
        return Tool(
            name=self.name,
            description="Return the contents of multiple files in your vault, concatenated with headers",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepaths": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Path to a file (relative to vault root)"
                        },
                        "description": "List of file paths to read"
                    }
                },
                "required": ["filepaths"]
            }
        )


class GetRecentChangesTool(ObsidianProxyTool):
    def __init__(self, context: ToolContext):
        super().__init__("get_recent_changes", "obsidian_get_recent_changes", context)

    def get_tool_description(self) -> Tool:
        """Define the get_recent_changes tool."""
        return Tool(
            name=self.name,
            description="Get recently modified files in the vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of files to return (default: 10)",
                        "default": 10
                    },
                    "days": {
                        "type": "integer",
                        "description": "Only include files modified within this many days (default: 90)",
                        "default": 90
                    }
                }
            }
        )


class GetRecentDailiesTool(ToolHandler):
    def __init__(self, context: ToolContext):
        super().__init__("get_recent_dailies", context)

    def get_tool_description(self) -> Tool:
        """Define the get_recent_dailies tool."""
        return Tool(
            name=self.name,
            description="Get the most recent daily notes from the vault, including today's note",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of daily notes to return (default: 7)",
                        "default": 7
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Whether to include note content (default: false)",
                        "default": False
                    }
                }
            }
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle get_recent_dailies tool calls."""

        limit = args.get('limit', 7)
        include_content = args.get('include_content', False)

        result = implementation.get_recent_dailies(
            self.context.vault_path,
            limit=limit,
            include_content=include_content
        )

        return [TextContent(type="text", text=result)]


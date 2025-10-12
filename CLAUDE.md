# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

MCP server for Obsidian vault operations. Communicates with Obsidian via the Local REST API plugin (custom fork required for move operations) and reads markdown files directly from the filesystem.

## Project Structure

- `src/mcp_vault/__init__.py` - Package entry point
- `src/mcp_vault/server.py` - MCP server with tool registration and handlers
- `src/mcp_vault/tools.py` - Tool definitions using `ToolHandler` base class
- `src/mcp_vault/implementation.py` - Markdown parsing and heading analysis logic

## Contributing Guidelines

### Adding a New Tool

1. Create a new class in `tools.py` that extends `ToolHandler`
2. Implement `get_tool_description()` to return MCP `Tool` object with JSON schema
3. Implement `run_tool(args: dict)` with the tool's logic
4. Register the tool in `register_tools()` function by adding it to the returned dictionary

Example pattern:
```python
class MyNewTool(ToolHandler):
    def get_tool_description(self) -> Tool:
        return Tool(name="my_tool", ...)

    async def run_tool(self, args: dict) -> list[TextContent]:
        # Implementation here
        pass
```

### Code Conventions

- All server operations use async/await
- Tools return `list[TextContent]` from MCP types
- File paths in arguments are relative to vault root
- Use the ToolHandler pattern for consistency

## Runtime Requirements

- **Python >=3.13**: Required for modern type hints and async features
- **Environment Variable**: `VAULT_PATH` must be set to absolute path of Obsidian vault
- **External Dependencies**:
  - Obsidian Local REST API plugin (custom fork) running on localhost:27124
  - API token read from `.obsidian/plugins/obsidian-local-rest-api/data.json`
  - See README for details on the required fork for move_file functionality

## Testing

**TODO**: No tests currently exist. Once test files are added or the testing TODO in README is addressed, update this section with:
- Testing approach and framework
- How to run tests
- Any special considerations for testing MCP tools

*User: Please review this section after implementing tests.*

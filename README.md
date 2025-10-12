# mcp-vault

A Model Context Protocol (MCP) server for interacting with Obsidian vaults. This server provides tools that allow AI assistants to perform operations on your Obsidian vault through the MCP protocol.

## Overview

`mcp-vault` bridges AI assistants (like Claude) with your Obsidian vault, enabling them to:
- Move and rename files within your vault
- Extract and analyze markdown heading structures
- Navigate heading hierarchies with parent chain resolution

The server communicates with Obsidian through the [Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) for file operations, and directly reads markdown files for heading analysis.

### Details

For the `move_file` functionality, I'm relying on a fork of the plugin (from an open PR) which implements the MOVE functionality. See below:
- The discussion: https://github.com/coddingtonbear/obsidian-local-rest-api/discussions/190
- The 'solution' (open PR): https://github.com/coddingtonbear/obsidian-local-rest-api/pull/191
- The custom impl (base of the PR): https://github.com/mairas/obsidian-local-rest-api/tree/move-only

To properly use this MCP server as a whole (for now), you need to clone, compile and use the 'move-only' branch of the fork.
See [USAGE](./USAGE.md) for more details.

Note that the heading operations that support mcp-obsidian's patch_content tool work without this custom modification.

## Prerequisites

- Python >=3.13
- [uv](https://github.com/astral-sh/uv) for dependency management
- Obsidian with the [Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) installed and configured
- The Local REST API plugin must be running on `localhost:27124`

## Installation

```bash
# Clone the repository
git clone https://github.com/phate45/mcp-vault
cd mcp-vault

# Install dependencies
uv sync
```

## Configuration

Example from Claude Code's `~/.claude.json`:
```json
	"mcpServers": {
      "mcp-vault": {
        "type": "stdio",
        "command": "uv",
        "args": [
          "run",
          "--directory",
          "/home/user/Projects/mcp-vault",
          "mcp-vault"
        ],
        "env": {
          "VAULT_PATH": "/home/user/Documents/vault/"
        }
      }
    },
```

Can be added with the `claude mcp add` as such:
```bash
claude mcp add --transport stdio mcp-vault \
    --env VAULT_PATH="/home/user/Documents/vault/"
    -- uv run --directory "/home/user/Projects/mcp-vault" mcp-vault
```

## Available Tools

### move_file
Move or rename a file within your vault using the Obsidian Local REST API.

**Arguments:**
- `from_path` (string): Source file path (relative to vault root)
- `to_path` (string): Destination file path (relative to vault root)

**Usage:**
If you move vault files around outside of Obsidian, the backlinks won't be properly updated. This calls Obsidian api directly to make sure everything is updated.

### list_headings
Extract all markdown headings from a file.

**Arguments:**
- `file_path` (string): Path to the markdown file (relative to vault root)

**Returns:** List of headings with their levels (e.g., `## Heading Name`)

**Usage:**
Enable the agent to quickly skim the file structure without having to read the whole file into context.

### nail_heading
Get the full parent chain for a specific heading, useful for creating unambiguous heading references.

**Arguments:**
- `file_path` (string): Path to the markdown file (relative to vault root)
- `heading` (string): The heading title to find

**Returns:** Parent chain in the format `Parent::Child::Target` (returns just the heading name if it has no parents)

**Usage:**
Create the proper 'target' string for the mcp-obsidian's `obsidian_patch_content` function.

## Development

```bash
# Run the server
VAULT_PATH=<path> uv run mcp-vault
```
However, i would recommend to simply add the server to Claude or Codex and test it 'live' with the model using the MCP tool calls directly. The 'bare' stdio interface isn't very user friendly for direct testing.

### Disclaimer
Parts of the project were written by Claude Code. Nothing went into it that i did not personally review, though.
The AI was used mostly to provide quick feedback/second pair of eyes, and, of course, for testing the server itself.

### Open TODOs

- [ ] Add more detailed documentation regarding the usage (custom compiled version of the plugin, etc)
- [ ] Add proper testing (perhaps some github workflows?)
- [ ] Troubleshooting issues? (suppose i'll wait until someone reports an issue or i run into one myself)
- [ ] Create a a proper CHANGELOG (in case of continued development)
- [ ] Badges/screenshots/roadmap/other nice-to-haves

## Inspiration

This project wouldn't be possible if several others didn't exist:
- Claudesidian - The origin of the desire to integrate and automate: https://github.com/heyitsnoah/claudesidian
- mcp-obsidian - The integration that inspired me to fix what was 'missing': https://github.com/MarkusPfundstein/mcp-obsidian
- obsidian-local-rest-api plugin - The great enabler: https://github.com/coddingtonbear/obsidian-local-rest-api

## License

MIT - Use this however you want. Make it your own.


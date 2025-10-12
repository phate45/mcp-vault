# mcp-vault Usage Guide

## Prerequisites

Before you can use the `move_file` tool, you need to compile and install a custom version of the Obsidian Local REST API plugin that includes MOVE support.

> ⚠️ **Why the custom build?** The official `obsidian-local-rest-api` plugin doesn't currently support the MOVE HTTP method needed for file operations with automatic backlink updates. We're using a fork that implements this functionality from [PR #191](https://github.com/coddingtonbear/obsidian-local-rest-api/pull/191).

Below, I documented the process I went through to get it running in my Obsidian instance.

## Step 1: Install Build Dependencies

### Node.js via nvm (recommended)

```bash
# Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Reload your shell or source the nvm script
source ~/.bashrc

# Install the latest LTS version of Node.js
nvm install --lts
nvm use --lts

# Verify installation
node -v
```

### pnpm (package manager) (optional, but future steps reference it)

```bash
# Install pnpm globally
npm install -g pnpm

# Verify installation
pnpm -v
```

## Step 2: Clone and Build the Custom Plugin

```bash
# Navigate to a directory for the build (e.g., ~/Projects)
cd ~/Projects

# Clone the fork with MOVE support
git clone --branch move-only https://github.com/mairas/obsidian-local-rest-api.git && cd obsidian-local-rest-api

# Install dependencies
pnpm install

# Approve any build scripts (if prompted, i was)
pnpm approve-builds

# Add required dependencies (if not already present)
# I discovered this by running `pnpm run build` first, and said build failing on these two libraries
pnpm add body-parser moment
pnpm add -D @types/body-parser @types/moment

# Build the plugin
pnpm run build
```

After the build completes, you'll find `main.js` in the root of the repository.

### Optional: Build Documentation

If you want to generate the OpenAPI documentation:

```bash
# Install jsonnet (Debian/Ubuntu)
sudo apt install jsonnet

# Build the docs
pnpm run build-docs
```

The `openapi.yaml` file will be generated in the `docs/` directory.

The yaml file is already present, as it was generated and commited on the branch as is, but you can build it for yourself with the `jsonnet` addition for verification (or in case you hack on it).

## Step 3: Install the Custom Plugin in Obsidian

### Locate Your Obsidian Vault Plugin Directory

Your vault's plugin directory is typically:
```
<vault-path>/.obsidian/plugins/obsidian-local-rest-api/
```

### Replace the Plugin Files
Note: This should be done with Obsidian not running.

```bash
# Backup the original (if you have the official plugin installed)
cp <vault-path>/.obsidian/plugins/obsidian-local-rest-api/main.js \
   <vault-path>/.obsidian/plugins/obsidian-local-rest-api/main.js.backup

# Copy the compiled main.js to your vault's plugin directory
cp ~/Projects/obsidian-local-rest-api/main.js \
   <vault-path>/.obsidian/plugins/obsidian-local-rest-api/main.js
```

### Install from scratch (if plugin not already installed)

If you don't have the Local REST API plugin installed yet:

1. Install the plugin through the Community plugin browser
2. Run the 'backup & replace' operation from the previous code block

## Step 4: Configure the Plugin in Obsidian

1. Go to **Settings → Community Plugins**
2. Enable "Local REST API" if it's not already enabled
3. Click the gear icon next to the plugin to configure:
   - Set up API authentication (API key/token)
   - Verify the port (default: 27124)
   - Enable HTTPS if desired

## Step 5: Configure mcp-vault

Set up the environment variable pointing to your vault (optional if you give it explicitly to claude):

```bash
# Add to your shell RC file (~/.bashrc, ~/.zshrc, etc.)
export VAULT_PATH="/path/to/your/vault/"
```

### Claude Code Configuration

Add to your `~/.claude.json`:

```json
{
  "mcpServers": {
    "mcp-vault": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-vault",
        "mcp-vault"
      ],
      "env": {
        "VAULT_PATH": "/path/to/your/vault/"
      }
    }
  }
}
```

Or use the `claude mcp add` command:

```bash
claude mcp add --transport stdio mcp-vault \
    --env VAULT_PATH="/path/to/your/vault/" \
    -- uv run --directory "/path/to/mcp-vault" mcp-vault
```

## Verification

### Test the REST API MOVE Endpoint

Create a test file in your vault and try moving it:

```bash
# Example using curl
curl -k -X MOVE \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Destination: new-path.md" \
  "https://localhost:27124/vault/old-path.md"
```

Expected response:
```json
{
  "message": "File successfully moved",
  "oldPath": "old-path.md",
  "newPath": "new-path.md"
}
```

### Test mcp-vault Integration

In Claude Code, test the integration:

```
Use mcp-vault to move the file "test.md" to "archive/test.md"
```

If successful, the file will be moved and all backlinks will be automatically updated.

## Troubleshooting

### Build Fails

- **Missing dependencies:** Ensure Node.js and pnpm are properly installed
- **Permission errors:** Check file permissions in the build directory

### MOVE Endpoint Not Working

- Verify the custom build was copied correctly
- Check that the plugin is enabled in Obsidian settings
- Ensure the REST API is running (check Settings → Local REST API)
- Verify your API token is correct

### mcp-vault Can't Connect

- Check `VAULT_PATH` environment variable is set correctly
- Verify the REST API is running on the expected port

## Known Limitations

- **Custom build required:** Until PR #191 is merged upstream, you must maintain this custom build
- **SSL verification disabled:** The MCP server disables SSL verification for localhost connections with self-signed certificates
- **Manual updates:** Plugin updates will require rebuilding from the fork

## Future Plans

Once the MOVE functionality is merged into the official plugin, this custom build process will no longer be necessary. Monitor:
- [PR #191](https://github.com/coddingtonbear/obsidian-local-rest-api/pull/191) for merge status
- The official plugin for release notes

## Support

If you encounter issues:
1. Check the [mcp-vault issues](https://github.com/phate45/mcp-vault/issues)
2. Review the [REST API plugin discussion](https://github.com/coddingtonbear/obsidian-local-rest-api/discussions/190)
3. Verify your setup matches this guide

## References

- **Discussion:** https://github.com/coddingtonbear/obsidian-local-rest-api/discussions/190
- **PR with MOVE support:** https://github.com/coddingtonbear/obsidian-local-rest-api/pull/191
- **Fork repository:** https://github.com/mairas/obsidian-local-rest-api/tree/move-only
- **Original plugin:** https://github.com/coddingtonbear/obsidian-local-rest-api

# NotebookLM MCP Server Setup Guide

There is no official public API for NotebookLM yet, but the community has created a robust MCP server that bridges this gap.

## 📦 The Package
**Package:** `@roomi-fields/notebooklm-mcp`
**Repository:** [github.com/roomi-fields/notebooklm-mcp](https://github.com/roomi-fields/notebooklm-mcp)

This MCP server allows an AI agent to:
- Create notebooks
- Upload sources (URLs, Text, YouTube)
- Generate audio overviews
- Query your notebooks

## 🚀 How to Install

### Option 1: Claude Desktop (Recommended)

To give me (or any agent running in Claude Desktop) access to this tool, add the following to your configuration file:

**Config Path:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "npx",
      "args": [
        "-y",
        "@roomi-fields/notebooklm-mcp"
      ]
    }
  }
}
```

> **Note:** You may need to restart Claude Desktop after saving this file.

### Option 2: Command Line / Generic MCP Client

If you are using a different MCP client, the command to run the server is:

```bash
npx -y @roomi-fields/notebooklm-mcp
```

## ⚠️ Important Considerations

1.  **Authentication:** This tool generally uses your existing Google login session from your browser (Chrome/Edge). It automates the interaction. You may need to be logged into NotebookLM in your default browser.
2.  **Unofficial:** This is a community maintained project. If Google changes their internal API or UI, this tool might break until updated.
3.  **Privacy:** As with any community tool, review the code if dealing with highly sensitive data. The code acts as a proxy between the MCP protocol and the NotebookLM web interface.

## 🔄 Verification

Once installed and restarted:
1.  Ask me: "List my notebooks in NotebookLM"
2.  Ask me: "Create a new notebook called 'Blackglass Research'"
3.  Ask me: "Add [URL] to my notebook"

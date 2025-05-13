# MCP Installation Guide

This document explains how to install the MCP (Model Context Protocol) package required for enabling full connectivity between AI Dev Toolkit and Claude Desktop.

## What is MCP?

MCP (Model Context Protocol) is the protocol used by Claude Desktop to communicate with external tools and servers. It allows AI Dev Toolkit to provide file indexing, tool reference, and task management capabilities to Claude Desktop.

## Installation Options

There are two ways to run the AI Dev Toolkit server:

1. **Limited Functionality Mode** (No MCP): File indexing and task management work, but Claude Desktop cannot connect.
2. **Full Functionality Mode** (With MCP): Complete integration with Claude Desktop.

## Installing MCP

We've provided a script to make the MCP installation process easier:

```bash
# Regular installation (using system Python)
python scripts/install_mcp_dependencies.py

# Or, create a virtual environment (recommended)
python scripts/install_mcp_dependencies.py --venv
```

If you choose the virtual environment option, you'll need to activate it before running the server:

**Windows:**
```
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```
source .venv/bin/activate
```

## Running the Server

After installing MCP, you can run the server with:

```bash
python development/launch_librarian.py [directories...]
```

Replace `[directories...]` with the paths to the directories you want to monitor.

## Verifying Claude Desktop Connection

Once the server is running, you can verify the connection with Claude Desktop:

1. Open Claude Desktop
2. Go to Settings > Developer
3. Verify that "ai-librarian" appears in the list of MCP servers
4. The status should be "Connected"

## Troubleshooting

If you encounter issues:

1. **Error: No module named 'mcp'**: The MCP package is not installed. Run the installation script.
2. **Server runs but Claude Desktop doesn't connect**: Check the Claude Desktop configuration file in:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`
3. **Connection refused errors**: Make sure no other instances of the server are running.

## Manual MCP Installation

If the script doesn't work, you can install MCP manually:

```bash
pip install mcp[cli]
```

This installs the MCP package with CLI support, which is required for the server to run properly.
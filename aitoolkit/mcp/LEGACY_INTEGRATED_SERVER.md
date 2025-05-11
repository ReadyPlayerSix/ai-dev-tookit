# Legacy Integrated Server

## Deprecation Notice

The file `integrated_server.py` in this directory is deprecated and should not be used for new installations or development. It is kept for reference purposes only.

## Current Architecture

The current MCP server implementation is located at:
`aitoolkit/librarian/server.py`

This is the only server that should be used with Claude.

## Historical Context

The integrated server was an earlier attempt to combine the AI Librarian and file system functionality into a single server. This approach was later abandoned in favor of a unified server implementation that was more robust and maintainable.

Key reasons for the change:
1. Simplified architecture with fewer moving parts
2. Improved stability and error handling
3. Better performance
4. Clearer integration with Claude Desktop
5. More maintainable codebase

## Installation

The current installation script is located at:
`development/install_to_claude.py`

This script installs the correct server (server.py) to Claude Desktop.

## Related Files

Several related legacy files exist in the `legacy/` directory:
- `install_integrated_server.py`
- `install_unified_server.py`
- Other deprecated installation scripts

Created: May 11, 2025
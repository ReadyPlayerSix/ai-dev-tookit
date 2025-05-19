#!/bin/bash
# Git commands to commit the timeout fixes

# Add all the modified files
git add .tool_reference/README.md
git add .tool_reference/categories.json
git add .tool_reference/registry.json
git add .tool_reference/relationships.json
git add aitoolkit/librarian/task_board.py
git add aitoolkit/librarian/unified_context_integration.py
git add config/mcp_timeout_config.json
git add docs/timeout-prevention-guide.md

# Add all the new files
git add aitoolkit/utils/resource_monitor.py
git add claude_desktop_config.json
git add scripts/diagnose_timeout.py
git add scripts/disable_problematic_modules.py
git add scripts/fix_timeout_minimal.py
git add scripts/fix_timeouts.py
git add scripts/start_server_safe.py

# Optional: add the test file if you want to keep it
# git add test_server_start.py

# Create the commit
git commit -m "Fix critical MCP server timeout issues preventing Claude Desktop connection

- Fixed syntax errors in task_board.py causing server startup failure
- Reduced background thread activity (workers from 4 to 1, disabled context updates)
- Increased MCP timeout values (30s to 5min default, 10min for file operations)
- Added diagnostic and emergency fix scripts for timeout issues
- Created comprehensive timeout prevention documentation
- Improved thread management with proper cleanup and non-daemon threads

This resolves the connection timeout issues that prevented the AI Librarian 
server from working with Claude Desktop after ~3 tool uses."

# Push to origin
git push origin main
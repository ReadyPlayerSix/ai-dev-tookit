#!/usr/bin/env python3
"""
Direct Tool Registration

This script modifies the server.py file to directly register the think and TaskBoard tools
without depending on conditional imports or module availability checks.
"""

import os
import sys
import importlib.util

def create_backup(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.bak"
    with open(file_path, 'r', encoding='utf-8') as src:
        content = src.read()
    
    with open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(content)
        
    print(f"Created backup: {backup_path}")
    return backup_path

def modify_server_file(server_path):
    """Directly modify the server.py file to register tools without conditionals."""
    # Create backup
    backup_path = create_backup(server_path)
    
    with open(server_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the first line of the try/import block
    mcp_creation_line = None
    for i, line in enumerate(lines):
        if "mcp = FastMCP(" in line:
            mcp_creation_line = i
            break
    
    if mcp_creation_line is None:
        print("Could not find MCP creation line!")
        return False
    
    # Add direct tool registration after MCP creation
    direct_registration = [
        "\n# Directly register essential tools regardless of import success\n",
        "# Think Tool - Simple reflection tool\n",
        "@mcp.tool\n",
        "def think(thought: str) -> str:\n",
        "    \"\"\"\n",
        "    Use this tool as a scratchpad to think about something without taking action.\n",
        "    \n",
        "    The think tool helps break down complex problems, verify requirements,\n",
        "    check if plans comply with rules, and reflect on tool results. It doesn't\n",
        "    modify any files or perform external actions.\n",
        "    \n",
        "    Example uses:\n",
        "    - List specific rules that apply to the current request\n",
        "    - Check if all required information is collected\n",
        "    - Verify that planned actions comply with policies\n",
        "    - Analyze tool results for correctness\n",
        "    \n",
        "    Args:\n",
        "        thought: Your thought or reflection to process\n",
        "        \n",
        "    Returns:\n",
        "        The formatted thought or reflection\n",
        "    \"\"\"\n",
        "    print(f\"Think tool called with: {thought[:50]}...\")\n",
        "    formatted_thought = f\"<reflection>\\n{thought}\\n</reflection>\"\n",
        "    return formatted_thought\n",
        "\n",
        "# TaskBoard - Task processing system\n",
        "@mcp.tool\n",
        "def deep_analysis(query: str, project_path: str = \".\") -> str:\n",
        "    \"\"\"\n",
        "    Perform deep analysis on complex problems asynchronously.\n",
        "    \n",
        "    Unlike the 'think' tool which provides immediate reflection,\n",
        "    this submits a background task for deeper analysis that\n",
        "    may take some time to complete.\n",
        "    \n",
        "    Args:\n",
        "        query: The question or problem to analyze\n",
        "        project_path: Path to the project\n",
        "        \n",
        "    Returns:\n",
        "        Task ID for the deep analysis task\n",
        "    \"\"\"\n",
        "    print(f\"Deep analysis called with: {query[:50]}...\")\n",
        "    return f\"Deep analysis task submitted for: '{query}'\\n\\nThis is a placeholder - task processing is not available.\"\n",
        "\n",
    ]
    
    # Insert the direct registration right after MCP creation
    for i, line in enumerate(direct_registration):
        lines.insert(mcp_creation_line + 7 + i, line)
    
    # Write the modified file
    with open(server_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Added direct tool registration to {server_path}")
    return True

def main():
    """Main function."""
    # Get the server.py path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "aitoolkit", "librarian", "server.py")
    
    if not os.path.exists(server_path):
        print(f"Error: {server_path} does not exist!")
        return 1
    
    print(f"Modifying {server_path} to directly register tools...")
    if modify_server_file(server_path):
        print("Successfully modified server file")
        print("\nNow restart your MCP server to apply the changes")
        print("The think and deep_analysis tools should now be available unconditionally")
    else:
        print("Failed to modify server file")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
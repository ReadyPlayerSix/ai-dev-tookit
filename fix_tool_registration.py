#!/usr/bin/env python3
"""
Fix Tool Registration

This script updates server.py to ensure the think tool and TaskBoard tools
are properly registered with the MCP system.
"""

import os
import sys
import re

def find_think_tool_registration(server_path):
    """Find the think tool registration code in server.py"""
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if the think tool is registered
    think_tool_pattern = r'@mcp\.tool\(\)[^@]*def think\('
    think_matches = re.findall(think_tool_pattern, content, re.DOTALL)
    
    return bool(think_matches)

def fix_think_tool_registration(server_path):
    """Fix the think tool registration"""
    with open(server_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the TASKBOARD_AVAILABLE section
    taskboard_section_start = None
    taskboard_tools_start = None
    for i, line in enumerate(lines):
        if "# Register TaskBoard tools if available" in line:
            taskboard_section_start = i
        elif taskboard_section_start and "print(\"Registering TaskBoard tools...\")" in line:
            taskboard_tools_start = i
    
    if not taskboard_tools_start:
        print("Could not find the TaskBoard tools registration section")
        return False
    
    # Check if the think tool is already defined
    think_tool_exists = False
    for i in range(taskboard_tools_start, len(lines)):
        if "@mcp.tool()" in lines[i] and "def think(" in lines[i+1]:
            think_tool_exists = True
            break
    
    if think_tool_exists:
        print("think tool already defined")
        # Force the import to use the standalone version
        for i in range(taskboard_tools_start, len(lines)):
            if "def think(" in lines[i] and "try:" in lines[i+1]:
                j = i + 2
                lines[j] = "            from aitoolkit.librarian.think_tool import think as standalone_think\n"
                
                # Add extra debugging
                lines.insert(j+1, "            print(\"Successfully imported standalone think tool\")\n")
                
                with open(server_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                    
                print("Updated think tool to use explicit import path")
                return True
    else:
        # Add the think tool definition
        insert_pos = taskboard_tools_start + 2
        
        think_tool_code = [
            "    @mcp.tool()\n",
            "    def think(thought: str) -> str:\n",
            "        \"\"\"\n",
            "        Use this tool as a scratchpad to think about something without taking action.\n",
            "        \n",
            "        The think tool helps break down complex problems, verify requirements,\n",
            "        check if plans comply with rules, and reflect on tool results. It doesn't\n",
            "        modify any files or perform external actions.\n",
            "        \n",
            "        Example uses:\n",
            "        - List specific rules that apply to the current request\n",
            "        - Check if all required information is collected\n",
            "        - Verify that planned actions comply with policies\n",
            "        - Analyze tool results for correctness\n",
            "        \n",
            "        Args:\n",
            "            thought: Your thought or reflection to process\n",
            "            \n",
            "        Returns:\n",
            "            The formatted thought or reflection\n",
            "        \"\"\"\n",
            "        try:\n",
            "            print(\"Importing standalone think tool\")\n",
            "            from aitoolkit.librarian.think_tool import think as standalone_think\n",
            "            print(\"Successfully imported standalone think tool\")\n",
            "            return standalone_think(thought)\n",
            "        except ImportError as e:\n",
            "            print(f\"Error importing think_tool: {e}\")\n",
            "            # Fallback implementation if the module isn't available\n",
            "            return f\"<reflection>\\n{thought}\\n</reflection>\"\n",
            "    \n"
        ]
        
        lines[insert_pos:insert_pos] = think_tool_code
        
        with open(server_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print("Added think tool definition")
        return True
        
    return False

def check_taskboard_availability(server_path):
    """Check if TASKBOARD_AVAILABLE is set correctly"""
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if TASKBOARD_AVAILABLE is being set
    availability_pattern = r'TASKBOARD_AVAILABLE\s*=\s*True'
    matches = re.findall(availability_pattern, content)
    
    return bool(matches)

def main():
    """Main function"""
    # Get the repository root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "aitoolkit/librarian/server.py")
    
    print(f"Checking server.py at {server_path}")
    
    # Check if file exists
    if not os.path.exists(server_path):
        print(f"Error: {server_path} does not exist!")
        return 1
    
    # Check if TaskBoard is properly available
    taskboard_available = check_taskboard_availability(server_path)
    print(f"TaskBoard availability: {taskboard_available}")
    
    # Check if think tool is registered
    think_registered = find_think_tool_registration(server_path)
    print(f"Think tool registration: {think_registered}")
    
    # Fix think tool registration if needed
    if not think_registered:
        print("Fixing think tool registration...")
        if fix_think_tool_registration(server_path):
            print("Successfully fixed think tool registration")
        else:
            print("Failed to fix think tool registration")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
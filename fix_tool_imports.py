#!/usr/bin/env python3
"""
Fix Think Tool and TaskBoard Imports
This script ensures that server.py can properly find the required
modules after the project files were cleaned up.
"""

import os
import sys

def check_imports():
    """Test importing key modules to verify they are available"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to the path to ensure imports work
    sys.path.insert(0, script_dir)
    
    print("Testing imports...")
    
    try:
        from aitoolkit.librarian.think_tool import think
        print("✅ Successfully imported think_tool.think")
    except ImportError as e:
        print(f"❌ Error importing think_tool.think: {e}")
    
    try:
        from aitoolkit.librarian.task_board import task_deep_analysis
        print("✅ Successfully imported task_board.task_deep_analysis")
    except ImportError as e:
        print(f"❌ Error importing task_board.task_deep_analysis: {e}")
    
    try:
        from aitoolkit.librarian.task_board import submit_background_task
        print("✅ Successfully imported task_board.submit_background_task")
    except ImportError as e:
        print(f"❌ Error importing task_board.submit_background_task: {e}")

def main():
    # Check imports
    check_imports()
    
    # Server path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "aitoolkit", "librarian", "server.py")
    
    print(f"\nServer path: {server_path}")
    if os.path.exists(server_path):
        print("✅ Server file exists")
    else:
        print("❌ Server file not found!")
        return 1
    
    # Create a simple test script that can be run to verify the tool registration
    test_script_path = os.path.join(script_dir, "test_tool_registration.py")
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
'''
Test Tool Registration
This script tests that all the required tools are properly registered with the MCP server.
'''

import os
import sys
import importlib

# Add the parent directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # First, try to import the server module to see all registered tools
        from aitoolkit.librarian.server import mcp
        print("Successfully imported server.mcp")
        
        # Get all registered tools
        tools = mcp._tools if hasattr(mcp, '_tools') else []
        print(f"\\nRegistered MCP tools: {len(tools)}")
        
        # Check for specific tools
        has_think = False
        has_deep_analysis = False
        has_taskboard = False
        
        for tool_name in [t.__name__ for t in tools]:
            print(f"- {tool_name}")
            if tool_name == "think":
                has_think = True
            elif tool_name == "deep_analysis":
                has_deep_analysis = True
            elif tool_name in ["submit_background_task", "get_task_status", "get_task_result"]:
                has_taskboard = True
        
        print("\\nTool status:")
        print(f"Think tool: {'✅ Present' if has_think else '❌ Missing'}")
        print(f"Deep analysis: {'✅ Present' if has_deep_analysis else '❌ Missing'}")
        print(f"TaskBoard tools: {'✅ Present' if has_taskboard else '❌ Missing'}")
        
        # Try to import and use the think tool directly
        try:
            from aitoolkit.librarian.think_tool import think
            result = think("This is a test thought")
            print("\\nDirect think tool test: ✅ Success")
            print(f"Result: {result[:50]}...")
        except Exception as e:
            print(f"\\nDirect think tool test: ❌ Failed - {e}")
        
        # Try to import and use task_deep_analysis directly
        try:
            from aitoolkit.librarian.task_board import task_deep_analysis
            print("\\nDirect task_deep_analysis import: ✅ Success")
        except Exception as e:
            print(f"\\nDirect task_deep_analysis import: ❌ Failed - {e}")
        
    except ImportError as e:
        print(f"Error importing server module: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")
    
    print(f"\n✅ Created test script at {test_script_path}")
    print("Run the test script to verify tool registration:")
    print(f"python3 {test_script_path}")
    
    # Make the test script executable
    os.chmod(test_script_path, 0o755)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
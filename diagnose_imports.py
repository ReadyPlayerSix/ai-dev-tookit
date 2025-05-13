#!/usr/bin/env python3
"""
Diagnose import issues specifically with TaskBoard and think tool registration.
This script attempts to import each module in isolation to identify where the problem is.
"""

import os
import sys
import traceback

def try_import(module_name, from_module=None):
    """Try to import a module and print the result."""
    try:
        if from_module:
            print(f"Attempting to import {module_name} from {from_module}...")
            exec(f"from {from_module} import {module_name}")
            print(f"✅ Successfully imported {module_name} from {from_module}")
        else:
            print(f"Attempting to import {module_name}...")
            exec(f"import {module_name}")
            print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        traceback.print_exc()
        return False

def main():
    # Add the current directory to the path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    print("Python path:")
    for path in sys.path:
        print(f"- {path}")
    print()
    
    # First check aitoolkit
    try_import("aitoolkit")
    
    # Check main modules
    try_import("aitoolkit.librarian.server")
    try_import("aitoolkit.librarian.task_board")
    try_import("aitoolkit.librarian.think_tool")
    
    # Check TaskBoard-related modules
    try_import("aitoolkit.librarian.taskboard_integration")
    try_import("aitoolkit.librarian.server_taskboard_integration")
    try_import("apply_taskboard_integration", "aitoolkit.librarian.server_taskboard_integration")
    
    # Try to import the functions directly
    try_import("think", "aitoolkit.librarian.think_tool")
    try_import("task_deep_analysis", "aitoolkit.librarian.task_board")
    try_import("submit_background_task", "aitoolkit.librarian.task_board")
    
    # Try to reconstruct the import chain that happens in server.py
    print("\nAttempting to replicate server.py import chain:")
    try:
        print("Importing dependencies...")
        from aitoolkit.librarian.server_taskboard_integration import apply_taskboard_integration
        print("✅ Imported apply_taskboard_integration")
        
        from aitoolkit.librarian.task_board import (
            submit_background_task,
            get_task_status_mcp,
            get_task_result_mcp,
            cancel_task_mcp,
            list_tasks_mcp
        )
        print("✅ Imported TaskBoard functions")
        
        # Check if think_task is available
        try:
            from aitoolkit.librarian.task_board import think as think_task
            print("✅ Imported think as think_task")
        except ImportError as e:
            print(f"❌ Error importing think as think_task: {e}")
        
        # This should be set to True if imports succeed
        print("✅ TASKBOARD_AVAILABLE would be set to True")
        
        # Try think_tool import
        try:
            from aitoolkit.librarian.think_tool import think as standalone_think
            print("✅ Imported standalone think function")
        except ImportError as e:
            print(f"❌ Error importing standalone think: {e}")
        
    except ImportError as e:
        print(f"❌ Error in import chain: {e}")
        traceback.print_exc()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
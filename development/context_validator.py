#!/usr/bin/env python3
'''
Context Validator Tool

This script validates Claude's understanding of the project structure,
tool paths, and execution environment. It helps Claude correct its
internal context to match reality.

Usage:
    python context_validator.py --check [all|server|tools|structure]
'''

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def check_server_connection():
    '''Check which server implementation is active'''
    print("Checking server connection...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", "from aitoolkit.librarian.server import mcp; print('AI Librarian server is active')"],
            capture_output=True,
            text=True
        )
        if "AI Librarian server is active" in result.stdout:
            print("✅ Connected to AI Librarian server (librarian/server.py)")
            return True
        else:
            print("❌ Not connected to AI Librarian server")
            return False
    except Exception as e:
        print(f"❌ Error checking server connection: {str(e)}")
        return False

def check_tool_paths():
    '''Check if tools are properly registered and accessible'''
    print("Checking tool paths...")
    tools_to_check = [
        "initialize_librarian",
        "query_component",
        "find_implementation"
    ]
    
    success_count = 0
    for tool in tools_to_check:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"from aitoolkit.librarian.server import {tool}; print('{tool} is available')"],
                capture_output=True,
                text=True
            )
            if f"{tool} is available" in result.stdout:
                print(f"✅ {tool} is properly registered and available")
                success_count += 1
            else:
                print(f"❌ {tool} is not properly registered")
        except Exception as e:
            print(f"❌ Error checking {tool}: {str(e)}")
    
    return success_count == len(tools_to_check)

def check_project_structure():
    '''Check if the project structure matches expectations'''
    print("Checking project structure...")
    
    expected_paths = [
        "aitoolkit/librarian/server.py",
        "aitoolkit/librarian/filesystem.py",
        "aitoolkit/librarian/enhanced_indexer.py",
        "aitoolkit/librarian/todos.py"
    ]
    
    success_count = 0
    for path in expected_paths:
        if os.path.exists(path):
            print(f"✅ {path} exists as expected")
            success_count += 1
        else:
            print(f"❌ {path} not found")
    
    return success_count == len(expected_paths)

def main():
    parser = argparse.ArgumentParser(description="Validate Claude's context understanding")
    parser.add_argument(
        "--check",
        choices=["all", "server", "tools", "structure"],
        default="all",
        help="What aspect of the context to check"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("                    Context Validator for Claude")
    print("=" * 80)
    print("")
    
    success = True
    
    if args.check in ["all", "server"]:
        server_success = check_server_connection()
        success = success and server_success
        print("")
    
    if args.check in ["all", "tools"]:
        tools_success = check_tool_paths()
        success = success and tools_success
        print("")
    
    if args.check in ["all", "structure"]:
        structure_success = check_project_structure()
        success = success and structure_success
        print("")
    
    # Print summary
    print("=" * 80)
    if success:
        print("✅ All checked aspects of Claude's context are valid")
    else:
        print("❌ Some context validation checks failed - Claude may need to update its understanding")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

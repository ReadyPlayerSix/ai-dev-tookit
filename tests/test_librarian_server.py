#!/usr/bin/env python3
"""
Test script for the AI Librarian MCP server

This script tests if the AI Librarian MCP server is correctly initialized
and can perform basic operations.
"""

import os
import sys
import subprocess
import time
import importlib.util

def check_mcp_installed():
    """Check if the MCP package is installed."""
    if importlib.util.find_spec("mcp") is None:
        print("MCP package is not installed. Please run:")
        print("pip install 'mcp[cli]>=0.1.5'")
        sys.exit(1)
    print("✅ MCP package is installed")

def check_server_script():
    """Check if the server script exists."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "aitoolkit", "librarian", "server.py")
    
    if not os.path.exists(server_path):
        print(f"❌ Server script not found at {server_path}")
        sys.exit(1)
    print(f"✅ Server script found at {server_path}")

def test_run_server():
    """Test if the server can start."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_path = os.path.join(script_dir, "run_librarian_server.py")
    test_dir = os.path.join(script_dir, "test_directory")
    
    # Create a test directory if it doesn't exist
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        
    # Create a simple Python file in the test directory
    test_file = os.path.join(test_dir, "test_file.py")
    with open(test_file, 'w') as f:
        f.write("""
def hello_world():
    \"\"\"A simple test function.\"\"\"
    return "Hello, World!"
    
class TestClass:
    \"\"\"A simple test class.\"\"\"
    def method(self):
        return "Hello from TestClass!"
""")
    
    # Start the server in a separate process
    print("Starting server for testing (will terminate after 5 seconds)...")
    process = subprocess.Popen(
        [sys.executable, launcher_path, test_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for the server to start
    time.sleep(5)
    
    # Check if the process is still running (successful startup)
    if process.poll() is None:
        print("✅ Server started successfully!")
        
        # Check if the .ai_reference directory was created
        ai_ref_path = os.path.join(test_dir, ".ai_reference")
        if os.path.exists(ai_ref_path):
            print(f"✅ AI reference directory created at {ai_ref_path}")
        else:
            print(f"❌ AI reference directory not created at {ai_ref_path}")
        
        # Now terminate the server
        process.terminate()
        process.wait(timeout=5)
        print("Server terminated after test.")
    else:
        stdout, stderr = process.communicate()
        print("❌ Server failed to start properly!")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
def main():
    """Run all tests."""
    print("=== Testing AI Librarian MCP Server ===")
    check_mcp_installed()
    check_server_script()
    test_run_server()
    print("=== Tests completed ===")

if __name__ == "__main__":
    main()

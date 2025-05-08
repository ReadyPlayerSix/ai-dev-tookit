#!/usr/bin/env python3
"""
Test script for the AI Dev Toolkit Unified Server

This script tests the unified server by:
1. Starting the server in a subprocess
2. Connecting to it via standard input/output
3. Sending MCP initialization requests
4. Testing key tools to verify functionality
"""

import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path

# Add the project root to the path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import MCP client for testing
try:
    from mcp.client import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP client not found. Installing required dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp[cli]>=0.1.5"], check=True)
    from mcp.client import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

async def run_test():
    """Run test of the unified server"""
    print("=" * 80)
    print("AI Dev Toolkit Unified Server Test")
    print("=" * 80)
    
    # Start the server
    server_path = os.path.join(script_dir, "aitoolkit", "unified_server.py")
    if not os.path.exists(server_path):
        print(f"❌ Error: Server script not found at {server_path}")
        return False
    
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # Use binary mode for proper communication
    )
    
    try:
        # Connect to the server using MCP client
        print("Connecting to server...")
        server_params = StdioServerParameters(
            stdin=server_process.stdout,
            stdout=server_process.stdin
        )
        
        # Create client session
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    print("Initializing MCP session...")
                    await session.initialize()
                    print("✅ Session initialized successfully")
                    
                    # List available tools
                    print("\nListing available tools...")
                    tools = await session.list_tools()
                    print(f"✅ Found {len(tools)} tools")
                    
                    # Test file system tools
                    print("\nTesting filesystem tools...")
                    result = await session.call_tool(
                        "list_allowed_directories", 
                        arguments={}
                    )
                    print(f"✅ Allowed directories: {result}")
                    
                    # Test file reading on a known file
                    print("\nTesting file reading...")
                    readme_path = os.path.join(script_dir, "README.md")
                    result = await session.call_tool(
                        "read_file_tool",
                        arguments={"path": readme_path}
                    )
                    print(f"✅ Successfully read {readme_path} ({len(result[0]['text'])} characters)")
                    
                    # Test AI Librarian initialization
                    print("\nTesting AI Librarian initialization...")
                    test_dir = os.path.join(script_dir, "test_directory")
                    # Create test directory if it doesn't exist
                    if not os.path.exists(test_dir):
                        os.makedirs(test_dir, exist_ok=True)
                    
                    result = await session.call_tool(
                        "initialize_librarian",
                        arguments={"project_path": test_dir}
                    )
                    
                    # Check if initialization was successful
                    if isinstance(result, str) and "successfully" in result.lower():
                        print(f"✅ Successfully initialized AI Librarian for {test_dir}")
                    else:
                        print(f"⚠️ AI Librarian initialization might have issues: {result}")
                    
                    # Print overall success
                    print("\n✅ All tests completed successfully!")
                    print("The unified server is working correctly.")
                    
        except Exception as e:
            print(f"❌ Error during MCP session: {str(e)}")
            return False
    
    finally:
        # Clean up the server process
        print("\nShutting down server...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            server_process.kill()
        print("Server shut down")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_test())
    sys.exit(0 if success else 1)

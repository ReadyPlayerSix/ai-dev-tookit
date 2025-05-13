#!/usr/bin/env python3
"""
Diagnose MCP Tools

This script connects to the MCP API to discover which tools are actually registered
and available from the MCP server. It's a more direct way to see what tools Claude
Desktop would see.
"""

import os
import sys
import json
import socket
import time
import base64
import subprocess

def find_mcp_port():
    """Try to find the MCP server port by checking common locations."""
    # Common file locations for MCP port information
    possible_locations = [
        os.path.join(os.path.expanduser("~"), ".mcp", "server_info.json"),
        "/tmp/mcp_server_info.json",
        "/var/run/mcp_server_info.json",
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            try:
                with open(location, 'r') as f:
                    data = json.load(f)
                    if 'port' in data:
                        return data['port']
            except:
                pass
    
    # Try to find the port by checking running processes
    try:
        output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
        for line in output.split('\n'):
            if "mcp.server" in line or "FastMCP" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "--port" and i+1 < len(parts):
                        try:
                            return int(parts[i+1])
                        except:
                            pass
    except:
        pass
    
    # Default port for MCP
    return 9999

def query_mcp_api(port, path="/api/tools"):
    """Query the MCP API at the given port and path."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("localhost", port))
        
        # Send a GET request to the MCP API
        request = f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n"
        sock.send(request.encode('utf-8'))
        
        # Receive the response
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
        
        # Parse the response
        response_str = response.decode('utf-8')
        
        # Extract JSON payload (skip HTTP headers)
        json_start = response_str.find('{')
        if json_start == -1:
            return f"Invalid response format: {response_str[:100]}..."
        
        json_str = response_str[json_start:]
        return json.loads(json_str)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        sock.close()

def main():
    """Main function."""
    print("Diagnosing MCP tools...")
    print("-" * 50)
    
    # Find the MCP port
    port = find_mcp_port()
    print(f"Using MCP port: {port}")
    
    # Query the MCP API
    tools = query_mcp_api(port, "/api/tools")
    
    # Process the result
    if isinstance(tools, dict) and 'tools' in tools:
        tool_list = tools['tools']
        print(f"Found {len(tool_list)} tools registered with MCP:")
        for i, tool in enumerate(tool_list, 1):
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description').replace('\n', ' ')[:100]
            print(f"{i}. {name}: {description}")
            
        # Specifically check for think and TaskBoard tools
        think_tool = next((t for t in tool_list if t.get('name') == 'think'), None)
        deep_analysis = next((t for t in tool_list if t.get('name') == 'deep_analysis'), None)
        taskboard_tools = [t for t in tool_list if t.get('name') in [
            'submit_background_task', 'get_task_status', 'get_task_result', 'cancel_task', 'list_tasks'
        ]]
        
        print("\nSpecific Tools:")
        print(f"Think Tool: {'✅ Present' if think_tool else '❌ Missing'}")
        print(f"Deep Analysis: {'✅ Present' if deep_analysis else '❌ Missing'}")
        print(f"TaskBoard Tools: {'✅ Present' if taskboard_tools else '❌ Missing'}")
    else:
        print(f"Failed to retrieve tools: {tools}")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nDiagnosis interrupted by user")
        sys.exit(1)
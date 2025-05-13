#!/usr/bin/env python3
"""
Script to install MCP dependencies for AI Dev Toolkit.

This script helps set up the MCP package required for connecting
AI Dev Toolkit to Claude Desktop.
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

def install_mcp_package(use_venv=False):
    """
    Install the MCP package required for Claude Desktop connectivity.
    
    Args:
        use_venv: Whether to create and use a virtual environment
    """
    print("\n=== Installing MCP Dependencies ===\n")
    
    # Determine Python executable to use
    python_exe = sys.executable
    pip_cmd = [python_exe, "-m", "pip"]
    
    # Create virtual environment if requested
    venv_path = None
    if use_venv:
        venv_path = Path.cwd() / ".venv"
        print(f"Creating virtual environment at {venv_path}...")
        
        try:
            subprocess.run([python_exe, "-m", "venv", str(venv_path)], check=True)
            
            # Get the Python executable from the virtual environment
            if platform.system() == "Windows":
                python_exe = str(venv_path / "Scripts" / "python.exe")
                pip_cmd = [python_exe, "-m", "pip"]
            else:
                python_exe = str(venv_path / "bin" / "python")
                pip_cmd = [python_exe, "-m", "pip"]
            
            print(f"Virtual environment created successfully. Using {python_exe}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            print("Please install the python3-venv package:")
            if platform.system() == "Linux":
                print("    sudo apt install python3-venv")
            return False
    
    # Upgrade pip to latest version
    try:
        print("Upgrading pip...")
        subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading pip: {e}")
        print("Continuing with existing pip version...")
    
    # Install MCP package
    try:
        print("\nInstalling MCP package...")
        subprocess.run([*pip_cmd, "install", "mcp[cli]"], check=True)
        print("\n✅ MCP package installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing MCP package: {e}")
        return False
    
    # Verify installation
    try:
        print("\nVerifying MCP installation...")
        result = subprocess.run(
            [python_exe, "-c", "import mcp; print(f'MCP version: {mcp.__version__}')"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✅ MCP package verified!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error verifying MCP installation: {e}")
        if e.output:
            print(f"Output: {e.output}")
        return False
    
    # Create activation instructions
    if use_venv:
        print("\n=== Virtual Environment Activation ===\n")
        print("To activate the virtual environment, use:")
        if platform.system() == "Windows":
            print(f"    {venv_path}\\Scripts\\activate.bat")
        else:
            print(f"    source {venv_path}/bin/activate")
        
        print("\nTo run the AI Dev Toolkit server with MCP, use:")
        if platform.system() == "Windows":
            print(f"    {venv_path}\\Scripts\\python.exe aitoolkit\\librarian\\server.py")
        else:
            print(f"    {venv_path}/bin/python aitoolkit/librarian/server.py")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Install MCP dependencies for AI Dev Toolkit")
    parser.add_argument(
        "--venv",
        action="store_true",
        help="Create and use a virtual environment"
    )
    
    args = parser.parse_args()
    
    if install_mcp_package(args.venv):
        print("\n=== MCP Installation Complete ===\n")
        print("You can now connect AI Dev Toolkit to Claude Desktop.")
        print("Use the following command to start the server:")
        print("    python development/launch_librarian.py")
        
        if args.venv:
            print("\nNote: Make sure to activate the virtual environment first!")
        
        return 0
    else:
        print("\n=== MCP Installation Failed ===\n")
        print("The server will run in limited functionality mode without Claude Desktop connectivity.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
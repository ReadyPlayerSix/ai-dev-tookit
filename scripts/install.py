#!/usr/bin/env python3
"""
⚠️ DEVELOPMENT STATUS: PRE-ALPHA ⚠️

This installer is still under development and provides basic setup functionality.
Full installation capabilities will be added in future releases.

Installation script for AI Dev Toolkit MCP Server.

This script helps set up the AI Dev Toolkit MCP Server by:
1. Checking for required dependencies
2. Installing them if necessary
3. Configuring Claude Desktop (optional)
"""

import os
import sys
import subprocess
import argparse
import platform

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"Error: Python 3.8 or higher is required (you have {platform.python_version()})")
        return False
    return True

def check_pip():
    """Check if pip is installed."""
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        return True
    except subprocess.CalledProcessError:
        print("Error: pip is not installed")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("Checking for required packages...")
    required_packages = ['mcp']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        # First check requirements.txt
        if not os.path.exists("requirements.txt"):
            print("⚠️ requirements.txt not found!")
            return False
            
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("📦 Base dependencies installed successfully!")
        
        # Check for MCP package specifically
        missing_packages = check_dependencies()
        if missing_packages:
            print("\nInstalling missing packages:")
            for package in missing_packages:
                print(f"Installing {package}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}[cli]"])
                    print(f"✅ {package} installed successfully!")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error installing {package}: {e}")
                    return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def configure_claude_desktop():
    """Guide user through Claude Desktop configuration."""
    print("\nClaude Desktop Configuration Guide:")
    print("1. Open Claude Desktop app")
    print("2. Go to Settings > MCP Servers")
    print("3. Click \"Add Server\"")
    print("4. Enter the following details:")
    print("   - Name: AI Dev Toolkit")
    print("   - URL: http://localhost:8000")
    print("5. Click \"Save\"")
    print("6. Grant permissions when prompted\n")

def get_script_directory():
    """Get the directory where the server.py script is located."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "src", "server.py")
    if os.path.exists(server_path):
        return server_path
    else:
        print(f"Error: server.py not found at {server_path}")
        return None

def create_run_script():
    """Create a run script for the server."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "src", "server.py")
    
    if os.name == 'nt':  # Windows
        bat_path = os.path.join(script_dir, "run_server.bat")
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\n"{sys.executable}" "{server_path}"\n')
        print(f"Created run script: {bat_path}")
    else:  # Unix-like
        sh_path = os.path.join(script_dir, "run_server.sh")
        with open(sh_path, 'w') as f:
            f.write(f'#!/bin/bash\n"{sys.executable}" "{server_path}"\n')
        os.chmod(sh_path, 0o755)  # Make executable
        print(f"Created run script: {sh_path}")

def test_server_connection():
    """Test if the MCP server can start correctly."""
    print("Testing server initialization...")
    server_path = get_script_directory()
    if not server_path:
        return False
    
    try:
        # Just import the modules to see if they load correctly
        # We don't actually start the server in test mode
        import importlib.util
        spec = importlib.util.spec_from_file_location("server", server_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Server modules loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

def main():
    """Main entry point for the installation script."""
    parser = argparse.ArgumentParser(description="Install AI Dev Toolkit MCP Server")
    parser.add_argument("--skip-checks", action="store_true", help="Skip dependency checks")
    parser.add_argument("--create-run-script", action="store_true", help="Create a run script")
    parser.add_argument("--test-server", action="store_true", help="Test server initialization")
    args = parser.parse_args()
    
    print("✨ === AI Dev Toolkit MCP Server Installation === ✨\n")
    print("⚠️ NOTE: This project is currently in ALPHA stage! ⚠️\n")
    
    if not args.skip_checks:
        # Check Python version
        if not check_python_version():
            return 1
        
        # Check pip
        if not check_pip():
            return 1
        
        # Install dependencies
        if not install_dependencies():
            return 1
    
    # Create run script if requested
    if args.create_run_script:
        create_run_script()
    
    # Test server if requested
    if args.test_server:
        if not test_server_connection():
            print("\n⚠️ Server test failed. Please check the logs above for details.")
            print("You may still continue with the installation, but the server might not work correctly.")
    
    # Get server path
    server_path = get_script_directory()
    if not server_path:
        return 1
    
    # Guide for Claude Desktop
    configure_claude_desktop()
    
    # Final instructions
    print("\n🎉 Installation completed! 🎉")
    print("\nNext steps:")
    print("1. Start the server: python", server_path)
    print("2. Connect Claude Desktop to the server")
    print("3. In Claude, access tools with: @AI Dev Toolkit")
    print("\nFor more details, see the documentation in the ./docs directory")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

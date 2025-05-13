#!/usr/bin/env python3
"""
GitHub Installation Script for AI Dev Toolkit

This script is a simplified wrapper that downloads and runs the full installation script.
It's designed to provide a single-command solution for installing AI Dev Toolkit 
directly from GitHub for both Claude Desktop and Claude Code users.
"""

import os
import sys
import subprocess
import tempfile
from urllib.request import urlretrieve

# GitHub repository URL and branch
GITHUB_REPO = "isekaiZen/ai-dev-toolkit"
BRANCH = "main"

# Path to the installer script within the repository
INSTALLER_SCRIPT = "scripts/install_for_claude_code.py"

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"Error: Python 3.8 or higher is required (you have {sys.version.split()[0]})")
        return False
    return True

def download_installer():
    """Download the installer script from GitHub."""
    print("Downloading AI Dev Toolkit installer from GitHub...")
    
    # Construct URL to raw file
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRANCH}/{INSTALLER_SCRIPT}"
    
    # Create a temporary file to store the installer
    fd, temp_path = tempfile.mkstemp(suffix='.py')
    os.close(fd)  # Close the file descriptor
    
    try:
        # Download the installer script
        urlretrieve(url, temp_path)
        print("✅ Download completed successfully")
        return temp_path
    except Exception as e:
        print(f"❌ Error downloading installer: {str(e)}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return None

def run_installer(installer_path, args):
    """Run the downloaded installer script."""
    print("\nLaunching AI Dev Toolkit installer...\n")
    
    try:
        # Execute the installer with the current Python interpreter
        subprocess.run([sys.executable, installer_path] + args)
        return True
    except Exception as e:
        print(f"❌ Error running installer: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(installer_path):
            os.unlink(installer_path)

def main():
    """Main function to download and run the installer."""
    print("=== AI Dev Toolkit GitHub Installer ===\n")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Download the installer script
    installer_path = download_installer()
    if not installer_path:
        return 1
    
    # Forward any command-line arguments to the installer
    args = sys.argv[1:]
    
    # Run the installer
    success = run_installer(installer_path, args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
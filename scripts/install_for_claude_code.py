#!/usr/bin/env python3
"""
AI Dev Toolkit Installer for Claude Code

This script provides a streamlined installation process for Claude Code users
to install and configure the AI Dev Toolkit directly from GitHub.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
import argparse
import tempfile

# GitHub repository URL
GITHUB_REPO = "https://github.com/isekaiZen/ai-dev-toolkit.git"

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"Error: Python 3.8 or higher is required (you have {sys.version.split()[0]})")
        return False
    return True

def check_git():
    """Check if git is installed."""
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Git is installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("❌ Git is not installed. Please install git.")
        return False

def check_tkinter():
    """Check if tkinter is installed and working."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        print("✅ Tkinter is installed and working")
        return True
    except ImportError:
        print("❌ Tkinter is not installed. The GUI will not be available.")
        print("To install on Debian/Ubuntu: sudo apt-get install python3-tk")
        print("To install on Fedora: sudo dnf install python3-tkinter")
        print("To install on macOS: brew install python-tk@3.10 (adjust version as needed)")
        return False
    except Exception as e:
        print(f"❌ Tkinter error: {str(e)}")
        return False

def clone_repository(install_dir):
    """Clone the AI Dev Toolkit repository."""
    try:
        print(f"Cloning AI Dev Toolkit repository to {install_dir}...")
        
        # Clone the repository
        subprocess.run(
            ["git", "clone", GITHUB_REPO, install_dir], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        print("✅ Repository cloned successfully")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Error cloning repository: {str(e)}")
        return False

def install_dependencies(install_dir):
    """Install required Python dependencies."""
    try:
        requirements_file = os.path.join(install_dir, "requirements.txt")
        print(f"Installing dependencies from {requirements_file}...")
        
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            check=True
        )
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        return False

def configure_claude_desktop(install_dir, allowed_dirs):
    """Configure Claude Desktop with AI Librarian MCP server if available."""
    # Determine Claude Desktop config path based on platform
    home = Path.home()
    
    if os.name == 'nt':  # Windows
        config_dir = home / "AppData" / "Roaming" / "Claude"
    elif os.name == 'posix':  # macOS/Linux
        if os.path.exists(home / "Library" / "Application Support" / "Claude"):  # macOS
            config_dir = home / "Library" / "Application Support" / "Claude"
        else:  # Linux
            config_dir = home / ".config" / "Claude"
    else:
        print(f"Unsupported platform for Claude Desktop: {os.name}")
        return False
    
    # Check if Claude Desktop config directory exists
    if not config_dir.exists():
        print("Claude Desktop configuration directory not found.")
        print("Skipping Claude Desktop integration.")
        return False
    
    # Path to Claude Desktop config file
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create or update config
    config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print("Found existing Claude Desktop configuration.")
        except:
            print(f"Warning: Could not read existing config file {config_file}")
    
    # Add or update AI Librarian server configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Configure the server
    config["mcpServers"]["ai-librarian"] = {
        "command": "python",
        "args": [str(Path(install_dir) / "aitoolkit" / "librarian" / "server.py")],
        "env": {
            "AI_LIBRARIAN_ALLOWED_DIRS": ",".join(allowed_dirs)
        }
    }
    
    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Successfully installed AI Librarian MCP server to Claude Desktop")
    print(f"Configuration saved to: {config_file}")
    print("Please restart Claude Desktop to apply changes")
    
    return True

def create_desktop_shortcut(install_dir):
    """Create a desktop shortcut for the GUI launcher."""
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        if sys.platform == "win32":  # Windows
            launcher_path = os.path.join(install_dir, "scripts", "launchers", "launch_gui.bat")
            shortcut_path = os.path.join(desktop_path, "AI Dev Toolkit.lnk")
            
            # Use PowerShell to create the shortcut
            ps_command = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{launcher_path}'
            $Shortcut.WorkingDirectory = '{install_dir}'
            $Shortcut.Description = 'AI Dev Toolkit Control Panel'
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            
        elif sys.platform == "darwin":  # macOS
            launcher_path = os.path.join(install_dir, "scripts", "launchers", "launch_gui.py")
            app_dir = os.path.join(desktop_path, "AI Dev Toolkit.app", "Contents", "MacOS")
            os.makedirs(app_dir, exist_ok=True)
            
            # Create shell script launcher
            with open(os.path.join(app_dir, "launcher"), "w") as f:
                f.write(f"""#!/bin/bash
cd "{install_dir}"
python "{launcher_path}"
""")
            os.chmod(os.path.join(app_dir, "launcher"), 0o755)
            
        elif sys.platform.startswith("linux"):  # Linux
            launcher_path = os.path.join(install_dir, "scripts", "launchers", "launch_gui.py")
            desktop_file_path = os.path.join(desktop_path, "ai-dev-toolkit.desktop")
            
            with open(desktop_file_path, "w") as f:
                f.write(f"""[Desktop Entry]
Type=Application
Name=AI Dev Toolkit
Comment=AI Dev Toolkit Control Panel
Exec=python "{launcher_path}"
Path={install_dir}
Terminal=false
Categories=Development;
""")
            os.chmod(desktop_file_path, 0o755)
        
        print("✅ Desktop shortcut created")
        return True
    except Exception as e:
        print(f"❌ Error creating desktop shortcut: {str(e)}")
        print("Shortcut creation skipped, but installation is still successful.")
        return False

def setup_claude_code_integration(install_dir):
    """Set up integration with Claude Code."""
    try:
        # Create CLAUDE.md file if it doesn't exist
        claude_md_path = os.path.join(install_dir, "CLAUDE.md")
        if not os.path.exists(claude_md_path):
            shutil.copy(
                os.path.join(install_dir, "docs", "claude_code_reference.md"), 
                claude_md_path
            )
            print("✅ Created CLAUDE.md for Claude Code integration")
        
        # Add CLAUDE.md to .gitignore
        gitignore_path = os.path.join(install_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()
            
            if "CLAUDE.md" not in gitignore_content:
                with open(gitignore_path, "a") as f:
                    f.write("\n# Claude Code integration\nCLAUDE.md\n")
                print("✅ Added CLAUDE.md to .gitignore")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up Claude Code integration: {str(e)}")
        return False

def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install AI Dev Toolkit for Claude Code")
    parser.add_argument("--install-dir", help="Installation directory (default: ~/ai-dev-toolkit)")
    parser.add_argument("--allowed-dirs", nargs="*", help="Directories to allow AI Librarian to access")
    parser.add_argument("--claude-desktop", action="store_true", help="Configure for Claude Desktop")
    parser.add_argument("--no-desktop-shortcut", action="store_true", help="Skip desktop shortcut creation")
    parser.add_argument("--no-dependencies", action="store_true", help="Skip installing dependencies")
    
    args = parser.parse_args()
    
    print("=== AI Dev Toolkit Installer for Claude Code ===\n")
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not check_git():
        return 1
    
    has_tkinter = check_tkinter()
    if not has_tkinter:
        print("\nWarning: Tkinter issues detected. The GUI may not work correctly.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return 1
    
    # Determine installation directory
    if args.install_dir:
        install_dir = os.path.expanduser(args.install_dir)
    else:
        install_dir = os.path.expanduser("~/ai-dev-toolkit")
    
    # Ask user to choose Claude Desktop or Claude Code
    claude_desktop = args.claude_desktop
    if not args.claude_desktop:
        choice = input("\nAre you using Claude Desktop or Claude Code? (D/C): ").strip().lower()
        claude_desktop = choice.startswith('d')
    
    # Clone repository
    if os.path.exists(install_dir):
        print(f"\nDirectory {install_dir} already exists.")
        response = input("Use existing directory? (y/n): ").strip().lower()
        if response != 'y':
            new_dir = input(f"Enter new installation directory (or leave empty to cancel): ")
            if not new_dir:
                print("Installation cancelled.")
                return 1
            install_dir = os.path.expanduser(new_dir)
    
    if not os.path.exists(install_dir):
        if not clone_repository(install_dir):
            return 1
    else:
        print(f"Using existing repository at {install_dir}")
    
    # Install dependencies
    if not args.no_dependencies:
        if not install_dependencies(install_dir):
            return 1
    
    # Get allowed directories for AI Librarian
    if args.allowed_dirs:
        allowed_dirs = [os.path.abspath(os.path.expanduser(d)) for d in args.allowed_dirs]
    else:
        print("\nThe AI Librarian needs access to your project directories.")
        
        # Always include install directory
        allowed_dirs = [install_dir]
        print(f"Default directory: {install_dir}")
        
        # Ask for additional directories
        add_more = input("Do you want to add more directories? (y/n): ").lower() == 'y'
        
        while add_more:
            dir_path = input("Enter directory path (or leave empty to finish): ")
            if not dir_path:
                break
                
            path = os.path.abspath(os.path.expanduser(dir_path))
            if os.path.exists(path) and os.path.isdir(path):
                allowed_dirs.append(path)
                print(f"Added: {path}")
            else:
                print(f"Directory not found: {path}")
            
            add_more = input("Add another directory? (y/n): ").lower() == 'y'
    
    # Configure for Claude Desktop if requested
    if claude_desktop:
        configure_claude_desktop(install_dir, allowed_dirs)
    
    # Set up Claude Code integration
    setup_claude_code_integration(install_dir)
    
    # Create desktop shortcut if applicable
    if has_tkinter and not args.no_desktop_shortcut:
        create_desktop_shortcut(install_dir)
    
    print("\n✅ Installation completed successfully!")
    print(f"AI Dev Toolkit installed to: {install_dir}")
    
    print("\nAllowed directories:")
    for dir_path in allowed_dirs:
        print(f"- {dir_path}")
    
    if claude_desktop:
        print("\nClaude Desktop configured to use AI Librarian")
        print("Please restart Claude Desktop to apply changes")
    
    print("\nYou can now use the AI Dev Toolkit:")
    
    if has_tkinter:
        print("  - Launch the GUI:")
        if sys.platform == "win32":
            print(f"    - {os.path.join(install_dir, 'scripts', 'launchers', 'launch_gui.bat')}")
        print(f"    - python {os.path.join(install_dir, 'scripts', 'launchers', 'launch_gui.py')}")
    
    print("  - Run the AI Librarian server:")
    print(f"    - python {os.path.join(install_dir, 'development', 'launch_librarian.py')} [allowed_directory_paths...]")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
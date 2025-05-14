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
import fnmatch  # For adapter pattern testing

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

def install_dependencies(install_dir, is_wsl=False):
    """Install required Python dependencies, excluding MCP (not needed for Claude Code)."""
    try:
        # Create a temporary requirements file without MCP
        requirements_file = os.path.join(install_dir, "requirements.txt")
        temp_requirements = os.path.join(tempfile.gettempdir(), "claude_code_requirements.txt")
        
        with open(requirements_file, 'r') as src:
            lines = [line for line in src if not line.strip().startswith("mcp")]
        
        with open(temp_requirements, 'w') as dest:
            dest.writelines(lines)
        
        print(f"Installing dependencies for Claude Code from filtered requirements...")
        
        # Find the correct pip command
        pip_commands = [
            [sys.executable, "-m", "pip"],
            ["pip3"],
            ["pip"]
        ]
        
        if is_wsl:
            print("WSL environment: Checking for available pip command...")
            
        success = False
        errors = []
        
        for pip_cmd in pip_commands:
            try:
                # Check if this pip command exists
                test_cmd = pip_cmd.copy()
                if len(test_cmd) == 1:
                    test_cmd.append("--version")
                else:
                    test_cmd.append("--version")
                    
                subprocess.run(test_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # If we get here, the command exists, so try to use it
                if is_wsl:
                    print(f"Using {' '.join(pip_cmd)} to install dependencies...")
                
                install_cmd = pip_cmd.copy()
                install_cmd.extend(["install", "-r", temp_requirements])
                
                subprocess.run(install_cmd, check=True)
                print("✅ Dependencies installed successfully")
                success = True
                break
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                errors.append(f"Command '{' '.join(pip_cmd)}' failed: {str(e)}")
                continue
        
        if not success:
            if is_wsl:
                print("⚠️ Could not install dependencies using pip. You may need to install Python/pip in your WSL environment:")
                print("sudo apt update && sudo apt install python3-pip")
                print("\nErrors encountered:")
                for error in errors:
                    print(f"- {error}")
            else:
                print(f"⚠️ Warning: Error installing dependencies")
                print("Continuing with installation anyway as dependencies are optional for Claude Code.")
            
        # Always return True to continue installation
        return True
    except Exception as e:
        print(f"⚠️ Warning: Error preparing dependencies: {str(e)}")
        print("Continuing with installation anyway as dependencies are optional for Claude Code.")
        return True  # Return True to continue installation
    finally:
        # Clean up temp file
        if os.path.exists(temp_requirements):
            try:
                os.remove(temp_requirements)
            except:
                pass

# Function removed - this is a Claude Code only installer

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

def check_for_existing_ai_references(allowed_dirs):
    """Check for existing .ai_reference directories that need upgrading."""
    existing_references = []
    for dir_path in allowed_dirs:
        try:
            for root, dirs, _ in os.walk(dir_path):
                if ".ai_reference" in dirs:
                    ai_ref_path = os.path.join(root, ".ai_reference")
                    existing_references.append(root)  # Add the parent directory (project path)
        except Exception as e:
            print(f"Warning: Could not check for .ai_reference in {dir_path}: {str(e)}")
    
    return existing_references

def upgrade_existing_ai_references(existing_projects):
    """Upgrade existing .ai_reference directories to the latest format."""
    if not existing_projects:
        return
    
    print("\n=== Upgrading Existing AI Reference Directories ===")
    for project_path in existing_projects:
        try:
            print(f"\nUpgrading project: {project_path}")
            
            # Check if we should proceed
            response = input(f"Upgrade .ai_reference in {project_path}? (y/n): ").strip().lower()
            if response != 'y':
                print("Skipping this project")
                continue
            
            # Backup existing .ai_reference
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            backup_path = os.path.join(project_path, ".ai_reference.backup")
            
            try:
                if os.path.exists(backup_path):
                    # Remove old backup if it exists
                    import shutil
                    shutil.rmtree(backup_path)
                
                # Create backup
                import shutil
                shutil.copytree(ai_ref_path, backup_path)
                print(f"✅ Created backup at: {backup_path}")
            except Exception as e:
                print(f"⚠️ Could not create backup: {str(e)}")
                response = input("Continue without backup? (y/n): ").strip().lower()
                if response != 'y':
                    print("Skipping this project")
                    continue
            
            # Look for CLAUDE.md and update it
            claude_md_path = os.path.join(project_path, "CLAUDE.md")
            setup_claude_md_auto_init(claude_md_path)
            
            # Run the initialization script directly for this project
            print(f"Running initialization for {project_path}...")
            from sys import path as sys_path
            sys_path.append(os.path.abspath(os.path.dirname(__file__)))
            
            try:
                # Try to run the ai_dev_toolkit initialization
                cmd = [sys.executable, "-c", 
                       f"import sys; sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}'); "
                       f"from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit; "
                       f"result = initialize_ai_dev_toolkit('{project_path}'); "
                       f"print('Status: ' + result.get('status', 'unknown')); "
                       f"print(result.get('message', 'No message'))"]
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(result.stdout)
                
                print(f"✅ Successfully upgraded .ai_reference in {project_path}")
            except Exception as e:
                print(f"❌ Error upgrading project: {str(e)}")
                print("The backup remains available at", backup_path)
        
        except Exception as e:
            print(f"❌ Error processing project {project_path}: {str(e)}")

def setup_claude_md_auto_init(claude_md_path):
    """Add auto-initialization code to CLAUDE.md."""
    auto_init_code = """```python
# Automatically initialize AI Dev Toolkit on startup
import os
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Initialize the toolkit with the current project path
current_dir = os.path.dirname(os.path.abspath(__file__))
initialize_ai_dev_toolkit(current_dir)
```

"""
    
    try:
        if os.path.exists(claude_md_path):
            # Add initialization code to existing CLAUDE.md if not already there
            with open(claude_md_path, 'r') as f:
                content = f.read()
            
            if "initialize_ai_dev_toolkit" not in content:
                # Find where to insert the code (after the initial header)
                header_end = content.find("\n\n")
                if header_end != -1:
                    modified_content = content[:header_end+2] + auto_init_code + content[header_end+2:]
                else:
                    modified_content = content + "\n\n" + auto_init_code
                
                # Write the modified content
                with open(claude_md_path, 'w') as f:
                    f.write(modified_content)
                
                print("✅ Added auto-initialization to existing CLAUDE.md")
            else:
                print("✅ CLAUDE.md already contains auto-initialization code")
        
        return True
    except Exception as e:
        print(f"❌ Error adding auto-initialization to CLAUDE.md: {str(e)}")
        return False

def setup_claude_code_integration(install_dir):
    """Set up integration with Claude Code."""
    try:
        # Create CLAUDE.md file if it doesn't exist
        claude_md_path = os.path.join(install_dir, "CLAUDE.md")
        if not os.path.exists(claude_md_path):
            # Get reference template content
            reference_path = os.path.join(install_dir, "docs", "claude_code_reference.md")
            if os.path.exists(reference_path):
                with open(reference_path, 'r') as f:
                    content = f.read()
                
                # Add auto-initialization code at the top
                auto_init_code = """```python
# Automatically initialize AI Dev Toolkit on startup
import os
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Initialize the toolkit with the current project path
current_dir = os.path.dirname(os.path.abspath(__file__))
initialize_ai_dev_toolkit(current_dir)
```

"""
                # Find where to insert the code (after the initial header)
                header_end = content.find("\n\n")
                if header_end != -1:
                    modified_content = content[:header_end+2] + auto_init_code + content[header_end+2:]
                else:
                    modified_content = content + "\n\n" + auto_init_code
                
                # Write the modified content
                with open(claude_md_path, 'w') as f:
                    f.write(modified_content)
                
                print("✅ Created CLAUDE.md with auto-initialization for Claude Code")
            else:
                print(f"❌ Reference file not found: {reference_path}")
                return False
        else:
            # Use the shared function to add auto-init code
            setup_claude_md_auto_init(claude_md_path)
        
        # Add CLAUDE.md to .gitignore
        gitignore_path = os.path.join(install_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()
            
            if "CLAUDE.md" not in gitignore_content:
                with open(gitignore_path, "a") as f:
                    f.write("\n# Claude Code integration\nCLAUDE.md\n")
                print("✅ Added CLAUDE.md to .gitignore")
        
        # Create or update adapter file
        adapter_dir = os.path.join(install_dir, ".ai_reference")
        os.makedirs(adapter_dir, exist_ok=True)
        
        adapter_file = os.path.join(adapter_dir, "claude_code_adapter.md")
        
        # Only create if it doesn't exist
        if not os.path.exists(adapter_file):
            adapter_content = """# Claude Code Adapter for AI Dev Toolkit

This adapter file helps Claude Code efficiently work with the AI Dev Toolkit by providing optimized patterns for accessing indexed data instead of performing expensive filesystem operations.

## Core Principles

1. Always check indexed data before filesystem operations
2. Use component registry for component lookups
3. Use script index for file structure understanding
4. Only fall back to standard tools when indexed data is insufficient

## Adapter Patterns

### Component Lookup Pattern

```python
# Instead of searching files for a component:
def find_component(project_path, component_name):
    # First check component registry
    registry_path = f"{project_path}/.ai_reference/component_registry.json"
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
            if component_name in registry["components"]:
                component = registry["components"][component_name]
                # Found in registry, get direct file path
                file_path = component["primary_file"]
                return {"file_path": file_path, "component": component}
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
        
    # Fallback to search if not found in registry
    matches = search_files(project_path, component_name)
    return {"search_results": matches}
```

### File Structure Pattern

```python
# Instead of globbing directories:
def get_project_structure(project_path, file_pattern="*.py"):
    # First check script index
    index_path = f"{project_path}/.ai_reference/script_index.json"
    try:
        with open(index_path, 'r') as f:
            script_index = json.load(f)
            matching_files = [
                file_path for file_path in script_index["files"].keys() 
                if fnmatch.fnmatch(file_path, file_pattern)
            ]
            if matching_files:
                return {"files": matching_files, "source": "script_index"}
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
        
    # Fallback to glob if not found in script index
    return {"files": glob(f"{project_path}/**/{file_pattern}"), "source": "filesystem"}
```

### File Reading with Cache Pattern

```python
# Memory cache for file contents
_file_cache = {}
_cache_timestamp = {}
_cache_max_age = 300  # 5 minutes

def read_cached_file(file_path):
    current_time = time.time()
    
    # Check if in cache and still fresh
    if file_path in _file_cache and (current_time - _cache_timestamp.get(file_path, 0) < _cache_max_age):
        return _file_cache[file_path]
        
    # Read file and update cache
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            _file_cache[file_path] = content
            _cache_timestamp[file_path] = current_time
            return content
    except Exception as e:
        return None
```

## Usage Instructions for Claude Code

When working with a project that has an `.ai_reference` directory:

1. First check if component_registry.json, script_index.json, and bidirectional_refs.json exist
2. Use these files directly to answer questions about code structure and relationships
3. Read specific files only when indexed information is insufficient
4. Cache file contents to avoid repeated reads of the same files
5. Leverage mini-librarians for detailed component information

This approach will significantly reduce filesystem operations and improve performance."""
            
            with open(adapter_file, 'w') as f:
                f.write(adapter_content)
            print(f"✅ Created Claude Code adapter at {adapter_file}")
        else:
            print(f"✅ Claude Code adapter already exists at {adapter_file}")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up Claude Code integration: {str(e)}")
        return False

def test_adapter_functionality(install_dir):
    """Test if the Claude Code adapter is working correctly."""
    print("\n=== Testing Claude Code Adapter Functionality ===")
    
    adapter_file = os.path.join(install_dir, ".ai_reference", "claude_code_adapter.md")
    if not os.path.exists(adapter_file):
        print("❌ Adapter file not found")
        return False
    
    print(f"✅ Adapter file exists at {adapter_file}")
    
    # Test component_registry.json access
    registry_path = os.path.join(install_dir, ".ai_reference", "component_registry.json")
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
                component_count = len(registry.get("components", {}))
                print(f"✅ Component registry loaded successfully with {component_count} components")
                
                # Test if we can find a specific component
                if component_count > 0:
                    component_name = next(iter(registry.get("components", {}).keys()))
                    component = registry["components"][component_name]
                    print(f"✅ Component example: {component_name} defined in {component.get('primary_file', 'unknown')}")
        except Exception as e:
            print(f"❌ Error loading component registry: {str(e)}")
    else:
        print("⚠️ Component registry not found. Run indexing to create it.")
    
    # Test script_index.json access
    script_index_path = os.path.join(install_dir, ".ai_reference", "script_index.json")
    if os.path.exists(script_index_path):
        try:
            with open(script_index_path, 'r') as f:
                script_index = json.load(f)
                file_count = len(script_index.get("files", {}))
                print(f"✅ Script index loaded successfully with {file_count} files")
                
                # Test if we can find a specific file pattern
                if file_count > 0:
                    py_files = [path for path in script_index.get("files", {}).keys() if path.endswith(".py")]
                    if py_files:
                        print(f"✅ Found {len(py_files)} Python files in index, example: {py_files[0]}")
        except Exception as e:
            print(f"❌ Error loading script index: {str(e)}")
    else:
        print("⚠️ Script index not found. Run indexing to create it.")
    
    # Test bidirectional_refs.json access
    refs_path = os.path.join(install_dir, ".ai_reference", "bidirectional_refs.json")
    if os.path.exists(refs_path):
        try:
            with open(refs_path, 'r') as f:
                refs = json.load(f)
                ref_count = len(refs)
                print(f"✅ Bidirectional references loaded successfully with {ref_count} entries")
                
                # Test if we can find relationships
                if ref_count > 0 and isinstance(refs, dict):
                    ref_key = next(iter(refs.keys()))
                    ref_value = refs[ref_key]
                    print(f"✅ Reference example: {ref_key} -> {ref_value}")
        except Exception as e:
            print(f"❌ Error loading bidirectional references: {str(e)}")
    else:
        print("⚠️ Bidirectional references not found. Run indexing to create it.")
    
    # Test adapter patterns
    print("\n--- Testing Adapter Patterns ---")
    
    # Try component lookup pattern
    try:
        # Find a test component (filesystem.py)
        target_name = "filesystem"
        
        # First check component registry
        found_component = False
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                registry = json.load(f)
                for name, component in registry.get("components", {}).items():
                    if target_name.lower() in name.lower():
                        print(f"✅ Component lookup pattern success: Found {name} in {component.get('primary_file', 'unknown')}")
                        found_component = True
                        break
        
        # If not found, try script index
        if not found_component and os.path.exists(script_index_path):
            with open(script_index_path, 'r') as f:
                script_index = json.load(f)
                for file_path in script_index.get("files", {}).keys():
                    if target_name.lower() in file_path.lower():
                        print(f"✅ File lookup pattern success: Found {file_path}")
                        found_component = True
                        break
        
        if not found_component:
            print("⚠️ Test component not found. Full indexing may be needed.")
    except Exception as e:
        print(f"⚠️ Error testing adapter patterns: {str(e)}")
    
    print("\nAdapter test completed. Claude Code should now use indexed data efficiently!\n")
    return True

def detect_wsl():
    """Detect if running in Windows Subsystem for Linux."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except:
        return False

def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install AI Dev Toolkit for Claude Code")
    parser.add_argument("--install-dir", help="Installation directory (default: ~/ai-dev-toolkit)")
    parser.add_argument("--allowed-dirs", nargs="*", help="Directories to allow AI Librarian to access")
    parser.add_argument("--no-desktop-shortcut", action="store_true", help="Skip desktop shortcut creation")
    parser.add_argument("--no-dependencies", action="store_true", help="Skip installing dependencies")
    parser.add_argument("--test-adapter", action="store_true", help="Test adapter functionality")
    parser.add_argument("--wsl", action="store_true", help="Use WSL-specific settings (automatically detected if not specified)")
    
    args = parser.parse_args()
    
    print("=== AI Dev Toolkit Installer for Claude Code ===\n")
    
    # Check if running in WSL
    is_wsl = args.wsl or detect_wsl()
    if is_wsl:
        print("🖥️ WSL (Windows Subsystem for Linux) environment detected")
        print("- Windows drives are typically mounted at /mnt/c/, /mnt/d/, etc.")
        print("- Using adapted settings for WSL environment\n")
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not check_git():
        return 1
    
    has_tkinter = check_tkinter()
    if not has_tkinter:
        print("\nWarning: Tkinter issues detected. The GUI may not work correctly.")
        print("Continuing installation without GUI features.")
    
    # Determine installation directory
    if args.install_dir:
        install_dir = os.path.expanduser(args.install_dir)
    else:
        if is_wsl:
            # Suggest a Windows drive path for the installation
            default_windows_path = "/mnt/c/Users/Public/ai-dev-toolkit"
            install_dir = input(f"\nPlease enter installation directory path (default: {default_windows_path}): ")
            if not install_dir:
                install_dir = default_windows_path
            install_dir = os.path.expanduser(install_dir)
        else:
            install_dir = os.path.expanduser("~/ai-dev-toolkit")
    
    # No Claude Desktop option - this is exclusively for Claude Code
    
    # Clone repository
    if os.path.exists(install_dir):
        print(f"\nDirectory {install_dir} already exists.")
        # Non-interactive mode: use existing directory by default
        if sys.stdin.isatty():
            # Only prompt if running interactively
            response = input("Use existing directory? (y/n): ").strip().lower()
            if response != 'y':
                new_dir = input(f"Enter new installation directory (or leave empty to cancel): ")
                if not new_dir:
                    print("Installation cancelled.")
                    return 1
                install_dir = os.path.expanduser(new_dir)
        else:
            print("Using existing directory for non-interactive run.")
    
    if not os.path.exists(install_dir):
        if not clone_repository(install_dir):
            return 1
    else:
        print(f"Using existing repository at {install_dir}")
    
    # Install dependencies
    if not args.no_dependencies:
        install_dependencies(install_dir, is_wsl)  # Pass WSL flag to the function
    
    # Get allowed directories for AI Librarian
    if args.allowed_dirs:
        allowed_dirs = [os.path.abspath(os.path.expanduser(d)) for d in args.allowed_dirs]
    else:
        print("\nThe AI Librarian needs access to your project directories.")
        
        # Always include install directory
        allowed_dirs = [install_dir]
        print(f"Default directory: {install_dir}")
        
        # Interactive mode only if stdin is a tty
        if sys.stdin.isatty():
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
        else:
            print("Non-interactive mode: Using only the default directory.")
    
    # Set up Claude Code integration
    setup_claude_code_integration(install_dir)
    
    # Run indexer to populate .ai_reference
    print("\n=== Running AI Librarian Indexer ===")
    print("This will populate the .ai_reference directory with project metadata...")
    
    try:
        # Try to import and run the enhanced indexer directly
        sys.path.append(install_dir)
        
        try:
            from aitoolkit.librarian.enhanced_indexer import initialize_enhanced_librarian
            result = initialize_enhanced_librarian(install_dir)
            print(f"\u2705 Successfully indexed project: {result.get('message', 'Indexing complete')}")
        except ImportError:
            # Fallback to using the command line
            print("Direct import failed, using command line indexer...")
            indexer_path = os.path.join(install_dir, "development", "launch_librarian.py")
            if os.path.exists(indexer_path):
                cmd = [sys.executable, indexer_path, install_dir]
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print("\u2705 Successfully indexed project via command line")
                except subprocess.SubprocessError as e:
                    print(f"\u26a0\ufe0f Warning: Error during indexing: {str(e)}")
                    print("The adapter will still work, but with limited functionality until indexing is complete.")
            else:
                print(f"\u26a0\ufe0f Warning: Indexer not found at {indexer_path}")
                print("The adapter will still work, but with limited functionality until indexing is complete.")
    except Exception as e:
        print(f"\u26a0\ufe0f Warning: Error during indexing: {str(e)}")
        print("The adapter will still work, but with limited functionality until indexing is complete.")
    
    # Create desktop shortcut if applicable
    if has_tkinter and not args.no_desktop_shortcut:
        create_desktop_shortcut(install_dir)
    
    # Check for existing .ai_reference directories that need upgrading
    print("\nChecking for existing AI Reference directories to upgrade...")
    existing_projects = check_for_existing_ai_references(allowed_dirs)
    
    if existing_projects:
        print(f"\nFound {len(existing_projects)} project(s) with existing .ai_reference directories:")
        for i, project in enumerate(existing_projects):
            print(f"{i+1}. {project}")
        
        # Non-interactive mode: skip upgrades by default
        if sys.stdin.isatty():
            # Only prompt if running interactively
            response = input("\nWould you like to upgrade these projects to use the latest AI Dev Toolkit features? (y/n): ").strip().lower()
            if response == 'y':
                upgrade_existing_ai_references(existing_projects)
            else:
                print("\nSkipping upgrades. You can manually upgrade projects later with:")
                print("python scripts/install_for_claude_code.py --allowed-dirs [project_paths]")
        else:
            print("\nSkipping upgrades in non-interactive mode.")
    
    # Test adapter functionality if requested
    if args.test_adapter:
        test_adapter_functionality(install_dir)
    
    print("\n✅ Installation completed successfully!")
    print(f"AI Dev Toolkit installed to: {install_dir}")
    
    print("\nAllowed directories:")
    for dir_path in allowed_dirs:
        print(f"- {dir_path}")
    
    print("\nClaude Code adapter installed and configured")
    print("Claude Code will now use the AI Dev Toolkit with optimized performance")
    
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
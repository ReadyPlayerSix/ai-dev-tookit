#!/usr/bin/env python3
"""
AI Dev Toolkit GUI Installer

This script sets up the enhanced GUI for the AI Dev Toolkit.
It installs necessary files and creates shortcuts.
"""

import os
import sys
import shutil
import subprocess

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"Error: Python 3.8 or higher is required (you have {sys.version.split()[0]})")
        return False
    return True

def check_tkinter():
    """Check if tkinter is installed and working."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        print("✅ Tkinter is installed and working")
        return True
    except ImportError:
        print("❌ Tkinter is not installed. Please install the python3-tk package.")
        return False
    except Exception as e:
        print(f"❌ Tkinter error: {str(e)}")
        return False

def install_gui_files():
    """Install the GUI files to the correct locations."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gui_dir = os.path.join(script_dir, "gui")
        
        # Check if GUI directory exists
        if not os.path.exists(gui_dir):
            os.makedirs(gui_dir, exist_ok=True)
        
        # Copy new GUI files to the gui directory
        enhanced_gui_path = os.path.join(script_dir, "enhanced_configurator.py")
        if os.path.exists(enhanced_gui_path):
            # Backup original configurator if it exists
            original_configurator = os.path.join(gui_dir, "configurator.py")
            if os.path.exists(original_configurator):
                backup_path = os.path.join(gui_dir, "configurator.py.bak")
                print(f"Backing up original configurator to {backup_path}")
                shutil.copy2(original_configurator, backup_path)
            
            # Copy enhanced GUI
            print(f"Installing enhanced GUI to {os.path.join(gui_dir, 'configurator.py')}")
            shutil.copy2(enhanced_gui_path, os.path.join(gui_dir, "configurator.py"))
        else:
            print("Enhanced configurator file not found. Please run this script from the correct directory.")
            return False
        
        # Copy launcher files
        launcher_script = os.path.join(script_dir, "launch_gui.py")
        batch_launcher = os.path.join(script_dir, "launch_gui.bat")
        
        if os.path.exists("launch_gui.py.new"):
            print("Installing launcher script")
            shutil.copy2("launch_gui.py.new", launcher_script)
            os.chmod(launcher_script, 0o755)  # Make executable
        
        if os.path.exists("launch_gui.bat.new"):
            print("Installing batch launcher")
            shutil.copy2("launch_gui.bat.new", batch_launcher)
        
        print("✅ GUI files installed successfully")
        return True
    except Exception as e:
        print(f"❌ Error installing GUI files: {str(e)}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut for the GUI."""
    try:
        if sys.platform == "win32":
            script_dir = os.path.dirname(os.path.abspath(__file__))
            batch_file = os.path.join(script_dir, "launch_gui.bat")
            
            if not os.path.exists(batch_file):
                print("❌ Batch launcher not found. Skipping shortcut creation.")
                return False
            
            # Get desktop path
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Create shortcut
            shortcut_path = os.path.join(desktop_path, "AI Dev Toolkit.lnk")
            
            # Use PowerShell to create the shortcut
            ps_command = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{batch_file}'
            $Shortcut.WorkingDirectory = '{script_dir}'
            $Shortcut.Description = 'AI Dev Toolkit Control Panel'
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", ps_command], check=True)
            
            print(f"✅ Desktop shortcut created at {shortcut_path}")
            return True
        else:
            # For Linux/Mac, we'd need different approaches
            print("⚠️ Desktop shortcut creation not implemented for this platform.")
            return True
    except Exception as e:
        print(f"❌ Error creating desktop shortcut: {str(e)}")
        return False

def main():
    """Main installation function."""
    print("=== AI Dev Toolkit GUI Installer ===\n")
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not check_tkinter():
        print("\nWarning: Tkinter issues detected. The GUI may not work correctly.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return 1
    
    # Install files
    print("\nInstalling GUI files...")
    if not install_gui_files():
        return 1
    
    # Create shortcut
    print("\nCreating desktop shortcut...")
    create_desktop_shortcut()
    
    print("\n✅ Installation completed successfully!")
    print("You can now launch the AI Dev Toolkit GUI using:")
    print("  - The desktop shortcut (if created)")
    print("  - launch_gui.bat (Windows)")
    print("  - python launch_gui.py (Any platform)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

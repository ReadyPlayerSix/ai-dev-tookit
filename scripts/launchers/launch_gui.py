#!/usr/bin/env python3
"""
AI Dev Toolkit GUI Launcher

This script launches the GUI configurator for the AI Dev Toolkit.
It provides a unified control panel for managing Claude Desktop integration,
server configuration, project management, and AI Librarian functionality.
"""

import os
import sys
import importlib.util
import traceback

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    for module in ["tkinter", "json", "subprocess", "threading"]:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)
    
    return missing

def main():
    """Main entry point for the launcher."""
    print("Starting AI Dev Toolkit GUI...")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Error: Missing dependencies: {', '.join(missing)}")
        print("Please install required dependencies using pip:")
        print(f"  pip install {' '.join(missing)}")
        return 1
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Make sure script directory is in the path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Path to GUI module
    gui_path = os.path.join(script_dir, "gui", "configurator.py")
    
    if not os.path.exists(gui_path):
        print(f"Error: GUI module not found at {gui_path}")
        return 1
    
    # Launch the GUI
    try:
        print(f"Importing GUI from {gui_path}")
        
        # Try direct import first
        try:
            import tkinter as tk
            from gui.configurator import AIDevToolkitGUI
            
            root = tk.Tk()
            app = AIDevToolkitGUI(root)
            root.mainloop()
            
        except ImportError as ie:
            print(f"Direct import failed: {str(ie)}")
            print("Trying alternative import method...")
            
            # If direct import fails, try to load module spec
            spec = importlib.util.spec_from_file_location("configurator", gui_path)
            configurator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(configurator)
            
            import tkinter as tk
            root = tk.Tk()
            app = configurator.AIDevToolkitGUI(root)
            root.mainloop()
    
    except Exception as e:
        print(f"Error launching GUI: {str(e)}")
        print("Detailed error information:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

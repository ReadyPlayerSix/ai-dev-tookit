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
import tkinter as tk

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
    
    # Add the parent directory to the Python path so 'aitoolkit' can be found
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # This is the key fix - add the parent directory to Python's path
    # so the 'aitoolkit' module can be found
    if parent_dir not in sys.path:
        print(f"Adding {parent_dir} to Python path")
        sys.path.insert(0, parent_dir)
    
    try:
        # Import the GUI class after fixing the path
        from aitoolkit.gui.configurator import AIDevToolkitGUI
        
        # Create and run the GUI
        root = tk.Tk()
        app = AIDevToolkitGUI(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Error launching GUI: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

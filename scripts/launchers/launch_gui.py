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
    
    # Use the new unified launcher 
    try:
        # Point the user to use launch_new_gui.py instead
        print("NOTE: This launcher is deprecated. Please use launch_new_gui.py instead.")
        print("Redirecting to the new unified launcher...")
        
        # Try to import from the unified configurator
        try:
            import tkinter as tk
            from aitoolkit.gui.legacy.configurator_unified import AIDevToolkitGUI
            
            root = tk.Tk()
            app = AIDevToolkitGUI(root)
            root.mainloop()
            
        except ImportError as ie:
            print(f"Import failed: {str(ie)}")
            print("Trying alternative import method...")
            
            # Add the parent directory to the Python path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(os.path.dirname(script_dir))
            
            if project_dir not in sys.path:
                sys.path.insert(0, project_dir)
            
            # Try again with the updated path
            import tkinter as tk
            from aitoolkit.gui.legacy.configurator_unified import AIDevToolkitGUI
            
            root = tk.Tk()
            app = AIDevToolkitGUI(root)
            root.mainloop()
    
    except Exception as e:
        print(f"Error launching GUI: {str(e)}")
        print("Detailed error information:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

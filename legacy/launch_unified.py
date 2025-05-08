#!/usr/bin/env python3
"""
AI Dev Toolkit Unified Launcher

This is the single, definitive entry point for launching the AI Dev Toolkit GUI.
It properly handles all path setup, error reporting, and ensures clean application closure.
"""

import os
import sys
import tkinter as tk
import traceback
import argparse

def main():
    """Launch the AI Dev Toolkit GUI with proper error handling and path setup."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch the AI Dev Toolkit GUI")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    if args.debug:
        print("Debug mode enabled")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script location: {os.path.abspath(__file__)}")
    
    # Add the project root directory to Python path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
        
    if args.debug:
        print(f"Added to sys.path: {root_dir}")
        print(f"Full sys.path: {sys.path}")
    
    try:
        # Import the unified GUI class
        from aitoolkit.gui.configurator_unified import AIDevToolkitGUI
        
        if args.debug:
            print("Successfully imported AIDevToolkitGUI")
        
        # Create and run the GUI with proper error handling
        root = tk.Tk()
        
        # Set window icon if available
        try:
            icon_path = os.path.join(root_dir, "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
        except Exception as e:
            if args.debug:
                print(f"Could not set icon: {str(e)}")
        
        # Create application instance
        app = AIDevToolkitGUI(root)
        
        if args.debug:
            print("GUI initialized successfully, entering main loop")
        
        # Run the application
        root.mainloop()
        
        # Ensure clean exit
        if hasattr(app, 'server_process') and app.server_process:
            try:
                print("Shutting down server process...")
                app.server_process.terminate()
                app.server_process.wait(timeout=5)
                print("Server process terminated")
            except Exception as e:
                print(f"Error shutting down server: {str(e)}")
        
        return 0
        
    except ImportError as e:
        print(f"Error: Could not import the AIDevToolkitGUI class: {str(e)}")
        print("Make sure you're running this script from the project root directory.")
        if args.debug:
            traceback.print_exc()
        return 1
        
    except Exception as e:
        print(f"Error launching GUI: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

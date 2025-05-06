#!/usr/bin/env python3
"""
AI Dev Toolkit GUI Launcher

This script is a simple entry point to launch the AI Dev Toolkit GUI.
"""

import os
import sys
import traceback

def main():
    """Main entry point for the launcher."""
    print("Starting AI Dev Toolkit GUI...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the script directory to the Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    try:
        # Import and run the launcher from the new package structure
        from aitoolkit.launch_gui import main as gui_main
        return gui_main()
    except ImportError:
        print("Error importing from aitoolkit package. Make sure the package is properly installed.")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"Error launching GUI: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test if the AI Librarian server can start without errors
"""

import sys
import traceback

try:
    # Try to import the server module
    print("Testing server imports...")
    import aitoolkit.librarian.server
    print("✓ Server module imported successfully")
    
    # Try to import task board
    print("\nTesting task board imports...")
    from aitoolkit.librarian.task_board import TaskBoard
    print("✓ Task board imported successfully")
    
    # Try to import unified context
    print("\nTesting unified context imports...")
    from aitoolkit.librarian.unified_context_integration import register_unified_context_tools
    print("✓ Unified context imported successfully")
    
    print("\n✅ All modules import successfully! The server should be able to start.")
    
except Exception as e:
    print(f"\n❌ Error importing modules: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
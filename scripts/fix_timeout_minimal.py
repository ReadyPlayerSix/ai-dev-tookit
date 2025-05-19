#!/usr/bin/env python3
"""
Minimal timeout fix for AI Dev Toolkit

This script applies the essential fixes to prevent tool timeouts
without breaking the server.
"""

import os
import sys

def fix_daemon_threads(project_path):
    """Fix daemon thread issues that prevent cleanup"""
    
    print("Fixing daemon thread issues...")
    
    # Update unified context to not use daemon threads
    unified_context_file = os.path.join(project_path, "aitoolkit/librarian/unified_context_integration.py")
    if os.path.exists(unified_context_file):
        with open(unified_context_file, 'r') as f:
            content = f.read()
        
        # Make sure threads are not daemon to allow proper cleanup
        content = content.replace('daemon=True', 'daemon=False')
        
        with open(unified_context_file, 'w') as f:
            f.write(content)
        print("✓ Fixed daemon thread in unified context")
    
    # Update task_board to not use daemon threads
    taskboard_file = os.path.join(project_path, "aitoolkit/librarian/task_board.py")
    if os.path.exists(taskboard_file):
        with open(taskboard_file, 'r') as f:
            content = f.read()
        
        # Make worker threads not daemon
        content = content.replace('daemon=True', 'daemon=False')
        
        with open(taskboard_file, 'w') as f:
            f.write(content)
        print("✓ Fixed daemon threads in task board")

def disable_background_updates(project_path):
    """Optionally disable background updates"""
    
    print("\nOptional: Disable background updates to reduce load")
    response = input("Disable background context updates? (y/n): ").lower()
    
    if response == 'y':
        unified_context_file = os.path.join(project_path, "aitoolkit/librarian/unified_context_integration.py")
        if os.path.exists(unified_context_file):
            with open(unified_context_file, 'r') as f:
                content = f.read()
            
            # Comment out the thread start
            content = content.replace(
                'update_thread.start()',
                '# update_thread.start()  # Disabled to prevent timeouts'
            )
            
            with open(unified_context_file, 'w') as f:
                f.write(content)
            print("✓ Disabled background updates")

if __name__ == "__main__":
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("Applying minimal timeout fixes...")
    fix_daemon_threads(project_path)
    disable_background_updates(project_path)
    
    print("\n✅ Minimal fixes applied!")
    print("\nRestart the AI Librarian server for changes to take effect.")
    print("If timeouts persist, consider:")
    print("1. Increasing Claude Desktop timeout in config")
    print("2. Reducing the number of worker threads")
    print("3. Disabling background tasks entirely")
#!/usr/bin/env python3
"""
Temporarily disable problematic modules that cause timeouts
"""

import os
import sys

def disable_modules(project_path):
    """Disable modules that are causing timeout issues"""
    
    print("Disabling problematic modules temporarily...")
    
    # Disable unified context background thread
    unified_context_file = os.path.join(project_path, "aitoolkit/librarian/unified_context_integration.py")
    if os.path.exists(unified_context_file):
        with open(unified_context_file, 'r') as f:
            content = f.read()
        
        # Comment out the thread start
        content = content.replace(
            'update_thread.start()',
            '# update_thread.start()  # DISABLED FOR TIMEOUT PREVENTION'
        )
        
        # Make daemon=False just in case
        content = content.replace('daemon=True', 'daemon=False')
        
        with open(unified_context_file, 'w') as f:
            f.write(content)
        print("✓ Disabled unified context background thread")
    
    # Reduce TaskBoard workers to 1
    taskboard_file = os.path.join(project_path, "aitoolkit/librarian/task_board.py")
    if os.path.exists(taskboard_file):
        with open(taskboard_file, 'r') as f:
            content = f.read()
        
        # Reduce workers to 1
        content = content.replace('max_workers: int = 2', 'max_workers: int = 1')
        content = content.replace('max_workers: int = 4', 'max_workers: int = 1')
        
        # Make threads non-daemon
        content = content.replace('daemon=True', 'daemon=False')
        
        with open(taskboard_file, 'w') as f:
            f.write(content)
        print("✓ Reduced TaskBoard workers to 1")
    
    # Comment out problematic imports in server.py temporarily
    server_file = os.path.join(project_path, "aitoolkit/librarian/server.py")
    if os.path.exists(server_file):
        with open(server_file, 'r') as f:
            content = f.read()
        
        # Add timeout to MCP settings
        if "MCP_DEFAULT_TIMEOUT" not in content:
            timeout_settings = '''# Increased timeouts to prevent connection issues
os.environ["MCP_DEFAULT_TIMEOUT"] = "300000"  # 5 minutes
os.environ["MCP_MAX_REQUEST_TIMEOUT"] = "600000"  # 10 minutes
os.environ["MCP_HEARTBEAT_INTERVAL"] = "30000"  # 30 seconds

'''
            # Insert after the os import
            content = content.replace('import os\n', 'import os\n' + timeout_settings)
        
        with open(server_file, 'w') as f:
            f.write(content)
        print("✓ Updated server timeout settings")

if __name__ == "__main__":
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    disable_modules(project_path)
    
    print("\n✅ Modules disabled successfully!")
    print("\nThe server should now start without timeout issues.")
    print("To re-enable features later, revert these changes.")
    print("\nRestart Claude Desktop and try connecting again.")
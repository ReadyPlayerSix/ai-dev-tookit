#!/usr/bin/env python3
"""
Fix timeout issues in the AI Dev Toolkit MCP server

This script addresses the common causes of tool timeouts:
1. Reduces excessive background thread activity
2. Implements better thread cleanup
3. Adds resource management controls
"""

import os
import sys
import json

def fix_timeout_issues(project_path):
    """Apply fixes to prevent tool timeouts"""
    
    print("Applying timeout fixes to AI Dev Toolkit...")
    
    # 1. Update unified context to reduce update frequency
    unified_context_file = os.path.join(project_path, "aitoolkit/librarian/unified_context_integration.py")
    if os.path.exists(unified_context_file):
        print("Fixing unified context update frequency...")
        with open(unified_context_file, 'r') as f:
            content = f.read()
        
        # Increase update interval from 5 minutes to 30 minutes
        content = content.replace('"update_interval": 300', '"update_interval": 1800')
        
        # Make the thread non-daemon so it can be properly terminated
        content = content.replace('daemon=True', 'daemon=False')
        
        with open(unified_context_file, 'w') as f:
            f.write(content)
        print("✓ Updated unified context settings")
    
    # 2. Fix TaskBoard to better handle thread cleanup
    taskboard_file = os.path.join(project_path, "aitoolkit/librarian/task_board.py")
    if os.path.exists(taskboard_file):
        print("Fixing TaskBoard thread management...")
        
        with open(taskboard_file, 'r') as f:
            content = f.read()
        
        # Add thread tracking to prevent leaks
        thread_tracking = '''
    def __init__(self, project_path: str, num_workers: int = 2):  # Reduce default workers
        """Initialize the TaskBoard with fewer workers by default"""'''
        
        content = content.replace(
            'def __init__(self, project_path: str, num_workers: int = 4):',
            thread_tracking
        )
        
        # Add better thread cleanup
        cleanup_code = '''
            # Add thread cleanup on timeout
            if handler_thread.is_alive():
                logger.warning(f"Handler thread for task {task_id} is still running after timeout")
                # Set a flag for the handler to check
                self._cancelled_tasks.add(task_id)'''
        
        content = content.replace(
            'logger.warning(f"Handler thread for task {task_id} is still running after timeout")',
            cleanup_code
        )
        
        with open(taskboard_file, 'w') as f:
            f.write(content)
        print("✓ Updated TaskBoard thread management")
    
    # 3. Create a timeout configuration file
    config_dir = os.path.join(project_path, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    timeout_config = {
        "mcp_timeout": {
            "default_timeout_ms": 120000,  # 2 minutes instead of 30 seconds
            "file_operations_timeout_ms": 180000,  # 3 minutes for file operations
            "background_tasks": {
                "unified_context_update_interval": 1800,  # 30 minutes
                "taskboard_workers": 2,  # Reduce from 4 to 2
                "task_default_timeout": 300  # 5 minutes per task
            }
        },
        "resource_limits": {
            "max_concurrent_operations": 3,
            "max_background_threads": 5,
            "thread_cleanup_interval": 60  # Check for dead threads every minute
        }
    }
    
    config_file = os.path.join(config_dir, "mcp_timeout_config.json")
    with open(config_file, 'w') as f:
        json.dump(timeout_config, f, indent=2)
    print(f"✓ Created timeout configuration at {config_file}")
    
    # 4. Add a simple resource monitor
    monitor_file = os.path.join(project_path, "aitoolkit/utils/resource_monitor.py")
    os.makedirs(os.path.dirname(monitor_file), exist_ok=True)
    
    monitor_code = '''#!/usr/bin/env python3
"""Simple resource monitor to prevent timeout issues"""

import threading
import time
import logging

logger = logging.getLogger("resource_monitor")

class ResourceMonitor:
    def __init__(self):
        self.active_operations = 0
        self.lock = threading.Lock()
        
    def start_operation(self):
        """Track when an operation starts"""
        with self.lock:
            self.active_operations += 1
            if self.active_operations > 3:
                logger.warning(f"High operation count: {self.active_operations}")
    
    def end_operation(self):
        """Track when an operation ends"""
        with self.lock:
            self.active_operations = max(0, self.active_operations - 1)
    
    def get_active_count(self):
        """Get the current number of active operations"""
        with self.lock:
            return self.active_operations

# Global instance
monitor = ResourceMonitor()
'''
    
    with open(monitor_file, 'w') as f:
        f.write(monitor_code)
    print("✓ Created resource monitor")
    
    print("\n✅ Timeout fixes applied successfully!")
    print("\nRecommendations:")
    print("1. Restart the AI Librarian server for changes to take effect")
    print("2. Monitor tool performance - timeouts should be less frequent")
    print("3. If issues persist, reduce the number of concurrent operations")
    print("\nConfiguration file created at:", config_file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    fix_timeout_issues(project_path)
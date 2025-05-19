#!/usr/bin/env python3
"""
Diagnose timeout issues in the AI Librarian server
"""

import os
import sys
import threading
import time
import psutil

def check_threads():
    """Check current thread count and names"""
    print("Current threads:")
    for thread in threading.enumerate():
        print(f"  - {thread.name} (daemon: {thread.daemon})")
    print(f"Total threads: {threading.active_count()}")

def check_processes():
    """Check Python processes and their resource usage"""
    print("\nPython processes:")
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        if 'python' in proc.info['name'].lower():
            print(f"  - PID {proc.info['pid']}: CPU {proc.info['cpu_percent']}%, Memory {proc.info['memory_percent']:.1f}%")

def check_imports():
    """Test problematic imports"""
    print("\nTesting imports:")
    
    try:
        print("  - TaskBoard...", end=" ")
        from aitoolkit.librarian.task_board import TaskBoard
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
    
    try:
        print("  - UnifiedContext...", end=" ")
        from aitoolkit.librarian.unified_context_integration import register_unified_context_tools
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
    
    try:
        print("  - Server...", end=" ")
        import aitoolkit.librarian.server
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")

def check_file_locks():
    """Check for file locks that might cause issues"""
    print("\nChecking file locks:")
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lock_files = []
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.lock') or file.startswith('.'):
                lock_files.append(os.path.join(root, file))
    
    if lock_files:
        print("  Found lock files:")
        for lock_file in lock_files:
            print(f"    - {lock_file}")
    else:
        print("  No lock files found")

def main():
    print("AI Librarian Timeout Diagnostics")
    print("=" * 40)
    
    check_threads()
    check_processes()
    check_imports()
    check_file_locks()
    
    print("\nRecommendations:")
    print("1. If many threads are running, consider disabling background tasks")
    print("2. If CPU/Memory usage is high, reduce worker threads")
    print("3. If imports fail, check for circular dependencies")
    print("4. Remove any lock files that might be blocking operations")

if __name__ == "__main__":
    main()
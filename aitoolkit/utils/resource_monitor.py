#!/usr/bin/env python3
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

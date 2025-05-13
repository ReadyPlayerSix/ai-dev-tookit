"""
AI Librarian components for the AI Dev Toolkit.

This module contains the functionality for the AI Librarian, which provides
persistent code comprehension and context maintenance across conversations.
"""

# Explicitly expose key modules
try:
    from .think_tool import think
    from .task_board import (
        task_deep_analysis, 
        submit_background_task,
        get_task_status_mcp as get_task_status,
        get_task_result_mcp as get_task_result,
        cancel_task_mcp as cancel_task,
        list_tasks_mcp as list_tasks
    )
    
    # Export important functions
    __all__ = [
        'think',
        'task_deep_analysis', 
        'submit_background_task',
        'get_task_status',
        'get_task_result',
        'cancel_task',
        'list_tasks'
    ]
except ImportError as e:
    import logging
    logging.warning(f"Could not import some librarian components: {e}")
    __all__ = []

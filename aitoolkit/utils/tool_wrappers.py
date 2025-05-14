#!/usr/bin/env python3
"""
Tool Wrapper Utilities

This module provides wrappers for MCP tools, especially for long-running operations
like search, indexing, and initialization functions.

Usage:
    from aitoolkit.utils.tool_wrappers import make_robust, apply_robustness
    
    # Apply to a specific function
    @make_robust(timeout=60.0)
    def my_search_function():
        # Implementation
        
    # Or apply to existing functions
    my_search_function = apply_robustness(my_search_function)
"""

import os
import sys
import logging
import inspect
import functools
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TypeVar, Set

# Configure logging
logger = logging.getLogger("tool-wrappers")

# Import request helpers
try:
    from .request_helpers import robust_operation, with_retry, with_queue_clearing, with_timeout
except ImportError:
    logger.warning("Could not import request helpers, using stub implementations")
    # Create stub decorators if imports fail
    def robust_operation(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def with_retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def with_queue_clearing(func):
        return func
    
    def with_timeout(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Type variable for the return type of the function
T = TypeVar('T')

# Keywords that indicate a function might be long-running
SEARCH_KEYWORDS = {
    'search', 'find', 'query', 'lookup', 'locate', 'discover', 'scan', 
    'analyze', 'parse', 'index', 'initialize', 'generate', 'build', 'create'
}

# File operation keywords that might be used in long operations
FILE_OPERATION_KEYWORDS = {
    'read_multiple', 'search_files', 'directory_tree', 'write_file', 
    'edit_file', 'enhanced_edit', 'apply_bookmark', 'write_tool', 'search_tool'
}

# Timeout multipliers for specific operations (in seconds)
OPERATION_TIMEOUTS = {
    'search': 120.0,  # 2 minutes for search operations
    'write': 120.0,   # 2 minutes for write operations 
    'find': 90.0,     # 1.5 minutes for find operations
    'query': 90.0,    # 1.5 minutes for query operations
    'default': 60.0   # Default timeout
}

def is_likely_long_running(func_name: str) -> bool:
    """
    Determine if a function is likely to be long-running based on its name.
    
    Args:
        func_name: The name of the function to check
        
    Returns:
        True if the function is likely to be long-running, False otherwise
    """
    func_name_lower = func_name.lower()
    
    # Check for search keywords
    for keyword in SEARCH_KEYWORDS:
        if keyword in func_name_lower:
            return True
    
    # Check for file operation keywords
    for keyword in FILE_OPERATION_KEYWORDS:
        if keyword in func_name_lower:
            return True
    
    return False

def determine_timeout(func_name: str, default_timeout: float = 60.0) -> float:
    """
    Determine the appropriate timeout for a function based on its name.
    
    Args:
        func_name: Function name
        default_timeout: Default timeout to use if no specific match
        
    Returns:
        Timeout in seconds
    """
    func_name_lower = func_name.lower()
    
    # Check for specific operation types
    for operation_type, timeout_value in OPERATION_TIMEOUTS.items():
        if operation_type in func_name_lower:
            logger.info(f"Using {timeout_value}s timeout for {func_name} (matched {operation_type})")
            return timeout_value
    
    # Return default if no specific match
    return default_timeout

def make_robust(
    max_retries: int = 2, 
    timeout: float = None,  # Now optional, will be auto-determined if None
    clear_queue: bool = True,
    force: bool = False
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to make a function more robust against timeouts and failures.
    Only applies to functions that are likely to be long-running,
    unless force=True is specified.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds (if None, will determine based on function name)
        clear_queue: Whether to clear the request queue before operation
        force: Whether to apply robustness features regardless of the function name
        
    Returns:
        Decorated function with robustness features
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        func_name = func.__name__
        
        # Only apply to functions that are likely to be long-running
        if force or is_likely_long_running(func_name):
            # Determine appropriate timeout if not specified
            actual_timeout = timeout if timeout is not None else determine_timeout(func_name)
            
            logger.info(f"Applying robustness features to function: {func_name} (timeout: {actual_timeout}s)")
            return robust_operation(
                max_retries=max_retries,
                timeout=actual_timeout,
                clear_queue=clear_queue
            )(func)
        else:
            return func
    
    return decorator

def apply_robustness(
    func: Callable[..., T],
    max_retries: int = 2, 
    timeout: float = None,  # Now optional, will be auto-determined if None
    clear_queue: bool = True,
    force: bool = False
) -> Callable[..., T]:
    """
    Apply robustness features to an existing function.
    Only applies to functions that are likely to be long-running,
    unless force=True is specified.
    
    Args:
        func: The function to apply robustness features to
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds (if None, will determine based on function name)
        clear_queue: Whether to clear the request queue before operation
        force: Whether to apply robustness features regardless of the function name
        
    Returns:
        Function with robustness features applied
    """
    func_name = func.__name__
    
    # Only apply to functions that are likely to be long-running
    if force or is_likely_long_running(func_name):
        # Determine appropriate timeout if not specified
        actual_timeout = timeout if timeout is not None else determine_timeout(func_name)
        
        logger.info(f"Applying robustness features to function: {func_name} (timeout: {actual_timeout}s)")
        decorated = func
        decorated = with_timeout(actual_timeout)(decorated)
        decorated = with_retry(max_retries=max_retries)(decorated)
        
        if clear_queue:
            decorated = with_queue_clearing(decorated)
            
        return decorated
    else:
        return func

def wrap_mcp_tool(mcp_obj, tool_func: Callable[..., T]) -> Callable[..., T]:
    """
    Wrap an MCP tool function with robustness features.
    This is meant to be used when registering tools with the MCP server.
    
    Args:
        mcp_obj: The MCP server object
        tool_func: The tool function to wrap
        
    Returns:
        Wrapped tool function
    """
    # Get the original tool decorator
    original_tool = mcp_obj.tool
    
    # Apply robustness if the function name suggests it's long-running
    func_name = tool_func.__name__
    
    @functools.wraps(tool_func)
    def wrapped_tool(*args, **kwargs):
        # Apply robustness features based on function name
        if is_likely_long_running(func_name):
            # Determine appropriate timeout
            timeout = determine_timeout(func_name)
            logger.info(f"Applying robustness to MCP tool: {func_name} (timeout: {timeout}s)")
            robust_func = apply_robustness(tool_func, timeout=timeout)
            return original_tool()(robust_func)
        else:
            return original_tool()(tool_func)
    
    return wrapped_tool

def wrap_all_search_tools(module):
    """
    Find and wrap all search-related functions in a module with robustness features.
    
    Args:
        module: The module containing the functions to wrap
    """
    # Get all functions in the module
    for name, obj in inspect.getmembers(module):
        # Only consider functions
        if inspect.isfunction(obj):
            # Check if the function is likely to be long-running
            if is_likely_long_running(name):
                # Apply robustness features
                setattr(module, name, apply_robustness(obj))
                logger.info(f"Applied robustness features to {module.__name__}.{name}")

def patch_mcp_server(server_instance):
    """
    Patch an MCP server instance to apply robustness features to its tools.
    
    Args:
        server_instance: The MCP server instance to patch
        
    Returns:
        Patched server instance
    """
    # Save original tool method
    original_tool = server_instance.tool
    
    # Replace with our wrapped version
    def robust_tool(*args, **kwargs):
        # Get the original decorator
        orig_decorator = original_tool(*args, **kwargs)
        
        # Create a new decorator that applies robustness
        def new_decorator(func):
            if is_likely_long_running(func.__name__):
                # Apply robustness first, then the original decorator
                robust_func = apply_robustness(func)
                return orig_decorator(robust_func)
            else:
                # Just apply the original decorator
                return orig_decorator(func)
        
        return new_decorator
    
    # Replace the tool method
    server_instance.tool = robust_tool
    
    return server_instance

# Sample usage in main
if __name__ == "__main__":
    # Example of applying robustness to a search function
    @make_robust(timeout=30.0)
    def search_documents(query):
        # Some long-running search implementation
        import time
        time.sleep(5)  # Simulate long operation
        return f"Found results for: {query}"
    
    # Test it
    result = search_documents("test query")
    print(result)

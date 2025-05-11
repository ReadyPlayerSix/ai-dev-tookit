#!/usr/bin/env python3
"""
Request Helper Utilities

This module provides helper functions for handling request timeouts, 
retries, and other common issues with AI Toolkit functions.
"""

import time
import logging
import functools
import random
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar

# Configure logging
logger = logging.getLogger("request-helpers")

# Type variable for the return type of the function
T = TypeVar('T')

def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_exceptions: List[Exception] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying functions that might time out or fail temporarily.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        jitter: Whether to add randomness to delay to prevent thundering herd
        retry_exceptions: List of exceptions that should trigger a retry,
                        defaults to (TimeoutError, ConnectionError)
    
    Returns:
        Decorated function with retry capability
    """
    if retry_exceptions is None:
        retry_exceptions = (TimeoutError, ConnectionError)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            # Try the initial call
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not any(isinstance(e, exc) for exc in retry_exceptions):
                    raise  # Don't retry exceptions not in retry_exceptions
                last_exception = e
            
            # Retry logic
            for retry in range(max_retries):
                try:
                    # Calculate delay with optional jitter
                    current_delay = min(delay, max_delay)
                    if jitter:
                        # Add random jitter of up to 25% of the delay
                        current_delay = current_delay * (1 + random.uniform(-0.25, 0.25))
                    
                    logger.info(f"Retry {retry + 1}/{max_retries} after {current_delay:.2f}s delay")
                    time.sleep(current_delay)
                    
                    # Increase delay for next potential retry
                    delay *= backoff_factor
                    
                    # Try the function again
                    return func(*args, **kwargs)
                except Exception as e:
                    if not any(isinstance(e, exc) for exc in retry_exceptions):
                        raise  # Don't retry exceptions not in retry_exceptions
                    last_exception = e
                    logger.warning(f"Retry {retry + 1} failed: {str(e)}")
            
            # If we get here, all retries failed
            logger.error(f"All {max_retries} retries failed")
            if last_exception:
                raise last_exception
            raise RuntimeError("All retries failed with unknown error")
    
        return wrapper
    return decorator

def clear_request_queue():
    """
    Attempt to clear any stale requests in the queue.
    This is a placeholder that should be customized based on
    your actual implementation details.
    """
    # This is just a basic implementation - you would need to
    # customize this based on your MCP server implementation
    logger.info("Clearing request queue")
    time.sleep(0.5)  # Small delay to allow any pending requests to complete
    return True

def with_queue_clearing(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to clear the request queue before executing a function.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function that clears the queue first
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # Clear the request queue first
        clear_request_queue()
        
        # Then execute the function
        return func(*args, **kwargs)
    
    return wrapper

def with_timeout(timeout: float = 60.0) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to add a timeout to a function.
    This is a basic implementation that may need to be adjusted based on your needs.
    
    Args:
        timeout: Timeout in seconds
        
    Returns:
        Decorated function with timeout
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # This is a simplified version - in real-world usage, you might 
            # want to use a proper timeout mechanism like concurrent.futures
            import signal
            
            def handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
            
            # Set the timeout handler
            original_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(timeout))
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore the original handler and cancel the alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)
        
        return wrapper
    return decorator

def chunk_operation(chunk_size: int = 100) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to break a large operation into smaller chunks.
    This is useful for operations that process large collections of data.
    
    Args:
        chunk_size: Size of chunks to process
        
    Returns:
        Decorated function that processes data in chunks
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # This needs to be customized based on the actual function being decorated
            # Here's a simplified example assuming the first argument is a list to be chunked
            if not args:
                return func(*args, **kwargs)
                
            first_arg = args[0]
            if not isinstance(first_arg, (list, tuple)):
                return func(*args, **kwargs)
                
            # Break into chunks
            results = []
            for i in range(0, len(first_arg), chunk_size):
                chunk = first_arg[i:i + chunk_size]
                # Replace the first argument with the chunk
                chunk_args = (chunk,) + args[1:]
                chunk_result = func(*chunk_args, **kwargs)
                results.append(chunk_result)
                
            # This assumes you know how to combine the results
            # For simplicity, we just return the list of results
            return results
        
        return wrapper
    return decorator

# Combined decorators for common use cases
def robust_operation(
    max_retries: int = 3, 
    timeout: float = 60.0,
    clear_queue: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Combined decorator for robust operations with retry, timeout, and queue clearing.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds
        clear_queue: Whether to clear the request queue before operation
        
    Returns:
        Decorated function with all specified robustness features
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Apply decorators in the correct order: timeout → retry → queue clearing
        decorated = func
        decorated = with_timeout(timeout)(decorated)
        decorated = with_retry(max_retries=max_retries)(decorated)
        
        if clear_queue:
            decorated = with_queue_clearing(decorated)
            
        return decorated
    
    return decorator

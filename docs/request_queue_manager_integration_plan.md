# Request Queue Manager Integration Plan

## Overview

This document outlines a comprehensive plan for integrating request queue management capabilities into the AI Dev Toolkit core architecture. Rather than creating separate components, this plan focuses on enhancing existing structures to maintain architectural integrity and ensure professional integration.

## Goals

1. Resolve timeout issues in MCP server requests
2. Prevent request queue buildups
3. Provide tools to monitor and manage the request queue
4. Maintain architectural consistency with the existing codebase
5. Ensure backward compatibility

## Analysis of Existing Architecture

Before implementation, we need to understand the current architecture:

### Key Components

1. **MonitoringPauser Class**: Used to pause file monitoring during operations
2. **MCP Server Implementation**: Handles tool requests and responses
3. **Enhanced Edit File Implementation**: Already implements timeout and error handling

### Architectural Patterns

The toolkit uses several patterns we should follow:
- Context managers for resource management
- Singleton patterns for system-wide services
- Thread-safety mechanisms for concurrent operations
- Hierarchical logging

## Detailed Integration Plan

### Phase 1: Core Implementation

#### 1.1 Enhance MonitoringPauser

Extend the existing `MonitoringPauser` context manager to include request tracking:

```python
class MonitoringPauser:
    """
    Context manager that pauses file monitoring and tracks request execution.
    """
    
    def __init__(self, description=None, timeout=60.0):
        self.description = description
        self.timeout = timeout
        self.request_id = None
        
    def __enter__(self):
        # Existing monitoring pause code
        pause_monitoring()
        
        # Add request tracking
        if TRACKING_ENABLED:
            self.request_id = register_request(self.description, self.timeout)
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Complete the request
        if TRACKING_ENABLED and self.request_id:
            complete_request(self.request_id)
        
        # Existing monitoring resume code
        resume_monitoring()
```

#### 1.2 Add Request Tracking to server.py

Add request tracking capabilities directly to the server.py file:

```python
# In server.py

# Request tracking state
_active_requests = {}
_request_lock = threading.RLock()

def register_request(description, timeout=60.0):
    """Register a new request with a timeout."""
    request_id = str(uuid.uuid4())
    with _request_lock:
        _active_requests[request_id] = {
            'start_time': time.time(),
            'description': description,
            'timeout': timeout
        }
    return request_id

def complete_request(request_id):
    """Mark a request as completed."""
    with _request_lock:
        if request_id in _active_requests:
            _active_requests.pop(request_id)
            return True
    return False
```

#### 1.3 Add Request Monitoring Thread

Add a monitoring thread to detect stale requests:

```python
# In server.py

def _start_request_monitor():
    """Start the request monitoring thread."""
    def monitor_loop():
        while True:
            _check_stale_requests()
            time.sleep(5)  # Check every 5 seconds
            
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    
def _check_stale_requests():
    """Check for stale requests and log warnings."""
    current_time = time.time()
    with _request_lock:
        for request_id, info in list(_active_requests.items()):
            elapsed = current_time - info['start_time']
            if elapsed > info['timeout']:
                logger.warning(f"Stale request detected: {info['description']} (ID: {request_id})")
                logger.warning(f"  Elapsed time: {elapsed:.2f}s, Timeout: {info['timeout']}s")
```

### Phase 2: MCP Tool Integration

#### 2.1 Add Request Management MCP Tools

Add tools to manage the request queue:

```python
@mcp.tool()
def clear_request_queue() -> Dict[str, Any]:
    """
    Clear all pending requests in the MCP server queue.
    
    Returns:
        Dictionary with information about the cleared requests
    """
    active_requests = {}
    with _request_lock:
        active_requests = _active_requests.copy()
        count = len(_active_requests)
        _active_requests.clear()
        
    return {
        "status": "success",
        "message": f"Cleared {count} pending requests",
        "count": count,
        "requests": [
            {"id": req_id, "description": info["description"]}
            for req_id, info in active_requests.items()
        ]
    }

@mcp.tool()
def get_request_status() -> Dict[str, Any]:
    """
    Get the status of all active requests in the MCP server.
    
    Returns:
        Dictionary with information about active requests
    """
    current_time = time.time()
    active_requests = {}
    
    with _request_lock:
        active_requests = _active_requests.copy()
        
    request_info = [
        {
            "id": req_id,
            "description": info["description"],
            "elapsed_seconds": current_time - info["start_time"],
            "timeout_seconds": info["timeout"]
        }
        for req_id, info in active_requests.items()
    ]
    
    return {
        "status": "success",
        "active_request_count": len(active_requests),
        "requests": request_info
    }
```

#### 2.2 Enhance Tool Decorator

Modify the MCP tool decorator to automatically track requests:

```python
# Enhance the mcp.tool decorator
original_tool_decorator = mcp.tool

def enhanced_tool_decorator(*args, **kwargs):
    """Enhanced tool decorator that adds request tracking."""
    original_decorator = original_tool_decorator(*args, **kwargs)
    
    def wrapper(func):
        @functools.wraps(func)
        def wrapped_tool(*tool_args, **tool_kwargs):
            # Extract function name and arguments for description
            func_name = func.__name__
            description = f"{func_name}({', '.join(map(str, tool_args))})"
            
            # Use MonitoringPauser with request tracking
            with MonitoringPauser(description=description, timeout=120.0):
                return func(*tool_args, **tool_kwargs)
        
        return original_decorator(wrapped_tool)
    
    return wrapper

# Replace the original decorator
mcp.tool = enhanced_tool_decorator
```

### Phase 3: GUI Integration

#### 3.1 Add Request Management Buttons to Dashboard

Add buttons to the Dashboard tab of the GUI:

```python
# In the setup_dashboard method of the GUI class

# Create a frame for request management
request_frame = ttk.LabelFrame(
    actions_frame, 
    text="Request Management",
    padding="5 5 5 5"
)
request_frame.pack(fill=tk.X, pady=(10, 5), padx=5)

# Add Clear Request Queue button
ttk.Button(
    request_frame,
    text="Clear Request Queue",
    command=self.clear_request_queue
).pack(fill=tk.X, pady=2, padx=5)

# Add Check Queue Status button
ttk.Button(
    request_frame,
    text="Check Queue Status",
    command=self.check_request_status
).pack(fill=tk.X, pady=2, padx=5)
```

#### 3.2 Add Request Management Methods to GUI

Add methods to handle the button actions:

```python
def clear_request_queue(self):
    """Clear all pending requests."""
    try:
        # Call the MCP tool directly
        # Import only when needed to avoid circular imports
        from aitoolkit.librarian.server import clear_request_queue
        
        result = clear_request_queue()
        
        # Show a message
        messagebox.showinfo(
            "Request Queue Cleared",
            f"Successfully cleared {result['count']} pending requests."
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Failed to clear request queue: {str(e)}"
        )

def check_request_status(self):
    """Check the status of all requests."""
    try:
        # Call the MCP tool directly
        from aitoolkit.librarian.server import get_request_status
        
        result = get_request_status()
        count = result['active_request_count']
        
        # Format the message
        if count == 0:
            message = "No active requests in the queue."
        else:
            requests_str = "\n".join([
                f"• {req['description']} - {req['elapsed_seconds']:.1f}s elapsed"
                for req in result['requests']
            ])
            message = f"{count} active requests in the queue:\n\n{requests_str}"
        
        # Show a message
        messagebox.showinfo(
            "Request Queue Status",
            message
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Failed to check request queue status: {str(e)}"
        )
```

### Phase 4: Error Handling Enhancement

#### 4.1 Enhance Tool Error Handling with Timeouts

Improve the error handling for all tools to include timeout handling:

```python
def tool_with_timeout(func, timeout=60.0):
    """Wrap a tool function with timeout handling."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Start a timer
            start_time = time.time()
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Check execution time
            elapsed = time.time() - start_time
            if elapsed > timeout * 0.9:  # 90% of timeout
                logger.warning(f"Tool {func.__name__} took {elapsed:.2f}s (close to timeout of {timeout}s)")
                
            return result
            
        except Exception as e:
            # Check if this might be a timeout
            elapsed = time.time() - start_time
            if elapsed > timeout * 0.8:  # 80% of timeout
                logger.error(f"Possible timeout in {func.__name__}: {elapsed:.2f}s (timeout: {timeout}s)")
            
            # Re-raise the exception
            raise
    
    return wrapper
```

#### 4.2 Apply Timeout Wrapper to Existing Tools

```python
# Apply timeout wrapper to all tool functions
for name in dir(server_module):
    attr = getattr(server_module, name)
    if callable(attr) and hasattr(attr, '__wrapped__'):
        # It's a tool function
        # Set an appropriate timeout based on the function
        if "edit_file" in name:
            timeout = 120.0  # 2 minutes for file edits
        elif "read_file" in name:
            timeout = 30.0  # 30 seconds for file reads
        else:
            timeout = 60.0  # Default 1 minute timeout
            
        # Wrap the function
        setattr(server_module, name, tool_with_timeout(attr, timeout))
```

### Phase 5: Testing and Validation

#### 5.1 Unit Tests for Request Management

Create unit tests to verify:
- Request tracking functionality
- Timeout detection
- Queue management tools
- GUI integration

```python
def test_request_tracking():
    """Test request tracking functionality."""
    # Register a request
    request_id = register_request("Test request", 10.0)
    
    # Verify it was registered
    with _request_lock:
        assert request_id in _active_requests
        
    # Complete the request
    assert complete_request(request_id)
    
    # Verify it was removed
    with _request_lock:
        assert request_id not in _active_requests
```

#### 5.2 Integration Tests with Existing Tools

Test integration with existing tools:

```python
def test_tool_with_timeout():
    """Test tool timeout behavior."""
    # Create a test tool that takes longer than timeout
    @tool_with_timeout
    def slow_tool():
        time.sleep(2.0)  # 2 seconds
        return "Done"
    
    # Set a short timeout
    slow_tool.timeout = 1.0  # 1 second
    
    # Execute with timeout tracking
    try:
        slow_tool()
        assert False, "Should have raised an exception"
    except Exception:
        # Should raise a timeout exception
        pass
```

### Phase 6: Documentation

#### 6.1 Update Internal Documentation

Update the internal documentation to explain:
- Request tracking architecture
- Timeout handling
- Integration with existing components

```markdown
## Request Tracking Architecture

The AI Dev Toolkit now includes robust request tracking to prevent timeout issues.
This functionality is integrated with the existing `MonitoringPauser` class to ensure
architectural consistency.

### Key Components:

1. **Enhanced MonitoringPauser**: Tracks requests along with file monitoring
2. **Request Queue Management**: Monitors for stale requests
3. **Timeout Handling**: Ensures tools don't run indefinitely
```

#### 6.2 Update User-Facing Documentation

Update the user-facing documentation to explain:
- New GUI features
- New MCP tools
- How to handle timeout issues

```markdown
## Request Queue Management

The AI Dev Toolkit now includes tools to manage the request queue:

### GUI Features:

- **Clear Request Queue**: Clears all pending requests
- **Check Queue Status**: Shows information about active requests

### MCP Tools:

- **clear_request_queue**: Clears all pending requests
- **get_request_status**: Shows information about active requests

### Handling Timeout Issues:

If you're experiencing timeout issues:

1. Use the "Check Queue Status" button to see if there are any stuck requests
2. Use the "Clear Request Queue" button to clear the queue
3. Restart the MCP server if issues persist
```

## Implementation Timeline

1. **Phase 1 (Core Implementation)**: 2 days
2. **Phase 2 (MCP Tool Integration)**: 1 day
3. **Phase 3 (GUI Integration)**: 1 day
4. **Phase 4 (Error Handling Enhancement)**: 2 days
5. **Phase 5 (Testing and Validation)**: 2 days
6. **Phase 6 (Documentation)**: 1 day

**Total Estimated Time**: 9 days

## Risk Assessment

### Potential Issues:

1. **Thread Safety**: Ensure all operations are thread-safe to avoid race conditions
2. **Performance Impact**: Monitor for any performance degradation from request tracking
3. **Backward Compatibility**: Ensure existing tools continue to function correctly
4. **Error Handling**: Consider edge cases where timeouts overlap with other errors

### Mitigation Strategies:

1. Use proper synchronization primitives (locks, atomic operations)
2. Implement lightweight tracking with minimal overhead
3. Thoroughly test with existing functionality
4. Design comprehensive error handling with clear messages

## Conclusion

This integration plan provides a professional approach to enhancing the AI Dev Toolkit with request queue management capabilities. By integrating directly with existing architectural components rather than adding separate modules, we maintain the integrity of the codebase while adding essential functionality.

The implementation follows the project's established patterns and practices, ensuring a clean and maintainable enhancement that addresses the timeout issues without introducing unnecessary complexity or potential points of failure.

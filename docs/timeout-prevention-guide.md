# Timeout Prevention Guide

This guide addresses the common timeout issues experienced with the AI Dev Toolkit MCP server and provides solutions.

## Common Causes of Timeouts

1. **Excessive Background Threads**
   - Unified Context update thread running every 5 minutes
   - Multiple TaskBoard worker threads processing tasks
   - Orphaned task handler threads that don't terminate

2. **Resource Contention**
   - Too many concurrent operations
   - Circular imports causing deadlocks
   - File system operations blocking each other

3. **Thread Leakage**
   - Tasks that timeout leave threads running
   - Daemon threads not properly cleaned up
   - No limit on concurrent operations

## Applied Fixes

### 1. Unified Context Update Optimization
- Increased update interval from 5 to 30 minutes
- Made threads non-daemon for proper cleanup
- Added resource monitoring

### 2. TaskBoard Thread Management
- Reduced default workers from 4 to 2
- Added thread tracking for cleanup
- Implemented task cancellation flags

### 3. Timeout Configuration
Created `config/mcp_timeout_config.json` with:
- Extended default timeout to 2 minutes
- File operations timeout to 3 minutes  
- Background task controls

### 4. Resource Monitoring
Added simple resource monitor to track:
- Active operation count
- Thread lifecycle
- Resource warnings

## Recommended Settings

```json
{
  "mcp_timeout": {
    "default_timeout_ms": 120000,
    "file_operations_timeout_ms": 180000,
    "background_tasks": {
      "unified_context_update_interval": 1800,
      "taskboard_workers": 2,
      "task_default_timeout": 300
    }
  }
}
```

## Manual Adjustments

If timeouts persist:

1. **Reduce Worker Threads**
   ```python
   # In task_board.py
   def __init__(self, project_path: str, num_workers: int = 1):
   ```

2. **Disable Background Updates**
   ```python
   # In unified_context_integration.py
   # Comment out: update_thread.start()
   ```

3. **Increase Claude Desktop Timeout**
   In Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "ai-librarian": {
         "timeout": 180000
       }
     }
   }
   ```

## Monitoring

Watch for these signs:
- Tools timing out after 3-4 uses
- Server becoming unresponsive
- High CPU usage from Python processes

## Testing

After applying fixes:
1. Restart the AI Librarian server
2. Test file operations repeatedly
3. Monitor task completion times
4. Check thread count doesn't grow

## Emergency Recovery

If server becomes unresponsive:
1. Kill the Python process
2. Clear the TaskBoard queue
3. Restart with minimal workers
4. Gradually increase concurrency

## Future Improvements

Consider implementing:
- Connection pooling
- Better thread lifecycle management
- Automatic resource throttling
- Health check endpoints
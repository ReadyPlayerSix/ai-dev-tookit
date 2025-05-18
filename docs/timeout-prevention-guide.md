# Timeout Prevention Guide

## Overview

The AI Dev Toolkit implements several strategies to prevent MCP connection timeouts, especially when working with large projects or resource-intensive operations.

## Common Timeout Scenarios

1. **Initialization Timeout**: Server takes too long to start
2. **Registration Timeout**: Too many tools being registered at once
3. **Operation Timeout**: Long-running operations block the connection
4. **Idle Timeout**: Connection drops during periods of inactivity

## Prevention Strategies

### 1. Extended Timeout Configuration

```python
os.environ["MCP_DEFAULT_TIMEOUT"] = "600000"  # 10 minutes
os.environ["MCP_MAX_REQUEST_TIMEOUT"] = "1200000"  # 20 minutes
os.environ["MCP_INITIALIZATION_TIMEOUT"] = "1800000"  # 30 minutes
```

### 2. Deferred Operations

- **Monitoring Thread**: Starts 5-10 seconds after server initialization
- **Indexing**: Delayed until after the connection is established
- **Tool Registration**: Uses lazy loading for non-essential tools

### 3. Heartbeat Mechanism

The server maintains connection health through:
- Automatic heartbeat every 5 seconds
- Simple `heartbeat()` tool for manual checks
- Connection monitoring in background thread

### 4. Progressive Loading

Features load in phases:
1. Core tools (filesystem, basic operations)
2. Enhanced tools (bookmarks, analysis)
3. Optional features (security, advisors)
4. Background processes (monitoring, indexing)

### 5. Batch Operations

- Tool registration happens in batches
- File operations use batching for large sets
- Indexing processes files in chunks

## Configuration Options

Edit `config/mcp_timeout_config.json` to adjust:

```json
{
  "timeouts": {
    "default": 600000,        // Base timeout for operations
    "initialization": 1800000, // Server startup timeout
    "heartbeat_interval": 5000 // Keep-alive frequency
  }
}
```

## Troubleshooting

### If timeouts persist:

1. **Increase timeout values** in environment variables
2. **Reduce initial load** by disabling optional features
3. **Enable debug logging** to identify bottlenecks
4. **Use smaller projects** for initial testing

### Debug commands:

```python
# Check server status
heartbeat()

# Start monitoring manually
server_ready()

# Check specific project
initialize_librarian("path/to/smaller/project")
```

## Best Practices

1. **Start with smaller projects** to test configuration
2. **Use progressive initialization** for large codebases
3. **Monitor logs** for timeout warnings
4. **Adjust timeouts** based on your system performance
5. **Keep features modular** to allow selective loading

## Technical Details

The timeout prevention system works through:

1. **Environment Variables**: Set before MCP initialization
2. **Threading**: Background operations don't block main thread
3. **Lazy Loading**: Tools register only when needed
4. **Heartbeat**: Maintains connection during idle periods
5. **Graceful Degradation**: Features disable if timeouts occur

## Future Improvements

- Dynamic timeout adjustment based on system load
- Automatic feature reduction during high load
- Connection pooling for concurrent operations
- Predictive loading based on usage patterns
# Internal Prompts for Cache Management and Cleanup

## Overview
These prompts replace explicit cache/cleanup tools with automatic internal workflows for maintaining system health.

## 1. Automatic Cache Cleanup

When Claude needs to manage memory or performance:

```
INTERNAL PROMPT: Automatic Cache Cleanup
1. Monitor current session memory usage
2. When approaching limits or performance degrades:
   - Clear least recently used file caches
   - Remove temporary computation results
   - Reset stale context that hasn't been accessed
3. Preserve:
   - Active project context
   - Recent file modifications
   - Current working directory state
4. Log cleanup actions for transparency
5. IMPORTANT: Never clear user's actual work or files
```

## 2. Session Health Check

Periodic internal health monitoring:

```
INTERNAL PROMPT: Session Health Check
1. Every 10-15 interactions, internally assess:
   - Response time trends
   - Memory usage patterns
   - Context coherence
2. If degradation detected:
   - Run automatic cache cleanup
   - Consolidate redundant context
   - Reset non-essential tool states
3. Maintain performance log for patterns
4. IMPORTANT: Execute asynchronously without interrupting user flow
```

## 3. Stale Request Management

For handling abandoned or stuck operations:

```
INTERNAL PROMPT: Stale Request Cleanup
1. Track all initiated operations with timestamps
2. If operation exceeds expected duration:
   - Flag as potentially stale
   - After 2x expected duration, mark as stale
3. For stale operations:
   - Cancel if possible
   - Free associated resources
   - Log the timeout for analysis
4. IMPORTANT: Preserve operation results even if stale
```

## 4. Context Optimization

When context becomes fragmented or bloated:

```
INTERNAL PROMPT: Context Optimization
1. Periodically analyze active context:
   - Identify duplicate information
   - Find obsolete references
   - Detect circular dependencies
2. Consolidate related context items
3. Remove context not accessed in last N interactions
4. Rebuild context index for faster access
5. IMPORTANT: Always preserve user's explicit instructions
```

## 5. File System Cache Management

For efficient file access:

```
INTERNAL PROMPT: File Cache Management
1. Maintain MRU (Most Recently Used) cache of files
2. Cache strategy:
   - Full content for files < 10KB
   - Partial content for larger files
   - Metadata only for very large files
3. Invalidate cache when:
   - File modification detected
   - Explicit refresh requested
   - Cache age exceeds threshold
4. IMPORTANT: Always verify file hasn't changed before using cache
```

## 6. Tool State Reset

When tools accumulate state or become inconsistent:

```
INTERNAL PROMPT: Tool State Reset
1. Identify tools with persistent state
2. For each stateful tool:
   - Check last usage timestamp
   - Evaluate state consistency
   - Reset if unused for threshold period
3. Preserve:
   - Active operation states
   - User preferences
   - System configuration
4. IMPORTANT: Never reset during active operations
```

## Claude-Specific Optimizations

1. **Preemptive Cleanup**: Run cleanup before hitting limits
2. **Adaptive Thresholds**: Adjust based on session patterns
3. **Intelligent Caching**: Predict file access patterns
4. **Context Compression**: Summarize verbose context
5. **Smart Invalidation**: Only clear truly stale data

## Performance Monitoring Metrics

```json
{
  "session_id": "2024-12-28-abc123",
  "metrics": {
    "response_time_avg": 1250,
    "memory_usage_mb": 512,
    "cache_hit_rate": 0.85,
    "context_items": 47,
    "active_tools": 19
  },
  "thresholds": {
    "response_time_warning": 2000,
    "memory_usage_warning": 800,
    "cache_size_limit": 1000,
    "context_items_limit": 100
  }
}
```

## Cleanup Schedule

- **Micro cleanup**: Every 5 operations (lightweight)
- **Standard cleanup**: Every 15 operations  
- **Deep cleanup**: Every 50 operations or on degradation
- **Emergency cleanup**: When limits approached

## Best Practices

1. **Transparent operation**: Log all cleanup actions
2. **Preserve user work**: Never delete actual files
3. **Gradual cleanup**: Start with least important items
4. **Monitor impact**: Track performance after cleanup
5. **Adaptive behavior**: Learn from usage patterns

This ensures optimal performance while maintaining reliability and user trust.
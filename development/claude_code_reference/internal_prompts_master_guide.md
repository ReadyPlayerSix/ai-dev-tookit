# Master Guide for Internal Prompts

## Overview
This guide consolidates all internal prompts that replace explicit tools, reducing the active tool count while maintaining functionality through structured internal workflows.

## Tool Consolidation Strategy

### Tools to Keep (19 total)
These remain as explicit MCP tools:
- query_component
- find_implementation  
- read_file
- read_multiple_files
- edit_file
- enhanced_edit_file
- move_file
- search_files
- write_file
- find_related_files
- create_directory
- directory_tree
- get_file_info
- think
- deep_analysis
- list_allowed_directories
- check_project_access

### Tools Replaced by Internal Prompts (29 total)
These are handled through internal workflows:

1. **Bookmark Management** (6 tools → internal prompts)
   - See: internal_prompts_bookmarks.md

2. **TODO Management** (5 tools → internal prompts)
   - See: internal_prompts_todos.md

3. **Cache & Cleanup** (7 tools → automatic)
   - See: internal_prompts_cache_cleanup.md

4. **TaskBoard** (6 tools → deep_analysis integration)
   - See: internal_prompts_deep_analysis.md

5. **Miscellaneous** (5 tools → context/automatic)
   - Git operations → automated in relevant commands
   - Tool reference → integrated into help system
   - Initialization → automatic on startup

### Enhanced File Operations
While keeping file operation tools, we optimize their usage:
- See: internal_prompts_file_operations.md

## Implementation Guidelines

### 1. Timing and Patience
- **Allow operations to complete** before proceeding
- **Check for confirmations** after write operations
- **Batch related operations** for efficiency
- **Use timeouts** to prevent hanging

### 2. Error Handling
```
INTERNAL PATTERN: Safe Operation
1. Verify prerequisites (paths exist, permissions, etc.)
2. Execute operation with error catching
3. Confirm success before proceeding
4. Provide meaningful error messages
5. Suggest alternatives on failure
```

### 3. State Management
- **Use file system** for persistence (.ai_reference/)
- **JSON format** for structured data
- **Consistent naming** for easy retrieval
- **Atomic operations** to prevent corruption

### 4. Performance Optimization
- **Lazy loading**: Only read what's needed
- **Batch operations**: Use read_multiple_files
- **Cache strategically**: Reuse recent reads
- **Async when appropriate**: Long operations

## Claude-Specific Instructions

### Initialization Sequence
```
ON SESSION START:
1. Check .ai_reference/ directory exists
2. Load project configuration if available
3. Initialize internal caches
4. Set up monitoring for cleanup triggers
5. Ready for user interaction
```

### Request Processing Flow
```
FOR EACH USER REQUEST:
1. Identify if internal prompt applies
2. If yes: Follow internal workflow
3. If no: Use appropriate MCP tool
4. Always provide clear feedback
5. Log significant actions
```

### Performance Monitoring
```
CONTINUOUSLY MONITOR:
- Response times
- Memory usage  
- Cache efficiency
- Error rates
Trigger cleanup when thresholds exceeded
```

## Directory Structure

```
project/
├── .ai_reference/
│   ├── bookmarks/
│   ├── todos/
│   ├── tasks/
│   ├── cache/
│   ├── config/
│   └── logs/
├── src/
└── ...
```

## Example Workflows

### Creating and Using a Bookmark
1. User: "Bookmark this function"
2. Claude: [Internal prompt: Create Bookmark]
3. Claude: Creates bookmark file in .ai_reference/bookmarks/
4. Claude: "Bookmarked login function at line 45"
5. Later - User: "Go to my login bookmark"
6. Claude: [Internal prompt: Apply Bookmark]
7. Claude: Reads bookmark and shows code

### Managing TODOs
1. User: "Add TODO: fix authentication bug"
2. Claude: [Internal prompt: Add TODO]
3. Claude: Creates TODO file with high priority
4. Claude: "Added TODO with ID: 20241228_auth_fix"
5. User: "Show my TODOs"
6. Claude: [Internal prompt: List TODOs]
7. Claude: Reads and formats TODO list

### Running Deep Analysis
1. User: "Analyze this module for security issues"
2. Claude: [Internal prompt: Deep Analysis]
3. Claude: Creates analysis task, returns ID
4. Claude: "Started security analysis (ID: sec_123)"
5. User: "Check analysis status"
6. Claude: [Internal prompt: Check Analysis Status]
7. Claude: Shows progress and partial results

## Success Metrics

1. **Reduced timeout errors** by staying under 30 tools
2. **Improved response times** through batching
3. **Better error messages** from structured workflows
4. **Consistent behavior** across sessions
5. **Cleaner codebase** with fewer explicit tools

## Migration Path

1. **Phase 1**: Implement internal prompts alongside existing tools
2. **Phase 2**: Test internal prompts thoroughly
3. **Phase 3**: Deprecate old tools gradually
4. **Phase 4**: Remove old tool code
5. **Phase 5**: Monitor and optimize

This approach ensures smooth operation while significantly reducing the tool count and improving performance.
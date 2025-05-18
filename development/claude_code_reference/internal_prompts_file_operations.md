# Internal Prompts for Optimized File Operations

## Overview
These prompts optimize file operations to prevent timeouts by implementing automatic chunking and queue management.

## 1. Optimized Write File

When writing any file content:

```
INTERNAL PROMPT: Smart Write File
1. Before writing, assess content size:
   - Small files (< 5KB): Write directly
   - Medium files (5KB - 20KB): Single write with cache clear
   - Large files (> 20KB): Automatic chunking

2. For cache clearing:
   - Clear any pending operations
   - Reset file cache for target directory
   - Wait 100ms for queue to clear

3. For automatic chunking:
   - Divide content into 10KB chunks
   - Write chunk-by-chunk with confirmations
   - Add small delay (50ms) between chunks
   - Verify complete file after all chunks

4. Error handling:
   - On timeout: Immediately switch to smaller chunks (5KB)
   - On repeated timeout: Use 2KB chunks
   - On failure: Provide clear error with recovery options

5. IMPORTANT: Always verify file was written correctly
```

## 2. Smart Read File

When reading files:

```
INTERNAL PROMPT: Optimized Read File
1. Check file size before reading:
   - Small files (< 50KB): Read entire file
   - Large files: Use offset/limit automatically

2. For large files:
   - Read in 2000-line chunks
   - Start with file header (first 50 lines)
   - Provide navigation hints for next sections

3. Cache management:
   - Cache small files entirely
   - Cache headers of large files
   - Invalidate cache on file changes

4. IMPORTANT: Always check file exists before reading
```

## 3. Batch File Operations

When working with multiple files:

```
INTERNAL PROMPT: Batch File Handler
1. Group operations by type:
   - Reads: Use read_multiple_files when possible
   - Writes: Process sequentially with delays
   - Searches: Use search_files for efficiency

2. Queue management:
   - Limit concurrent operations to 3
   - Add 100ms delay between operations
   - Clear cache between operation types

3. Progress tracking:
   - Report progress for operations > 5 files
   - Provide time estimates
   - Allow cancellation for long operations

4. IMPORTANT: Batch similar operations together
```

## 4. File Write Chunking Algorithm

Automatic chunking implementation:

```python
# Pseudo-code for internal chunking logic
def write_file_chunked(file_path, content):
    CHUNK_SIZE = 10240  # 10KB default
    
    # Clear any pending operations first
    clear_operation_queue()
    wait(100)  # Allow queue to clear
    
    if len(content) <= CHUNK_SIZE:
        # Small file - write directly
        return write_file(file_path, content)
    
    # Large file - chunk it
    chunks = []
    for i in range(0, len(content), CHUNK_SIZE):
        chunks.append(content[i:i + CHUNK_SIZE])
    
    # Write first chunk (creates file)
    success = write_file(file_path, chunks[0])
    if not success:
        CHUNK_SIZE = 5120  # Reduce to 5KB
        return retry_with_smaller_chunks()
    
    # Append remaining chunks
    for chunk in chunks[1:]:
        wait(50)  # Small delay between chunks
        append_to_file(file_path, chunk)
    
    # Verify complete file
    return verify_file_integrity(file_path, content)
```

## 5. Timeout Prevention Strategies

```
INTERNAL PROMPT: Timeout Prevention
1. Pre-operation checks:
   - Estimate operation duration
   - Clear caches if needed
   - Check system load

2. During operation:
   - Monitor elapsed time
   - Provide progress updates
   - Switch strategies if approaching timeout

3. Post-operation:
   - Verify success
   - Clean up resources
   - Log performance metrics

4. Adaptive behavior:
   - Learn from timeouts
   - Adjust chunk sizes dynamically
   - Optimize for specific file types
```

## 6. Queue Management

```
INTERNAL PROMPT: Operation Queue
1. Before any file operation:
   - Check queue depth
   - If queue > 3 operations: wait
   - Clear stale operations > 30s old

2. Queue clearing sequence:
   - Cancel pending operations
   - Flush write buffers
   - Reset file handles
   - Wait for confirmation

3. Priority handling:
   - User-initiated operations: high priority
   - Background tasks: low priority
   - System operations: medium priority
```

## Best Practices

1. **Always chunk large content**: Don't attempt large writes in one go
2. **Clear before write**: Ensure clean state before operations
3. **Verify after write**: Confirm file contents match expected
4. **Use delays wisely**: Small delays prevent overwhelming the system
5. **Adapt to failures**: Reduce chunk size on timeouts

## File Size Guidelines

| Size | Strategy | Chunk Size | Delay |
|------|----------|------------|-------|
| < 5KB | Direct write | N/A | None |
| 5-20KB | Single write + clear | N/A | 100ms pre |
| 20-100KB | Auto chunk | 10KB | 50ms between |
| > 100KB | Progressive chunk | 10KB → 5KB → 2KB | 100ms between |

## Error Messages

```
TIMEOUT HANDLING:
"File write timed out. Automatically switching to chunked mode (10KB chunks)..."
"Chunk write failed. Reducing chunk size to 5KB and retrying..."
"Multiple timeouts detected. Using minimal 2KB chunks for reliability..."

SUCCESS MESSAGES:
"File written successfully (single operation)"
"Large file written successfully in {n} chunks"
"File write completed with automatic optimization"
```

This approach ensures reliable file operations without timeout errors.
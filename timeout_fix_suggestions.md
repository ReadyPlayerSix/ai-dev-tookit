# MCP Server Timeout Fix Suggestions

## Common Causes of MCP Timeouts

### 1. Import Issues (Like we fixed)
- Circular imports or missing modules can cause initialization to hang
- The MCPConnector import error we fixed could have been blocking proper initialization

### 2. Blocking Operations During Startup
```python
# In server.py, these environment variables help but may not be enough:
os.environ["MCP_DEFAULT_TIMEOUT"] = "300000"  # 5 minutes
os.environ["MCP_MAX_REQUEST_TIMEOUT"] = "600000"  # 10 minutes
os.environ["MCP_INITIALIZATION_TIMEOUT"] = "1200000"  # 20 minutes
os.environ["MCP_REGISTRATION_TIMEOUT"] = "600000"  # 10 minutes
os.environ["MCP_LAZY_TOOL_REGISTRATION"] = "true"  # This is good
```

### 3. Tool Registration Bottlenecks
The server registers many tools at startup which can cause timeouts:
- Unified Context tools
- TaskBoard tools
- Security Analyzer tools
- Core librarian tools

### Recommended Fixes

1. **Add startup diagnostics**:
```python
import time
startup_time = time.time()

def log_startup_phase(phase):
    elapsed = time.time() - startup_time
    logger.info(f"Startup phase '{phase}' at {elapsed:.2f}s")
```

2. **Defer heavy initialization**:
```python
# Instead of initializing everything at startup
def lazy_initialize_project(project_path):
    """Initialize project data only when first accessed"""
    if project_path not in librarian_context["projects"]:
        # Initialize here
        pass
```

3. **Add timeout recovery**:
```python
@mcp.tool()
def initialize_librarian(project_path: str):
    """Initialize with timeout protection"""
    try:
        with timeout(30):  # 30 second timeout
            # Initialization code
            pass
    except TimeoutError:
        logger.error(f"Initialization timeout for {project_path}")
        # Return partial initialization
        return {"status": "partial", "message": "Initialization timed out"}
```

4. **Batch tool registration**:
```python
# Register tools in phases
async def register_tools_phased():
    # Phase 1: Core tools only
    register_core_tools()
    
    # Phase 2: Optional tools after startup
    asyncio.create_task(register_optional_tools())
```

5. **Add connection health check**:
```python
@mcp.tool()
def health_check():
    """Simple health check that responds quickly"""
    return {"status": "ok", "timestamp": time.time()}
```

## Most Likely Issue

The import error we fixed was probably causing a cascade of initialization failures. When Python can't import a module, it can leave the import system in an inconsistent state, especially with circular dependencies. This could explain why it took multiple restarts to clear.

## Prevention

1. Add import validation at startup
2. Use lazy loading for optional components
3. Add timeout protection around all initialization
4. Log startup phases for debugging
5. Implement graceful degradation when components fail
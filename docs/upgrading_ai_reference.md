# Upgrading Projects with Older .ai_reference Directories

When working with projects that have older versions of the `.ai_reference` directory, you can update them to use the latest AI Dev Toolkit features, including the improved timeout mechanisms for write and search operations.

## Quick Upgrade Method

The simplest way to upgrade an existing project with an older `.ai_reference` directory is to use the `initialize_ai_dev_toolkit` function:

```python
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Pass your project path
initialize_ai_dev_toolkit("/path/to/your/project")
```

This one-stop function will:
1. Detect your existing `.ai_reference` directory
2. Upgrade it to the latest format
3. Apply the new timeout mechanisms
4. Configure the toolkit with optimal settings

## Manual Steps

If you prefer a more controlled upgrade process, you can follow these steps:

1. **Backup your existing reference directory**:
   ```bash
   cp -r /path/to/your/project/.ai_reference /path/to/your/project/.ai_reference.backup
   ```

2. **Re-initialize the AI Librarian**:
   ```python
   from aitoolkit.librarian.enhanced_indexer import initialize_enhanced_librarian
   initialize_enhanced_librarian("/path/to/your/project")
   ```

3. **Initialize the Tool Reference System** (if needed):
   ```python
   from aitoolkit.librarian.simple_tool_index import initialize_tool_index
   initialize_tool_index("/path/to/your/project")
   ```

4. **Build bidirectional references**:
   ```python
   from aitoolkit.librarian.bidirectional_refs import build_bidirectional_references
   build_bidirectional_references("/path/to/your/project")
   ```

## Adding to CLAUDE.md

To ensure your project always uses the latest timeout mechanisms, add this code at the beginning of your `CLAUDE.md` file:

```python
# Automatically initialize AI Dev Toolkit on startup
import os
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Initialize the toolkit with the current project path
current_dir = os.path.dirname(os.path.abspath(__file__))
initialize_ai_dev_toolkit(current_dir)
```

## Verifying the Upgrade

After upgrading, you can verify that the new timeout mechanisms are in effect by:

1. Looking for the `OPERATION_TIMEOUTS` dictionary in the logs
2. Checking for timeout messages with dynamic values (e.g., "Using 120.0s timeout for search_files")
3. Observing improved reliability in file write and search operations

## Timeouts for Different Operations

The new timeout system uses the following default timeouts:

- **Search operations**: 120 seconds (2 minutes)
- **Write operations**: 120 seconds (2 minutes)
- **Find operations**: 90 seconds (1.5 minutes)
- **Query operations**: 90 seconds (1.5 minutes)
- **Other operations**: 60 seconds (1 minute)

These timeouts can be customized if needed by modifying the `OPERATION_TIMEOUTS` dictionary in your local copy of the AI Dev Toolkit.

# AI Reference System - Usage Guide for Claude

## Overview

The AI Dev Toolkit includes a sophisticated indexing system stored in the `.ai_reference` directory for each project. This document explains how to best utilize this system to avoid performance issues and timeouts.

## Internal Prompts for Claude

### Hierarchical Tool Selection

When working with code, use tools in this order of preference:

1. **Component-Level Tools** - Query the indexed component registry
2. **Index-Based Search** - Use indexed metadata when possible
3. **Direct File Operations** - Only as a last resort for specific paths

```
ALWAYS USE: Query component registry before file system walks
PREFER: Indexed lookups over direct file operations
AVOID: Repeated calls to search_files and read_file across directories
```

### Workflow Decision Trees

Use these decision flows when answering common questions:

#### Finding Implementations
```
User asks "where is X implemented?" →
  1. Check component_registry.json →
  2. Identify specific file path →
  3. Targeted read_file of ONLY that path
```

#### Understanding Code Structure
```
User asks about project structure →
  1. Check project_info in script_index.json →
  2. Reference diagnostics/code_structure.md →
  3. Only list_directories if specific newer details needed
```

#### Searching for Patterns
```
User asks to find all uses of X →
  1. Check dependencies in component_registry.json →
  2. Identify specific files to check →
  3. Targeted read_file for each specific file
```

## Optimized Tool Usage

### Component Registry Access

To access the component registry (fastest approach):

```python
# Load component registry first
registry_path = f"{project_path}/.ai_reference/component_registry.json"
with open(registry_path, 'r') as f:
    registry = json.load(f)

# Find component
component = registry["components"].get(component_name)
if component:
    # Use the primary_file path for targeted file reading
    file_path = component["primary_file"]
    # Now read just this specific file
```

### Script Index Lookup

For finding files containing specific classes/functions:

```python
# Load script index
index_path = f"{project_path}/.ai_reference/script_index.json"
with open(index_path, 'r') as f:
    script_index = json.load(f)

# Search for class/function in the index
matches = []
for file_path, info in script_index["files"].items():
    if target_name in info["classes"] or target_name in info["functions"]:
        matches.append(file_path)
```

### TaskBoard for Long Operations

For operations that might time out:

```python
# Submit as background task instead of direct execution
task_id = submit_background_task(
    task_type="search",
    target_path=project_path,
    pattern=search_pattern
)

# Check status and get results when ready
task_result = get_task_result(task_id)
```

## Performance Optimization Rules

1. **Avoid Directory Walks**: Never walk the file system if the information exists in the index
2. **Use Targeted Reads**: Only read specific files identified by the index
3. **Leverage Component Relationships**: Use dependencies and references from the registry
4. **Submit Long-Running Tasks**: Use TaskBoard for operations that might time out
5. **Cache Results**: Remember recent results to avoid repeated lookups

## Timeout Avoidance Strategies

1. Use the `.ai_reference` index files first and foremost
2. Submit potentially long-running operations through the TaskBoard
3. Break large operations into smaller targeted operations
4. Avoid MonitoringPauser when possible by using indexed data
5. Use read_multiple_files instead of multiple read_file calls

## Git Repository Tracking

The AI Dev Toolkit now includes Git repository tracking functionality. This feature allows the AI to understand the Git history, branches, tags, and repository status, making it easier to work with the codebase.

### Using Git Tracking Tools

There are two main tools for Git tracking:

1. **get_git_info**: Retrieves information about the Git repository
   ```python
   git_info = get_git_info(project_path)
   ```
   This returns a comprehensive overview of the repository, including:
   - Current branch and status
   - Recent commits
   - Available branches
   - Tags
   - Remote repositories
   
   The information is cached to improve performance for repeated calls.

2. **update_git_history**: Creates or updates Git history files in a specified directory
   ```python
   result = update_git_history(project_path, history_dir=".git_history")
   ```
   This creates three files:
   - `git_info.json`: Detailed repository information in JSON format
   - `git_info.txt`: Human-readable summary of the repository
   - `latest_version.txt`: Quick reference showing the latest tag and commit

### Benefits for AI Understanding

These tools help Claude better understand the project by:
- Providing context about recent changes
- Identifying the current branch and commit
- Understanding the repository structure
- Tracking project versions through tags

To make the most of this feature, regularly use the `get_git_info` tool when working with code to ensure Claude has up-to-date repository context.

---

*This guide helps Claude use the AI Reference System effectively, avoiding performance issues and timeouts by leveraging the indexed data structures rather than repeated filesystem operations. It also explains how to utilize Git tracking functionality for improved codebase understanding.*
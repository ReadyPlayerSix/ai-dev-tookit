# AI Dev Toolkit Tools Reference

This document provides a reference for all the tools available in the AI Dev Toolkit.

## File System Tools

### Reading Files

- `read_file(path)` - Read the contents of a file
- `read_multiple_files(paths)` - Read the contents of multiple files
- `get_file_info(path)` - Get metadata about a file

### Writing Files

- `write_file(path, content)` - Create or overwrite a file
- `edit_file(path, edits, dryRun=False)` - Make line-based edits to a file

### Directory Operations

- `create_directory(path)` - Create a directory
- `list_directory(path)` - List the contents of a directory
- `directory_tree(path)` - Get a recursive tree view of files and directories
- `search_files(path, pattern, excludePatterns=[])` - Search for files matching a pattern

### Access Control

- `list_allowed_directories()` - List directories the server has access to
- `check_project_access(project_path)` - Check if the server has access to a directory

## AI Librarian Tools

### Initialization and Management

- `initialize_librarian(project_path)` - Initialize the AI Librarian for a project
- `generate_librarian(project_path)` - Generate or update the AI Librarian for a project

### Code Understanding

- `query_component(project_path, component_name)` - Get information about a component
- `find_implementation(project_path, search_text, file_pattern=None)` - Find code matching a pattern

## Project Management Tools

- `create_project_plan(spec)` - Create a project plan from a specification
- `generate_project_structure(plan)` - Generate a project structure from a plan
- `scaffold_component(spec)` - Generate scaffolding for a component

## Think Tool

- `think(thought)` - Use as a scratchpad to reflect on problems, verify requirements, check rules, or analyze results before taking action

## Prompts

- `ai_librarian_help()` - Get help with the AI Librarian

## Usage Examples

### Working with Files

```python
# Read a file
content = read_file('path/to/file.txt')

# Write a file
write_file('path/to/file.txt', 'Hello, world!')

# Edit a file
edit_file('path/to/file.txt', [
    {'oldText': 'Hello', 'newText': 'Hi'}
])

# List a directory
files = list_directory('path/to/directory')
```

### Using the AI Librarian

```python
# Initialize the AI Librarian
initialize_librarian('path/to/project')

# Query a component
info = query_component('path/to/project', 'MyClass')

# Find implementations
results = find_implementation('path/to/project', 'def process', '*.py')
```

### Creating Projects

```python
# Create a project plan
plan = create_project_plan('Create a web application that...')

# Generate project structure
generate_project_structure(plan)
```

## Error Handling

All tools will return meaningful error messages if they fail. For example:

- File not found
- Permission denied
- Invalid arguments
- Project not initialized

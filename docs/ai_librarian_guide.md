# AI Librarian Guide

The AI Librarian is a key component of the AI Dev Toolkit that provides persistent code understanding capabilities for Claude and other AI assistants.

## What is the AI Librarian?

The AI Librarian analyzes your codebase and creates a structured representation that helps AI assistants:

- Understand the structure of your code
- Track classes, functions, and components 
- Maintain context across conversations
- Monitor code changes in real-time
- Provide more accurate assistance

## How to Use the AI Librarian

### Initialization

Before using the AI Librarian, you need to initialize it for your project:

```python
initialize_librarian("path/to/your/project")
```

This creates a `.ai_reference` directory in your project that contains:

- `component_registry.json` - Registry of all code components
- `script_index.json` - Index of all script files
- `scripts/` - Mini-librarians for individual scripts
- `diagnostics/` - Diagnostic information

### Querying Components

Once initialized, you can query information about specific components:

```python
query_component("path/to/your/project", "ComponentName")
```

This will return detailed information about the component, including:
- File location
- Component type (class or function)
- Source code with line numbers

### Finding Implementations

You can search for specific code patterns:

```python
find_implementation("path/to/your/project", "search_text", "*.py")
```

The third parameter is optional and allows you to filter by file pattern.

### Updating the Librarian

The AI Librarian automatically monitors your project for changes, but you can manually update it:

```python
generate_librarian("path/to/your/project")
```

## Integration with Claude

When using Claude with the AI Dev Toolkit, the AI Librarian provides:

1. **Persistent Context**: Claude remembers your code structure across conversations
2. **Intelligent Navigation**: Claude can quickly locate relevant components
3. **Change Tracking**: Claude stays in sync with your code changes
4. **Improved Understanding**: Claude has deeper insight into your codebase

## How It Works

The AI Librarian:

1. Scans your project for code files
2. Parses each file to identify classes, functions, and imports
3. Generates a "mini-librarian" for each file
4. Creates an index of all scripts
5. Builds a component registry for all classes and functions
6. Monitors your project for changes
7. Updates its understanding when your code changes

## Best Practices

- Initialize the AI Librarian at the root of your project
- Let the AI Librarian monitor your project as you work
- Use specific component names when asking questions
- Refer to file paths relative to your project root

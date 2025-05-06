# AI Librarian: Persistent Context System

The AI Librarian is one of the core components of the AI Dev Toolkit, providing a sophisticated persistent context system that enables Claude to maintain awareness of your codebase across multiple conversations.

## How It Works

### 1. Initialization and Indexing

When you initialize the AI Librarian for a project:

```
initialize_librarian("D:/path/to/your/project")
```

The system:
- Creates a `.ai_reference` directory in your project
- Indexes all Python files in the project
- Creates "mini-librarians" for each file (JSON metadata)
- Builds a component registry of all classes and functions
- Adds the project to active monitoring

### 2. Real-Time Monitoring

Once initialized, the AI Dev Toolkit server:
- Continuously monitors your project files for changes
- Automatically detects when files are added, removed, or modified
- Updates the in-memory representation of your codebase
- Ensures Claude always has access to the most current version

### 3. Persistent Context

Unlike traditional AI interactions where context is lost between sessions, the AI Librarian:
- Maintains a persistent in-memory representation of your codebase
- Preserves this context between different conversations with Claude
- Enables Claude to "remember" your project structure and components
- Saves context state when the server shuts down and restores it on restart

## Benefits

### Improved Assistance

- **More Accurate Responses**: Claude understands your codebase structure, making recommendations more relevant
- **Reduced Context Switching**: No need to re-explain your project in each conversation
- **Higher Quality Code Suggestions**: With a complete understanding of your project, Claude can offer more integrated solutions

### Productivity Enhancement

- **Faster Development**: Spend less time explaining your code structure
- **More Efficient Collaboration**: Claude can instantly locate and reference components across your project
- **Reduced Manual Updates**: No need to manually update Claude on changes to your codebase

## Usage Examples

### Querying Components

```
query_component("D:/path/to/your/project", "MyClass")
```

This will return detailed information about the `MyClass` component, including its code and location. The system automatically uses the in-memory representation for faster lookups.

### Finding Implementations

```
find_implementation("D:/path/to/your/project", "connect_database")
```

This will search your codebase for implementations containing "connect_database" text, efficiently using the context system.

### Updating the Context

```
generate_librarian("D:/path/to/your/project")
```

While the system automatically monitors changes, you can manually trigger an update if needed.

## Technical Details

The persistent context system uses:
- Efficient in-memory caching of code components
- File system monitoring with timestamp tracking
- Import relationship tracking between components
- Automatic project reloading when the server starts

This creates a seamless experience where Claude maintains awareness of your code across multiple conversations, significantly enhancing its ability to assist you with development tasks.

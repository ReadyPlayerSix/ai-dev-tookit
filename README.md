# AI Dev Toolkit

The AI Dev Toolkit is an all-in-one solution for managing Model Context Protocol (MCP) servers and enhancing AI assistants like Claude with advanced development capabilities.

## What is AI Dev Toolkit?

AI Dev Toolkit serves two primary functions:

1. **MCP Server Manager**: A user-friendly interface for configuring, enabling, and managing MCP servers
2. **Development Tools Suite**: A collection of powerful MCP servers for software development tasks

## Key Features

### MCP Server Management

- **Simplified Configuration**: Easy-to-use GUI for managing MCP servers
- **One-Click Setup**: Automatically configure Claude Desktop to use your selected MCP servers
- **External Integration**: Add and manage third-party MCP servers from GitHub or other sources
- **Project Management**: Configure which directories each MCP server can access

### Built-in MCP Servers

- **AI Librarian**: Persistent code comprehension system that analyzes project codebases
- **Project Starter**: Tools for project generation and scaffolding
- **File System Tools**: Secure file operations with configurable access controls
- **Think Tool**: A scratchpad for structured reasoning

## Getting Started

### Installation

#### NPM Installation (Recommended)

```bash
npm install -g ai-dev-toolkit
```

#### Direct Python Installation

```bash
cd ai-dev-toolkit
python scripts/install.py
```

#### GUI Installation

```bash
python scripts/launchers/launch_gui.py
```

### Quick Setup

1. **Launch the GUI**: Run the AI Dev Toolkit configuration interface
2. **Select MCP Servers**: Choose which built-in servers you want to enable
3. **Configure Access**: Add project directories you want the servers to access
4. **Apply Changes**: Click "Apply" to update your Claude Desktop configuration
5. **Restart Claude**: Restart Claude Desktop to apply your changes

## Using AI Dev Toolkit

### AI Librarian

Initialize the AI Librarian for your project to enable persistent code understanding:

```
initialize_librarian("path/to/your/project")
```

The AI Librarian:
- Analyzes your codebase structure
- Builds a component registry
- Tracks code changes in real-time
- Maintains context across conversations
- Enables smarter code-aware responses

See `docs/ai_librarian_guide.md` for more information.

### Project Starter

Create new projects with intelligent scaffolding:

```
create_project_plan("Create a React application with authentication")
```

The Project Starter:
- Creates detailed project plans
- Generates project structures
- Scaffolds components based on specifications
- Follows best practices for various frameworks

### Think Tool

Structured reasoning for complex problems:

```
think("How should I architect a microservice with three components?")
```

## Configuration

The configuration interface allows you to:

1. **Enable/Disable Servers**: Choose which MCP servers to activate
2. **Configure Access**: Manage which directories each server can access
3. **Add External Servers**: Integrate third-party MCP servers from GitHub or other sources
4. **Save Profiles**: Create and switch between different configurations

## Documentation

- `docs/project_structure.md` - Project structure documentation
- `docs/ai_librarian_guide.md` - AI Librarian usage guide
- `docs/tools_reference.md` - Complete reference for all available tools

## Contributing

Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to contribute to the project.

## Security

We take security seriously. Please review our [Security Policy](SECURITY.md) for information about reporting vulnerabilities.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

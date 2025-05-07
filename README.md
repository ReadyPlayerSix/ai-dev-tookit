# AI Dev Toolkit

A comprehensive toolkit for AI-assisted development that enhances Claude's capabilities.

## Features

- **AI Librarian**: Maintains persistent context of your codebase across conversations
- **File System Tools**: Securely access and manipulate files through Claude
- **GUI Configurator**: Easy setup for Claude Desktop integration
- **Project Templates**: Quickly set up new projects with best practices

## Components

### AI Librarian
- Indexes your project code and maintains a comprehensive understanding of components
- Tracks file changes to keep context up to date
- Enables precise code search and navigation
- Preserves context across multiple conversations

### File System Tools
- Read and write files with proper encoding detection
- List directory contents with clear formatting
- Search for files matching specific patterns
- Generate directory trees for visual structure understanding
- Get detailed file information

### GUI Configurator
- Configure Claude Desktop integration with a user-friendly interface
- Enable/disable specific toolkit features
- Set file access permissions
- Manage project settings

## Getting Started

1. Clone this repository
2. Run `python install_to_claude.py` to set up the toolkit with Claude Desktop
3. Launch Claude Desktop and start using the enhanced capabilities

## Configuration

The toolkit can be configured through:
- The GUI configurator: `python aitoolkit/launch_gui.py`
- Direct configuration file editing (see [Configuration Guide](docs/configuration.md))

## Requirements

- Python 3.8+
- Claude Desktop (latest version)

## License

MIT

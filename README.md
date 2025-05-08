# AI Dev Toolkit

A comprehensive toolkit that enhances Claude's capabilities with persistent context, filesystem access, and development tools.

## 🌟 Overview

AI Dev Toolkit integrates with Claude Desktop to provide AI-assisted development capabilities beyond what's available out of the box. The toolkit creates a bridge between your projects and Claude, allowing it to understand your codebase, assist with development tasks, and maintain context across conversations.

## 🚀 Features

### AI Librarian
- **Code Understanding**: Maintains a comprehensive index of your codebase
- **Persistent Context**: Remembers code structure across conversations
- **Component Tracking**: Identifies functions, classes, and modules
- **Smart Search**: Find implementations and references quickly
- **Real-time Updates**: Monitors project changes automatically

### File System Tools
- **Secure File Access**: Controlled access to your project files
- **Directory Management**: List, search, and navigate directories
- **File Operations**: Read from and write to files with proper encoding detection
- **Directory Visualization**: Generate tree views of project structure
- **File Analysis**: Detailed information about files and their contents

### GUI Configurator
- **Easy Setup**: Intuitive interface for toolkit configuration
- **Claude Desktop Integration**: Seamless installation to Claude Desktop
- **Customization**: Enable/disable specific features as needed
- **Directory Management**: Set allowed directories for AI access
- **Visual Feedback**: See active components and configuration status

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Claude Desktop (latest version)
- Git (for cloning the repository)

### Quick Install
```bash
# Clone the repository
git clone https://github.com/isekaizen/ai-dev-toolkit.git
cd ai-dev-toolkit

# Install dependencies
pip install -r requirements.txt

# Install to Claude Desktop
python install_to_claude.py
```

## 📊 Usage

### Basic Usage
1. Launch Claude Desktop after installation
2. AI Dev Toolkit servers will be available automatically
3. Start a conversation with Claude
4. Claude can now access your projects and maintain context

### AI Librarian
```
# Initialize AI Librarian for a project
/initialize_librarian /path/to/your/project

# Search for code implementations
Find implementations of the login function
```

### File System Operations
```
# List files in a directory
Show me the files in /path/to/directory

# Read file content
Show me the content of /path/to/file.py

# Search for files
Find all Python files containing "authentication"
```

## ⚙️ Configuration

### GUI Configuration
The toolkit includes a graphical configuration tool:
```bash
python aitoolkit/launch_gui.py
```

### Manual Configuration
Claude Desktop configuration file is typically located at:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

## 🔍 Troubleshooting

Common issues and solutions:
- **Toolkit Not Appearing in Claude**: Ensure configuration was saved correctly
- **Permission Errors**: Check allowed directories settings
- **Connection Issues**: Verify Claude Desktop is properly configured

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- [Configuration Guide](docs/configuration.md)
- [AI Librarian Documentation](docs/librarian.md)
- [File System Tools Reference](docs/filesystem.md)

## 🙏 Acknowledgements

- Special thanks to the Claude team for making this integration possible
- All contributors who have helped improve the toolkit

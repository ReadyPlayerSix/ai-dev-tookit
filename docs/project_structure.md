# AI Dev Toolkit Project Structure

This document describes the organization of the AI Dev Toolkit codebase.

## Directory Structure

- `aitoolkit/` - Main Python package
  - `gui/` - GUI implementation for the toolkit
  - `librarian/` - AI Librarian implementation
  - `mcp/` - MCP protocol implementation
  - `server/` - MCP server implementation
  - `utils/` - Utility functions

- `config/` - Configuration files and examples
  - `claude_desktop_config_examples.json` - Example configuration for Claude Desktop
  - `ai_librarian_config_example.json` - Example configuration for AI Librarian

- `docs/` - Documentation files
  - `project_structure.md` - This file

- `examples/` - Example projects and usage

- `npm-wrapper/` - NPM package for distribution
  - `bin/` - Binary scripts
  - `package.json` - NPM package definition

- `scripts/` - Utility and launcher scripts
  - `launchers/` - Scripts to launch the server and GUI
  - `rebuild_librarian.py` - Script to rebuild the AI Librarian
  - `run_enhanced_indexer.py` - Script to run the enhanced indexer
  - `gui_installer.py` - GUI installer script
  - `install.py` - Installation script

- `tests/` - Unit tests

## Main Components

1. **AI Librarian** - Persistent code comprehension system
   - Analyzes project codebases
   - Generates mini-librarian files for each code file
   - Maintains a component registry

2. **MCP Server** - Model Context Protocol implementation
   - Provides tools for file operations
   - Exposes AI Librarian functionality
   - Handles prompts and resources

3. **GUI** - User interface
   - Configurator for easy setup
   - Project management

4. **npm-wrapper** - Distribution package
   - Allows installation via NPM
   - Provides convenient CLI commands

## Installation and Usage

The toolkit can be installed and used in several ways:

1. **NPM Installation** (Recommended)
   ```bash
   npm install -g ai-dev-toolkit
   ```

2. **Direct Python Installation**
   ```bash
   cd ai-dev-toolkit
   python scripts/install.py
   ```

3. **GUI Installation**
   ```bash
   python scripts/gui_installer.py
   ```

## Configuration

Configuration is stored in the following files:

- `config/claude_desktop_config_examples.json` - Example configuration for Claude Desktop
- `.ai_reference/` - Directory created in each project for AI Librarian data

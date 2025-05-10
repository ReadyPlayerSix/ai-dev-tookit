# Development Files

This directory contains files that are under development or planned for future releases but are not yet ready for production use.

## Installation and Launcher Files

- `install_librarian.py`: Installation script for adding the AI Librarian to Claude Desktop
- `launch_librarian.py`: Script for launching the standalone AI Librarian server
- `install_to_claude.py`: Alternative installation script for the AI Librarian MCP server
- `launch.py`: Script for launching the AI Dev Toolkit GUI

## Diagnostic and Utility Tools

- `context_validator.py`: Tool for validating Claude's understanding of the project context

## Usage

During development, you can test these files by running them directly from this directory:

```bash
# Run the installation scripts
python install_librarian.py
python install_to_claude.py

# Launch the AI Librarian server
python launch_librarian.py [directory1] [directory2] ...

# Run context validation
python context_validator.py --check all

# Launch the GUI (when GUI development is complete)
python launch.py
```

## Notes

- These files are not part of the current release and may change significantly before release
- Documentation and error handling are still being improved
- GUI integration is pending
- These files will be moved back to the root directory when the project reaches beta stage


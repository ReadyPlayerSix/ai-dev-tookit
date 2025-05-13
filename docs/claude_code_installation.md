# AI Dev Toolkit Installation Guide for Claude Code

This guide helps you install the AI Dev Toolkit for use with Claude Code.

## Quick Start

The fastest way to get started is to use the direct GitHub installer:

```bash
# Download and run the installer
wget https://raw.githubusercontent.com/isekaiZen/ai-dev-toolkit/main/scripts/install_from_github.py
python install_from_github.py
```

This will:
1. Clone the repository from GitHub
2. Install necessary dependencies
3. Configure the toolkit for your project directories
4. Set up Claude Code integration
5. Create desktop shortcuts for the GUI (if tkinter is available)

## Manual Installation

If you prefer to manually control the installation:

```bash
# Clone the repository
git clone https://github.com/isekaiZen/ai-dev-toolkit.git
cd ai-dev-toolkit

# Install dependencies
pip install -r requirements.txt

# Run the installer
python scripts/install_for_claude_code.py
```

## Installation Options

The installer supports several options:

```
usage: install_for_claude_code.py [-h] [--install-dir INSTALL_DIR] [--allowed-dirs [ALLOWED_DIRS ...]]
                                [--claude-desktop] [--no-desktop-shortcut] [--no-dependencies]

Install AI Dev Toolkit for Claude Code

optional arguments:
  -h, --help            show this help message and exit
  --install-dir INSTALL_DIR
                        Installation directory (default: ~/ai-dev-toolkit)
  --allowed-dirs [ALLOWED_DIRS ...]
                        Directories to allow AI Librarian to access
  --claude-desktop      Configure for Claude Desktop
  --no-desktop-shortcut
                        Skip desktop shortcut creation
  --no-dependencies     Skip installing dependencies
```

## Examples

### Install to a custom directory:
```bash
python install_for_claude_code.py --install-dir ~/dev/ai-toolkit
```

### Specify allowed directories:
```bash
python install_for_claude_code.py --allowed-dirs ~/projects/project1 ~/projects/project2
```

### Install for both Claude Code and Claude Desktop:
```bash
python install_for_claude_code.py --claude-desktop
```

### Skip GUI desktop shortcut:
```bash
python install_for_claude_code.py --no-desktop-shortcut
```

## After Installation

Once the installation is complete, you can:

1. **Access the GUI**
   - Use the desktop shortcut created during installation
   - Or run the launcher script directly:
     ```bash
     python ~/ai-dev-toolkit/scripts/launchers/launch_gui.py
     ```

2. **Launch the AI Librarian server**
   ```bash
   python ~/ai-dev-toolkit/development/launch_librarian.py
   ```

3. **Use in your projects**
   ```python
   from aitoolkit.librarian.ai_dev_toolkit import initialize_librarian
   
   # Initialize for your project
   initialize_librarian("/path/to/your/project")
   ```

## Troubleshooting

### Common Installation Issues

1. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission errors**
   - Check if you have permission to write to the installation directory
   - Try running with sudo or administrative privileges

3. **Tkinter issues**
   - Install tkinter for GUI support:
     - Debian/Ubuntu: `sudo apt-get install python3-tk`
     - Fedora: `sudo dnf install python3-tkinter`
     - macOS: `brew install python-tk@3.10` (adjust version as needed)

4. **Git not found**
   - Install Git:
     - Debian/Ubuntu: `sudo apt-get install git`
     - Fedora: `sudo dnf install git`
     - macOS: `brew install git`
     - Windows: Download from https://git-scm.com/download/win

### Getting Help

If you encounter any issues:
- Check the [troubleshooting section in README.md](../README.md#troubleshooting)
- Browse the [documentation](../docs/)
- Open an issue on GitHub

## Updating

To update an existing installation:

```bash
cd ~/ai-dev-toolkit
git pull
pip install -r requirements.txt
```
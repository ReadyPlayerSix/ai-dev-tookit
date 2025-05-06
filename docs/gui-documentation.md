# AI Dev Toolkit GUI

The AI Dev Toolkit GUI provides a comprehensive control panel for managing Claude Desktop integration, server configuration, project management, and AI Librarian functionality.

## Overview

The GUI simplifies the configuration and use of the AI Dev Toolkit through a user-friendly interface. It includes features for:

1. Managing Claude Desktop integration
2. Starting and stopping the MCP server
3. Managing project directories
4. Initializing and updating the AI Librarian
5. Creating new projects

## Installation

The GUI is pre-installed with the AI Dev Toolkit. To use it:

### Windows
- Run `launch_gui.bat` from the AI Dev Toolkit directory

### Linux/Mac
- Run `python launch_gui.py` from the AI Dev Toolkit directory

If you need to re-install or update the GUI:
1. Run `python gui_installer.py` from the AI Dev Toolkit directory
2. Follow the on-screen instructions

## Features

### Dashboard

The dashboard provides a quick overview of:
- Claude Desktop status
- MCP server status
- Active projects
- Recent server logs

It also includes quick action buttons for common tasks.

### Claude Desktop Integration

This section allows you to:
- Detect Claude Desktop installation
- Configure Claude Desktop to work with the AI Dev Toolkit
- Enable/disable the MCP server in Claude's configuration
- Add allowed project directories

### Server Management

The server management tab provides tools to:
- Start, stop, and restart the MCP server
- View server logs in real-time
- Monitor server status

### Project Management

This section allows you to:
- Add and remove project directories
- View project information
- Initialize and update the AI Librarian for projects
- Create new projects from templates

### AI Librarian

The AI Librarian tab provides:
- Project monitoring status
- Component registry information
- Tools for initializing and updating the AI Librarian
- Component browsing and details

## Usage Guide

### First-Time Setup

1. Launch the GUI using `launch_gui.bat` (Windows) or `python launch_gui.py` (Linux/Mac)
2. The GUI will automatically attempt to detect Claude Desktop
3. If detected, it will load the configuration
4. Add project directories you want to use with Claude
5. Enable the MCP server in Claude's configuration
6. Apply the changes and restart Claude Desktop

### Managing the MCP Server

1. Go to the "Server Management" tab
2. Click "Start Server" to start the MCP server
3. The server logs will appear in the log view
4. Click "Stop Server" when you're done

### Setting Up a Project with AI Librarian

1. Add your project directory in the "Project Management" tab
2. Select the project and click "Initialize AI Librarian"
3. Start the MCP server if not already running
4. In Claude Desktop, use the AI Librarian tools to work with your project

### Creating a New Project

1. Go to the "Project Management" tab
2. Enter a project name, select a type, and choose a location
3. Click "Create Project"
4. The new project will be added to your project directories
5. You can then initialize the AI Librarian for the new project

## Troubleshooting

### Claude Desktop Not Detected

If the GUI cannot detect Claude Desktop:
1. Make sure Claude Desktop is installed
2. Click "Browse..." to manually locate the config file
   - Usually found in `%APPDATA%\Claude\config.json`

### Server Won't Start

If the MCP server fails to start:
1. Check if another process is using port 8000
2. Make sure all dependencies are installed
3. Check the server logs for specific error messages

### GUI Won't Launch

If the GUI fails to launch:
1. Make sure Python 3.8 or higher is installed
2. Install tkinter if missing (`pip install tk` or system package manager)
3. Run the GUI installer: `python gui_installer.py`
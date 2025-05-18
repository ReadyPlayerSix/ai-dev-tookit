# AI Dev Toolkit GUI

This directory contains the GUI implementation for the AI Dev Toolkit.

## Overview

The GUI provides a user-friendly interface for:
- Configuring Claude Desktop integration
- Managing project directories
- Controlling the MCP server
- Viewing project documentation
- Managing toolkit settings

## GUI Versions

### Modern Sidebar GUI (configurator.py)

The modern GUI implementation features:
- Sidebar navigation similar to VS Code or WSL Settings
- Improved visual design with clearer color scheme
- Better spacing and layout for controls
- The same functionality as the legacy UI but with a more modern look and feel

### Legacy Tabbed GUI (legacy/configurator_unified.py)

The original implementation with:
- Tabs across the top of the window
- All the same functionality as the modern version

## Usage

The `launch_gui.py` script will automatically use the modern GUI if available,
falling back to the legacy version if needed. This ensures compatibility across
different installations.

## Design Decisions

The modern UI was designed with these principles in mind:
1. Familiar interface pattern (sidebar navigation is used in many modern applications)
2. Clear section navigation and visual hierarchy
3. Consistent styling and spacing
4. Better use of screen real estate
5. Maintaining full functionality of the original design

## Implementation Notes

The sidebar design puts navigation controls in a fixed-width panel on the left side
of the window, with the main content area on the right. This creates more vertical
space for content and makes navigation more visible.

The main differences from the legacy version:
- Navigation moved from top tabs to left sidebar
- Status indicator added to sidebar footer
- Consistent styling throughout the interface
- Better use of available space for content areas
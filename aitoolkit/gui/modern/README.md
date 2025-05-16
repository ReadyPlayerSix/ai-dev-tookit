# Modern Sidebar GUI for AI Dev Toolkit

This directory contains the modern sidebar-based GUI for the AI Dev Toolkit, designed with a similar look and feel to the WSL Settings application.

## Features

- **Sidebar Navigation**: Easy access to all sections via a modern left sidebar
- **Dark Sidebar with Light Content**: Visual distinction between navigation and content
- **Improved Visual Hierarchy**: Clear section separation and information organization
- **Status Indicators**: Server status visible directly in the sidebar
- **Modern Styling**: More contemporary look and feel

## Usage

The modern sidebar GUI is the default interface when launching the AI Dev Toolkit GUI:

```bash
python launch_gui.py
```

If you prefer the legacy tabbed interface, you can specify it with:

```bash
python launch_gui.py legacy
```

## Implementation

The modern GUI is implemented in `configurator_sidebar.py` with the primary class `ModernAIDevToolkitGUI`. It maintains all the functionality of the legacy interface while reorganizing the UI for better usability.

## Design Inspiration

This design is inspired by:
- WSL Settings window
- Visual Studio Code
- Modern Windows 11 settings interfaces
- Contemporary web applications

## Comparison with Legacy GUI

| Feature | Modern Sidebar GUI | Legacy Tabbed GUI |
|---------|-------------------|-------------------|
| Navigation | Left sidebar with icons | Top tabs |
| Status Display | Integrated in sidebar | In content area only |
| Visual Style | Dark sidebar, light content | Uniform light theme |
| Page Organization | Full-width pages | Tabbed pages |
| Bottom Buttons | Persistent across pages | Persistent across tabs |

## Notes for Developers

When modifying the modern GUI:
1. Maintain compatibility with the legacy GUI for backward compatibility
2. Follow the established styling patterns for consistency
3. Keep the sidebar focused on navigation only
4. Place all content in the content frame
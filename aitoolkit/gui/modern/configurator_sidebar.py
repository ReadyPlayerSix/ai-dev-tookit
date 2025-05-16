"""
AI Dev Toolkit Modern Sidebar GUI

This is the modern sidebar GUI implementation for the AI Dev Toolkit.
It replaces the tabbed interface with a modern WSL Settings-like sidebar navigation.
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import time
from pathlib import Path
import webbrowser
import traceback
import re
from typing import List, Tuple, Optional, Dict, Callable, Any

# Import psutil if available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class ModernAIDevToolkitGUI:
    """Modern sidebar-based GUI for AI Dev Toolkit."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Dev Toolkit")
        self.root.geometry("1000x700")  # Wider window for sidebar layout
        self.root.minsize(800, 600)     # Set minimum size
        self.root.resizable(True, True)
        
        # Set version
        self.version = "0.5.7"
        
        # Track changes
        self.has_changes = False
        
        # Capture window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set theme and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define colors
        self.use_dark_mode = True  # Default to dark mode
        
        # Set color themes
        self.dark_colors = {
            "bg": "#2d2d2d",          # Darker background (was #333333)
            "content_bg": "#2d2d2d",   # Darker background for content
            "sidebar_bg": "#252526",  # Dark background for sidebar
            "sidebar_text": "#ffffff", # White text for sidebar
            "sidebar_hover": "#37373d", # Slightly lighter for hover
            "sidebar_selected": "#2d2d2d", # Match content background for selected
            "accent": "#0078d4",      # Microsoft blue accent color
            "text": "#ffffff",
            "section_bg": "#2d2d2d",  # Match content_bg for seamless appearance
            "button_bg": "#3c3c3c",   # Lighter color for buttons (swapped with background)
            "success": "#107c10",     # Green for success
            "warning": "#797673",     # Yellow for warning
            "error": "#d83b01",       # Red for error
        }
        
        self.light_colors = {
            "bg": "#e8e8e8",          # Darker background for light mode
            "content_bg": "#e8e8e8",  # Darker background for content
            "sidebar_bg": "#252526",  # Still keep dark sidebar
            "sidebar_text": "#ffffff", # White text for sidebar
            "sidebar_hover": "#37373d", # Slightly lighter for hover
            "sidebar_selected": "#1e1e1e", # Darker for selected
            "accent": "#0078d4",      # Microsoft blue accent color
            "text": "#000000",
            "section_bg": "#e8e8e8",  # Match content_bg for seamless appearance
            "button_bg": "#f8f8f8",   # Lighter background for buttons
            "success": "#107c10",     # Green for success
            "warning": "#797673",     # Yellow for warning
            "error": "#d83b01",       # Red for error
        }
        
        # Set the active color theme
        self.colors = self.dark_colors if self.use_dark_mode else self.light_colors
        
        # Remove any borders globally by setting borderwidth to 0
        self.root.option_add('*TButton.borderWidth', 0)
        self.root.option_add('*TFrame.borderWidth', 0)
        self.root.option_add('*TLabel.borderWidth', 0)
        self.root.option_add('*TEntry.borderWidth', 0)
        self.root.option_add('*TCombobox.borderWidth', 0)
        
        # Configure styles
        self.configure_styles()
        
        # Variables
        self.claude_desktop_path = tk.StringVar()
        self.config_path = tk.StringVar()
        self.project_dirs = []
        self.project_enabled = {}  # Map of project path to enabled status
        self.server_status = tk.StringVar(value="Stopped")
        self.server_process = None
        self.server_log = tk.StringVar(value="")
        
        # Server configuration type - for official MCP servers
        self.server_config_type = tk.StringVar(value="npm")  # Default to npm package (recommended)
        
        # AI Dev Toolkit Server enabled/disabled
        self.ai_dev_toolkit_server_enabled = tk.BooleanVar(value=True)
        
        # Set developer mode (off by default)
        self.developer_mode_enabled = tk.BooleanVar(value=False)
        
        # Create main layout
        self.create_layout()
        
        # Initial checks - order matters for config path
        self.detect_claude_desktop()  # This sets up config_path
        self.load_config()  # This uses config_path
        self.load_gui_settings()  # This uses config_path
        self.check_server_status()
        self.scan_for_projects()
        
        # No automatic server status checking - it can interfere with Claude Desktop
    
    def configure_styles(self):
        """Configure ttk styles for modern look and feel."""
        # Main styles
        self.style.configure('TFrame', background=self.colors["bg"])
        self.style.configure('TLabel', font=('Segoe UI', 10), background=self.colors["bg"], foreground=self.colors["text"])
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), 
                           background=self.colors["bg"], foreground=self.colors["text"])
                           
        # Style for text entry widgets - no borders
        self.style.configure('TEntry', 
                          fieldbackground=self.colors["section_bg"],
                          foreground=self.colors["text"],
                          insertcolor=self.colors["text"],
                          borderwidth=0,
                          relief="flat")
        
        # Combobox style - no borders
        self.style.configure('TCombobox',
                          fieldbackground=self.colors["section_bg"],
                          foreground=self.colors["text"],
                          selectbackground=self.colors["accent"],
                          borderwidth=0,
                          relief="flat")
                          
        # Scrollbar style - minimal appearance
        self.style.configure('TScrollbar',
                          background=self.colors["section_bg"],
                          troughcolor=self.colors["content_bg"],
                          bordercolor=self.colors["content_bg"],  # Match background
                          borderwidth=0,
                          relief="flat",
                          arrowsize=12)
        
        # Status styles - more modern and consistent with dark/light theme
        self.style.configure('Status.TLabel', font=('Segoe UI', 10), padding=5,
                            background=self.colors["section_bg"], foreground=self.colors["text"])
                            
        # Modern status indicators with pills/badges
        self.style.configure('Running.Status.TLabel', 
                            font=('Segoe UI', 10, 'bold'),
                            background=self.colors["section_bg"], 
                            foreground=self.colors["success"])
                            
        self.style.configure('Stopped.Status.TLabel', 
                            font=('Segoe UI', 10, 'bold'),
                            background=self.colors["section_bg"], 
                            foreground=self.colors["error"])
                            
        self.style.configure('Warning.Status.TLabel', 
                            font=('Segoe UI', 10, 'bold'),
                            background=self.colors["section_bg"], 
                            foreground=self.colors["warning"])
        
        # Sidebar styles with larger font
        self.style.configure('Sidebar.TFrame', background=self.colors["sidebar_bg"])
        self.style.configure('Sidebar.TLabel', background=self.colors["sidebar_bg"], 
                             foreground=self.colors["sidebar_text"], font=('Segoe UI', 13))  # Increased from 12 to 13
        
        # Selected sidebar item styles with larger font
        self.style.configure('SidebarSelected.TFrame', background=self.colors["sidebar_selected"])
        self.style.configure('SidebarSelected.TLabel', background=self.colors["sidebar_selected"], 
                             foreground=self.colors["sidebar_text"], font=('Segoe UI', 13, 'bold'))  # Added bold for selected items
        
        self.style.configure('SidebarTitle.TLabel', background=self.colors["sidebar_bg"], 
                           foreground=self.colors["sidebar_text"], font=('Segoe UI', 14, 'bold'), padding=10)
        self.style.configure('SidebarFooter.TLabel', background=self.colors["sidebar_bg"], 
                           foreground=self.colors["sidebar_text"], font=('Segoe UI', 9), padding=5)
        
        # Content styles
        self.style.configure('Content.TFrame', background=self.colors["content_bg"])
        self.style.configure('ContentHeader.TLabel', font=('Segoe UI', 18, 'bold'), 
                           background=self.colors["content_bg"], foreground=self.colors["accent"])
        
        # Custom button styles for the sidebar
        self.style.configure('Sidebar.TButton', 
                           background=self.colors["sidebar_bg"],
                           foreground=self.colors["sidebar_text"],
                           borderwidth=0,
                           focusthickness=0,
                           font=('Segoe UI', 11),
                           padding=(20, 10, 10, 10),  # Increased left padding for better justification
                           anchor='w')  # Left-justify text in sidebar buttons
        
        self.style.map('Sidebar.TButton',
                      background=[('active', self.colors["sidebar_hover"]),
                                  ('selected', self.colors["sidebar_selected"])],
                      relief=[('pressed', 'flat'),
                              ('!pressed', 'flat')])
        
        # Section styles - fully seamless with content background
        self.style.configure('Section.TLabelframe', 
                           background=self.colors["content_bg"],  # Now matches content background
                           padding=10,
                           borderwidth=0,  # No border
                           relief="flat")  # Flat appearance
                           
        self.style.configure('Section.TLabelframe.Label', 
                           font=('Segoe UI', 11, 'bold'), 
                           background=self.colors["content_bg"],  # Make sure label matches too
                           foreground=self.colors["text"])
        
        # Style for the action buttons - match sidebar style with no borders
        self.style.configure('Action.TButton', 
                           font=('Segoe UI', 11),
                           background=self.colors["accent"],
                           foreground=self.colors["sidebar_text"],
                           borderwidth=0,
                           focusthickness=0,
                           padding=8)
                           
        # Style for normal buttons
        self.style.configure('TButton', 
                           font=('Segoe UI', 10),
                           background=self.colors["section_bg"],
                           borderwidth=0,
                           focusthickness=0,
                           padding=5)
                           
        # Button hover/pressed states
        self.style.map('TButton',
                     background=[('active', '#005fb8'),  # Use the same blue as Action buttons for consistency
                                ('pressed', '#004a92')],
                     relief=[('pressed', 'flat'),
                            ('!pressed', 'flat')])
                            
        self.style.map('Action.TButton',
                     background=[('active', '#005fb8'),  # Slightly darker accent color on hover
                                ('pressed', '#004a92')], # Even darker on press
                     relief=[('pressed', 'flat'),
                            ('!pressed', 'flat')])
                            
        # Action button styles for modern frame-based buttons - now lighter than content
        button_bg = self.colors["button_bg"]  # Use the new button color (lighter)
        hover_bg = "#4c4c4c" if self.use_dark_mode else "#e0e0e0"   # Hover color
        
        self.style.configure('ActionButton.TFrame', background=button_bg)
        self.style.configure('ActionButton.TLabel', 
                          background=button_bg,
                          foreground=self.colors["text"],
                          font=('Segoe UI', 10))
                          
        # Hover state
        self.style.configure('ActionButtonHover.TFrame', background=hover_bg)
        self.style.configure('ActionButtonHover.TLabel', 
                          background=hover_bg,
                          foreground=self.colors["text"],
                          font=('Segoe UI', 10))
        
        # Checkbutton style for dark mode with improved hover
        self.style.configure('TCheckbutton', 
                           background=self.colors["content_bg"],
                           foreground=self.colors["text"],
                           font=('Segoe UI', 10))
                           
        # Add hover state for checkbuttons
        self.style.map('TCheckbutton',
                     background=[('active', '#005fb8')],  # Use same blue hover as buttons
                     foreground=[('active', self.colors["sidebar_text"])])
        
        # Radiobutton style for dark mode
        self.style.configure('TRadiobutton', 
                           background=self.colors["content_bg"],
                           foreground=self.colors["text"],
                           font=('Segoe UI', 10))
        
        # Configure text widget colors using tag_configure after widgets are created
        # (Will be done when creating the text widgets)
    
    def create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Split into sidebar and content - increased sidebar width from 200 to 250
        self.sidebar_frame = ttk.Frame(self.main_container, width=250, style='Sidebar.TFrame')
        self.content_frame = ttk.Frame(self.main_container, style='Content.TFrame')
        
        # Place the frames
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Make sure sidebar keeps its width
        self.sidebar_frame.pack_propagate(False)
        
        # Create sidebar content
        self.create_sidebar()
        
        # Create content pages
        self.create_pages()
        
        # No global bottom button frame anymore - buttons will be on each page
        
        # Initially show the Dashboard page
        self.show_page("dashboard")
        
    def create_sidebar(self):
        """Create the sidebar with navigation buttons."""
        # Main navigation area
        nav_area = ttk.Frame(self.sidebar_frame, style='Sidebar.TFrame')
        nav_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Navigation buttons
        self.nav_buttons = {}
        self.active_button = None
        
        # Define main navigation items
        nav_items = [
            {"id": "dashboard", "text": "Dashboard", "icon": "📊"},  # Changed from home to bargraph icon
            {"id": "claude_config", "text": "Claude Desktop", "icon": "⚙️"},
            {"id": "projects", "text": "Projects", "icon": "📂"},
            {"id": "help", "text": "Help", "icon": "❓"},  # Help & Troubleshooting
            {"id": "settings", "text": "Settings", "icon": "🛠️"}
        ]
        
        # Add Developer tab only if enabled
        if self.developer_mode_enabled.get():
            nav_items.insert(3, {"id": "developer", "text": "Developer", "icon": "👨‍💻"})
        
        # Add main navigation buttons with more vertical space
        for item in nav_items:
            # Create a frame for each button to ensure consistent layout
            button_frame = ttk.Frame(nav_area, style='Sidebar.TFrame')
            button_frame.pack(side=tk.TOP, fill=tk.X, pady=2)  # Increased from 1 to 2
            
            # Add padding frame for vertical space
            padding_frame = ttk.Frame(button_frame, style='Sidebar.TFrame')
            padding_frame.pack(fill=tk.X, pady=8)  # Add 8 pixels of padding top and bottom
            
            # Icon label - fixed width ensures alignment - increased width
            icon_label = ttk.Label(
                padding_frame,
                text=item['icon'],
                style='Sidebar.TLabel',
                width=3,  # Increased from 2 to 3 to prevent cutoff
                anchor='center'
            )
            icon_label.pack(side=tk.LEFT, padx=(25, 5))  # Increased left padding from 20 to 25
            
            # Text label
            text_label = ttk.Label(
                padding_frame,
                text=item['text'],
                style='Sidebar.TLabel'
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
            
            # Make the entire frame clickable
            button_frame.bind("<Button-1>", lambda e, i=item["id"]: self.show_page(i))
            padding_frame.bind("<Button-1>", lambda e, i=item["id"]: self.show_page(i))
            icon_label.bind("<Button-1>", lambda e, i=item["id"]: self.show_page(i))
            text_label.bind("<Button-1>", lambda e, i=item["id"]: self.show_page(i))
            
            # Store references to both frames
            self.nav_buttons[item["id"]] = {
                "button_frame": button_frame, 
                "padding_frame": padding_frame,
                "icon_label": icon_label,
                "text_label": text_label
            }
        
        # Add status and utility area at the bottom
        status_frame = ttk.Frame(self.sidebar_frame, style='Sidebar.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # About button at bottom above status info - with more vertical space
        about_frame = ttk.Frame(status_frame, style='Sidebar.TFrame')
        about_frame.pack(side=tk.TOP, fill=tk.X, pady=2)  # Increased pady
        
        # Add padding frame for vertical space
        about_padding_frame = ttk.Frame(about_frame, style='Sidebar.TFrame')
        about_padding_frame.pack(fill=tk.X, pady=8)  # Match the other buttons padding
        
        # Icon label - fixed width ensures alignment - increased width
        about_icon = ttk.Label(
            about_padding_frame,
            text="ⓘ",
            style='Sidebar.TLabel',
            width=3,  # Increased from 2 to 3 to prevent cutoff
            anchor='center'
        )
        about_icon.pack(side=tk.LEFT, padx=(25, 5))  # Match the left padding of other buttons
        
        # Text label
        about_text = ttk.Label(
            about_padding_frame,
            text="About",
            style='Sidebar.TLabel'
        )
        about_text.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        
        # Make the entire frame clickable
        about_frame.bind("<Button-1>", lambda e: self.show_page("about"))
        about_padding_frame.bind("<Button-1>", lambda e: self.show_page("about"))
        about_icon.bind("<Button-1>", lambda e: self.show_page("about"))
        about_text.bind("<Button-1>", lambda e: self.show_page("about"))
        
        # Store references to both frames
        self.nav_buttons["about"] = {
            "button_frame": about_frame,
            "padding_frame": about_padding_frame,
            "icon_label": about_icon,
            "text_label": about_text
        }
        
        # Version info - left-aligned
        version_label = ttk.Label(status_frame, 
                                text=f"Version: {self.version}", 
                                style='SidebarFooter.TLabel',
                                anchor=tk.W)  # West alignment for left justification
        version_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10)  # Add padding for better appearance
        
        # App info with version instead of server status
        app_info_frame = ttk.Frame(status_frame, style='Sidebar.TFrame')
        app_info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # App name and version
        ttk.Label(
            app_info_frame,
            text="AI Dev Toolkit",
            style='SidebarFooter.TLabel',
            font=('Segoe UI', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        # Add a separator between navigation and status
        separator = ttk.Separator(status_frame, orient=tk.HORIZONTAL)
        separator.pack(side=tk.TOP, fill=tk.X, pady=5)
    
    def create_pages(self):
        """Create all the content pages."""
        # Dictionary to hold all pages
        self.pages = {}
        
        # Create each page as a frame
        self.pages["dashboard"] = self.create_dashboard_page()
        self.pages["claude_config"] = self.create_claude_config_page()
        self.pages["projects"] = self.create_projects_page()
        self.pages["developer"] = self.create_developer_page()  # Add developer page
        self.pages["help"] = self.create_help_page()  # Add help & troubleshooting page
        self.pages["settings"] = self.create_settings_page()
        self.pages["about"] = self.create_about_page()
        
        # Initially hide all pages
        for page in self.pages.values():
            page.pack_forget()
    
    def show_page(self, page_id):
        """Show the selected page and update navigation."""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        self.pages[page_id].pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Update navigation button states
        for btn_id, components in self.nav_buttons.items():
            if btn_id == page_id:
                # Selected button frame and components
                components["button_frame"].configure(style='SidebarSelected.TFrame')
                components["padding_frame"].configure(style='SidebarSelected.TFrame')
                components["icon_label"].configure(style='SidebarSelected.TLabel')
                components["text_label"].configure(style='SidebarSelected.TLabel')
                
                # Store reference to active button
                self.active_button = components["button_frame"]
            else:
                # Unselected buttons
                components["button_frame"].configure(style='Sidebar.TFrame')
                components["padding_frame"].configure(style='Sidebar.TFrame')
                components["icon_label"].configure(style='Sidebar.TLabel')
                components["text_label"].configure(style='Sidebar.TLabel')
                
    def create_dashboard_page(self):
        """Create the Dashboard page."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_label = ttk.Label(page, text="Dashboard", style='ContentHeader.TLabel')
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Quick actions spanning entire width in 2 columns of 3 buttons
        actions_frame = ttk.LabelFrame(page, text="Quick Actions", padding="10 10 10 10", style='Section.TLabelframe')
        actions_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Create a grid layout for the buttons with even columns and fixed size buttons
        # Use a parent frame to contain two equal-width columns
        actions_outer_frame = ttk.Frame(actions_frame, style='Content.TFrame')
        actions_outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a container frame that ensures equal width columns
        container_frame = ttk.Frame(actions_outer_frame, style='Content.TFrame')
        container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure the grid to have two equal columns
        container_frame.columnconfigure(0, weight=1, uniform='column')
        container_frame.columnconfigure(1, weight=1, uniform='column')
        
        # Create the columns using grid instead of pack to ensure exact equal width
        left_column = ttk.Frame(container_frame, style='Content.TFrame')
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        right_column = ttk.Frame(container_frame, style='Content.TFrame')
        right_column.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Left column buttons - stack them vertically
        
        # Restart Claude Desktop
        restart_claude_btn = self.create_action_button(
            parent=left_column,
            icon="🦙",
            text="Restart Claude Desktop",
            command=self.restart_claude_desktop
        )
        restart_claude_btn.pack(fill=tk.X, pady=3)
        
        # Clear Request Queue
        clear_queue_btn = self.create_action_button(
            parent=left_column,
            icon="🧹",
            text="Clear Request Queue",
            command=self.clear_request_queue
        )
        clear_queue_btn.pack(fill=tk.X, pady=3)
        
        # Open Claude Config Directory
        open_config_btn = self.create_action_button(
            parent=left_column,
            icon="📁",
            text="Open Claude Config Directory",
            command=self.open_claude_directory
        )
        open_config_btn.pack(fill=tk.X, pady=3)
        
        # Right column buttons - stack them vertically
        
        # Restart MCP Server
        restart_server_btn = self.create_action_button(
            parent=right_column,
            icon="🚀",
            text="Restart MCP Server",
            command=self.restart_server
        )
        restart_server_btn.pack(fill=tk.X, pady=3)
        
        # Filter Server Log
        filter_log_btn = self.create_action_button(
            parent=right_column,
            icon="🔍",
            text="Filter Server Log",
            command=self.filter_server_log
        )
        filter_log_btn.pack(fill=tk.X, pady=3)
        
        # Check for Updates
        upgrade_btn = self.create_action_button(
            parent=right_column,
            icon="⚠️",
            text="Check for Updates",
            command=self.upgrade_toolkit
        )
        upgrade_btn.pack(fill=tk.X, pady=3)
        
        # Notes section (moved to row 2 since Help section was removed)
        notes_frame = ttk.LabelFrame(page, text="Notes", padding="10 10 10 10", style='Section.TLabelframe')
        notes_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Create a container for the text area and save button
        notes_content_frame = ttk.Frame(notes_frame, style='Content.TFrame')
        notes_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a text widget for notes with word wrapping and monospace font
        self.notes_text = tk.Text(notes_content_frame, height=20,  # Increased for more note-taking space
                         bg=self.colors["button_bg"], fg=self.colors["text"],  # Match button background color
                         insertbackground=self.colors["text"], 
                         selectbackground=self.colors["accent"],
                         selectforeground=self.colors["sidebar_text"],
                         borderwidth=0, relief="flat",
                         font=('Consolas', 10),  # Monospace font similar to Claude Desktop tool output
                         wrap=tk.WORD)  # Enable word wrapping
        
        # Set up auto-save to trigger on key press with a delay
        self.notes_autosave_id = None
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        notes_scrollbar = ttk.Scrollbar(notes_content_frame, orient=tk.VERTICAL, command=self.notes_text.yview)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_text.config(yscrollcommand=notes_scrollbar.set)
        
        # Add a save button at the bottom
        notes_button_frame = ttk.Frame(notes_frame, style='Content.TFrame')
        notes_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Auto save checkbox with improved styling
        self.auto_save_notes = tk.BooleanVar(value=True)
        
        # Create a custom frame for better visibility
        auto_save_frame = ttk.Frame(notes_button_frame, style='Content.TFrame')
        auto_save_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Add a small icon to make it more visible
        ttk.Label(
            auto_save_frame,
            text="🔄",
            font=('Segoe UI', 11),
            foreground=self.colors["accent"]
        ).pack(side=tk.LEFT, padx=(0, 2))
        
        # Add the checkbox with bold text
        auto_save_check = ttk.Checkbutton(
            auto_save_frame,
            text="Auto Save Notes",
            variable=self.auto_save_notes,
            style='TCheckbutton',
            command=lambda: self.schedule_autosave() if self.auto_save_notes.get() else None
        )
        auto_save_check.pack(side=tk.LEFT)
        
        # Status text to show when notes were last saved
        self.notes_status_var = tk.StringVar(value="")
        notes_status_label = ttk.Label(
            notes_button_frame, 
            textvariable=self.notes_status_var, 
            style='TLabel'
        )
        notes_status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load previous notes or add default text
        self.load_notes()
        
        # Add key binding for Ctrl+S to manually save notes
        self.notes_text.bind("<Control-s>", lambda e: self.save_notes_manually())
        
        # Add key binding to trigger auto-save after a delay
        self.notes_text.bind("<Key>", self.schedule_autosave)
        
        # Add a method to save notes when the app closes
        self.root.bind("<Destroy>", self.save_notes)
        
        # Configure grid weights
        page.columnconfigure(0, weight=1)
        page.columnconfigure(1, weight=1)
        page.rowconfigure(2, weight=3)  # Make notes section expand with more weight
        
        return page
    
    def create_claude_config_page(self):
        """Create the Claude Desktop Configuration page."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_label = ttk.Label(page, text="Claude Desktop Configuration", style='ContentHeader.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Claude Desktop section
        claude_config_frame = ttk.LabelFrame(page, text="Claude Desktop", padding="10 10 10 10",
                                           style='Section.TLabelframe')
        claude_config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Claude Desktop status
        self.claude_config_status_label = ttk.Label(claude_config_frame, 
                                                 text="Checking Claude Desktop installation...", 
                                                 style='TLabel')
        self.claude_config_status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Claude Desktop path
        path_frame = ttk.Frame(claude_config_frame)
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(path_frame, text="Config Path:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.config_path, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # Use action button for Browse
        browse_btn = self.create_action_button(
            parent=path_frame,
            icon="📁",
            text="Browse...",
            command=self.browse_config
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Safety disclaimer
        safety_frame = ttk.Frame(claude_config_frame, style='TFrame')
        safety_frame.pack(fill=tk.X, pady=(10, 0))
        
        safety_label = ttk.Label(safety_frame, 
                               text="Note: This application edits Claude Desktop's configuration file. Claude itself does not have direct access to edit these files.",
                               wraplength=750, style='TLabel')
        safety_label.pack(fill=tk.X)
        
        # AI Dev Toolkit Servers section
        server_selection_frame = ttk.LabelFrame(page, text="AI Dev Toolkit Servers", padding="10 10 10 10",
                                              style='Section.TLabelframe')
        server_selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Note about server selection
        server_note = ttk.Label(server_selection_frame, 
                              text="The following MCP server is available for Claude Desktop:",
                              wraplength=750)
        server_note.pack(anchor=tk.W, pady=(0, 10))
        
        # AI Dev Toolkit Integrated Server checkbox
        integrated_server_check = ttk.Checkbutton(server_selection_frame, 
                                               text="AI Dev Toolkit Integrated Server", 
                                               variable=self.ai_dev_toolkit_server_enabled,
                                               style='TCheckbutton',
                                               command=self.update_server_status)
        integrated_server_check.pack(anchor=tk.W, pady=5)
        
        # Description of the integrated server
        integrated_description = ttk.Label(server_selection_frame, 
                                        text="The integrated server combines multiple capabilities:",
                                        wraplength=750)
        integrated_description.pack(anchor=tk.W, padx=(20, 0), pady=(0, 5))
        
        # List the integrated server features
        features_frame = ttk.Frame(server_selection_frame)
        features_frame.pack(fill=tk.X, padx=(30, 0))
        
        ttk.Label(features_frame, text="• File System Tools - Read, write, and navigate the file system", 
                 wraplength=700).pack(anchor=tk.W, pady=2)
        ttk.Label(features_frame, text="• AI Librarian - Code analysis with self-verification and persistent memory", 
                 wraplength=700).pack(anchor=tk.W, pady=2)
        ttk.Label(features_frame, text="• Task Management - Track and organize development tasks", 
                 wraplength=700).pack(anchor=tk.W, pady=2)
        ttk.Label(features_frame, text="• Enhanced Code Analysis - Find related files, references, and component details", 
                 wraplength=700).pack(anchor=tk.W, pady=2)
        ttk.Label(features_frame, text="• Think Tool - Structured reasoning for complex problems", 
                 wraplength=700).pack(anchor=tk.W, pady=2)
        
        # Note about Claude Desktop compatibility
        claude_compat_note = ttk.Label(server_selection_frame, 
                                    text="Note: These servers are currently compatible with Claude Desktop only.",
                                    wraplength=750, style='TLabel')
        claude_compat_note.pack(fill=tk.X, pady=(10, 0))
        
        # Official MCP Servers section
        mcp_servers_frame = ttk.LabelFrame(page, text="Official MCP Servers", padding="10 10 10 10",
                                         style='Section.TLabelframe')
        mcp_servers_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Note about official MCP servers
        mcp_servers_note = ttk.Label(mcp_servers_frame, 
                                   text="There are many official MCP servers available from the Model Context Protocol repository. " +
                                   "Visit the link below to explore them.",
                                   wraplength=750)
        mcp_servers_note.pack(anchor=tk.W, pady=(0, 10))
        
        # Server configuration type
        server_type_frame = ttk.Frame(mcp_servers_frame, style='TFrame')
        server_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_type_frame, text="Server Configuration Type:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(server_type_frame, text="NPM Package (Recommended)", 
                       variable=self.server_config_type, value="npm",
                       command=self.update_server_config_type).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(server_type_frame, text="Python with uv (For Development)", 
                       variable=self.server_config_type, value="uv",
                       command=self.update_server_config_type).pack(side=tk.LEFT)
        
        # Server status (automatic based on tools)
        self.server_config_status_label = ttk.Label(mcp_servers_frame, 
                                                text="MCP Server configuration is determined by selected servers", 
                                                style='TLabel')
        self.server_config_status_label.pack(anchor=tk.W, pady=(5, 5))
        
        # NPM configuration note
        self.npm_config_note = ttk.Label(mcp_servers_frame, 
                                       text="Using NPM Package: This approach is recommended for most users and works with standard Claude Desktop configuration.",
                                       wraplength=750, style='TLabel')
        self.npm_config_note.pack(fill=tk.X, pady=(0, 5))
        
        # uv configuration note - hidden initially
        self.uv_config_note = ttk.Label(mcp_servers_frame, 
                                      text="Using Python with uv: This approach requires uv to be installed and is recommended for development. All paths must be absolute.",
                                      wraplength=750, style='TLabel')
        
        # GitHub link for MCP servers
        mcp_servers_link = ttk.Label(mcp_servers_frame, 
                                   text="Official MCP Servers Repository", 
                                   foreground="blue", cursor="hand2")
        mcp_servers_link.pack(anchor=tk.W, pady=2)
        mcp_servers_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/modelcontextprotocol/servers"))
        
        # Button for adding project directories - use action button for consistency
        add_proj_btn = self.create_action_button(
            parent=page,
            icon="📂",
            text="Add Project Directories",
            command=lambda: self.show_page("projects")
        )
        add_proj_btn.pack(anchor=tk.W, pady=(10, 0), fill=tk.X)
        
        # Action buttons
        button_frame = ttk.Frame(page, style='Content.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Use action buttons for consistent styling
        apply_exit_btn = self.create_action_button(
            parent=button_frame,
            icon="✅",
            text="Apply and Exit",
            command=self.apply_and_exit
        )
        apply_exit_btn.pack(side=tk.RIGHT, padx=5)
        
        apply_btn = self.create_action_button(
            parent=button_frame,
            icon="💾",
            text="Apply Changes",
            command=self.apply_claude_config
        )
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        discard_btn = self.create_action_button(
            parent=button_frame,
            icon="❌",
            text="Discard Changes",
            command=self.discard_and_exit
        )
        discard_btn.pack(side=tk.RIGHT, padx=5)
        
        return page
    
    def create_projects_page(self):
        """Create the Projects page."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_label = ttk.Label(page, text="Project Management", style='ContentHeader.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Main content frame with two columns
        main_content = ttk.Frame(page)
        main_content.pack(fill=tk.BOTH, expand=True)
        main_content.columnconfigure(0, weight=3)  # Directory list side
        main_content.columnconfigure(1, weight=2)  # Controls and viewer side
        
        # Left side: Project lists and documents
        left_side = ttk.Frame(main_content)
        left_side.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Project Document Viewer (top part of left side)
        doc_viewer_frame = ttk.LabelFrame(left_side, text="Project Documentation", 
                                        padding="10 10 10 10", style='Section.TLabelframe')
        doc_viewer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # README/Documentation viewer with scrollbars
        self.doc_text = tk.Text(doc_viewer_frame, height=10, width=60, wrap=tk.WORD,
                              bg=self.colors["content_bg"], fg=self.colors["text"],
                              insertbackground=self.colors["text"], selectbackground=self.colors["accent"])
        doc_scroll_y = ttk.Scrollbar(doc_viewer_frame, orient=tk.VERTICAL, command=self.doc_text.yview)
        
        self.doc_text.configure(yscrollcommand=doc_scroll_y.set)
        self.doc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        doc_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize with placeholder text
        self.doc_text.insert(tk.END, "Select a project to view its documentation.\n\nThe README.md or other documentation files from the project root will be displayed here.")
        self.doc_text.config(state=tk.DISABLED)
        
        # Project navigation buttons
        doc_nav_frame = ttk.Frame(doc_viewer_frame)
        doc_nav_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.prev_doc_btn = ttk.Button(doc_nav_frame, text="←", width=3, command=self.prev_document, state=tk.DISABLED)
        self.prev_doc_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.current_doc_var = tk.StringVar(value="No document")
        self.current_doc_label = ttk.Label(doc_nav_frame, textvariable=self.current_doc_var)
        self.current_doc_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.next_doc_btn = ttk.Button(doc_nav_frame, text="→", width=3, command=self.next_document, state=tk.DISABLED)
        self.next_doc_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Projects Directory List (bottom part of left side)
        projects_frame = ttk.LabelFrame(left_side, text="Project Directories", 
                                      padding="10 10 10 10", style='Section.TLabelframe')
        projects_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project list using a Treeview with expanded columns
        self.projects_treeview = ttk.Treeview(
            projects_frame, 
            columns=("Private", "Path", "Status", "LastAccessed", "GitStatus"), 
            selectmode='browse', 
            height=10
        )
        
        # Configure the treeview
        self.projects_treeview.heading('#0', text='Enabled')
        self.projects_treeview.heading('Private', text='Public/Private')
        self.projects_treeview.heading('Path', text='Project Path')
        self.projects_treeview.heading('Status', text='Access')
        self.projects_treeview.heading('LastAccessed', text='Last Accessed')
        self.projects_treeview.heading('GitStatus', text='Git Status')
        
        # Set treeview colors to match content background
        self.style.configure("Treeview", 
                          background=self.colors["content_bg"],
                          foreground=self.colors["text"],
                          fieldbackground=self.colors["content_bg"],
                          borderwidth=0)
                          
        # Selected items in treeview
        self.style.map("Treeview",
                    background=[('selected', self.colors["accent"])],
                    foreground=[('selected', self.colors["sidebar_text"])])
        
        # Set column widths and icons
        self.projects_treeview.column('#0', width=80, stretch=False, anchor='center')
        self.projects_treeview.column('Private', width=100, stretch=False, anchor='center')
        self.projects_treeview.column('Path', width=300, stretch=True)
        self.projects_treeview.column('Status', width=90, stretch=False)
        self.projects_treeview.column('LastAccessed', width=120, stretch=False)
        self.projects_treeview.column('GitStatus', width=100, stretch=False)
        
        # Add scrollbars
        tree_frame = ttk.Frame(projects_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.projects_treeview.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.projects_treeview.xview)
        
        self.projects_treeview.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Pack the treeview and scrollbars
        self.projects_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Right side: Controls and logs
        right_side = ttk.Frame(main_content)
        right_side.grid(row=0, column=1, sticky="nsew")
        
        # Project Controls (top part of right side)
        controls_frame = ttk.LabelFrame(right_side, text="Project Controls", 
                                      padding="10 10 10 10", style='Section.TLabelframe')
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button grid for controls - 2 columns
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # Configure grid columns for even spacing
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        # Use action buttons for consistent styling
        add_btn = self.create_action_button(
            parent=btn_frame,
            icon="➕",
            text="Add Project",
            command=self.add_directory
        )
        add_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        remove_btn = self.create_action_button(
            parent=btn_frame,
            icon="➖",
            text="Remove Project",
            command=self.remove_directory
        )
        remove_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        create_btn = self.create_action_button(
            parent=btn_frame,
            icon="🆕",
            text="Create Project",
            command=self.toggle_create_project_area
        )
        create_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Open Project With button
        open_project_frame = ttk.Frame(btn_frame)
        open_project_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Create action button for Open Project With
        self.open_with_btn = self.create_action_button(
            parent=open_project_frame,
            icon="📂",
            text="Open Project With...",
            command=self.open_project_with
        )
        self.open_with_btn.pack(side=tk.TOP, pady=(0, 5))
        
        # Default application selection
        self.default_app_var = tk.StringVar(value="Default Application")
        default_apps = ["VS Code", "Notepad", "Explorer", "Custom..."]
        
        self.default_app_combo = ttk.Combobox(open_project_frame, textvariable=self.default_app_var, values=default_apps, width=18)
        self.default_app_combo.pack(side=tk.TOP)
        
        # Message area for project updates
        self.project_message_var = tk.StringVar()
        self.project_message_label = ttk.Label(page, textvariable=self.project_message_var, 
                                            style='TLabel', wraplength=750)
        self.project_message_label.pack(fill=tk.X, pady=(10, 0))
        
        # Initially set a default message
        self.project_message_var.set("Add project directories that Claude should have access to.")
        
        # Create project section (hidden initially)
        self.create_project_frame = ttk.LabelFrame(page, text="Create New Project", 
                                               padding="10 10 10 10", style='Section.TLabelframe')
        
        # Data structures for project management
        self.project_privacy = {}  # Dictionary to store privacy settings
        self.project_last_accessed = {}  # Dictionary to store last accessed times
        self.project_git_status = {}  # Dictionary to store git status
        self.project_documents = {}  # Dictionary to store project documents
        self.current_project = None  # Currently selected project
        self.current_doc_index = 0  # Index of currently displayed document
        
        # Action buttons
        button_frame = ttk.Frame(page, style='Content.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Use action buttons for consistent styling
        apply_exit_btn = self.create_action_button(
            parent=button_frame,
            icon="✅",
            text="Apply and Exit",
            command=self.apply_and_exit
        )
        apply_exit_btn.pack(side=tk.RIGHT, padx=5)
        
        apply_btn = self.create_action_button(
            parent=button_frame,
            icon="💾",
            text="Apply Changes",
            command=self.apply_claude_config
        )
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        discard_btn = self.create_action_button(
            parent=button_frame,
            icon="❌",
            text="Discard Changes",
            command=self.discard_and_exit
        )
        discard_btn.pack(side=tk.RIGHT, padx=5)
        
        return page
    
    def create_settings_page(self):
        """Create the Settings page."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_label = ttk.Label(page, text="Settings", style='ContentHeader.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Appearance section
        appearance_frame = ttk.LabelFrame(page, text="Appearance", padding="10 10 10 10", style='Section.TLabelframe')
        appearance_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Color Mode selection (like Claude Desktop)
        color_mode_frame = ttk.Frame(appearance_frame, style='Content.TFrame')
        color_mode_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(color_mode_frame, text="Color Mode:", style='TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        # Create color mode radio buttons
        self.theme_var = tk.StringVar(value="dark" if self.use_dark_mode else "light")
        
        color_mode_options = ttk.Frame(color_mode_frame, style='Content.TFrame')
        color_mode_options.grid(row=0, column=1, sticky='w')
        
        ttk.Radiobutton(color_mode_options, text="Light", 
                      variable=self.theme_var, value="light",
                      command=self.toggle_theme).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(color_mode_options, text="Match System", 
                      variable=self.theme_var, value="system",
                      command=self.toggle_theme).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(color_mode_options, text="Dark", 
                      variable=self.theme_var, value="dark",
                      command=self.toggle_theme).pack(side=tk.LEFT)
        
        # Font selection (like Claude Desktop)
        font_frame = ttk.Frame(appearance_frame, style='Content.TFrame')
        font_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(font_frame, text="Font:", style='TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        # Create font radio buttons
        self.font_var = tk.StringVar(value="default")
        
        font_options = ttk.Frame(font_frame, style='Content.TFrame')
        font_options.grid(row=0, column=1, sticky='w')
        
        ttk.Radiobutton(font_options, text="Default", 
                      variable=self.font_var, value="default",
                      command=self.change_font).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(font_options, text="Match System", 
                      variable=self.font_var, value="system",
                      command=self.change_font).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(font_options, text="Dyslexic Friendly", 
                      variable=self.font_var, value="dyslexic",
                      command=self.change_font).pack(side=tk.LEFT)
        
        # Text size section
        text_size_frame = ttk.Frame(appearance_frame, style='Content.TFrame')
        text_size_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(text_size_frame, text="Text Size:", style='TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        # Create text size slider
        self.text_size_var = tk.IntVar(value=10)
        
        text_size_scale = ttk.Scale(text_size_frame, from_=8, to=16, 
                                  variable=self.text_size_var, 
                                  orient=tk.HORIZONTAL,
                                  length=200,
                                  command=lambda v: self.update_text_size())
        text_size_scale.grid(row=0, column=1, sticky='w')
        
        self.text_size_label = ttk.Label(text_size_frame, text="10", width=3)
        self.text_size_label.grid(row=0, column=2, padx=(5, 0))
        
        # Advanced options section
        advanced_frame = ttk.LabelFrame(page, text="Advanced Options", padding="10 10 10 10", style='Section.TLabelframe')
        advanced_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Developer mode toggle
        dev_mode_frame = ttk.Frame(advanced_frame, style='Content.TFrame')
        dev_mode_frame.pack(fill=tk.X, pady=10)
        
        # Create a checkbox for developer mode
        dev_mode_check = ttk.Checkbutton(
            dev_mode_frame,
            text="Enable Developer Mode",
            variable=self.developer_mode_enabled,
            command=self.toggle_developer_mode
        )
        dev_mode_check.pack(side=tk.LEFT)
        
        # Warning label for developer mode
        dev_mode_warning = ttk.Label(
            dev_mode_frame,
            text="Enables advanced features including terminal access. Requires restart to take effect.",
            font=('Segoe UI', 9, 'italic'),
            foreground="#d83b01"  # Warning color
        )
        dev_mode_warning.pack(side=tk.LEFT, padx=(10, 0))
        
        # Server configuration section
        server_frame = ttk.LabelFrame(page, text="Server Configuration", padding="10 10 10 10", style='Section.TLabelframe')
        server_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Log settings
        log_frame = ttk.Frame(server_frame, style='Content.TFrame')
        log_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(log_frame, text="Log Level:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        # Log level dropdown
        self.log_level_var = tk.StringVar(value="INFO")
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        log_level_combo = ttk.Combobox(log_frame, textvariable=self.log_level_var, values=log_levels, width=15)
        log_level_combo.pack(side=tk.LEFT)
        
        # Save settings button
        button_frame = ttk.Frame(page, style='Content.TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        # Use action buttons for consistent styling
        save_btn = self.create_action_button(
            parent=button_frame,
            icon="💾",
            text="Save Settings",
            command=self.save_settings
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Reset to defaults button
        reset_btn = self.create_action_button(
            parent=button_frame,
            icon="🔄",
            text="Reset to Defaults",
            command=self.reset_settings
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)
        
        return page
        
    def toggle_theme(self, show_message=True):
        """Toggle between dark and light themes."""
        selected_theme = self.theme_var.get()
        
        # Handle system theme if selected
        if selected_theme == "system":
            # Detect system theme - simplified for demonstration
            import platform
            system = platform.system()
            
            # On Windows, try to detect dark mode
            if system == "Windows":
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    # 0 means dark mode is on
                    new_mode = value == 0
                except:
                    # Default to dark mode if detection fails
                    new_mode = True
            else:
                # Default to dark for other platforms
                new_mode = True
        else:
            # Explicit light/dark setting
            new_mode = selected_theme == "dark"
            
        if new_mode != self.use_dark_mode:
            self.use_dark_mode = new_mode
            self.colors = self.dark_colors if self.use_dark_mode else self.light_colors
            self.configure_styles()
            
            # Only show message if explicitly requested (user interaction)
            if show_message:
                messagebox.showinfo(
                    "Theme Changed", 
                    f"Theme changed to {self.theme_var.get()} mode.\nPlease restart the application for the changes to take full effect."
                )
    
    def change_font(self):
        """Change the font based on selection."""
        selected_font = self.font_var.get()
        
        # Define font mappings
        font_family = "Segoe UI"  # Default
        
        if selected_font == "system":
            # Try to detect system font - simplified
            import platform
            system = platform.system()
            if system == "Windows":
                font_family = "Segoe UI"
            elif system == "Darwin":  # macOS
                font_family = "SF Pro"
            else:  # Linux
                font_family = "Ubuntu"
        elif selected_font == "dyslexic":
            font_family = "OpenDyslexic"  # Or fallback to another font if not available
            
        # Update fonts in the text areas - just the areas with monospace font for now
        try:
            # Update the log text font
            if hasattr(self, 'log_text'):
                current_font = self.log_text['font']
                if isinstance(current_font, str):
                    # For string fonts, completely replace
                    self.log_text.configure(font=(font_family, 10))
                else:
                    # For font tuples, update the family
                    size = current_font[1] if len(current_font) > 1 else 10
                    self.log_text.configure(font=(font_family, size))
                    
            # Update the notes text font
            if hasattr(self, 'notes_text'):
                current_font = self.notes_text['font']
                if isinstance(current_font, str):
                    self.notes_text.configure(font=(font_family, 10))
                else:
                    size = current_font[1] if len(current_font) > 1 else 10
                    self.notes_text.configure(font=(font_family, size))
                    
            messagebox.showinfo(
                "Font Changed", 
                f"Font changed to {selected_font} style.\nSome changes may require restarting the application."
            )
        except Exception as e:
            messagebox.showerror("Font Error", f"Error changing font: {str(e)}")
    
    def update_text_size(self):
        """Update text size based on slider value."""
        new_size = self.text_size_var.get()
        self.text_size_label.config(text=str(new_size))
        
        try:
            # Update the log text size
            if hasattr(self, 'log_text'):
                current_font = self.log_text['font']
                if isinstance(current_font, str):
                    # For string fonts, create a new font tuple
                    self.log_text.configure(font=('Consolas', new_size))
                else:
                    # For font tuples, update just the size
                    family = current_font[0]
                    self.log_text.configure(font=(family, new_size))
                    
            # Update the notes text size
            if hasattr(self, 'notes_text'):
                current_font = self.notes_text['font']
                if isinstance(current_font, str):
                    self.notes_text.configure(font=('Consolas', new_size))
                else:
                    family = current_font[0]
                    self.notes_text.configure(font=(family, new_size))
        except Exception as e:
            print(f"Error updating text size: {str(e)}")
    
    def create_developer_page(self):
        """Create the Developer page with terminal."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_label = ttk.Label(page, text="Developer Tools", style='ContentHeader.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Disclaimer
        disclaimer_frame = ttk.Frame(page, style='Content.TFrame')
        disclaimer_frame.pack(fill=tk.X, pady=(0, 15))
        
        warning_icon = ttk.Label(disclaimer_frame, text="⚠️", font=('Segoe UI', 14))
        warning_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        disclaimer_text = ttk.Label(
            disclaimer_frame,
            text="This tab is intended for advanced users and developers. The terminal provides direct access to your system shell and can run any command with your user permissions.",
            wraplength=700,
            font=('Segoe UI', 10, 'italic')
        )
        disclaimer_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Terminal section
        terminal_frame = ttk.LabelFrame(page, text="Terminal", padding="10 10 10 10", style='Section.TLabelframe')
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Terminal shell selection
        shell_frame = ttk.Frame(terminal_frame, style='Content.TFrame')
        shell_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(shell_frame, text="Shell:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Shell dropdown
        import platform
        system = platform.system()
        
        if system == "Windows":
            shells = ["cmd.exe", "PowerShell", "Git Bash (if installed)"]
            default_shell = "cmd.exe"
        else:  # Unix/Linux/macOS
            shells = ["/bin/bash", "/bin/sh", "/bin/zsh (if installed)"]
            default_shell = "/bin/bash"
            
        self.shell_var = tk.StringVar(value=default_shell)
        shell_dropdown = ttk.Combobox(shell_frame, textvariable=self.shell_var, values=shells, width=30)
        shell_dropdown.pack(side=tk.LEFT)
        
        # Start shell button
        ttk.Button(
            shell_frame, 
            text="Start New Shell", 
            command=self.start_terminal
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Terminal output
        terminal_output_frame = ttk.Frame(terminal_frame, style='Content.TFrame')
        terminal_output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Terminal text widget with monospace font and dark background
        self.terminal_text = tk.Text(
            terminal_output_frame,
            height=20,
            width=80,
            bg="#121212",  # Darker than the button_bg for better terminal look
            fg="#00ff00",  # Classic terminal green text
            insertbackground="#00ff00",
            selectbackground=self.colors["accent"],
            selectforeground="#ffffff",
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.terminal_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        terminal_scrollbar = ttk.Scrollbar(terminal_output_frame, orient=tk.VERTICAL, command=self.terminal_text.yview)
        terminal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_text.config(yscrollcommand=terminal_scrollbar.set)
        
        # Make the terminal text read-only initially
        self.terminal_text.config(state=tk.DISABLED)
        
        # Initial terminal content
        self.terminal_text.config(state=tk.NORMAL)
        self.terminal_text.insert(tk.END, f"AI Dev Toolkit Developer Terminal\n")
        self.terminal_text.insert(tk.END, f"Using {self.shell_var.get()} - Click 'Start New Shell' to begin\n\n")
        self.terminal_text.insert(tk.END, "Note: This terminal provides direct access to your system shell.\n")
        self.terminal_text.insert(tk.END, "Commands run here have the same permissions as your user account.\n\n")
        self.terminal_text.insert(tk.END, "USAGE: Type commands in the 'Command:' field below and press Enter or click 'Execute'.\n")
        self.terminal_text.insert(tk.END, "       The output will appear in this window (which is read-only).\n\n")
        self.terminal_text.config(state=tk.DISABLED)
        
        # Command input
        input_frame = ttk.Frame(terminal_frame, style='Content.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(input_frame, text="Command:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.command_var = tk.StringVar()
        command_entry = ttk.Entry(input_frame, textvariable=self.command_var, width=50)
        command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Bind Enter key to execute command
        command_entry.bind("<Return>", lambda e: self.execute_command())
        
        ttk.Button(
            input_frame,
            text="Execute",
            command=self.execute_command
        ).pack(side=tk.RIGHT)
        
        # Initialize terminal process and command history
        self.terminal_process = None
        self.command_history = []
        self.command_index = -1
        
        # Initialize terminal state
        self.terminal_active = False
        
        return page
        
    def start_terminal(self):
        """Start a new terminal process"""
        # Clean up any existing process
        if self.terminal_process:
            try:
                self.terminal_process.terminate()
                self.terminal_process = None
            except:
                pass
        
        # Get the selected shell
        shell = self.shell_var.get()
        
        # Clear terminal output
        if hasattr(self, 'terminal_text'):
            self.terminal_text.delete('1.0', tk.END)
            self.terminal_text.insert(tk.END, f"Starting new terminal with {shell}...\n\n")
        
        try:
            # Start the shell process
            import subprocess
            import os
            
            # Determine the appropriate shell command
            if shell == "PowerShell":
                command = ["powershell.exe", "-NoLogo"]
            elif "Git Bash" in shell:
                # Try common Git Bash locations
                git_bash = None
                potential_paths = [
                    r"C:\Program Files\Git\bin\bash.exe",
                    r"C:\Program Files (x86)\Git\bin\bash.exe",
                    os.path.expanduser("~/AppData/Local/Programs/Git/bin/bash.exe")
                ]
                for path in potential_paths:
                    if os.path.exists(path):
                        git_bash = path
                        break
                
                if git_bash:
                    command = [git_bash, "--login", "-i"]
                else:
                    self.terminal_text.insert(tk.END, "Git Bash not found. Please install Git for Windows or select another shell.\n")
                    return
            else:
                # Use the shell as specified
                command = [shell]
            
            # Start the process with pipes for I/O
            self.terminal_process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                shell=False
            )
            
            # Set terminal as active
            self.terminal_active = True
            
            # Start reader thread for output
            self.start_terminal_reader()
            
            # Display prompt
            self.terminal_text.insert(tk.END, "> ")
            
        except Exception as e:
            self.terminal_text.insert(tk.END, f"Error starting terminal: {str(e)}\n")
    
    def start_terminal_reader(self):
        """Start a thread to read terminal output"""
        if not self.terminal_process:
            return
            
        # Create a daemon thread to read output
        output_thread = threading.Thread(
            target=self.read_terminal_output,
            daemon=True
        )
        output_thread.start()
    
    def read_terminal_output(self):
        """Read output from the terminal process"""
        if not self.terminal_process:
            return
            
        try:
            # Read from stdout
            for line in iter(self.terminal_process.stdout.readline, ''):
                # Schedule update in the main thread
                if hasattr(self, 'root') and self.root.winfo_exists():
                    self.root.after(0, self.update_terminal_output, line)
                    
            # Read from stderr
            for line in iter(self.terminal_process.stderr.readline, ''):
                # Schedule update in the main thread
                if hasattr(self, 'root') and self.root.winfo_exists():
                    self.root.after(0, self.update_terminal_output, line, True)
        except:
            pass
    
    def update_terminal_output(self, line, is_error=False):
        """Update terminal output in the main thread"""
        if hasattr(self, 'terminal_text'):
            # Add the line to the terminal
            self.terminal_text.insert(tk.END, line)
            
            # Color error text in red
            if is_error:
                line_start = self.terminal_text.index("end-1l linestart")
                line_end = self.terminal_text.index("end-1l lineend")
                self.terminal_text.tag_add("error", line_start, line_end)
                self.terminal_text.tag_config("error", foreground="red")
            
            # Scroll to the end
            self.terminal_text.see(tk.END)
    
    def execute_command(self):
        """Execute a command in the terminal"""
        if not self.terminal_process or not self.terminal_active:
            # Start a new terminal if none is active
            self.start_terminal()
            return
            
        # Get the command
        command = self.command_var.get()
        
        if not command:
            return
            
        # Add to history
        self.command_history.append(command)
        self.command_index = len(self.command_history)
        
        # Clear the command entry
        self.command_var.set("")
        
        # Display the command in the terminal
        self.terminal_text.insert(tk.END, f"{command}\n")
        
        # Send the command to the process
        try:
            self.terminal_process.stdin.write(f"{command}\n")
            self.terminal_process.stdin.flush()
        except:
            # Terminal process might have closed
            self.terminal_text.insert(tk.END, "Terminal process is not responding. Please start a new shell.\n")
            self.terminal_active = False
        
        # Scroll to the end
        self.terminal_text.see(tk.END)
    
    def toggle_developer_mode(self):
        """Toggle developer mode."""
        # Show message about restart needed
        messagebox.showinfo(
            "Developer Mode Changed",
            f"Developer Mode has been {'enabled' if self.developer_mode_enabled.get() else 'disabled'}.\n\n"
            f"This change will take effect after restarting the application."
        )
    
    def reset_settings(self):
        """Reset settings to defaults."""
        # Reset theme to dark
        self.theme_var.set("dark")
        self.use_dark_mode = True
        self.colors = self.dark_colors
        
        # Reset font to default
        self.font_var.set("default")
        
        # Reset text size to 10
        self.text_size_var.set(10)
        self.text_size_label.config(text="10")
        
        # Reset log level to INFO
        self.log_level_var.set("INFO")
        
        # Reset developer mode to off
        self.developer_mode_enabled.set(False)
        
        # Apply changes
        self.configure_styles()
        
        # Update text areas
        if hasattr(self, 'log_text'):
            self.log_text.configure(font=('Consolas', 10))
        if hasattr(self, 'notes_text'):
            self.notes_text.configure(font=('Consolas', 10))
            
        messagebox.showinfo(
            "Settings Reset", 
            "All settings have been reset to defaults."
        )
    
    def save_settings(self):
        """Save settings to configuration file."""
        # Create a settings dictionary
        settings = {
            "theme": self.theme_var.get(),
            "font": self.font_var.get(),
            "text_size": self.text_size_var.get(),
            "log_level": self.log_level_var.get(),
            "developer_mode": self.developer_mode_enabled.get(),
            "auto_save_notes": self.auto_save_notes.get() if hasattr(self, 'auto_save_notes') else True
        }
        
        try:
            # Determine the save path
            import os
            config_dir = os.path.dirname(self.config_path.get()) if self.config_path.get() else os.path.expanduser("~/.ai-dev-toolkit")
            
            # Create directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            
            # Save the settings
            settings_file = os.path.join(config_dir, "gui_settings.json")
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
                
            messagebox.showinfo(
                "Settings Saved", 
                f"Settings have been saved to {settings_file}"
            )
        except Exception as e:
            messagebox.showerror(
                "Save Error", 
                f"Error saving settings: {str(e)}"
            )
    
    def load_notes(self):
        """Load notes from file or insert default text if file doesn't exist."""
        try:
            # Clear existing text first
            if hasattr(self, 'notes_text'):
                self.notes_text.delete("1.0", tk.END)
            
            # Determine the save path (in the user's config directory)
            import os
            config_dir = os.path.dirname(self.config_path.get()) if self.config_path.get() else os.path.expanduser("~/.ai-dev-toolkit")
            notes_file = os.path.join(config_dir, "notes.txt")
            
            # Ensure directory exists
            os.makedirs(config_dir, exist_ok=True)
            
            # Load existing notes if file exists
            if os.path.exists(notes_file):
                with open(notes_file, "r", encoding="utf-8") as f:
                    notes_content = f.read()
                self.notes_text.insert(tk.END, notes_content)
                print(f"Notes loaded from {notes_file}")
                # Update status message
                if hasattr(self, 'notes_status_var'):
                    self.notes_status_var.set(f"Notes loaded from {os.path.basename(config_dir)}")
            else:
                # Add default text
                default_note = "This is your personal notepad. Notes are saved between sessions.\n\nUse this area to keep track of your development tasks, ideas, code snippets, or any other information you need to reference while working."
                self.notes_text.insert(tk.END, default_note)
                # Update status
                if hasattr(self, 'notes_status_var'):
                    self.notes_status_var.set("Using default notes")
        except Exception as e:
            # If an error occurs, just use the default text
            default_note = "This is your personal notepad. Notes are saved between sessions.\n\nUse this area to keep track of your development tasks, ideas, code snippets, or any other information you need to reference while working."
            if hasattr(self, 'notes_text'):
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert(tk.END, default_note)
            # Update status
            if hasattr(self, 'notes_status_var'):
                self.notes_status_var.set(f"Error loading notes: {str(e)}")
            print(f"Error loading notes: {str(e)}")
    
    def save_notes(self, event=None):
        """Save notes to a file when the application closes. Returns True on success, False on failure."""
        try:
            # Skip if the widget doesn't exist yet or auto-save is disabled
            if not hasattr(self, 'notes_text') or (hasattr(self, 'auto_save_notes') and not self.auto_save_notes.get()):
                return False
                
            # For event-based calls, only process if event is from root window
            if event and hasattr(event, 'widget') and event.widget != self.root:
                return False
                
            # Check if notes_text widget still exists and is valid
            try:
                # Test if we can access the widget (will raise exception if destroyed)
                self.notes_text.winfo_exists()
                
                # Get the notes content
                notes_content = self.notes_text.get("1.0", tk.END)
                
                # Determine the save path (in the user's config directory)
                import os
                config_dir = os.path.dirname(self.config_path.get()) if self.config_path.get() else os.path.expanduser("~/.ai-dev-toolkit")
                
                # Create directory if it doesn't exist
                os.makedirs(config_dir, exist_ok=True)
                
                # Save the notes
                notes_file = os.path.join(config_dir, "notes.txt")
                with open(notes_file, "w", encoding="utf-8") as f:
                    f.write(notes_content)
                    
                print(f"Notes saved to {notes_file}")
                
                # Update status if the variable exists
                if hasattr(self, 'notes_status_var'):
                    import datetime
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    self.notes_status_var.set(f"Last saved at {now}")
                
                return True
            except tk.TclError:
                # Widget was destroyed, ignore
                print("Widget was destroyed while saving notes")
                return False
        except Exception as e:
            print(f"Error saving notes: {str(e)}")
            if hasattr(self, 'notes_status_var'):
                self.notes_status_var.set(f"Error saving: {str(e)}")
            return False
            
    def schedule_autosave(self, event=None):
        """Schedule an auto-save after typing with a 2-second delay."""
        # Skip if auto-save is disabled
        if not hasattr(self, 'auto_save_notes') or not self.auto_save_notes.get():
            return
            
        # Cancel any existing auto-save timer
        if hasattr(self, 'notes_autosave_id') and self.notes_autosave_id:
            self.root.after_cancel(self.notes_autosave_id)
            
        # Schedule new auto-save timer (2000ms = 2 seconds)
        self.notes_autosave_id = self.root.after(2000, self.perform_autosave)
    
    def perform_autosave(self):
        """Perform the actual auto-save operation."""
        try:
            # Reset the timer ID
            self.notes_autosave_id = None
            
            # Skip if auto-save is disabled
            if not hasattr(self, 'auto_save_notes') or not self.auto_save_notes.get():
                return
                
            # Save the notes
            success = self.save_notes()
            
            # Show a temporary message in the status bar
            if success and hasattr(self, 'notes_status_var'):
                import datetime
                now = datetime.datetime.now().strftime("%H:%M:%S")
                self.notes_status_var.set(f"Auto-saved at {now}")
        except Exception as e:
            if hasattr(self, 'notes_status_var'):
                self.notes_status_var.set(f"Auto-save error: {str(e)}")
            print(f"Error auto-saving notes: {str(e)}")
    
    def save_notes_manually(self):
        """Save notes manually, regardless of auto-save setting."""
        try:
            # Temporarily override auto-save setting
            auto_save_original = self.auto_save_notes.get() if hasattr(self, 'auto_save_notes') else True
            
            if hasattr(self, 'auto_save_notes'):
                self.auto_save_notes.set(True)
            
            # Save the notes
            success = self.save_notes()
            
            # Restore original setting
            if hasattr(self, 'auto_save_notes'):
                self.auto_save_notes.set(auto_save_original)
            
            # Show additional confirmation only on manual save
            if success and hasattr(self, 'notes_status_var'):
                import datetime
                now = datetime.datetime.now().strftime("%H:%M:%S")
                self.notes_status_var.set(f"Manual save at {now}")
                return True
            return success
        except Exception as e:
            if hasattr(self, 'notes_status_var'):
                self.notes_status_var.set(f"Error saving notes: {str(e)}")
            print(f"Error saving notes manually: {str(e)}")
            return False
        
    def create_help_page(self):
        """Create the Help & Troubleshooting page."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Welcome header
        header_frame = ttk.Frame(page, style='Content.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text="Help & Troubleshooting",
            font=('Segoe UI', 16, 'bold'),
            foreground=self.colors["accent"]
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header_frame,
            text="Get help with common issues and learn how to use the toolkit",
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W)
        
        # Common issues section
        issues_frame = ttk.LabelFrame(page, text="Common Issues", padding="10 10 10 10", style='Section.TLabelframe')
        issues_frame.pack(fill=tk.X, expand=False, pady=(0, 15))
        
        # Info icon
        info_frame = ttk.Frame(issues_frame, style='Content.TFrame')
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            info_frame,
            text="ⓘ",
            font=('Segoe UI', 24),
            foreground=self.colors["accent"]
        ).pack(side=tk.LEFT, padx=(10, 15))
        
        # Info text
        info_text_frame = ttk.Frame(info_frame, style='Content.TFrame')
        info_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(
            info_text_frame,
            text="MCP Server Information",
            font=('Segoe UI', 14, 'bold'),
        ).pack(anchor=tk.W)
        
        ttk.Label(
            info_text_frame,
            text="The MCP server is managed by Claude Desktop. Active monitoring is disabled to avoid interference with Claude Desktop's operation.",
            wraplength=600
        ).pack(anchor=tk.W, fill=tk.X, expand=True)
        
        # Troubleshooting tips
        tips_frame = ttk.Frame(issues_frame, style='Content.TFrame')
        tips_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(
            tips_frame,
            text="Troubleshooting Tips:",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor=tk.W)
        
        tips_text = (
            "• If Claude Desktop isn't responding, try restarting it\n"
            "• Use 'Filter Server Log' to check logs when troubleshooting issues\n"
            "• Make sure Claude Desktop has permission to access project directories\n"
            "• The 'Restart MCP Server' button can be used to manually restart the server"
        )
        
        ttk.Label(
            tips_frame,
            text=tips_text,
            justify=tk.LEFT,
            wraplength=600
        ).pack(anchor=tk.W)
        
        # Documentation section
        docs_frame = ttk.LabelFrame(page, text="Documentation & Resources", padding="10 10 10 10", style='Section.TLabelframe')
        docs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        docs_content = ttk.Frame(docs_frame, style='Content.TFrame')
        docs_content.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(
            docs_content,
            text="Quick Links:",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor=tk.W, pady=(0, 5))
        
        links_text = (
            "• README.md - Overview of the toolkit and installation instructions\n"
            "• docs/ai_librarian_guide.md - Detailed guide to using the AI Librarian\n"
            "• docs/todo_list_guide.md - Documentation for the task management system\n"
            "• docs/tools_reference.md - Complete reference of available tools\n"
            "• docs/think-tool-guide.md - Guide to using the Think Tool\n"
            "• docs/upgrading_ai_reference.md - Information about upgrading projects"
        )
        
        ttk.Label(
            docs_content,
            text=links_text,
            justify=tk.LEFT,
            wraplength=600
        ).pack(anchor=tk.W)
        
        # Open docs directory button
        button_frame = ttk.Frame(docs_frame, style='Content.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Use create_action_button for consistency with Quick Actions
        docs_btn = self.create_action_button(
            parent=button_frame,
            icon="📁",
            text="Open Documentation Folder",
            command=self.open_docs_directory
        )
        docs_btn.pack(fill=tk.X, pady=3)
        
        return page
        
    def create_about_page(self):
        """Create the About page."""
        page = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_label = ttk.Label(page, text="About AI Dev Toolkit", style='ContentHeader.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Version info
        version_frame = ttk.Frame(page)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, text=f"Version: {self.version}", font=('Segoe UI', 12)).pack(anchor=tk.W)
        
        # Description
        desc_frame = ttk.LabelFrame(page, text="Description", padding="10 10 10 10", style='Section.TLabelframe')
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        description = """The AI Dev Toolkit enhances Claude with powerful capabilities through its integrated MCP server:

1. File System Tools: Read, write, and navigate the file system securely
2. AI Librarian: Helps Claude understand your codebase with self-checks to ensure proper functionality
3. Task Management: Track development tasks across conversations
4. Enhanced Code Analysis: Find related files, references, and detailed component information
5. Project Starter: Project generation and scaffolding (Coming Soon)
6. Think Tool: Structured reasoning for complex problems"""
        
        ttk.Label(desc_frame, text=description, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Safety information
        safety_frame = ttk.LabelFrame(page, text="Important Safety Information", 
                                    padding="10 10 10 10", style='Section.TLabelframe')
        safety_frame.pack(fill=tk.X, pady=(0, 20))
        
        safety_text = """The AI Dev Toolkit provides an MCP (Model Context Protocol) server that Claude can use to access your files and execute tools on your computer.

IMPORTANT: The AI Dev Toolkit application edits Claude Desktop's configuration to enable these tools. Claude itself does not have direct access to edit configuration files. All file operations and tool executions happen in your local environment and with your explicit permission.

When you enable project directories, you are granting Claude permission to read from and write to those directories. Choose directories carefully."""
        
        ttk.Label(safety_frame, text=safety_text, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Links
        links_frame = ttk.Frame(page)
        links_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(links_frame, text="Resources:", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Documentation link
        doc_link = ttk.Label(links_frame, text="Model Context Protocol Documentation", 
                           foreground="blue", cursor="hand2")
        doc_link.pack(anchor=tk.W, pady=2)
        doc_link.bind("<Button-1>", lambda e: webbrowser.open("https://modelcontextprotocol.io"))
        
        # GitHub link
        github_link = ttk.Label(links_frame, text="AI Dev Toolkit on GitHub", 
                              foreground="blue", cursor="hand2")
        github_link.pack(anchor=tk.W, pady=2)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/isekaizen/ai-dev-toolkit"))
        
        # MCP Servers link 
        servers_link = ttk.Label(links_frame, text="Official MCP Servers Repository", 
                               foreground="blue", cursor="hand2")
        servers_link.pack(anchor=tk.W, pady=2)
        servers_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/modelcontextprotocol/servers"))
        
        return page
        
    def create_action_button(self, parent, icon, text, command):
        """Create a modern action button with icon and text."""
        button_frame = ttk.Frame(parent, style='ActionButton.TFrame')
        
        # Outer padding frame to add vertical space
        padding_frame = ttk.Frame(button_frame, style='ActionButton.TFrame')
        padding_frame.pack(fill=tk.BOTH, expand=True, pady=6)  # Add 6 pixels of padding top and bottom
        
        # Icon label - fixed width ensures alignment - increased width
        icon_label = ttk.Label(
            padding_frame,
            text=icon,
            style='ActionButton.TLabel',
            width=3,  # Increased from 2 to 3 to prevent cutoff
            anchor='center'
        )
        icon_label.pack(side=tk.LEFT, padx=(5, 5))
        
        # Text label with increased font size
        text_label = ttk.Label(
            padding_frame,
            text=text,
            style='ActionButton.TLabel',
            font=('Segoe UI', 11)  # Increased font size from 10 to 11
        )
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        
        # Make the entire frame clickable
        button_frame.bind("<Button-1>", lambda e: command())
        padding_frame.bind("<Button-1>", lambda e: command())
        icon_label.bind("<Button-1>", lambda e: command())
        text_label.bind("<Button-1>", lambda e: command())
        
        # Handle hover effect
        def on_enter(e):
            button_frame.configure(style='ActionButtonHover.TFrame')
            padding_frame.configure(style='ActionButtonHover.TFrame')
            icon_label.configure(style='ActionButtonHover.TLabel')
            text_label.configure(style='ActionButtonHover.TLabel', font=('Segoe UI', 11))
                    
        def on_leave(e):
            button_frame.configure(style='ActionButton.TFrame')
            padding_frame.configure(style='ActionButton.TFrame')
            icon_label.configure(style='ActionButton.TLabel')
            text_label.configure(style='ActionButton.TLabel', font=('Segoe UI', 11))
        
        # Bind hover events
        button_frame.bind("<Enter>", on_enter)
        padding_frame.bind("<Enter>", on_enter)
        icon_label.bind("<Enter>", on_enter)
        text_label.bind("<Enter>", on_enter)
        
        button_frame.bind("<Leave>", on_leave)
        padding_frame.bind("<Leave>", on_leave)
        icon_label.bind("<Leave>", on_leave)
        text_label.bind("<Leave>", on_leave)
        
        return button_frame
        
    #-----------------------------------------------------
    # Utility Methods - required from legacy implementation
    #-----------------------------------------------------
    def start_periodic_status_check(self):
        """Start a periodic check of server status"""
        self.check_status_periodically()
    
    def check_status_periodically(self):
        """Check server status periodically"""
        if hasattr(self, 'root') and self.root.winfo_exists():
            # Check server status
            self.check_server_status()
            
            # Schedule the next check - much more frequent (every 500ms)
            self.root.after(500, self.check_status_periodically)  # Check 2x per second
    
    def on_closing(self):
        """Handle window close event"""
        if self.has_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                "You have unsaved changes. Would you like to save them before exiting?")
            
            if response is None:  # Cancel was clicked
                return
            elif response:  # Yes was clicked
                self.apply_claude_config()
        
        # Stop the server if it's running and we started it
        # (don't stop externally started servers)
        if hasattr(self, 'server_process') and self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
        
        # Stop monitoring
        if hasattr(self, 'log_monitor_active'):
            self.log_monitor_active = False
        
        self.root.destroy()
    
    def apply_and_exit(self):
        """Apply changes and exit the application"""
        self.apply_claude_config()
        self.root.quit()
    
    def discard_and_exit(self):
        """Discard changes and exit the application"""
        if self.has_changes:
            if not messagebox.askyesno("Confirm", "You have unsaved changes. Are you sure you want to exit without saving?"):
                return
        self.root.quit()
    
    def apply_claude_config(self):
        """Apply changes to Claude Desktop configuration file"""
        config_path = self.config_path.get()
        if not config_path:
            messagebox.showinfo("No Config", "No Claude Desktop configuration file specified.")
            return
        
        try:
            # Read existing config
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Ensure mcpServers section exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            # Remove previous servers if they exist
            for old_server in ["integrated-server", "ai-librarian", "file-system-tools"]:
                if old_server in config["mcpServers"]:
                    del config["mcpServers"][old_server]
            
            # Add our server using the EXACT working pattern from ai-librarian
            if self.ai_dev_toolkit_server_enabled.get():
                server_config = self.generate_integrated_server_config()
                config["mcpServers"]["ai-librarian"] = server_config
            
            # Save the config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.project_message_var.set("Configuration saved successfully! You may need to restart Claude Desktop.")
            self.has_changes = False
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            print(f"Error saving config: {str(e)}")
    
    def generate_integrated_server_config(self):
        """Generate the configuration for the integrated server that EXACTLY matches the working ai-librarian pattern"""
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Get enabled directories
        enabled_dirs = [d for d in self.project_dirs if self.project_enabled.get(d, True)]
        
        # Use the EXACT working pattern from ai-librarian:
        # - command: "python" (not sys.executable)
        # - args: [script_path, dir1, dir2, ...] (putting directories directly in args array, not in env vars)
        server_config = {
            "command": "python",
            "args": [
                os.path.join(project_root, "aitoolkit", "librarian", "server.py")
            ] + enabled_dirs
        }
        
        return server_config
        
    # More required methods
    def detect_claude_desktop(self):
        """Detect Claude Desktop installation and config location"""
        # Only update the config status label (System Status section was removed)
        self.claude_config_status_label.config(text="Checking Claude Desktop installation...")
        
        # Detect platform and find config path
        import platform
        system = platform.system()
        
        config_path = None
        if system == "Windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                config_path = os.path.join(appdata, "Claude", "claude_desktop_config.json")
        elif system == "Darwin":  # macOS
            home = os.path.expanduser("~")
            config_path = os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
        elif system == "Linux":
            home = os.path.expanduser("~")
            config_path = os.path.join(home, ".config", "Claude", "claude_desktop_config.json")
        
        if config_path and os.path.exists(config_path):
            self.config_path.set(config_path)
            # Update only the config status label
            self.claude_config_status_label.config(text=f"Claude Desktop detected. Config: {config_path}")
        else:
            # Update only the config status label
            self.claude_config_status_label.config(text="Claude Desktop not found. Please specify the config path manually.")
    
    def load_config(self):
        """Load configuration from Claude Desktop config file"""
        config_path = self.config_path.get()
        if not config_path or not os.path.exists(config_path):
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check if AI Dev Toolkit is in the mcpServers section
            if "mcpServers" in config:
                has_integrated = "integrated-server" in config["mcpServers"]
                has_legacy_ai_librarian = "ai-librarian" in config["mcpServers"]
                has_legacy_file_system = "file-system-tools" in config["mcpServers"]
                
                self.ai_dev_toolkit_server_enabled.set(has_integrated or has_legacy_ai_librarian or has_legacy_file_system)
                
                # Load allowed directories from args
                # Clear existing project dirs to avoid duplication
                self.project_dirs = []
                
                # Load from AI Librarian server if present
                if has_legacy_ai_librarian and "args" in config["mcpServers"]["ai-librarian"]:
                    args = config["mcpServers"]["ai-librarian"]["args"]
                    # Skip the first item which is the script path
                    dir_paths = args[1:] if len(args) > 1 else []
                    
                    # Filter existing directories and add to project list
                    for dir_path in dir_paths:
                        if os.path.exists(dir_path) and dir_path not in self.project_dirs:
                            self.project_dirs.append(dir_path)
                            self.project_enabled[dir_path] = True
                
                # Load from integrated server if present
                elif has_integrated and "args" in config["mcpServers"]["integrated-server"]:
                    args = config["mcpServers"]["integrated-server"]["args"]
                    # Skip the first item which is the script path
                    dir_paths = args[1:] if len(args) > 1 else []
                    
                    # Filter existing directories and add to project list
                    for dir_path in dir_paths:
                        if os.path.exists(dir_path) and dir_path not in self.project_dirs:
                            self.project_dirs.append(dir_path)
                            self.project_enabled[dir_path] = True
                            
                # Update project displays
                self.update_projects_list()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
            print(f"Error loading config: {str(e)}")
            
    def load_gui_settings(self):
        """Load GUI settings from saved settings file."""
        try:
            # Determine the settings file path
            import os
            config_dir = os.path.dirname(self.config_path.get()) if self.config_path.get() else os.path.expanduser("~/.ai-dev-toolkit")
            settings_file = os.path.join(config_dir, "gui_settings.json")
            
            # Check if settings file exists
            if not os.path.exists(settings_file):
                return  # Use defaults if no settings file
                
            # Load settings
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                
            # Apply theme settings
            if "theme" in settings:
                self.theme_var.set(settings["theme"])
                self.use_dark_mode = settings["theme"] == "dark"
                if settings["theme"] == "system":
                    # Try to detect system theme
                    self.toggle_theme(show_message=False)  # Will handle detection without showing message
                else:
                    self.colors = self.dark_colors if self.use_dark_mode else self.light_colors
                    self.configure_styles()
                
            # Apply font settings
            if "font" in settings:
                self.font_var.set(settings["font"])
                
            # Apply text size
            if "text_size" in settings:
                self.text_size_var.set(settings["text_size"])
                
            # Apply log level
            if "log_level" in settings:
                self.log_level_var.set(settings["log_level"])
                
            # Apply developer mode setting
            if "developer_mode" in settings:
                self.developer_mode_enabled.set(settings["developer_mode"])
            
            # Apply auto-save notes setting
            if "auto_save_notes" in settings and hasattr(self, 'auto_save_notes'):
                self.auto_save_notes.set(settings["auto_save_notes"])
                
            # Apply font and size settings to text areas
            if hasattr(self, 'log_text') and hasattr(self, 'notes_text'):
                # Get the font family based on setting
                font_family = "Consolas"  # Default monospace
                if settings.get("font") == "dyslexic":
                    font_family = "OpenDyslexic"
                elif settings.get("font") == "system":
                    # Detect system monospace font
                    import platform
                    system = platform.system()
                    if system == "Windows":
                        font_family = "Consolas"
                    elif system == "Darwin":  # macOS
                        font_family = "Menlo"
                    else:  # Linux
                        font_family = "DejaVu Sans Mono"
                
                # Get size
                font_size = settings.get("text_size", 10)
                
                # Apply to text areas
                self.log_text.configure(font=(font_family, font_size))
                self.notes_text.configure(font=(font_family, font_size))
                
        except Exception as e:
            # Just log error, don't show message box for settings load failure
            print(f"Error loading GUI settings: {str(e)}")
            # Use defaults
    
    def check_server_status(self):
        """Minimal server check - only for internal use, not for display"""
        # Check if our own server process is running
        own_server_running = (hasattr(self, 'server_process') and 
                             self.server_process and 
                             self.server_process.poll() is None)
        
        # Stop any active log monitoring if it exists
        if hasattr(self, 'log_monitor_active') and self.log_monitor_active:
            self.log_monitor_active = False
                
    def check_for_external_server(self):
        """Check if an external MCP server is already running - optimized for speed."""
        try:
            # Fast socket check first (lowest overhead)
            import socket
            
            # Try to connect to the default port (3000) with minimal timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Reduced timeout for faster response
            result = sock.connect_ex(('localhost', 3000))
            sock.close()
            
            # If port is open, something is running there
            if result == 0:
                return True
            
            # Skip the more expensive psutil check most of the time
            # Only do the full check occasionally (every 10th check)
            if not hasattr(self, 'full_check_counter'):
                self.full_check_counter = 0
                
            self.full_check_counter += 1
            if self.full_check_counter >= 10:
                self.full_check_counter = 0
                
                # Also check if there's a running Python process with server.py in its command line
                # Only run this check occasionally to reduce CPU load
                if PSUTIL_AVAILABLE:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            cmdline = proc.cmdline()
                            if any("server.py" in cmd for cmd in cmdline if cmd):
                                # Found a running server.py process
                                return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                        
            return False
        except Exception as e:
            print(f"Error checking for external server: {str(e)}")
            return False
            
    def add_warning_message(self, message):
        """Add a warning message to the log text widget from the main thread"""
        try:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                
                # Add the warning message
                self.log_text.insert(tk.END, f"{message}\n")
                
                # Make the warning stand out
                self.log_text.tag_add("hang_warning", "end-2l", "end-1c")
                self.log_text.tag_config("hang_warning", foreground="red", font=('Consolas', 10, 'bold'))
                
                # Keep only the last 500 lines
                num_lines = int(self.log_text.index('end-1c').split('.')[0])
                if num_lines > 500:
                    self.log_text.delete('1.0', f"{num_lines-500}.0")
                
                # Scroll to the end
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error adding warning message: {str(e)}")
    
    def update_log_text(self, lines, has_request_start=False, has_request_end=False):
        """Update the log text widget from the main thread"""
        try:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                
                # Add each new line
                for line in lines:
                    self.log_text.insert(tk.END, f"{line}\n")
                
                # Keep only the last 500 lines
                num_lines = int(self.log_text.index('end-1c').split('.')[0])
                if num_lines > 500:
                    self.log_text.delete('1.0', f"{num_lines-500}.0")
                
                # Scroll to the end
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                
                # Update request tracking
                if has_request_start:
                    self.last_request_time = time.time()
                if has_request_end:
                    self.last_request_time = None
        except Exception as e:
            print(f"Error updating log text: {str(e)}")
            
    def get_external_server_pid(self):
        """Get the process ID of the external server"""
        try:
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.cmdline()
                        if any("server.py" in cmd for cmd in cmdline if cmd):
                            # Found the server process
                            return proc.pid
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
            return None
        except Exception as e:
            print(f"Error getting external server PID: {str(e)}")
            return None
            
    def find_server_log_file(self, server_pid):
        """Find the log file for the server process"""
        if not server_pid:
            return None
            
        try:
            # Common log file patterns to check
            log_patterns = [
                # Current working directory of the process
                os.path.join(os.getcwd(), "server.log"),
                os.path.join(os.getcwd(), "mcp_server.log"),
                os.path.join(os.getcwd(), "ai_librarian_server.log"),
                
                # Logs directory
                os.path.join(os.getcwd(), "logs", "server.log"),
                os.path.join(os.getcwd(), "logs", "mcp_server.log"),
                
                # Temp directory logs
                os.path.join(os.path.expandvars("%TEMP%"), "claude_server.log"),
                os.path.join("/tmp", f"claude_server_{server_pid}.log"),
                
                # Look in the AI Dev Toolkit directory
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "server.log"),
                
                # Check for AI Librarian logs
                os.path.join(os.path.expanduser("~"), ".claude", "logs", "server.log")
            ]
            
            # Check if any of these log files exist
            for log_path in log_patterns:
                try:
                    if os.path.exists(log_path) and os.path.isfile(log_path):
                        # Verify this is a log file by checking if it's writable
                        # and has recent modifications
                        if os.access(log_path, os.R_OK):
                            # Check if it was modified recently (last 24 hours)
                            if time.time() - os.path.getmtime(log_path) < 86400:  # 24 hours in seconds
                                return log_path
                except:
                    continue
                    
            # If no log file found by pattern, try looking at file descriptors
            # This only works on Linux/Unix systems with psutil
            if PSUTIL_AVAILABLE and hasattr(psutil, "Process"):
                try:
                    proc = psutil.Process(server_pid)
                    
                    # Check open files
                    for open_file in proc.open_files():
                        if "log" in open_file.path.lower() and os.access(open_file.path, os.R_OK):
                            return open_file.path
                except:
                    pass
                
            # Alternative approach: look for recently modified log files in project directories
            for dir_path in self.project_dirs:
                try:
                    # Check for log files in this directory and its logs subdirectory
                    log_dirs = [dir_path, os.path.join(dir_path, "logs")]
                    
                    for log_dir in log_dirs:
                        if os.path.exists(log_dir) and os.path.isdir(log_dir):
                            # Look for .log files
                            for file in os.listdir(log_dir):
                                if file.endswith(".log"):
                                    log_path = os.path.join(log_dir, file)
                                    # Check if it's a recently modified file
                                    if time.time() - os.path.getmtime(log_path) < 86400:  # 24 hours
                                        return log_path
                except:
                    continue
                    
            # No log file found
            return None
        except Exception as e:
            print(f"Error finding server log file: {str(e)}")
            return None
            
    def start_file_log_monitoring(self, log_file_path):
        """Start monitoring a log file for an external server"""
        self.log_monitor_active = True
        self.log_file_path = log_file_path
        self.file_monitor_thread = threading.Thread(target=self.monitor_log_file, daemon=True)
        self.file_monitor_thread.start()
        
    def monitor_log_file(self):
        """Monitor a log file for changes"""
        import time
        import re
        import os
        
        # Server hang detection patterns
        request_pattern = re.compile(r'Processing request.*')
        completion_pattern = re.compile(r'Request completed.*')
        hang_threshold = 60  # seconds
        self.last_request_time = None
        
        # Initial file position
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                # Go to the end of the file
                f.seek(0, 2)
                file_position = f.tell()
        except Exception as e:
            print(f"Error opening log file: {str(e)}")
            return
            
        # Monitoring loop
        while hasattr(self, 'log_monitor_active') and self.log_monitor_active:
            try:
                # Check if file exists and is readable
                if not os.path.exists(self.log_file_path) or not os.access(self.log_file_path, os.R_OK):
                    # File disappeared or permissions changed
                    time.sleep(1)
                    continue
                    
                # Open file and check for new content
                with open(self.log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                    f.seek(file_position)
                    new_lines = f.readlines()
                    file_position = f.tell()
                    
                    if new_lines:
                        # Process new lines - use the after method to update GUI from the main thread
                        if hasattr(self, 'root') and self.root.winfo_exists():
                            # Prepare the data for the update
                            timestamp = time.strftime('%H:%M:%S')
                            processed_lines = []
                            has_request_start = False
                            has_request_end = False
                            
                            for line in new_lines:
                                line = line.strip()
                                if line:  # Skip empty lines
                                    processed_lines.append(f"[{timestamp}] {line}")
                                    
                                    # Check for request patterns
                                    if request_pattern.search(line):
                                        has_request_start = True
                                    elif completion_pattern.search(line):
                                        has_request_end = True
                            
                            # Use the after method to update in the main thread
                            if processed_lines:
                                self.root.after(0, self.update_log_text, processed_lines, has_request_start, has_request_end)
                
                # Check for hanging requests
                if self.last_request_time and (time.time() - self.last_request_time) > hang_threshold:
                    # Add warning about hanging request - use the after method to update in the main thread
                    if hasattr(self, 'root') and self.root.winfo_exists():
                        timestamp = time.strftime('%H:%M:%S')
                        warning_message = f"[{timestamp}] WARNING: Request hang detected! " + \
                                        f"A request has been processing for over {hang_threshold} seconds. " + \
                                        f"Consider restarting Claude Desktop."
                        
                        # Schedule the warning update in the main thread
                        self.root.after(0, self.add_warning_message, warning_message)
                        
                        # Reset to avoid multiple warnings
                        self.last_request_time = time.time()
                
                # Sleep to avoid high CPU usage
                time.sleep(0.5)  # Check twice a second for new log entries
                
            except Exception as e:
                print(f"Error monitoring log file: {str(e)}")
                time.sleep(1)  # Wait a bit before trying again
                
    def start_log_monitoring(self):
        """Start monitoring server log for updates"""
        self.log_monitor_active = True
        self.last_request_time = None
        self.monitor_thread = threading.Thread(target=self.monitor_log_for_hangs, daemon=True)
        self.monitor_thread.start()
        
    def monitor_log_for_hangs(self):
        """Monitor the server log to detect potential hanging requests"""
        import time
        import re
        request_pattern = re.compile(r'Processing request.*')
        completion_pattern = re.compile(r'Request completed.*')
        
        hang_threshold = 60  # seconds before considering a request as hanging
        
        while hasattr(self, 'log_monitor_active') and self.log_monitor_active:
            # Check for new log entries if we have a log text widget
            if hasattr(self, 'log_text') and hasattr(self, 'server_process') and self.server_process:
                # Get any new output from the server process
                if hasattr(self.server_process, 'stdout') and self.server_process.stdout:
                    try:
                        # Read new output without blocking
                        output = self.server_process.stdout.readline().decode('utf-8')
                        if output:
                            # Enable text widget for editing
                            self.log_text.config(state=tk.NORMAL)
                            
                            # Add new log entry with timestamp
                            timestamp = time.strftime('%H:%M:%S')
                            self.log_text.insert(tk.END, f"[{timestamp}] {output}\n")
                            
                            # Keep only the last 500 lines
                            num_lines = int(self.log_text.index('end-1c').split('.')[0])
                            if num_lines > 500:
                                self.log_text.delete('1.0', f"{num_lines-500}.0")
                            
                            # Scroll to the end
                            self.log_text.see(tk.END)
                            
                            # Disable editing
                            self.log_text.config(state=tk.DISABLED)
                            
                            # Check for request start/end
                            if request_pattern.search(output):
                                self.last_request_time = time.time()
                            elif completion_pattern.search(output):
                                self.last_request_time = None
                    except Exception as e:
                        print(f"Error monitoring log: {str(e)}")
                
                # Check for hanging requests
                if self.last_request_time and (time.time() - self.last_request_time) > hang_threshold:
                    # Enable text widget for editing
                    self.log_text.config(state=tk.NORMAL)
                    
                    # Add warning about hanging request
                    timestamp = time.strftime('%H:%M:%S')
                    self.log_text.insert(tk.END, f"[{timestamp}] WARNING: Request hang detected! " +
                                      f"A request has been processing for over {hang_threshold} seconds. " +
                                      f"Consider restarting Claude Desktop.\n")
                    
                    # Make the warning stand out
                    self.log_text.tag_add("hang_warning", "end-2l", "end-1c")
                    self.log_text.tag_config("hang_warning", foreground="red", font=('Consolas', 10, 'bold'))
                    
                    # Scroll to the end
                    self.log_text.see(tk.END)
                    
                    # Disable editing
                    self.log_text.config(state=tk.DISABLED)
                    
                    # Reset to avoid multiple warnings
                    self.last_request_time = time.time()
                    
            # Sleep to avoid high CPU usage
            time.sleep(1)
    
    def scan_for_projects(self):
        """Scan authorized directories for .ai_reference folders to find existing projects"""
        # Clear status message
        self.project_message_var.set("Scanning for projects with .ai_reference folders...")
        
        # Keep track of found projects and their status
        found_projects = []
        
        # Only check for .ai_reference in directories we already have permission to access
        # This ensures we only find projects in locations Claude can actually use
        for dir_path in self.project_dirs:
            try:
                # Check if this directory itself has an .ai_reference folder
                if os.path.exists(os.path.join(dir_path, ".ai_reference")):
                    if dir_path not in found_projects:
                        found_projects.append(dir_path)
                
                # Check only immediate subdirectories of authorized directories
                # This avoids scanning unrelated system directories
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    for subdir in os.listdir(dir_path):
                        full_path = os.path.join(dir_path, subdir)
                        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, ".ai_reference")):
                            if full_path not in self.project_dirs and full_path not in found_projects:
                                found_projects.append(full_path)
            except (PermissionError, FileNotFoundError):
                # Skip directories we can't access
                continue
        
        # Add found projects that aren't already in the list
        new_projects = []
        for project in found_projects:
            if project not in self.project_dirs:
                self.project_dirs.append(project)
                self.project_enabled[project] = True
                new_projects.append(project)
        
        # Update the UI
        if new_projects:
            self.update_projects_list()
            self.project_message_var.set(f"Found {len(new_projects)} new projects with .ai_reference folders.")
        else:
            self.project_message_var.set("No new projects with .ai_reference folders found.")
    
    def update_projects_list(self):
        """Update the projects list display using the treeview"""
        # Clear the treeview
        for item in self.projects_treeview.get_children():
            self.projects_treeview.delete(item)
        
        # Remove any duplicate entries from project_dirs
        unique_dirs = []
        for dir_path in self.project_dirs:
            if dir_path not in unique_dirs:
                unique_dirs.append(dir_path)
        
        # Update project_dirs with the deduplicated list
        self.project_dirs = unique_dirs
        
        # Populate with current projects
        for i, dir_path in enumerate(self.project_dirs):
            enabled = self.project_enabled.get(dir_path, True)
            
            # Check if path has AI Librarian
            has_ai_ref = os.path.exists(os.path.join(dir_path, ".ai_reference"))
            status = "AI Librarian" if has_ai_ref else "Regular"
            
            # Default values for other columns
            private_status = self.project_privacy.get(dir_path, "Public")
            last_accessed = self.project_last_accessed.get(dir_path, "Unknown")
            git_status = self.project_git_status.get(dir_path, "Unknown")
            
            # Add to treeview with checkbox state
            item_id = self.projects_treeview.insert('', 'end', 
                                                  text="✓" if enabled else "◻", 
                                                  values=(private_status, dir_path, status, last_accessed, git_status))
    
    def update_server_status(self):
        """Update server status based on selected tools"""
        # Sidebar status indicator was removed completely
        # Just mark changes needed
        self.has_changes = True
    
    def update_server_config_type(self):
        """Update server configuration type information"""
        if self.server_config_type.get() == "npm":
            self.npm_config_note.pack(fill=tk.X, pady=(0, 5))
            if hasattr(self, 'uv_config_note'):
                self.uv_config_note.pack_forget()
        else:
            if hasattr(self, 'npm_config_note'):
                self.npm_config_note.pack_forget()
            self.uv_config_note.pack(fill=tk.X, pady=(0, 5))
    
    def browse_config(self):
        """Browse for Claude Desktop config file"""
        config_file = filedialog.askopenfilename(
            title="Select Claude Desktop Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if config_file:
            self.config_path.set(config_file)
    
    def restart_claude_desktop(self):
        """Restart the Claude Desktop application"""
        if not PSUTIL_AVAILABLE:
            messagebox.showwarning(
                "Missing Dependency", 
                "The psutil module is required for this feature.\n"
                "Please install it with: pip install psutil"
            )
            return
        
        try:
            # Find Claude Desktop process
            claude_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    # Look for Claude in process name
                    if proc.info['name'] and 'claude' in proc.info['name'].lower():
                        claude_processes.append(proc)
                    # Look for Claude in the path if available
                    elif proc.info['exe'] and 'claude' in proc.info['exe'].lower():
                        claude_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not claude_processes:
                messagebox.showinfo(
                    "Claude Desktop Not Found", 
                    "Could not find any running Claude Desktop processes."
                )
                return
            
            # Create confirmation dialog with the list of processes found
            confirm_dialog = tk.Toplevel(self.root)
            confirm_dialog.title("Confirm Restart")
            confirm_dialog.geometry("500x300")
            confirm_dialog.transient(self.root)
            confirm_dialog.grab_set()
            
            # Create main frame
            main_frame = ttk.Frame(confirm_dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                main_frame, 
                text="The following Claude Desktop processes will be restarted:", 
                font=('Segoe UI', 11)
            ).pack(pady=(0, 10))
            
            # List the processes
            process_frame = ttk.Frame(main_frame)
            process_frame.pack(fill=tk.BOTH, expand=True)
            
            process_text = tk.Text(process_frame, height=10, width=60)
            process_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(process_frame, orient=tk.VERTICAL, command=process_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            process_text.config(yscrollcommand=scrollbar.set)
            
            for proc in claude_processes:
                try:
                    name = proc.name()
                    pid = proc.pid
                    cmdline = " ".join(proc.cmdline()) if hasattr(proc, 'cmdline') else "Unknown"
                    exe_path = proc.exe() if hasattr(proc, 'exe') else "Unknown"
                    
                    process_text.insert(tk.END, f"PID: {pid} - {name}\n")
                    process_text.insert(tk.END, f"Path: {exe_path}\n")
                    process_text.insert(tk.END, f"Command: {cmdline}\n\n")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    process_text.insert(tk.END, f"PID: {proc.info['pid']} - Access Denied\n\n")
            
            process_text.config(state=tk.DISABLED)
            
            # Warning message
            ttk.Label(
                main_frame, 
                text="Warning: This will close Claude Desktop. Any unsaved work may be lost.",
                foreground="red"
            ).pack(pady=10)
            
            # Function to terminate and restart processes
            def terminate_and_restart():
                # Gather process info for restart before terminating
                restart_info = []
                
                for proc in claude_processes:
                    try:
                        # Store info needed for restart
                        info = {
                            'exe': proc.exe() if hasattr(proc, 'exe') else None,
                            'cmdline': proc.cmdline() if hasattr(proc, 'cmdline') else None,
                            'cwd': proc.cwd() if hasattr(proc, 'cwd') else None
                        }
                        restart_info.append(info)
                        
                        # Terminate the process
                        proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Wait for processes to terminate
                def check_termination():
                    all_terminated = True
                    for proc in claude_processes:
                        try:
                            if proc.is_running():
                                all_terminated = False
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                    
                    if all_terminated:
                        # All processes are terminated, attempt to restart
                        restart_claude(restart_info)
                    else:
                        # Check again in 500ms
                        confirm_dialog.after(500, check_termination)
                
                # Function to restart Claude Desktop
                def restart_claude(restart_info):
                    try:
                        # Try to restart Claude Desktop
                        restarted = False
                        
                        for info in restart_info:
                            exe = info['exe']
                            cmdline = info['cmdline']
                            cwd = info['cwd']
                            
                            if exe and os.path.exists(exe):
                                # Start the process
                                if cmdline:
                                    subprocess.Popen(cmdline, cwd=cwd)
                                else:
                                    subprocess.Popen([exe], cwd=cwd)
                                restarted = True
                        
                        if restarted:
                            messagebox.showinfo(
                                "Restart Successful", 
                                "Claude Desktop has been restarted."
                            )
                        else:
                            messagebox.showwarning(
                                "Restart Failed", 
                                "Terminated Claude Desktop, but couldn't restart it automatically.\n"
                                "Please restart Claude Desktop manually."
                            )
                    except Exception as e:
                        messagebox.showerror(
                            "Restart Error", 
                            f"Error restarting Claude Desktop: {str(e)}\n"
                            "Please restart Claude Desktop manually."
                        )
                    finally:
                        confirm_dialog.destroy()
                
                # Start checking for termination
                check_termination()
            
            # Function to just terminate without restart
            def just_terminate():
                for proc in claude_processes:
                    try:
                        proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                messagebox.showinfo(
                    "Claude Desktop Terminated", 
                    "Claude Desktop has been terminated. Please restart it manually."
                )
                confirm_dialog.destroy()
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(
                button_frame, 
                text="Terminate and Restart", 
                command=terminate_and_restart
            ).pack(side=tk.LEFT)
            
            ttk.Button(
                button_frame, 
                text="Just Terminate", 
                command=just_terminate
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame, 
                text="Cancel", 
                command=confirm_dialog.destroy
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"An error occurred: {str(e)}"
            )
    
    def restart_server(self):
        """Restart the MCP server process"""
        try:
            # Check if we already have a server process running
            own_server_running = (hasattr(self, 'server_process') and 
                                self.server_process and 
                                self.server_process.poll() is None)
            
            # Check for external server process
            external_server_running = self.check_for_external_server()
            
            # Stop any existing server
            if own_server_running:
                # Stop our own process
                self.stop_server()
            elif external_server_running:
                # Try to stop external server
                if self.stop_external_server():
                    messagebox.showinfo("Server Stopped", 
                                     "External server has been stopped. Starting a new server process that can be monitored.")
                else:
                    response = messagebox.askyesno("External Server", 
                                                "An external server is running, but we couldn't stop it automatically. " +
                                                "Start a new server anyway?")
                    if not response:
                        return
            
            # Start a new server process
            self.start_server()
            
            # Update status
            self.check_server_status()
        except Exception as e:
            messagebox.showerror("Restart Error", f"Error restarting server: {str(e)}")
            
    def stop_server(self):
        """Stop our own server process if it's running"""
        if hasattr(self, 'server_process') and self.server_process:
            try:
                # Terminate the process
                self.server_process.terminate()
                
                # Wait for it to exit (with timeout)
                try:
                    self.server_process.wait(timeout=5)
                except:
                    # Force kill if it didn't exit cleanly
                    if self.server_process.poll() is None:
                        self.server_process.kill()
                        self.server_process.wait(timeout=2)
                
                # Stop monitoring if active
                if hasattr(self, 'log_monitor_active'):
                    self.log_monitor_active = False
                
                # Update status
                self.check_server_status()
                
                return True
            except Exception as e:
                print(f"Error stopping server: {str(e)}")
                return False
        
        return True  # No server to stop
        
    def stop_external_server(self):
        """Try to stop an externally running server (e.g., started by Claude Desktop)"""
        try:
            if PSUTIL_AVAILABLE:
                # Try to find the server process by command line
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.cmdline()
                        if any("server.py" in cmd for cmd in cmdline if cmd):
                            # Found the server process, try to terminate it
                            proc.terminate()
                            try:
                                proc.wait(timeout=5)
                            except:
                                # Force kill if it didn't exit cleanly
                                if proc.is_running():
                                    proc.kill()
                                    proc.wait(timeout=2)
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
            
            # If we get here, either psutil isn't available or we didn't find/stop the process
            return False
        except Exception as e:
            print(f"Error stopping external server: {str(e)}")
            return False
            
    def start_server(self):
        """Start a new server process"""
        try:
            # Generate server configuration
            server_config = self.generate_integrated_server_config()
            
            # Prepare command and arguments
            command = server_config["command"]
            args = server_config["args"]
            
            # Get the full command
            full_command = [command] + args
            
            # Start the process
            import subprocess
            self.server_process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,  # We'll handle decoding in the monitor thread
                bufsize=1    # Line buffered
            )
            
            # Update the log text
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete('1.0', tk.END)
                self.log_text.insert(tk.END, f"Server started with PID {self.server_process.pid}\n")
                self.log_text.insert(tk.END, f"Command: {' '.join(full_command)}\n\n")
                self.log_text.insert(tk.END, "Waiting for log output...")
                self.log_text.config(state=tk.DISABLED)
            
            # Update status immediately
            self.check_server_status()
            
            return True
        except Exception as e:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"Error starting server: {str(e)}\n")
                self.log_text.config(state=tk.DISABLED)
            print(f"Error starting server: {str(e)}")
            return False
    
    def clear_request_queue(self):
        """Clear the request queue for the MCP server"""
        messagebox.showinfo("Not Implemented", "Clear Request Queue functionality is not yet implemented in the modern UI.")
    
    def filter_server_log(self):
        """Open log explorer window to view and filter server logs"""
        # Find log files
        log_files = self.find_server_log_files()
        
        if not log_files:
            messagebox.showinfo(
                "No Logs Found",
                "No server log files were found. Try starting the server first."
            )
            return
            
        # Create the log explorer window
        self.create_log_explorer_window(log_files)
    
    def find_server_log_files(self):
        """Find all server log files that might be relevant"""
        import os
        import glob
        
        log_files = []
        
        # Try to use the external log file if we found one
        if hasattr(self, 'external_log_file') and self.external_log_file:
            if os.path.exists(self.external_log_file):
                log_files.append(self.external_log_file)
        
        # Search in common locations
        log_locations = [
            # Current directory
            os.path.join(os.getcwd(), "*.log"),
            
            # Logs directory
            os.path.join(os.getcwd(), "logs", "*.log"),
            
            # Project root (up one level from GUI module)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "*.log"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "*.log"),
            
            # Home directory .claude folder
            os.path.join(os.path.expanduser("~"), ".claude", "logs", "*.log"),
            
            # Temp directories
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "claude_*.log"),
            os.path.join("/tmp", "claude_*.log")
        ]
        
        # Add any project directories
        for project_dir in self.project_dirs:
            log_locations.append(os.path.join(project_dir, "*.log"))
            log_locations.append(os.path.join(project_dir, "logs", "*.log"))
        
        # Find all matching log files
        for pattern in log_locations:
            try:
                matching_files = glob.glob(pattern)
                for file_path in matching_files:
                    if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                        # Check if it's a recent file (modified in last 7 days)
                        if os.path.getmtime(file_path) > time.time() - (7 * 86400):
                            log_files.append(file_path)
            except:
                pass
                
        # Remove duplicates and sort by modification time (newest first)
        unique_logs = list(set(log_files))
        sorted_logs = sorted(unique_logs, key=os.path.getmtime, reverse=True)
        
        return sorted_logs
        
    def create_log_explorer_window(self, log_files):
        """Create a log explorer window for viewing and filtering logs"""
        # Create a new top-level window
        log_window = tk.Toplevel(self.root)
        log_window.title("Server Log Explorer")
        log_window.geometry("1000x700")
        log_window.minsize(800, 600)
        
        # Set icon to match main window
        log_window.iconbitmap(self.root.iconbitmap()) if hasattr(self.root, 'iconbitmap') else None
        
        # Apply the same styling
        log_frame = ttk.Frame(log_window, style='Content.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create a header
        header_label = ttk.Label(log_frame, text="Server Log Explorer", style='ContentHeader.TLabel')
        header_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Create a paned window for the explorer view
        paned_window = ttk.PanedWindow(log_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Log file list
        left_frame = ttk.Frame(paned_window, style='Content.TFrame')
        paned_window.add(left_frame, weight=1)
        
        # Log files list header
        ttk.Label(left_frame, text="Log Files:", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Create a listbox for log files
        logs_frame = ttk.Frame(left_frame, style='Content.TFrame')
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_listbox = tk.Listbox(
            logs_frame,
            bg=self.colors["button_bg"],
            fg=self.colors["text"],
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["sidebar_text"],
            font=('Segoe UI', 10),
            borderwidth=0,
            highlightthickness=0
        )
        self.log_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_list_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.log_listbox.yview)
        log_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_listbox.config(yscrollcommand=log_list_scrollbar.set)
        
        # Populate the listbox
        self.log_files = log_files
        self.log_file_paths = {}  # Map display names to full paths
        
        for i, file_path in enumerate(log_files):
            # Create a friendly display name
            display_name = os.path.basename(file_path)
            
            # Add modification time
            try:
                mtime = os.path.getmtime(file_path)
                mtime_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
                display_name = f"{display_name} ({mtime_str})"
            except:
                pass
                
            # Add to the listbox and the map
            self.log_listbox.insert(tk.END, display_name)
            self.log_file_paths[display_name] = file_path
            
        # Bind selection event
        self.log_listbox.bind('<<ListboxSelect>>', lambda e: self.on_log_selected())
        
        # Right side: Log content and filtering options
        right_frame = ttk.Frame(paned_window, style='Content.TFrame')
        paned_window.add(right_frame, weight=3)
        
        # Filtering options
        filter_frame = ttk.Frame(right_frame, style='Content.TFrame')
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Filter dropdown
        self.filter_var = tk.StringVar(value="All Entries")
        filter_options = [
            "All Entries",
            "Errors Only",
            "Warnings Only", 
            "Request Processing",
            "Claude Desktop Communication",
            "Server Startup/Shutdown",
            "Custom Pattern..."
        ]
        
        filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=filter_options, width=25)
        filter_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        
        # Custom filter entry (hidden initially)
        self.custom_filter_var = tk.StringVar()
        self.custom_filter_entry = ttk.Entry(filter_frame, textvariable=self.custom_filter_var, width=20)
        
        # Apply filter button - use action button for consistent styling
        apply_btn = self.create_action_button(
            parent=filter_frame,
            icon="🔍",
            text="Apply Filter",
            command=self.apply_log_filter
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button - use action button for consistent styling
        export_btn = self.create_action_button(
            parent=filter_frame,
            icon="💾",
            text="Export Filtered Log",
            command=self.export_filtered_log
        )
        export_btn.pack(side=tk.LEFT)
        
        # Progress bar for filter operations
        self.filter_progress = ttk.Progressbar(right_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.filter_progress.pack(fill=tk.X, pady=(0, 10))
        
        # Log content view
        log_content_frame = ttk.Frame(right_frame, style='Content.TFrame')
        log_content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_view = tk.Text(
            log_content_frame,
            bg=self.colors["button_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["sidebar_text"],
            font=('Consolas', 10),  # Monospace for better log readability
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0
        )
        self.log_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_view_scrollbar = ttk.Scrollbar(log_content_frame, orient=tk.VERTICAL, command=self.log_view.yview)
        log_view_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_view.config(yscrollcommand=log_view_scrollbar.set)
        
        # Configure text tags for styling different log entry types
        self.log_view.tag_configure("error", foreground="#ff5252")
        self.log_view.tag_configure("warning", foreground="#ffab40")
        self.log_view.tag_configure("info", foreground="#64b5f6")
        self.log_view.tag_configure("debug", foreground="#9ccc65")
        self.log_view.tag_configure("highlight", background="#424242")
        
        # Initial state for the log view
        if self.log_listbox.size() > 0:
            self.log_listbox.selection_set(0)
            self.on_log_selected()
        else:
            self.log_view.insert(tk.END, "No log files found.")
            
        # Filter dropdown change handler
        def on_filter_change(*args):
            # Show/hide custom filter entry
            if self.filter_var.get() == "Custom Pattern...":
                self.custom_filter_entry.pack(side=tk.LEFT, padx=(0, 10))
            else:
                self.custom_filter_entry.pack_forget()
                
        # Bind to filter dropdown changes
        self.filter_var.trace('w', on_filter_change)
        
        # Set initial state for custom filter
        on_filter_change()
    
    def on_log_selected(self):
        """Handle log file selection from the listbox"""
        try:
            # Get the selected item
            selection = self.log_listbox.curselection()
            if not selection:
                return
                
            # Get the display name and file path
            display_name = self.log_listbox.get(selection[0])
            file_path = self.log_file_paths.get(display_name)
            
            if not file_path or not os.path.exists(file_path):
                self.log_view.delete(1.0, tk.END)
                self.log_view.insert(tk.END, "Selected log file not found.")
                return
                
            # Clear current view
            self.log_view.delete(1.0, tk.END)
            self.log_view.insert(tk.END, f"Loading log file: {display_name}...\n\n")
            
            # Start a background task to load the file
            threading.Thread(target=self.load_log_file, args=(file_path,), daemon=True).start()
        except Exception as e:
            self.log_view.insert(tk.END, f"Error loading log file: {str(e)}")
    
    def load_log_file(self, file_path):
        """Load a log file in a background thread"""
        try:
            # Reset progress bar
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(0, self.filter_progress.config, {'value': 0})
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            # Process the file in chunks for better responsiveness
            self.current_file_lines = lines
            self.current_file_path = file_path
            
            # Apply the current filter to the loaded file
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(0, self.apply_log_filter)
        except Exception as e:
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(0, self.update_log_view_error, str(e))
    
    def update_log_view_error(self, error_message):
        """Update the log view with an error message"""
        if hasattr(self, 'log_view'):
            self.log_view.delete(1.0, tk.END)
            self.log_view.insert(tk.END, f"Error: {error_message}")
    
    def apply_log_filter(self):
        """Apply the selected filter to the current log file"""
        if not hasattr(self, 'current_file_lines') or not self.current_file_lines:
            return
            
        # Clear current view
        self.log_view.delete(1.0, tk.END)
        
        # Reset progress bar
        self.filter_progress.config(value=0)
        
        # Get the selected filter
        filter_type = self.filter_var.get()
        custom_pattern = self.custom_filter_var.get() if filter_type == "Custom Pattern..." else None
        
        # Create filter patterns based on the selected type
        filter_patterns = []
        
        if filter_type == "All Entries":
            # No filtering needed
            pass
        elif filter_type == "Errors Only":
            filter_patterns = ["error", "exception", "traceback", "failed", "failure"]
        elif filter_type == "Warnings Only":
            filter_patterns = ["warning", "warn"]
        elif filter_type == "Request Processing":
            filter_patterns = ["request", "processing", "response", "claude desktop"]
        elif filter_type == "Claude Desktop Communication":
            filter_patterns = ["claude desktop", "connection", "response", "status", "heartbeat"]
        elif filter_type == "Server Startup/Shutdown":
            filter_patterns = ["starting", "started", "stopping", "stopped", "initializing", "initialized"]
        elif filter_type == "Custom Pattern..." and custom_pattern:
            filter_patterns = [custom_pattern.lower()]
        
        # Start a background thread to process filtering
        threading.Thread(
            target=self.process_log_filter,
            args=(self.current_file_lines, filter_patterns),
            daemon=True
        ).start()
    
    def process_log_filter(self, lines, filter_patterns):
        """Process log filtering in a background thread"""
        # Track if any matches were found
        matches_found = False
        line_count = len(lines)
        
        # Create regular expressions for the patterns
        import re
        regexes = [re.compile(pattern, re.IGNORECASE) for pattern in filter_patterns]
        
        # Filtered lines to display
        filtered_lines = []
        
        # Process all lines
        for i, line in enumerate(lines):
            # Update progress periodically
            if i % 100 == 0 and hasattr(self, 'root') and self.root.winfo_exists():
                progress_value = (i / line_count) * 100
                self.root.after(0, self.filter_progress.config, {'value': progress_value})
            
            # Check if line matches any pattern
            if not filter_patterns or any(regex.search(line) for regex in regexes):
                matches_found = True
                filtered_lines.append(line)
                
        # Final update to progress bar
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(0, self.filter_progress.config, {'value': 100})
        
        # Schedule update to the UI
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(0, self.update_filtered_log, filtered_lines, matches_found)
    
    def update_filtered_log(self, filtered_lines, matches_found):
        """Update the log view with filtered results"""
        if not hasattr(self, 'log_view'):
            return
            
        # Clear existing content
        self.log_view.delete(1.0, tk.END)
        
        if not matches_found and filtered_lines:
            # No matches but there were lines (happens with All Entries)
            pass
        elif not matches_found:
            self.log_view.insert(tk.END, "No matching entries found in the log file.")
            return
            
        # Insert filtered lines with appropriate styling
        for line in filtered_lines:
            line_lower = line.lower()
            
            # Determine the line tag based on its content
            tag = None
            if "error" in line_lower or "exception" in line_lower or "traceback" in line_lower:
                tag = "error"
            elif "warning" in line_lower or "warn" in line_lower:
                tag = "warning"
            elif "info" in line_lower:
                tag = "info"
            elif "debug" in line_lower:
                tag = "debug"
                
            # Insert the line
            end_index = self.log_view.index(tk.END)
            self.log_view.insert(tk.END, line)
            
            # Apply tag if one was determined
            if tag:
                line_start = f"{end_index.split('.')[0]}.0"
                line_end = self.log_view.index(f"{end_index.split('.')[0]}.end")
                self.log_view.tag_add(tag, line_start, line_end)
                
        # Scroll to the beginning
        self.log_view.see("1.0")
        
        # Update status with count of matches
        if hasattr(self, 'filter_progress'):
            self.filter_progress.config(value=100)
    
    def export_filtered_log(self):
        """Export the currently filtered log view to a file"""
        if not hasattr(self, 'log_view'):
            return
            
        try:
            # Get the current content
            current_content = self.log_view.get(1.0, tk.END)
            
            if not current_content.strip():
                messagebox.showinfo("Export", "No content to export.")
                return
                
            # Ask for a filename
            file_path = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Filtered Log"
            )
            
            if not file_path:
                return
                
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(current_content)
                
            messagebox.showinfo("Export Successful", f"Filtered log exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting log: {str(e)}")
    
    def open_claude_directory(self):
        """Open Claude Desktop directory in file explorer"""
        config_path = self.config_path.get()
        if config_path and os.path.exists(config_path):
            config_dir = os.path.dirname(config_path)
            try:
                import platform
                system = platform.system()
                
                if system == "Windows":
                    os.startfile(config_dir)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", config_dir], check=True)
                elif system == "Linux":
                    subprocess.run(["xdg-open", config_dir], check=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open directory: {str(e)}")
        else:
            messagebox.showinfo("Not Found", "Claude Desktop configuration directory not found.")
    
    def open_docs_directory(self):
        """Open the documentation directory in file explorer"""
        # Get the docs directory relative to the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Move up from aitoolkit/gui/modern to the project root
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        docs_path = os.path.join(project_root, "docs")
        
        if os.path.exists(docs_path):
            try:
                import platform
                system = platform.system()
                
                if system == "Windows":
                    os.startfile(docs_path)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", docs_path], check=True)
                elif system == "Linux":
                    subprocess.run(["xdg-open", docs_path], check=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open documentation directory: {str(e)}")
        else:
            messagebox.showinfo("Not Found", "Documentation directory not found.")
    
    def upgrade_toolkit(self):
        """Upgrade the toolkit using the upgrade_manager.py module"""
        import os
        import subprocess
        from tkinter import messagebox
        
        try:
            # Get the root directory of the toolkit
            toolkit_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Command to execute the upgrade script
            script_path = os.path.join(toolkit_root, "scripts", "upgrade_ai_toolkit.py")
            cmd = [sys.executable, script_path, toolkit_root]
            
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Show the results
            messagebox.showinfo(
                "Upgrade Complete", 
                f"The toolkit has been upgraded successfully.\n\n{result.stdout}"
            )
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Upgrade Error", 
                f"Error during upgrade process:\n{e.stderr}"
            )
        except Exception as e:
            messagebox.showerror(
                "Upgrade Error", 
                f"Could not upgrade the toolkit: {str(e)}"
            )
    
    def add_directory(self):
        """Add a directory to the project list"""
        dir_path = filedialog.askdirectory(title="Select Project Directory")
        if dir_path:
            if dir_path not in self.project_dirs:
                self.project_dirs.append(dir_path)
                self.project_enabled[dir_path] = True
                self.has_changes = True
                self.update_projects_list()
                self.project_message_var.set(f"Added project directory: {dir_path}")
            else:
                messagebox.showinfo("Already Added", "This directory is already in the project list.")
    
    def remove_directory(self):
        """Remove the selected directory from the treeview"""
        selected_item = self.projects_treeview.selection()
        if selected_item:
            # Get the directory path from the selected item
            values = self.projects_treeview.item(selected_item[0], 'values')
            if values:
                dir_path = values[1]  # Path is in the second column (index 1)
                
                # Remove directory from project_dirs list
                if dir_path in self.project_dirs:
                    self.project_dirs.remove(dir_path)
                    if dir_path in self.project_enabled:
                        del self.project_enabled[dir_path]
                    
                    # Update displays
                    self.update_projects_list()
                    
                    # Mark as changed
                    self.has_changes = True
                    
                    # Show message
                    self.project_message_var.set(f"Removed project directory: {dir_path}")
        else:
            messagebox.showinfo("No Selection", "Please select a project to remove.")
    
    def toggle_create_project_area(self):
        """Show or hide the create project area"""
        messagebox.showinfo("Not Implemented", "Create Project functionality is not yet implemented in the modern UI.")
    
    def open_project_with(self):
        """Open the selected project with the specified application"""
        messagebox.showinfo("Not Implemented", "Open Project With functionality is not yet implemented in the modern UI.")
    
    def prev_document(self):
        """Navigate to the previous document"""
        messagebox.showinfo("Not Implemented", "Document navigation is not yet implemented in the modern UI.")
    
    def next_document(self):
        """Navigate to the next document"""
        messagebox.showinfo("Not Implemented", "Document navigation is not yet implemented in the modern UI.")
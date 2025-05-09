"""
AI Dev Toolkit Enhanced Configurator GUI

This is an enhanced GUI implementation for the AI Dev Toolkit.
It includes improved project management features and visual enhancements.
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import time
from pathlib import Path
import webbrowser
import traceback
import datetime

class AIDevToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Dev Toolkit Control Panel")
        self.root.geometry("850x1001")  # Optimized size with appropriate width and taller height
        self.root.resizable(True, True)
        
        # Set version
        self.version = "0.4.0"
        
        # Track changes
        self.has_changes = False
        
        # Capture window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set theme and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TLabel', font=('Segoe UI', 10), background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), background='#f0f0f0')
        self.style.configure('Status.TLabel', font=('Segoe UI', 10), padding=5)
        self.style.configure('Running.Status.TLabel', background='#d4edda', foreground='#155724')
        self.style.configure('Stopped.Status.TLabel', background='#f8d7da', foreground='#721c24')
        self.style.configure('Warning.Status.TLabel', background='#fff3cd', foreground='#856404')
        self.style.configure('Disabled.TCheckbutton', foreground='#aaaaaa')
        self.style.configure('Info.TLabel', background='#edf9ff', foreground='#0c5460', padding=10)
        self.style.configure('ComingSoon.TLabel', foreground='#0056b3', font=('Segoe UI', 9, 'italic', 'bold'))
        self.style.map('TCheckbutton', 
                      foreground=[('disabled', '#aaaaaa')])
        
        # Style for server selection
        self.style.configure('Server.TCheckbutton', font=('Segoe UI', 10, 'bold'))
        
        # Style for larger Treeview checkboxes
        self.style.configure('Large.Treeview', rowheight=30)  # Make rows taller
        
        # Variables
        self.claude_desktop_path = tk.StringVar()
        self.config_path = tk.StringVar()
        # Server enabled is determined by tool selection
        self.project_dirs = []
        self.project_enabled = {}  # Map of project path to enabled status
        self.project_privacy = {}  # Map of project path to privacy status (Public/Private)
        self.project_last_accessed = {}  # Dictionary to store last accessed times
        self.project_git_status = {}  # Dictionary to store git status
        self.project_documents = {}  # Dictionary to store project documents
        self.server_status = tk.StringVar(value="Stopped")
        self.server_process = None
        self.server_log = tk.StringVar(value="")
        self.current_project = None  # Currently selected project
        self.current_doc_index = 0  # Index of currently displayed document
        
        # Store default application
        self.default_app = None
        
        # Server configuration type - for official MCP servers
        self.server_config_type = tk.StringVar(value="npm")  # Default to npm package (recommended)
        
        # AI Dev Toolkit Server enabled/disabled
        self.ai_dev_toolkit_server_enabled = tk.BooleanVar(value=True)
        
        # Build UI
        self.create_widgets()
        
        # Initial checks
        self.detect_claude_desktop()
        self.load_config()
        self.check_server_status()
        self.scan_for_projects()
    
    def create_widgets(self):
        # Main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard tab (first)
        self.dashboard_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Claude Desktop Configuration tab (second)
        self.claude_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.claude_frame, text="Claude Desktop Configuration")
        
        # Project Management tab (third)
        self.project_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.project_frame, text="Projects")
        
        # About tab (fourth)
        self.about_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.about_frame, text="About")
        
        # Create a static bottom button frame (shared across all tabs)
        self.bottom_button_frame = ttk.Frame(self.root)
        self.bottom_button_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Add buttons to the static bottom frame
        ttk.Button(self.bottom_button_frame, text="Apply and Exit", command=self.apply_and_exit).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.bottom_button_frame, text="Apply Changes", command=self.apply_claude_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.bottom_button_frame, text="Discard Changes and Exit", command=self.discard_and_exit).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Setup each tab
        self.setup_dashboard()
        self.setup_claude_tab()
        self.setup_project_tab()
        self.setup_about_tab()
        
        # Check if this is first launch and select Configuration tab
        # The Dashboard is first in order, but we initially show Configuration tab
        self.notebook.select(self.claude_frame)
    
    #-----------------------------------------------------
    # Dashboard Tab
    #-----------------------------------------------------
    def setup_dashboard(self):
        # Header
        header_label = ttk.Label(self.dashboard_frame, text="AI Dev Toolkit Dashboard", style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(self.dashboard_frame, text="System Status", padding="10 10 10 10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Claude Desktop status
        self.claude_status_label = ttk.Label(status_frame, text="Checking Claude Desktop...", style='Status.TLabel')
        self.claude_status_label.grid(row=0, column=0, sticky="w", pady=2)
        
        # Server status
        self.server_status_label = ttk.Label(status_frame, text="MCP Server: Stopped", 
                                           style='Stopped.Status.TLabel')
        self.server_status_label.grid(row=1, column=0, sticky="w", pady=2)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(self.dashboard_frame, text="Quick Actions", padding="10 10 10 10")
        actions_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15), padx=(0, 10))
        
        ttk.Button(actions_frame, text="Restart MCP Server", command=self.restart_server).pack(
            fill=tk.X, pady=5, padx=5)
        
        ttk.Button(actions_frame, text="Clear Server Log", command=self.clear_server_log).pack(
            fill=tk.X, pady=5, padx=5)
        
        ttk.Button(actions_frame, text="Edit Project Directories", 
                 command=lambda: self.notebook.select(self.project_frame)).pack(
            fill=tk.X, pady=5, padx=5)
        
        ttk.Button(actions_frame, text="Open Claude Desktop Location", 
                 command=self.open_claude_directory).pack(
            fill=tk.X, pady=5, padx=5)
        
        # Active projects
        projects_frame = ttk.LabelFrame(self.dashboard_frame, text="Active Projects", padding="10 10 10 10")
        projects_frame.grid(row=2, column=1, sticky="nsew", pady=(0, 15), padx=(10, 0))
        
        self.active_projects_listbox = tk.Listbox(projects_frame, height=6)
        self.active_projects_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        projects_scrollbar = ttk.Scrollbar(projects_frame, orient=tk.VERTICAL, command=self.active_projects_listbox.yview)
        projects_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.active_projects_listbox.config(yscrollcommand=projects_scrollbar.set)
        
        # Server log preview
        log_frame = ttk.LabelFrame(self.dashboard_frame, text="Server Log", padding="10 10 10 10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        self.log_text = tk.Text(log_frame, height=10, width=80, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        self.log_text.insert(tk.END, "Server log will appear here when the server is started.")
        self.log_text.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.dashboard_frame.columnconfigure(0, weight=1)
        self.dashboard_frame.columnconfigure(1, weight=1)
        self.dashboard_frame.rowconfigure(3, weight=1)
    
    #-----------------------------------------------------
    # Claude Desktop Tab
    #-----------------------------------------------------
    def setup_claude_tab(self):
        # Header
        header_label = ttk.Label(self.claude_frame, text="Claude Desktop Configuration", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Claude Desktop section
        claude_config_frame = ttk.LabelFrame(self.claude_frame, text="Claude Desktop", padding="10 10 10 10")
        claude_config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Claude Desktop status
        self.claude_config_status_label = ttk.Label(claude_config_frame, text="Checking Claude Desktop installation...", style='TLabel')
        self.claude_config_status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Claude Desktop path
        path_frame = ttk.Frame(claude_config_frame)
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(path_frame, text="Config Path:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.config_path, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse...", command=self.browse_config).pack(side=tk.LEFT)
        
        # Safety disclaimer
        safety_frame = ttk.Frame(claude_config_frame, style='TFrame')
        safety_frame.pack(fill=tk.X, pady=(10, 0))
        
        safety_label = ttk.Label(safety_frame, 
                               text="Note: This application edits Claude Desktop's configuration file. Claude itself does not have direct access to edit these files.",
                               wraplength=750, style='Info.TLabel')
        safety_label.pack(fill=tk.X)

        # AI Dev Toolkit Servers section
        server_selection_frame = ttk.LabelFrame(self.claude_frame, text="AI Dev Toolkit Servers", padding="10 10 10 10")
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
                                               style='Server.TCheckbutton',
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
        
        # Project Starter Server checkbox (Coming Soon)
        project_starter_frame = ttk.Frame(server_selection_frame)
        project_starter_frame.pack(fill=tk.X, anchor=tk.W, pady=5)
        project_starter_check = ttk.Checkbutton(project_starter_frame, 
                                              text="Project Starter Server - Project generation and scaffolding", 
                                              state='disabled',
                                              style='Server.TCheckbutton')
        project_starter_check.pack(side=tk.LEFT)
        
        # Coming Soon label for Project Starter - with more visible styling
        project_starter_coming_soon = ttk.Label(project_starter_frame, 
                                            text="(Coming Soon)",
                                            style='ComingSoon.TLabel')
        project_starter_coming_soon.pack(side=tk.LEFT, padx=5)
        
        # Think Tool Server checkbox (Coming Soon)
        think_tool_frame = ttk.Frame(server_selection_frame)
        think_tool_frame.pack(fill=tk.X, anchor=tk.W, pady=5)
        think_tool_check = ttk.Checkbutton(think_tool_frame, 
                                         text="Think Tool Server - Structured reasoning for complex problems", 
                                         state='disabled',
                                         style='Server.TCheckbutton')
        think_tool_check.pack(side=tk.LEFT)
        
        # Coming Soon label for Think Tool - with more visible styling
        think_tool_coming_soon = ttk.Label(think_tool_frame, 
                                       text="(Coming Soon)",
                                       style='ComingSoon.TLabel')
        think_tool_coming_soon.pack(side=tk.LEFT, padx=5)
        
        # Note about Claude Desktop compatibility
        claude_compat_note = ttk.Label(server_selection_frame, 
                                    text="Note: These servers are currently compatible with Claude Desktop only.",
                                    wraplength=750, style='Info.TLabel')
        claude_compat_note.pack(fill=tk.X, pady=(10, 0))
        
        # Official MCP Servers section
        mcp_servers_frame = ttk.LabelFrame(self.claude_frame, text="Official MCP Servers", padding="10 10 10 10")
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
        self.server_config_status_label = ttk.Label(mcp_servers_frame, text="MCP Server configuration is determined by selected servers", style='TLabel')
        self.server_config_status_label.pack(anchor=tk.W, pady=(5, 5))
        
        # NPM configuration note
        self.npm_config_note = ttk.Label(mcp_servers_frame, 
                                       text="Using NPM Package: This approach is recommended for most users and works with standard Claude Desktop configuration.",
                                       wraplength=750, style='Info.TLabel')
        self.npm_config_note.pack(fill=tk.X, pady=(0, 5))
        
        # uv configuration note - hidden initially
        self.uv_config_note = ttk.Label(mcp_servers_frame, 
                                       text="Using Python with uv: This approach requires uv to be installed and is recommended for development. All paths must be absolute.",
                                       wraplength=750, style='Info.TLabel')
        
        # GitHub link for MCP servers
        mcp_servers_link = ttk.Label(mcp_servers_frame, 
                                   text="Official MCP Servers Repository", 
                                   foreground="blue", cursor="hand2")
        mcp_servers_link.pack(anchor=tk.W, pady=2)
        mcp_servers_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/modelcontextprotocol/servers"))
        
        # Button for adding project directories
        add_proj_btn = ttk.Button(self.claude_frame, text="Add Project Directories", 
                                  command=lambda: self.notebook.select(self.project_frame))
        add_proj_btn.pack(side=tk.LEFT, pady=(10, 0))
    
    #-----------------------------------------------------
    # Project Management Tab
    #-----------------------------------------------------
    def setup_project_tab(self):
        # Header
        header_label = ttk.Label(self.project_frame, text="Project Management", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Main content frame with two columns
        main_content = ttk.Frame(self.project_frame)
        main_content.pack(fill=tk.BOTH, expand=True)
        main_content.columnconfigure(0, weight=3)  # Directory list side
        main_content.columnconfigure(1, weight=2)  # Controls and viewer side
        
        # Left side: Project lists and documents
        left_side = ttk.Frame(main_content)
        left_side.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Project Document Viewer (top part of left side)
        doc_viewer_frame = ttk.LabelFrame(left_side, text="Project Documentation", padding="10 10 10 10")
        doc_viewer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # README/Documentation viewer with scrollbars
        self.doc_text = tk.Text(doc_viewer_frame, height=10, width=60, wrap=tk.WORD)
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
        projects_frame = ttk.LabelFrame(left_side, text="Project Directories", padding="10 10 10 10")
        projects_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project list using a Treeview with expanded columns
        self.projects_treeview = ttk.Treeview(
            projects_frame, 
            columns=("Private", "Path", "Status", "LastAccessed", "GitStatus"), 
            selectmode='browse', 
            height=10,
            style='Large.Treeview'  # Apply the custom style for larger rows
        )
        
        # Configure the treeview
        self.projects_treeview.heading('#0', text='Enabled')
        self.projects_treeview.heading('Private', text='Public/Private')
        self.projects_treeview.heading('Path', text='Project Path')
        self.projects_treeview.heading('Status', text='Access')
        self.projects_treeview.heading('LastAccessed', text='Last Accessed')
        self.projects_treeview.heading('GitStatus', text='Git Status')
        
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
        
        # Bind events
        self.projects_treeview.bind('<ButtonRelease-1>', self.on_treeview_click)
        self.projects_treeview.bind('<<TreeviewSelect>>', self.on_project_selected)
        
        # Right side: Controls (logs moved to bottom)
        right_side = ttk.Frame(main_content)
        right_side.grid(row=0, column=1, sticky="nsew")
        
        # Project Controls
        controls_frame = ttk.LabelFrame(right_side, text="Project Controls", padding="10 10 10 10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button grid for controls
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # First row of buttons
        ttk.Button(btn_frame, text="Add Project", width=20, command=self.add_directory).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Remove Project", width=20, command=self.remove_directory).grid(row=0, column=1, padx=5, pady=5)
        
        # Second row of buttons
        ttk.Button(btn_frame, text="Create Project", width=20, command=self.toggle_create_project_area).grid(row=1, column=0, padx=5, pady=5)
        
        # Open Project With... button with default app selection
        open_project_frame = ttk.Frame(btn_frame)
        open_project_frame.grid(row=1, column=1, padx=5, pady=5)
        
        self.open_with_btn = ttk.Button(open_project_frame, text="Open Project With...", width=20, command=self.open_project_with)
        self.open_with_btn.pack(side=tk.TOP, pady=(0, 5))
        
        # Default application selection
        self.default_app_var = tk.StringVar(value="Default Application")
        default_apps = ["VS Code", "Notepad", "Explorer", "Custom..."]
        
        self.default_app_combo = ttk.Combobox(open_project_frame, textvariable=self.default_app_var, values=default_apps, width=18)
        self.default_app_combo.pack(side=tk.TOP)
        self.default_app_combo.bind("<<ComboboxSelected>>", self.set_default_application)
        
        # Project privacy section
        privacy_frame = ttk.Frame(controls_frame)
        privacy_frame.pack(fill=tk.X, pady=10)
        
        self.privacy_var = tk.StringVar(value="Public")
        ttk.Label(privacy_frame, text="Selected Project Privacy:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.public_radio = ttk.Radiobutton(
            privacy_frame, text="Public", variable=self.privacy_var, 
            value="Public", command=self.update_project_privacy
        )
        self.public_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        self.private_radio = ttk.Radiobutton(
            privacy_frame, text="Private", variable=self.privacy_var, 
            value="Private", command=self.update_project_privacy
        )
        self.private_radio.pack(side=tk.LEFT)
        
        # Log frame now at the bottom of the entire tab, not in the right side
        log_frame = ttk.LabelFrame(self.project_frame, text="Server Log", padding="10 10 10 10")
        log_frame.pack(fill=tk.X, expand=False, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8, width=100, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.insert(tk.END, "Server log will appear here when the server is started.")
        self.log_text.config(state=tk.DISABLED)
        
        # Message area for project updates
        self.project_message_var = tk.StringVar()
        self.project_message_label = ttk.Label(self.project_frame, textvariable=self.project_message_var, 
                                            style='Info.TLabel', wraplength=750)
        self.project_message_label.pack(fill=tk.X, pady=(10, 0))
        
        # Initially set a default message
        self.project_message_var.set("Add project directories that Claude should have access to.")
        
        # Create project section (hidden initially)
        self.create_project_frame = ttk.LabelFrame(self.project_frame, text="Create New Project", padding="10 10 10 10")
        
        # Project name
        name_frame = ttk.Frame(self.create_project_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Project Name:", width=15).pack(side=tk.LEFT)
        self.new_project_name = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.new_project_name).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Project type
        type_frame = ttk.Frame(self.create_project_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Project Type:", width=15).pack(side=tk.LEFT)
        self.new_project_type = tk.StringVar(value="web")
        type_combo = ttk.Combobox(type_frame, textvariable=self.new_project_type, 
                                values=["web", "cli", "library", "api"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Project location
        location_frame = ttk.Frame(self.create_project_frame)
        location_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(location_frame, text="Location:", width=15).pack(side=tk.LEFT)
        self.new_project_location = tk.StringVar()
        ttk.Entry(location_frame, textvariable=self.new_project_location).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(location_frame, text="Browse...", command=self.browse_project_location).pack(side=tk.LEFT)
        
        # Create button row
        button_row = ttk.Frame(self.create_project_frame)
        button_row.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_row, text="Cancel", 
                command=lambda: self.create_project_frame.pack_forget()).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_row, text="Create Project", 
                command=self.create_new_project).pack(side=tk.RIGHT)

    #-----------------------------------------------------
    # About Tab  
    #-----------------------------------------------------
    def setup_about_tab(self):
        # Header
        header_label = ttk.Label(self.about_frame, text="About AI Dev Toolkit", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Version info
        version_frame = ttk.Frame(self.about_frame)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, text=f"Version: {self.version}", font=('Segoe UI', 12)).pack(anchor=tk.W)
        
        # Description
        desc_frame = ttk.LabelFrame(self.about_frame, text="Description", padding="10 10 10 10")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        description = """The AI Dev Toolkit enhances Claude with powerful capabilities through its integrated MCP server:

1. File System Tools: Read, write, and navigate the file system securely
2. AI Librarian: Helps Claude understand your codebase with self-checks to ensure proper functionality
3. Task Management: Track development tasks across conversations
4. Enhanced Code Analysis: Find related files, references, and detailed component information
5. Project Starter: Project generation and scaffolding (Coming Soon)
6. Think Tool: Structured reasoning for complex problems (Coming Soon)"""
        
        ttk.Label(desc_frame, text=description, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Safety information
        safety_frame = ttk.LabelFrame(self.about_frame, text="Important Safety Information", padding="10 10 10 10")
        safety_frame.pack(fill=tk.X, pady=(0, 20))
        
        safety_text = """The AI Dev Toolkit provides an MCP (Model Context Protocol) server that Claude can use to access your files and execute tools on your computer.

IMPORTANT: The AI Dev Toolkit application edits Claude Desktop's configuration to enable these tools. Claude itself does not have direct access to edit configuration files. All file operations and tool executions happen in your local environment and with your explicit permission.

When you enable project directories, you are granting Claude permission to read from and write to those directories. Choose directories carefully."""
        
        ttk.Label(safety_frame, text=safety_text, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Links
        links_frame = ttk.Frame(self.about_frame)
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

    #---------------------------------------------------------
    # Core Functionality Methods
    #---------------------------------------------------------
    
    def detect_claude_desktop(self):
        """Detect Claude Desktop installation and config location"""
        self.claude_status_label.config(text="Checking Claude Desktop installation...")
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
            self.claude_status_label.config(text=f"Claude Desktop detected. Config: {config_path}")
            self.claude_config_status_label.config(text=f"Claude Desktop detected. Config: {config_path}")
        else:
            self.claude_status_label.config(text="Claude Desktop not found. Please specify the config path manually.")
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
                if has_legacy_ai_librarian and "args" in config["mcpServers"]["ai-librarian"]:
                    args = config["mcpServers"]["ai-librarian"]["args"]
                    # Skip the first item which is the script path
                    dir_paths = args[1:] if len(args) > 1 else []
                    
                    # Filter existing directories and add to project list
                    self.project_dirs = [dir_path for dir_path in dir_paths if os.path.exists(dir_path)]
                    for dir_path in self.project_dirs:
                        self.project_enabled[dir_path] = True
                elif has_integrated and "args" in config["mcpServers"]["integrated-server"]:
                    args = config["mcpServers"]["integrated-server"]["args"]
                    # Skip the first item which is the script path
                    dir_paths = args[1:] if len(args) > 1 else []
                    
                    # Filter existing directories and add to project list
                    self.project_dirs = [dir_path for dir_path in dir_paths if os.path.exists(dir_path)]
                    for dir_path in self.project_dirs:
                        self.project_enabled[dir_path] = True
                            
                # Update project displays
                self.update_projects_list()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
            print(f"Error loading config: {str(e)}")

    def update_server_status(self):
        """Update server status display based on enabled/disabled state"""
        if self.ai_dev_toolkit_server_enabled.get():
            self.server_status_label.config(text="MCP Server: Ready to Start", style="Warning.Status.TLabel")
        else:
            self.server_status_label.config(text="MCP Server: Disabled", style="Stopped.Status.TLabel")
        
        # Mark that changes have been made
        self.has_changes = True
    
    def update_server_config_type(self):
        """Update server configuration type displays"""
        if self.server_config_type.get() == "npm":
            self.npm_config_note.pack(fill=tk.X, pady=(0, 5))
            self.uv_config_note.pack_forget()
        else:
            self.npm_config_note.pack_forget()
            self.uv_config_note.pack(fill=tk.X, pady=(0, 5))
        
        # Mark that changes have been made
        self.has_changes = True
    
    def browse_config(self):
        """Browse for Claude Desktop config file"""
        config_path = filedialog.askopenfilename(
            title="Select Claude Desktop Configuration File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if config_path:
            self.config_path.set(config_path)
            self.load_config()
    
    def apply_claude_config(self):
        """Apply configuration to Claude Desktop config file"""
        config_path = self.config_path.get()
        if not config_path:
            messagebox.showerror("Error", "No Claude Desktop configuration path specified.")
            return
        
        try:
            # Load existing config
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Make sure mcpServers section exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            # Remove legacy servers if they exist
            if "ai-librarian" in config["mcpServers"]:
                del config["mcpServers"]["ai-librarian"]
            
            if "file-system-tools" in config["mcpServers"]:
                del config["mcpServers"]["file-system-tools"]
            
            # Detect directories to include in configuration
            enabled_dirs = []
            for dir_path in self.project_dirs:
                if self.project_enabled.get(dir_path, False):
                    enabled_dirs.append(dir_path)
            
            # Configure or remove the integrated server based on enabled state
            if self.ai_dev_toolkit_server_enabled.get():
                # Find the unified server path
                script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                script_path = os.path.join(script_dir, "launch_unified.py")
                
                if self.server_config_type.get() == "npm":
                    # NPM package configuration (recommended)
                    config["mcpServers"]["integrated-server"] = {
                        "command": "python",
                        "args": [script_path] + enabled_dirs,
                        "env": {}
                    }
                else:
                    # Python with uv configuration (for development)
                    config["mcpServers"]["integrated-server"] = {
                        "command": "python",
                        "args": [script_path] + enabled_dirs,
                        "pythonEnvType": "uv",
                        "absolutePaths": True,
                        "env": {}
                    }
            else:
                # Remove the integrated server if disabled
                if "integrated-server" in config["mcpServers"]:
                    del config["mcpServers"]["integrated-server"]
            
            # Save the updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Reset changes flag
            self.has_changes = False
            
            messagebox.showinfo("Success", "Configuration has been updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update configuration: {str(e)}")
            print(f"Error updating config: {str(e)}")
    
    def check_server_status(self):
        """Check if the MCP server is running"""
        # To be implemented - will check if server process exists and update UI
        pass
    
    def restart_server(self):
        """Restart the MCP server"""
        # To be implemented - will stop and restart the server process
        messagebox.showinfo("Restart Server", "Server restart functionality will be implemented in a future version.")
    
    def clear_server_log(self):
        """Clear the server log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Server log cleared.")
        self.log_text.config(state=tk.DISABLED)
    
    def open_claude_directory(self):
        """Open the Claude Desktop configuration directory"""
        config_path = self.config_path.get()
        if config_path and os.path.exists(config_path):
            config_dir = os.path.dirname(config_path)
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(config_dir)
                elif os.name == 'posix':  # macOS and Linux
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', config_dir])
                    else:  # Linux
                        subprocess.run(['xdg-open', config_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open directory: {str(e)}")
        else:
            messagebox.showerror("Error", "Claude Desktop configuration path not found.")

    def scan_for_projects(self):
        """Scan directories for .ai_reference folders to find existing projects"""
        # Clear status message
        self.project_message_var.set("Scanning for projects with .ai_reference folders...")
        
        # Keep track of found projects
        found_projects = []
        
        # Check current project_dirs for .ai_reference folders
        for dir_path in self.project_dirs:
            if os.path.exists(os.path.join(dir_path, ".ai_reference")):
                found_projects.append(dir_path)
                # Set last accessed time
                try:
                    last_accessed_file = os.path.join(dir_path, ".ai_reference", "last_accessed.txt")
                    if os.path.exists(last_accessed_file):
                        with open(last_accessed_file, 'r') as f:
                            self.project_last_accessed[dir_path] = f.read().strip()
                    else:
                        self.project_last_accessed[dir_path] = "Never"
                except:
                    self.project_last_accessed[dir_path] = "Unknown"
                
                # Check git status
                try:
                    git_dir = os.path.join(dir_path, ".git")
                    if os.path.exists(git_dir):
                        # Check if there are changes
                        result = subprocess.run(
                            ["git", "-C", dir_path, "status", "--porcelain"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            if result.stdout.strip():
                                self.project_git_status[dir_path] = "Changes"
                            else:
                                self.project_git_status[dir_path] = "Clean"
                        else:
                            self.project_git_status[dir_path] = "Unknown"
                    else:
                        self.project_git_status[dir_path] = "No Git"
                except:
                    self.project_git_status[dir_path] = "Unknown"
        
        # Look through common directories for potential projects
        home_dir = os.path.expanduser("~")
        common_project_locations = [
            os.path.join(home_dir, "Documents"),
            os.path.join(home_dir, "Projects"),
            os.path.join(home_dir, "Desktop"),
            os.path.join(home_dir, "git"),
            os.path.join(home_dir, "source"),
            # Add current working directory and parent
            os.getcwd(),
            os.path.dirname(os.getcwd())
        ]
        
        # Scan a limited depth to find projects
        for search_dir in common_project_locations:
            if os.path.exists(search_dir) and os.path.isdir(search_dir):
                try:
                    # Check all first-level subdirectories
                    for subdir in os.listdir(search_dir):
                        full_path = os.path.join(search_dir, subdir)
                        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, ".ai_reference")):
                            if full_path not in self.project_dirs and full_path not in found_projects:
                                found_projects.append(full_path)
                                
                except PermissionError:
                    # Skip directories we can't access
                    pass
        
        # Add found projects 
        if found_projects:
            for project in found_projects:
                if project not in self.project_dirs:
                    self.project_dirs.append(project)
                    self.project_enabled[project] = True
                    self.project_privacy[project] = "Public"  # Default to public
                    
                    # Set last accessed time
                    try:
                        last_accessed_file = os.path.join(project, ".ai_reference", "last_accessed.txt")
                        if os.path.exists(last_accessed_file):
                            with open(last_accessed_file, 'r') as f:
                                self.project_last_accessed[project] = f.read().strip()
                        else:
                            self.project_last_accessed[project] = "Never"
                    except:
                        self.project_last_accessed[project] = "Unknown"
                    
                    # Check git status
                    try:
                        git_dir = os.path.join(project, ".git")
                        if os.path.exists(git_dir):
                            # Check if there are changes
                            result = subprocess.run(
                                ["git", "-C", project, "status", "--porcelain"],
                                capture_output=True, text=True
                            )
                            if result.returncode == 0:
                                if result.stdout.strip():
                                    self.project_git_status[project] = "Changes"
                                else:
                                    self.project_git_status[project] = "Clean"
                            else:
                                self.project_git_status[project] = "Unknown"
                        else:
                            self.project_git_status[project] = "No Git"
                    except:
                        self.project_git_status[project] = "Unknown"
            
            self.update_projects_list()
            self.project_message_var.set(f"Found {len(found_projects)} projects with .ai_reference folders.")
        else:
            self.project_message_var.set("No new projects with .ai_reference folders found.")
        
        # Scan project directories for documentation files
        self.scan_project_documentation()
    
    def scan_project_documentation(self):
        """Scan project directories for documentation files"""
        doc_extensions = ['.md', '.txt', '.rst', '.adoc']
        
        for dir_path in self.project_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                # Look for documentation files in the root directory
                docs = []
                try:
                    for filename in os.listdir(dir_path):
                        if (os.path.isfile(os.path.join(dir_path, filename)) and 
                            any(filename.lower().endswith(ext) for ext in doc_extensions)):
                            # Prioritize README files
                            if filename.upper().startswith('README'):
                                docs.insert(0, filename)
                            # Prioritize all-caps documentation files
                            elif filename.isupper():
                                docs.append(filename)
                            # Add other documentation files
                            else:
                                docs.append(filename)
                    
                    self.project_documents[dir_path] = docs
                except PermissionError:
                    # Skip directories we can't access
                    self.project_documents[dir_path] = []
        
    def update_projects_list(self):
        """Update the projects list display using the treeview"""
        # Clear the treeview
        for item in self.projects_treeview.get_children():
            self.projects_treeview.delete(item)
        
        # Clear active projects listbox
        self.active_projects_listbox.delete(0, tk.END)
        
        # Get current time for any new entries
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Repopulate with current projects
        for i, dir_path in enumerate(self.project_dirs):
            enabled = self.project_enabled.get(dir_path, True)
            
            # Check if path has AI Librarian
            has_ai_ref = os.path.exists(os.path.join(dir_path, ".ai_reference"))
            status = "AI Librarian" if has_ai_ref else "Regular"
            
            # Get privacy setting (or use "Public" as default)
            privacy = self.project_privacy.get(dir_path, "Public")
            
            # Get last accessed time
            last_accessed = self.project_last_accessed.get(dir_path, current_time)
            
            # Get git status
            git_status = self.project_git_status.get(dir_path, "Unknown")
            
            # Add to treeview with checkbox state and all columns
            item_id = self.projects_treeview.insert('', 'end', 
                                                  text="✓" if enabled else "□", 
                                                  values=(privacy, dir_path, status, last_accessed, git_status))
            
            # Add to active projects listbox if enabled
            if enabled:
                self.active_projects_listbox.insert(tk.END, f"{dir_path} [{status}]")
    
    def on_treeview_click(self, event):
        """Handle click on treeview - toggle checkbox if clicked in the checkbox column"""
        # Get the item that was clicked
        region = self.projects_treeview.identify_region(event.x, event.y)
        item_id = self.projects_treeview.identify_row(event.y)
        
        if item_id and (region == 'tree' or region == 'cell'):
            # Get the column and check if it's the checkbox column
            column = self.projects_treeview.identify_column(event.x)
            
            if column == '#0' or int(event.x) < 70:  # Checkbox column
                # Toggle checkbox state
                current_text = self.projects_treeview.item(item_id, 'text')
                new_text = "□" if current_text == "✓" else "✓"
                self.projects_treeview.item(item_id, text=new_text)
                
                # Update state in project_enabled dictionary
                dir_path = self.projects_treeview.item(item_id, 'values')[1]  # Path is now the second column
                self.project_enabled[dir_path] = (new_text == "✓")
                
                # Update active projects list on dashboard
                self.update_active_projects_list()
                
                # Mark changes
                self.has_changes = True
            
            # Handle click on privacy column
            elif column == '#1' or (70 <= int(event.x) < 170):  # Privacy column
                # Toggle privacy state
                values = self.projects_treeview.item(item_id, 'values')
                dir_path = values[1]  # Path is now the second column
                current_privacy = values[0]
                new_privacy = "Private" if current_privacy == "Public" else "Public"
                
                # Update privacy in the dictionary
                self.project_privacy[dir_path] = new_privacy
                
                # Update the treeview
                self.projects_treeview.item(item_id, values=(new_privacy,) + values[1:])
                
                # Mark changes
                self.has_changes = True
    
    def on_project_selected(self, event):
        """Handle project selection in treeview"""
        selected_items = self.projects_treeview.selection()
        if selected_items:
            # Get the selected project path
            item_id = selected_items[0]
            values = self.projects_treeview.item(item_id, 'values')
            dir_path = values[1]  # Path is now the second column
            privacy = values[0]  # Privacy status
            
            # Update privacy selection
            self.privacy_var.set(privacy)
            
            # Save current project
            self.current_project = dir_path
            
            # Load README or other documentation
            self.load_project_documentation(dir_path)
    
    def load_project_documentation(self, dir_path):
        """Load README or other documentation for the selected project"""
        # Check if this is a private project
        if self.project_privacy.get(dir_path, "Public") == "Private":
            # Show private message
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, f"This project is set to PRIVATE.\n\nThe documentation for private projects is not displayed for security reasons.")
            self.doc_text.config(state=tk.DISABLED)
            
            # Disable navigation buttons
            self.prev_doc_btn.config(state=tk.DISABLED)
            self.next_doc_btn.config(state=tk.DISABLED)
            self.current_doc_var.set("Private Project")
            return
        
        # Get documentation files for this project
        docs = self.project_documents.get(dir_path, [])
        
        if not docs:
            # No documentation found
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, f"No documentation files found in {dir_path}.\n\nConsider adding a README.md file to the project root.")
            self.doc_text.config(state=tk.DISABLED)
            
            # Disable navigation buttons
            self.prev_doc_btn.config(state=tk.DISABLED)
            self.next_doc_btn.config(state=tk.DISABLED)
            self.current_doc_var.set("No documentation")
            return
        
        # Reset current document index
        self.current_doc_index = 0
        
        # Load the first document
        doc_name = docs[self.current_doc_index]
        doc_path = os.path.join(dir_path, doc_name)
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update the text widget
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, content)
            self.doc_text.config(state=tk.DISABLED)
            
            # Update navigation
            self.current_doc_var.set(doc_name)
            
            # Enable/disable navigation buttons based on document count
            self.prev_doc_btn.config(state=tk.DISABLED)  # First document
            self.next_doc_btn.config(state=tk.NORMAL if len(docs) > 1 else tk.DISABLED)
        except Exception as e:
            # Error loading document
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, f"Error loading {doc_name}:\n\n{str(e)}")
            self.doc_text.config(state=tk.DISABLED)
            
            # Update navigation
            self.current_doc_var.set(f"Error: {doc_name}")
            
            # Disable navigation buttons
            self.prev_doc_btn.config(state=tk.DISABLED)
            self.next_doc_btn.config(state=tk.DISABLED)
    
    def prev_document(self):
        """Show the previous document for the current project"""
        if not self.current_project:
            return
        
        # Get documentation files for this project
        docs = self.project_documents.get(self.current_project, [])
        
        if not docs or self.current_doc_index <= 0:
            return
        
        # Decrement index
        self.current_doc_index -= 1
        
        # Load the document
        doc_name = docs[self.current_doc_index]
        doc_path = os.path.join(self.current_project, doc_name)
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update the text widget
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, content)
            self.doc_text.config(state=tk.DISABLED)
            
            # Update navigation
            self.current_doc_var.set(doc_name)
            
            # Enable/disable navigation buttons based on index
            self.prev_doc_btn.config(state=tk.DISABLED if self.current_doc_index == 0 else tk.NORMAL)
            self.next_doc_btn.config(state=tk.NORMAL)
        except Exception as e:
            # Error loading document
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, f"Error loading {doc_name}:\n\n{str(e)}")
            self.doc_text.config(state=tk.DISABLED)
    
    def next_document(self):
        """Show the next document for the current project"""
        if not self.current_project:
            return
        
        # Get documentation files for this project
        docs = self.project_documents.get(self.current_project, [])
        
        if not docs or self.current_doc_index >= len(docs) - 1:
            return
        
        # Increment index
        self.current_doc_index += 1
        
        # Load the document
        doc_name = docs[self.current_doc_index]
        doc_path = os.path.join(self.current_project, doc_name)
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update the text widget
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, content)
            self.doc_text.config(state=tk.DISABLED)
            
            # Update navigation
            self.current_doc_var.set(doc_name)
            
            # Enable/disable navigation buttons based on index
            self.prev_doc_btn.config(state=tk.NORMAL)
            self.next_doc_btn.config(state=tk.DISABLED if self.current_doc_index == len(docs) - 1 else tk.NORMAL)
        except Exception as e:
            # Error loading document
            self.doc_text.config(state=tk.NORMAL)
            self.doc_text.delete(1.0, tk.END)
            self.doc_text.insert(tk.END, f"Error loading {doc_name}:\n\n{str(e)}")
            self.doc_text.config(state=tk.DISABLED)
    
    def update_active_projects_list(self):
        """Update the list of active projects on the dashboard"""
        self.active_projects_listbox.delete(0, tk.END)
        
        for dir_path in self.project_dirs:
            if self.project_enabled.get(dir_path, False):
                has_ai_ref = os.path.exists(os.path.join(dir_path, ".ai_reference"))
                status = "AI Librarian" if has_ai_ref else "Regular"
                privacy = self.project_privacy.get(dir_path, "Public")
                self.active_projects_listbox.insert(tk.END, f"{dir_path} [{status}, {privacy}]")
    
    def add_directory(self):
        """Add a directory to the project list"""
        dir_path = filedialog.askdirectory(title="Select Project Directory")
        if dir_path:
            if dir_path not in self.project_dirs:
                self.project_dirs.append(dir_path)
                self.project_enabled[dir_path] = True
                self.project_privacy[dir_path] = "Public"  # Default to public
                
                # Record the current time as last accessed
                self.project_last_accessed[dir_path] = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # Check git status
                try:
                    git_dir = os.path.join(dir_path, ".git")
                    if os.path.exists(git_dir):
                        # Check if there are changes
                        result = subprocess.run(
                            ["git", "-C", dir_path, "status", "--porcelain"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            if result.stdout.strip():
                                self.project_git_status[dir_path] = "Changes"
                            else:
                                self.project_git_status[dir_path] = "Clean"
                        else:
                            self.project_git_status[dir_path] = "Unknown"
                    else:
                        self.project_git_status[dir_path] = "No Git"
                except:
                    self.project_git_status[dir_path] = "Unknown"
                
                # Scan for documentation
                self.scan_project_documentation()
                
                self.has_changes = True
                self.update_projects_list()
                self.project_message_var.set(f"Added project: {dir_path}")
    
    def remove_directory(self):
        """Remove a directory from the project list"""
        selected_items = self.projects_treeview.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Please select a project to remove.")
            return
        
        # Get the selected project path
        item_id = selected_items[0]
        values = self.projects_treeview.item(item_id, 'values')
        dir_path = values[1]  # Path is in the second column
        
        # Confirm removal
        if messagebox.askyesno("Remove Project", f"Are you sure you want to remove this project?\n\n{dir_path}"):
            # Remove from project lists
            if dir_path in self.project_dirs:
                self.project_dirs.remove(dir_path)
            
            # Remove from dictionaries
            if dir_path in self.project_enabled:
                del self.project_enabled[dir_path]
            
            if dir_path in self.project_privacy:
                del self.project_privacy[dir_path]
            
            if dir_path in self.project_last_accessed:
                del self.project_last_accessed[dir_path]
            
            if dir_path in self.project_git_status:
                del self.project_git_status[dir_path]
            
            if dir_path in self.project_documents:
                del self.project_documents[dir_path]
            
            # Reset current project if removed
            if self.current_project == dir_path:
                self.current_project = None
                
                # Clear document viewer
                self.doc_text.config(state=tk.NORMAL)
                self.doc_text.delete(1.0, tk.END)
                self.doc_text.insert(tk.END, "Select a project to view its documentation.")
                self.doc_text.config(state=tk.DISABLED)
                
                # Reset navigation
                self.current_doc_var.set("No document")
                self.prev_doc_btn.config(state=tk.DISABLED)
                self.next_doc_btn.config(state=tk.DISABLED)
            
            # Update the UI
            self.has_changes = True
            self.update_projects_list()
            self.project_message_var.set(f"Removed project: {dir_path}")
    
    def update_project_privacy(self):
        """Update privacy setting for the current project"""
        if not self.current_project:
            return
        
        privacy = self.privacy_var.get()
        self.project_privacy[self.current_project] = privacy
        
        # Update the treeview
        for item_id in self.projects_treeview.get_children():
            values = self.projects_treeview.item(item_id, 'values')
            dir_path = values[1]  # Path is in the second column
            
            if dir_path == self.current_project:
                # Update the values tuple with new privacy status
                self.projects_treeview.item(item_id, values=(privacy,) + values[1:])
                break
        
        # Reload documentation if privacy changed
        self.load_project_documentation(self.current_project)
        
        # Update active projects list
        self.update_active_projects_list()
        
        # Mark changes
        self.has_changes = True
    
    def toggle_create_project_area(self):
        """Show or hide the create project area"""
        if self.create_project_frame.winfo_manager():
            self.create_project_frame.pack_forget()
        else:
            self.create_project_frame.pack(fill=tk.X, pady=(10, 0))
    
    def browse_project_location(self):
        """Browse for a location to create a new project"""
        dir_path = filedialog.askdirectory(title="Select Project Parent Directory")
        if dir_path:
            self.new_project_location.set(dir_path)
    
    def create_new_project(self):
        """Create a new project directory"""
        # To be implemented: creating a new project from template
        messagebox.showinfo("Coming Soon", "Project creation functionality will be implemented in a future version.")
        self.create_project_frame.pack_forget()
    
    def open_project_with(self):
        """Open the selected project with the default application"""
        if not self.current_project:
            messagebox.showinfo("Information", "Please select a project to open.")
            return
        
        try:
            # Use the default app if set, otherwise prompt
            if self.default_app:
                if self.default_app == "VS Code":
                    # Special handling for VS Code
                    subprocess.Popen(["code", self.current_project])
                elif self.default_app == "Explorer":
                    # Open in file explorer
                    if os.name == 'nt':  # Windows
                        os.startfile(self.current_project)
                    elif os.name == 'posix':  # macOS and Linux
                        if sys.platform == 'darwin':  # macOS
                            subprocess.run(['open', self.current_project])
                        else:  # Linux
                            subprocess.run(['xdg-open', self.current_project])
                elif self.default_app == "Notepad":
                    # Open with notepad
                    subprocess.Popen(["notepad", self.current_project])
                else:
                    # Other applications
                    subprocess.Popen([self.default_app, self.current_project])
            else:
                # Open with system default
                if os.name == 'nt':  # Windows
                    os.startfile(self.current_project)
                elif os.name == 'posix':  # macOS and Linux
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', self.current_project])
                    else:  # Linux
                        subprocess.run(['xdg-open', self.current_project])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open project: {str(e)}")
    
    def set_default_application(self, event=None):
        """Set the default application for opening projects"""
        app = self.default_app_var.get()
        if app == "Custom...":
            # Prompt for custom application
            app_path = filedialog.askopenfilename(
                title="Select Application",
                filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
            )
            if app_path:
                self.default_app = app_path
                # Update the display with just the executable name
                exe_name = os.path.basename(app_path)
                self.default_app_var.set(exe_name)
        else:
            self.default_app = app
    
    def on_closing(self):
        """Handle window closing"""
        if self.has_changes:
            response = messagebox.askyesnocancel(
                "Save Changes", 
                "You have unsaved changes. Would you like to save them before exiting?",
                icon=messagebox.WARNING
            )
            
            if response is None:  # Cancel
                return
            elif response:  # Yes, save changes
                self.apply_claude_config()
        
        # Cleanup and close
        self.root.destroy()
    
    def apply_and_exit(self):
        """Apply changes and exit"""
        self.apply_claude_config()
        self.root.destroy()
    
    def discard_and_exit(self):
        """Discard changes and exit"""
        if self.has_changes:
            if messagebox.askyesno("Discard Changes", "Are you sure you want to discard all changes?"):
                self.root.destroy()
        else:
            self.root.destroy()

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = AIDevToolkitGUI(root)
    root.mainloop()

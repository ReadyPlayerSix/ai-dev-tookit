"""
AI Dev Toolkit Unified Configurator GUI

This is the unified GUI implementation for the AI Dev Toolkit.
It replaces all previous implementations with a single, reliable version.
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

class AIDevToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Dev Toolkit Control Panel")
        self.root.geometry("850x1001")  # Optimized size with appropriate width and taller height
        self.root.resizable(True, True)
        
        # Set version
        self.version = "0.3.0"
        
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
        
        # Variables
        self.claude_desktop_path = tk.StringVar()
        self.config_path = tk.StringVar()
        # Server enabled is determined by tool selection
        self.project_dirs = []
        self.project_enabled = {}  # Map of project path to enabled status
        self.server_status = tk.StringVar(value="Stopped")
        self.server_process = None
        self.server_log = tk.StringVar(value="")
        
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
        
        # Projects section
        projects_frame = ttk.LabelFrame(self.project_frame, text="Project Directories", padding="10 10 10 10")
        projects_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Project controls
        proj_controls = ttk.Frame(projects_frame)
        proj_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(proj_controls, text="Add Project", command=self.add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(proj_controls, text="Remove Selected", command=self.remove_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(proj_controls, text="Create Project", command=self.toggle_create_project_area).pack(side=tk.LEFT)
        ttk.Button(proj_controls, text="Reload Directories", command=self.scan_for_projects).pack(side=tk.LEFT, padx=(5, 0))
        
        # Project list using a Treeview for better structure and selection
        self.projects_treeview = ttk.Treeview(projects_frame, columns=("Path", "Status"), 
                                             selectmode='browse', height=10)
        
        # Configure the treeview
        self.projects_treeview.heading('#0', text='Enabled')
        self.projects_treeview.heading('Path', text='Project Path')
        self.projects_treeview.heading('Status', text='Status')
        
        # Set column widths
        self.projects_treeview.column('#0', width=70, stretch=False)
        self.projects_treeview.column('Path', width=500, stretch=True)
        self.projects_treeview.column('Status', width=100, stretch=False)
        
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
        
        # Bind click event to toggle checkbox state
        self.projects_treeview.bind('<ButtonRelease-1>', self.on_treeview_click)
        
        # Message area for project updates - always visible
        self.project_message_var = tk.StringVar()
        self.project_message_label = ttk.Label(projects_frame, textvariable=self.project_message_var, 
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

    #-----------------------------------------------------
    # Utility Methods
    #-----------------------------------------------------
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
            
            self.update_projects_list()
            self.project_message_var.set(f"Found {len(found_projects)} projects with .ai_reference folders.")
        else:
            self.project_message_var.set("No new projects with .ai_reference folders found.")
        
    def update_projects_list(self):
        """Update the projects list display using the treeview"""
        # Clear the treeview
        for item in self.projects_treeview.get_children():
            self.projects_treeview.delete(item)
        
        # Clear active projects listbox
        self.active_projects_listbox.delete(0, tk.END)
        
        # Repopulate with current projects
        for i, dir_path in enumerate(self.project_dirs):
            enabled = self.project_enabled.get(dir_path, True)
            
            # Check if path has AI Librarian
            has_ai_ref = os.path.exists(os.path.join(dir_path, ".ai_reference"))
            status = "AI Librarian" if has_ai_ref else "Regular"
            
            # Add to treeview with checkbox state
            item_id = self.projects_treeview.insert('', 'end', 
                                                  text="✓" if enabled else "◻", 
                                                  values=(dir_path, status))
            
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
                new_text = "◻" if current_text == "✓" else "✓"
                self.projects_treeview.item(item_id, text=new_text)
                
                # Update state in project_enabled dictionary
                dir_path = self.projects_treeview.item(item_id, 'values')[0]
                self.project_enabled[dir_path] = (new_text == "✓")
                
                # Update active projects list on dashboard
                self.update_active_projects_list()
                
                # Mark changes
                self.has_changes = True
    
    def update_active_projects_list(self):
        """Update the list of active projects on the dashboard"""
        self.active_projects_listbox.delete(0, tk.END)
        
        for dir_path in self.project_dirs:
            if self.project_enabled.get(dir_path, False):
                has_ai_ref = os.path.exists(os.path.join(dir_path, ".ai_reference"))
                status = "AI Librarian" if has_ai_ref else "Regular"
                self.active_projects_listbox.insert(tk.END, f"{dir_path} [{status}]")
        
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
            dir_path = self.projects_treeview.item(selected_item[0], 'values')[0]
            
            # Remove directory from project_dirs list
            if dir_path in self.project_dirs:
                self.project_dirs.remove(dir_path)
                if dir_path in self.project_enabled:
                    del self.project_enabled[dir_path]
                
                # Update displays
                self.update_projects_list()
                self.update_active_projects_list()
                
                # Mark as changed
                self.has_changes = True
                
                # Show message
                self.project_message_var.set(f"Removed project directory: {dir_path}")
        else:
            messagebox.showinfo("No Selection", "Please select a project to remove.")
    
    def browse_config(self):
        """Browse for Claude Desktop config file"""
        config_file = filedialog.askopenfilename(
            title="Select Claude Desktop Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if config_file:
            self.config_path.set(config_file)
    
    def browse_project_location(self):
        """Browse for project location directory"""
        dir_path = filedialog.askdirectory(title="Select Project Location")
        if dir_path:
            self.new_project_location.set(dir_path)
    
    def create_new_project(self):
        """Create a new project"""
        # Validate inputs
        project_name = self.new_project_name.get().strip()
        project_type = self.new_project_type.get()
        location = self.new_project_location.get()
        
        if not project_name:
            messagebox.showerror("Error", "Project name is required.")
            return
        
        if not location:
            messagebox.showerror("Error", "Project location is required.")
            return
        
        # Create project directory
        project_dir = os.path.join(location, project_name)
        
        try:
            if os.path.exists(project_dir):
                messagebox.showerror("Error", f"Directory {project_dir} already exists.")
                return
                
            # Create directories
            os.makedirs(project_dir)
            os.makedirs(os.path.join(project_dir, "src"))
            os.makedirs(os.path.join(project_dir, "tests"))
            
            # Create basic files based on type
            if project_type == "web":
                with open(os.path.join(project_dir, "index.html"), 'w') as f:
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n  <title>Project</title>\n</head>\n<body>\n  <h1>Hello World</h1>\n</body>\n</html>")
                    
                with open(os.path.join(project_dir, "style.css"), 'w') as f:
                    f.write("body {\n  font-family: Arial, sans-serif;\n}")
                    
            elif project_type == "cli" or project_type == "library":
                with open(os.path.join(project_dir, "main.py"), 'w') as f:
                    f.write('def main():\n    print("Hello World!")\n\nif __name__ == "__main__":\n    main()')
                    
            elif project_type == "api":
                with open(os.path.join(project_dir, "api.py"), 'w') as f:
                    f.write('from flask import Flask\n\napp = Flask(__name__)\n\n@app.route("/")\ndef hello():\n    return "Hello World!"\n\nif __name__ == "__main__":\n    app.run(debug=True)')
            
            # Add README
            with open(os.path.join(project_dir, "README.md"), 'w') as f:
                f.write(f"# {project_name}\n\nA {project_type} project.\n")
            
            # Initialize AI Librarian
            from subprocess import run
            try:
                run([sys.executable, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                    "ai_librarian_init.py"), project_dir])
                has_ai_ref = True
            except Exception as e:
                print(f"Error initializing AI Librarian: {str(e)}")
                has_ai_ref = False
            
            # Add to project list
            self.project_dirs.append(project_dir)
            self.project_enabled[project_dir] = True
            self.has_changes = True
            self.update_projects_list()
            
            # Hide create project frame
            self.create_project_frame.pack_forget()
            
            # Show message
            ai_librarian_status = "and initialized AI Librarian" if has_ai_ref else "without AI Librarian"
            self.project_message_var.set(f"Created project {project_name} {ai_librarian_status}.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
    
    def toggle_create_project_area(self):
        """Show or hide the create project area"""
        if self.create_project_frame.winfo_ismapped():
            self.create_project_frame.pack_forget()
        else:
            self.create_project_frame.pack(fill=tk.X, pady=(0, 15))
    
    def update_server_status(self):
        """Update server status based on selected tools"""
        # Update server status based on selections
        if self.ai_dev_toolkit_server_enabled.get():
            self.server_status_label.config(text="MCP Server: Ready to Configure", style='Status.TLabel')
        else:
            self.server_status_label.config(text="MCP Server: Disabled", style='Stopped.Status.TLabel')
        
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
    
    def check_server_status(self):
        """Check if the server is running"""
        # This is a simple implementation - in a real app you would check the process status
        if hasattr(self, 'server_process') and self.server_process and self.server_process.poll() is None:
            self.server_status_label.config(text="MCP Server: Running", style='Running.Status.TLabel')
        else:
            self.server_status_label.config(text="MCP Server: Stopped", style='Stopped.Status.TLabel')
    
    def restart_server(self):
        """Restart the MCP server process"""
        # Stop the server if it's running
        if hasattr(self, 'server_process') and self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
        
        # Apply changes to ensure latest config is used
        self.apply_claude_config()
        
        # Start the server using the exact librarian server pattern
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            server_script_path = os.path.join(project_root, "aitoolkit", "librarian", "server.py")
            
            # Get enabled directories
            enabled_dirs = [d for d in self.project_dirs if self.project_enabled.get(d, True)]
            
            # Build command with directories - just like ai-librarian format
            cmd = ["python", server_script_path] + enabled_dirs
            
            # Start the server
            self.clear_server_log()
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Start a thread to read output
            def read_output():
                while self.server_process and self.server_process.poll() is None:
                    line = self.server_process.stdout.readline()
                    if line:
                        self.log_text.config(state=tk.NORMAL)
                        self.log_text.insert(tk.END, line)
                        self.log_text.see(tk.END)
                        self.log_text.config(state=tk.DISABLED)
            
            threading.Thread(target=read_output, daemon=True).start()
            
            # Update status
            self.server_status_label.config(text="MCP Server: Running", style='Running.Status.TLabel')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            print(f"Error starting server: {str(e)}")
    
    def clear_server_log(self):
        """Clear the server log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
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
    
    def generate_integrated_server_config(self):
        """Generate the configuration for the integrated server that EXACTLY matches the working ai-librarian pattern"""
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
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
    
    def on_closing(self):
        """Handle window close event"""
        if self.has_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                "You have unsaved changes. Would you like to save them before exiting?")
            
            if response is None:  # Cancel was clicked
                return
            elif response:  # Yes was clicked
                self.apply_claude_config()
        
        # Stop the server if it's running
        if hasattr(self, 'server_process') and self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
        
        self.root.destroy()

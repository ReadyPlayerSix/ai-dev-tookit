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

class AIDevToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Dev Toolkit Control Panel")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Set version
        self.version = "0.1.0"
        
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
        
        # Server configuration type
        self.server_config_type = tk.StringVar(value="npm")  # Default to npm package (recommended)
        
        # Servers enabled
        self.ai_librarian_server_enabled = tk.BooleanVar(value=False)
        
        # Tool selection variables
        self.file_system_tools_enabled = tk.BooleanVar(value=True)
        self.project_starter_tools_enabled = tk.BooleanVar(value=True)
        self.think_tool_enabled = tk.BooleanVar(value=True)
        self.ai_librarian_enabled = tk.BooleanVar(value=True)
        self.context_compression_enabled = tk.BooleanVar(value=False)
        
        # Build UI
        self.create_widgets()
        
        # Initial checks
        self.detect_claude_desktop()
        self.load_config()
        self.check_server_status()
    
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
                               wraplength=600, style='Info.TLabel')
        safety_label.pack(fill=tk.X)
        
        # MCP Server section
        server_config_frame = ttk.LabelFrame(self.claude_frame, text="MCP Server Configuration", padding="10 10 10 10")
        server_config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Server configuration type
        server_type_frame = ttk.Frame(server_config_frame, style='TFrame')
        server_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_type_frame, text="Server Configuration Type:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(server_type_frame, text="NPM Package (Recommended)", 
                       variable=self.server_config_type, value="npm",
                       command=self.update_server_config_type).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(server_type_frame, text="Python with uv (For Development)", 
                       variable=self.server_config_type, value="uv",
                       command=self.update_server_config_type).pack(side=tk.LEFT)
        
        # Server status (automatic based on tools)
        self.server_config_status_label = ttk.Label(server_config_frame, text="MCP Server configuration is determined by selected tools", style='TLabel')
        self.server_config_status_label.pack(anchor=tk.W, pady=(5, 5))
        
        # NPM configuration note
        self.npm_config_note = ttk.Label(server_config_frame, 
                                       text="Using NPM Package: This approach is recommended for most users and works with standard Claude Desktop configuration.",
                                       wraplength=600, style='Info.TLabel')
        self.npm_config_note.pack(fill=tk.X, pady=(0, 5))
        
        # uv configuration note - hidden initially
        self.uv_config_note = ttk.Label(server_config_frame, 
                                       text="Using Python with uv: This approach requires uv to be installed and is recommended for development. All paths must be absolute.",
                                       wraplength=600, style='Info.TLabel')
        
        # Server selection section
        server_selection_frame = ttk.LabelFrame(self.claude_frame, text="MCP Servers", padding="10 10 10 10")
        server_selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Note about server selection
        server_note = ttk.Label(server_selection_frame, 
                              text="Select which MCP servers to enable:",
                              wraplength=600)
        server_note.pack(anchor=tk.W, pady=(0, 10))
        
        # AI Librarian Server checkbox
        ai_librarian_server_check = ttk.Checkbutton(server_selection_frame, 
                                                 text="AI Librarian Server - Code understanding and context maintenance", 
                                                 variable=self.ai_librarian_server_enabled,
                                                 style='Server.TCheckbutton',
                                                 command=self.update_server_status)
        ai_librarian_server_check.pack(anchor=tk.W, pady=5)
        
        # Tool selection section
        tool_frame = ttk.LabelFrame(self.claude_frame, text="Available Tools", padding="10 10 10 10")
        tool_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Note about tool selection
        tool_note = ttk.Label(tool_frame, 
                            text="Select which tools will be available to Claude:",
                            wraplength=600)
        tool_note.pack(anchor=tk.W, pady=(0, 10))
        
        # File System Tools checkbox
        file_system_check = ttk.Checkbutton(tool_frame, 
                                          text="File System Tools - Read, write, and navigate the file system", 
                                          variable=self.file_system_tools_enabled,
                                          command=self.update_tool_dependencies)
        file_system_check.pack(anchor=tk.W, pady=2)
        
        # Project Starter Tools checkbox
        self.project_starter_check = ttk.Checkbutton(tool_frame, 
                                                  text="Project Starter Tools - Project generation and scaffolding", 
                                                  variable=self.project_starter_tools_enabled,
                                                  command=self.update_server_status)
        self.project_starter_check.pack(anchor=tk.W, pady=2)
        
        # AI Librarian checkbox
        self.ai_librarian_check = ttk.Checkbutton(tool_frame, 
                                               text="AI Librarian - Persistent code comprehension system", 
                                               variable=self.ai_librarian_enabled,
                                               command=self.update_server_status)
        self.ai_librarian_check.pack(anchor=tk.W, pady=2)
        
        # Think Tool checkbox
        think_tool_check = ttk.Checkbutton(tool_frame, 
                                         text="Think Tool - Structured reasoning for complex problems", 
                                         variable=self.think_tool_enabled,
                                         command=self.update_server_status)
        think_tool_check.pack(anchor=tk.W, pady=2)
        
        # Context Compression checkbox
        self.context_compression_check = ttk.Checkbutton(tool_frame, 
                                                      text="Context Compression - Store and retrieve conversation history (Recommended for longer project conversations)", 
                                                      variable=self.context_compression_enabled,
                                                      command=self.update_server_status)
        self.context_compression_check.pack(anchor=tk.W, pady=2)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.claude_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Apply and Exit", command=self.apply_and_exit).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply Changes", command=self.apply_claude_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Discard Changes and Exit", command=self.discard_and_exit).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Add Project Directories", 
                 command=lambda: self.notebook.select(self.project_frame)).pack(side=tk.RIGHT, padx=(5, 0))
    
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
        ttk.Button(proj_controls, text="Remove Project", command=self.remove_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(proj_controls, text="Create Project", command=self.toggle_create_project_area).pack(side=tk.LEFT)
        
        # Project list with checkboxes
        self.projects_container = ttk.Frame(projects_frame)
        self.projects_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Message area for project updates - always visible
        self.project_message_var = tk.StringVar()
        self.project_message_label = ttk.Label(projects_frame, textvariable=self.project_message_var, 
                                             style='Info.TLabel', wraplength=600)
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
        
        # Bottom actions frame
        actions_frame = ttk.Frame(self.project_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(actions_frame, text="Apply Changes", 
                 command=self.apply_project_changes).pack(side=tk.RIGHT)
        ttk.Button(actions_frame, text="Discard Changes", 
                 command=self.load_config).pack(side=tk.RIGHT, padx=(0, 5))
    
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
        
        description = """The AI Dev Toolkit enhances Claude with powerful capabilities:

1. File System Tools: Read, write, and navigate the file system
2. AI Librarian: Persistent code comprehension system that maintains context across conversations
3. Project Starter: Project generation and scaffolding
4. Think Tool: Structured reasoning for complex problems
5. Context Compression: Store and retrieve conversation history (Coming Soon)"""
        
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
    
    #-----------------------------------------------------
    # Claude Desktop Functions
    #-----------------------------------------------------
    def detect_claude_desktop(self):
        """Try to locate Claude Desktop installation and configuration"""
        print("Detecting Claude Desktop...")
        found_installation = False
        found_config = False
        
        # Common installation paths
        possible_install_paths = [
            os.path.expanduser("~/AppData/Local/Programs/Claude"),
            os.path.expanduser("~/AppData/Local/Claude"),
            os.path.expanduser("~/AppData/Roaming/Claude"),
            "C:/Program Files/Claude",
            "C:/Program Files (x86)/Claude",
            os.path.expanduser("~/AppData/Local/Programs/Anthropic/Claude"),
            os.path.expanduser("~/AppData/Local/Anthropic/Claude"),
            os.path.expanduser("~/AppData/Roaming/Anthropic/Claude"),
            "C:/Program Files/Anthropic/Claude",
            "C:/Program Files (x86)/Anthropic/Claude"
        ]
        
        # Common configuration paths
        possible_config_paths = [
            # Current paths for latest Claude Desktop versions
            os.path.expanduser("~/AppData/Roaming/Claude Desktop/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Roaming/Claude Desktop/config.json"),
            os.path.expanduser("~/AppData/Local/Claude Desktop/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Claude Desktop/config.json"),
            os.path.expanduser("~/AppData/Local/Programs/Claude Desktop/claude_desktop_config.json"),
            # Anthropic branded paths
            os.path.expanduser("~/AppData/Roaming/Anthropic/Claude Desktop/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Roaming/Anthropic/Claude Desktop/config.json"),
            os.path.expanduser("~/AppData/Local/Anthropic/Claude Desktop/claude_desktop_config.json"),
            # Legacy paths
            os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Programs/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Roaming/Claude/config.json"),
            os.path.join(os.path.expanduser("~/AppData/Roaming/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Local/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Local/Programs/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Roaming/Claude"), "config.json"),
            os.path.join(os.path.expanduser("~/AppData/Roaming/Anthropic/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Roaming/Anthropic/Claude"), "config.json"),
            os.path.join(os.path.expanduser("~/AppData/Local/Anthropic/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Local/Anthropic/Claude"), "config.json")
        ]
        
        # Print the paths we're checking - helps with debugging
        print("Checking installation paths:")
        for path in possible_install_paths:
            print(f"  {path} - {'EXISTS' if os.path.exists(path) else 'NOT FOUND'}")
        
        print("\nChecking config paths:")
        for path in possible_config_paths:
            print(f"  {path} - {'EXISTS' if os.path.exists(path) else 'NOT FOUND'}")
        
        # First, find the installation
        for path in possible_install_paths:
            if os.path.exists(path):
                # Look for executable
                exe_path = os.path.join(path, "Claude.exe")
                print(f"Checking executable: {exe_path} - {'EXISTS' if os.path.exists(exe_path) else 'NOT FOUND'}")
                if os.path.exists(exe_path):
                    self.claude_desktop_path.set(os.path.normpath(path))
                    found_installation = True
                    print(f"\nFound Claude Desktop installation at: {path}")
                    break
        
        # Now try to find the config file
        for config_path in possible_config_paths:
            norm_config_path = os.path.normpath(config_path)
            print(f"Normalized config path: {norm_config_path} - {'EXISTS' if os.path.exists(norm_config_path) else 'NOT FOUND'}")
            if os.path.exists(norm_config_path):
                self.config_path.set(norm_config_path)
                found_config = True
                print(f"Found Claude Desktop config at: {norm_config_path}")
                break
        
        # Update UI based on what we found
        if found_config:
            self.claude_status_label.config(text=f"Claude Desktop: Installed")
            self.claude_config_status_label.config(text=f"Config found: {os.path.basename(self.config_path.get())}")
            # If we have a config file, assume Claude is installed
            found_installation = True
            
            # Claude Desktop found, configuration is accessible
        else:
            self.claude_status_label.config(text="Claude Desktop not found. Please install it first.")
            self.claude_config_status_label.config(text="Claude Desktop not found. Please install it first.")
            
            # Claude Desktop not found, configuration is inaccessible
        
        print("\nDetection completed.")
    
    def browse_config(self):
        """Open file dialog to locate config file"""
        filename = filedialog.askopenfilename(
            title="Select Claude Desktop Config File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.config_path.set(filename)
            self.load_config()
            # Update tool selection based on loaded configuration
    
    def update_server_config_type(self):
        """Update server configuration type"""
        config_type = self.server_config_type.get()
        
        # Update UI based on selected configuration type
        if config_type == "npm":
            self.npm_config_note.pack(fill=tk.X, pady=(0, 5))
            self.uv_config_note.pack_forget()
        else:  # uv
            self.npm_config_note.pack_forget()
            self.uv_config_note.pack(fill=tk.X, pady=(0, 5))
        
        # Mark changes
        self.has_changes = True
        
        # Update server status
        self.update_server_status()
    
    def load_config(self):
        """Load current configuration from config file"""
        config_path = self.config_path.get()
        if not config_path or not os.path.exists(config_path):
            print(f"Config file not found at: {config_path}")
            return
        
        print(f"Loading config from: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_text = f.read().strip()
                
                # Show the exact character position
                if len(config_text) > 275:
                    print(f"Character at position 275: '{config_text[275]}' (ASCII {ord(config_text[275])})")
                    print(f"Context around position 275: '{config_text[270:280]}'")
                
                # Fix common JSON issues - especially trailing commas which are causing the problem
                import re
                # Remove trailing commas before closing braces or brackets
                fixed_text = re.sub(r',\s*([\]\}])', r'\1', config_text)
                
                try:
                    config = json.loads(fixed_text)
                    print("Successfully fixed JSON by removing trailing commas!")
                except json.JSONDecodeError as je:
                    print(f"Fixing still failed: {str(je)}")
                    # Create a minimal valid config as last resort
                    config = {"mcpServers": {}}
                    print("Using minimal default config")
            
            # Check if our MCP server is enabled
            print(f"Config keys: {list(config.keys())}")
            
            # Handle both camelCase and snake_case for backward compatibility
            mcpServers = {}
            if "mcp_servers" in config:
                mcp_servers_list = config.get("mcp_servers", [])
                # Ensure mcp_servers_list is a list
                if mcp_servers_list is None:
                    mcp_servers_list = []
                print(f"Found {len(mcp_servers_list)} MCP servers in snake_case config")
                # Convert snake_case list to dict format
                for server in mcp_servers_list:
                    if isinstance(server, dict) and "name" in server:
                        mcpServers[server["name"]] = server
            elif "mcpServers" in config:
                # Handle camelCase structure
                mcpServers = config.get("mcpServers", {})
                # Ensure mcpServers is a dict
                if mcpServers is None:
                    mcpServers = {}
                print(f"Found mcpServers in camelCase format with {len(mcpServers)} entries")
            
            print(f"Final MCP servers dict: {len(mcpServers)} entries")
            
            # Check for our servers in various possible names
            toolkit_server_names = ["AI Dev Toolkit", "aidevtoolkit", "ai-dev-toolkit"]
            librarian_server_names = ["AI Librarian", "ailibrarian", "ai-librarian"]
            
            # Flags for found servers
            toolkit_server_found = False
            librarian_server_found = False
            toolkit_server_config = None
            
            # Check for AI Dev Toolkit server
            for name in toolkit_server_names:
                if name in mcpServers:
                    toolkit_server_found = True
                    toolkit_server_config = mcpServers[name]
                    break
                    
            # Check for AI Librarian server
            for name in librarian_server_names:
                if name in mcpServers:
                    librarian_server_found = True
                    # Update AI Librarian enabled status
                    self.ai_librarian_server_enabled.set(True)
                    break
                    
            # Set combined server status
            server_found = toolkit_server_found or librarian_server_found
            server_config = toolkit_server_config
            
            # Debug print
            print(f"Found AI Dev Toolkit server: {toolkit_server_config}")
            
            if server_found and server_config is not None:
                print(f"Found AI Dev Toolkit server: {server_config}")
                
                # Determine server type from configuration
                if "command" in server_config:
                    command = server_config["command"]
                    if command == "npx":
                        self.server_config_type.set("npm")
                        print("Server type: npm")
                    elif command == "uv" or command == "python":
                        self.server_config_type.set("uv")
                        print("Server type: uv")
                        
                # Update UI for server type
                self.update_server_config_type()
                
                # Get project directories
                if server_config is not None:  # Add null check for server_config
                    if "allowed_directories" in server_config:
                        dirs = server_config["allowed_directories"]
                        self.project_dirs = dirs if dirs is not None else []
                    elif "allowedDirectories" in server_config:
                        dirs = server_config["allowedDirectories"]
                        self.project_dirs = dirs if dirs is not None else []
                    else:
                        self.project_dirs = []
                else:
                    self.project_dirs = []
                
                print(f"Loaded {len(self.project_dirs)} project directories")
                
                # Get enabled tools
                enabled_tools = []
                if server_config is not None:  # Add null check for server_config
                    if "enabled_tools" in server_config:
                        tools = server_config["enabled_tools"]
                        enabled_tools = tools if tools is not None else []
                    elif "enabledTools" in server_config:
                        tools = server_config["enabledTools"]
                        enabled_tools = tools if tools is not None else []
                
                print(f"Loaded enabled tools: {enabled_tools}")
                
                # Set tool checkboxes based on enabled tools
                self.file_system_tools_enabled.set("file_system" in enabled_tools)
                self.project_starter_tools_enabled.set("project_starter" in enabled_tools)
                self.ai_librarian_enabled.set("ai_librarian" in enabled_tools)
                self.think_tool_enabled.set("think" in enabled_tools)
                self.context_compression_enabled.set("context_compression" in enabled_tools)
            else:
                print("AI Dev Toolkit server not found in config")
                # Set defaults for a new installation
                self.project_dirs = []
                self.file_system_tools_enabled.set(True)
                self.project_starter_tools_enabled.set(True)
                self.ai_librarian_enabled.set(True)
                self.think_tool_enabled.set(True)
                self.context_compression_enabled.set(False)
            
            # Server is automatically enabled if any tools are enabled
            self.update_server_status()
            
            # Initialize project enabled status
            for path in self.project_dirs:
                self.project_enabled[path] = True
            
            # Update directory lists
            self.update_directory_list()
            self.update_projects_list()
            
            # Reset changes flag
            self.has_changes = False
            
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {str(je)}")
            messagebox.showerror("Error", f"Failed to parse config file: {str(je)}\n\nThe file may be corrupted or not in JSON format.")
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
    
    def update_server_status(self):
        """Update the server status based on selected tools and servers"""
        # Check which tools are enabled
        tools_enabled = (self.file_system_tools_enabled.get() or 
                        self.project_starter_tools_enabled.get() or 
                        self.think_tool_enabled.get() or 
                        self.ai_librarian_enabled.get() or 
                        self.context_compression_enabled.get())
        
        # Server is automatically enabled if tools are selected or AI Librarian server is enabled
        server_enabled = tools_enabled or self.ai_librarian_server_enabled.get()
        self.has_changes = True
        
        # Update status message
        if tools_enabled:
            config_type = "NPM package" if self.server_config_type.get() == "npm" else "Python with uv"
            self.server_config_status_label.config(text=f"MCP Server will be enabled ({config_type}) with selected tools")
        elif self.ai_librarian_server_enabled.get():
            self.server_config_status_label.config(text="AI Librarian MCP Server will be enabled")
        else:
            self.server_config_status_label.config(text="MCP Servers will be disabled (no tools or servers selected)")
    
    def update_tool_dependencies(self):
        """Update tool dependencies based on file system tools status"""
        self.has_changes = True
        if self.file_system_tools_enabled.get():
            # If file system tools are enabled, enable dependent tools
            self.project_starter_check.configure(state=tk.NORMAL)
            self.ai_librarian_check.configure(state=tk.NORMAL)
            self.context_compression_check.configure(state=tk.NORMAL)
        else:
            # If file system tools are disabled, disable dependent tools
            self.project_starter_tools_enabled.set(False)
            self.ai_librarian_enabled.set(False)
            
            self.project_starter_check.configure(state=tk.DISABLED)
            self.ai_librarian_check.configure(state=tk.DISABLED)
            
            # Context compression can still be enabled independently
            self.context_compression_check.configure(state=tk.NORMAL)
            
        # Update server status
        self.update_server_status()
    
    def add_directory(self):
        """Open directory selection dialog to add a project directory"""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            directory = os.path.normpath(directory)
            if directory not in self.project_dirs:
                self.project_dirs.append(directory)
                self.project_enabled[directory] = True
                self.update_directory_list()
                self.update_projects_list()
                self.has_changes = True
                
                # Show message if AI Librarian is enabled
                if self.ai_librarian_enabled.get():
                    ai_ref_path = os.path.join(directory, ".ai_reference")
                    if not os.path.exists(ai_ref_path):
                        self.show_project_message(f"An .ai_reference directory will be created in '{directory}' when you apply changes.")
    
    def remove_directory(self):
        """Remove selected directory from the list"""
        # Get the selected project from the projects list
        selected_project = None
        for widget in self.projects_container.winfo_children():
            if isinstance(widget, ttk.Frame):
                checkbox = widget.winfo_children()[0]
                if checkbox.instate(['focus']):
                    project_path = widget.winfo_children()[1].cget("text")
                    selected_project = project_path
                    break
        
        if selected_project and selected_project in self.project_dirs:
            self.project_dirs.remove(selected_project)
            if selected_project in self.project_enabled:
                del self.project_enabled[selected_project]
            self.update_directory_list()
            self.update_projects_list()
            self.has_changes = True
            self.show_project_message(f"Removed directory: {selected_project}")
    
    def update_directory_list(self):
        """Update directory lists in Claude Desktop tab"""
        # Update active projects list on dashboard
        self.active_projects_listbox.delete(0, tk.END)
        
        for directory in self.project_dirs:
            if self.project_enabled.get(directory, True):
                self.active_projects_listbox.insert(tk.END, directory)
    
    def apply_claude_config(self):
        """Save changes to the config file"""
        config_path = self.config_path.get()
        if not config_path:
            messagebox.showerror("Error", "Please select Claude Desktop configuration file")
            return
        
        try:
            # Try to safely read the existing config
            existing_config = {"mcpServers": {}}
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_text = f.read().strip()
                    
                # Try to fix common JSON issues - especially trailing commas
                import re
                fixed_text = re.sub(r',\s*([\]\}])', r'\1', config_text)
                
                try:
                    existing_config = json.loads(fixed_text)
                    print("Successfully fixed and loaded JSON")
                except json.JSONDecodeError:
                    # If that doesn't work, try a more aggressive approach
                    try:
                        # Try json5 library if available (handles many JSON syntax issues)
                        import json5
                        existing_config = json5.loads(config_text)
                        print("Used json5 to parse JSON")
                    except (ImportError, Exception) as e:
                        print(f"Could not parse existing config: {str(e)}")
                        # Continue with default empty config
                        if messagebox.askyesno("Error", "Cannot read existing configuration due to syntax errors. Continue with a new configuration? (This will preserve your settings file by creating a backup)"): 
                            # Create backup of the original file
                            import shutil
                            backup_path = config_path + ".backup"
                            shutil.copyfile(config_path, backup_path)
                            print(f"Created backup at {backup_path}")
                        else:
                            return
            except Exception as e:
                print(f"Error reading config: {str(e)}")
            
            # Now work with the existing_config, which is either:
            # 1. The successfully parsed existing config
            # 2. A new empty config with just {"mcpServers": {}}
            
            # Ensure mcpServers exists and is a dict
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            if not isinstance(existing_config["mcpServers"], dict):
                existing_config["mcpServers"] = {}
                
            # Get enabled tools
            enabled_tools = []
            if self.file_system_tools_enabled.get():
                enabled_tools.append("file_system")
            if self.project_starter_tools_enabled.get():
                enabled_tools.append("project_starter")
            if self.ai_librarian_enabled.get():
                enabled_tools.append("ai_librarian")
            if self.think_tool_enabled.get():
                enabled_tools.append("think")
            if self.context_compression_enabled.get():
                enabled_tools.append("context_compression")
            
            # Determine server status based on tools and servers
            server_enabled = len(enabled_tools) > 0 or self.ai_librarian_server_enabled.get()
            
            # Filter project directories to only include enabled ones
            enabled_directories = [path for path in self.project_dirs if self.project_enabled.get(path, True)]
            
            # For Windows paths in the config file, make sure backslashes are properly escaped
            enabled_directories_escaped = [path.replace('\\', '\\\\') for path in enabled_directories]
            
            # Get absolute path to this script's directory for Python configuration
            script_dir = os.path.dirname(os.path.abspath(__file__))
            repo_dir = os.path.dirname(script_dir)
            
            # Remove existing AI Dev Toolkit and AI Librarian servers if present
            toolkit_server_names = ["AI Dev Toolkit", "aidevtoolkit", "ai-dev-toolkit"]
            librarian_server_names = ["AI Librarian", "ailibrarian", "ai-librarian"]
            
            for name in toolkit_server_names + librarian_server_names:
                if name in existing_config["mcpServers"]:
                    del existing_config["mcpServers"][name]
            
            # AI Dev Toolkit Server Configuration
            if len(enabled_tools) > 0:
                toolkit_server_name = "ai-dev-toolkit"
                
                if self.server_config_type.get() == "npm":
                    # NPM package configuration
                    toolkit_config = {
                        "command": "npx",
                        "args": ["-y", "@isekaizen/ai-dev-toolkit"]
                    }
                    
                    # Add project directories to args if enabled
                    if enabled_directories_escaped:
                        toolkit_config["args"].extend(enabled_directories_escaped)
                else:  # uv
                    # Python with uv configuration
                    toolkit_config = {
                        "command": "uv",
                        "args": [
                            "run", 
                            "--directory", 
                            repo_dir,  # Use absolute path to repo
                            "src/server.py"
                        ],
                        "env": {
                            "PYTHONPATH": repo_dir
                        }
                    }
                    
                    # Add environment variables for tool configuration
                    if enabled_tools:
                        toolkit_config["env"]["AI_DEV_TOOLKIT_ENABLED_TOOLS"] = ",".join(enabled_tools)
                        
                    if enabled_directories_escaped:
                        toolkit_config["env"]["AI_DEV_TOOLKIT_ALLOWED_DIRS"] = ",".join(enabled_directories_escaped)
                
                # Add the AI Dev Toolkit server
                existing_config["mcpServers"][toolkit_server_name] = toolkit_config
            
            # AI Librarian Server Configuration
            if self.ai_librarian_server_enabled.get():
                librarian_server_name = "ai-librarian"
                
                # Path to the AI Librarian server
                librarian_server_path = os.path.join(repo_dir, "ai-librarian-server", "server.py")
                
                # Create configuration
                librarian_config = {
                    "command": "python",
                    "args": [
                        librarian_server_path
                    ]
                }
                
                # Add directories
                if enabled_directories_escaped:
                    for dir_path in enabled_directories_escaped:
                        librarian_config["args"].append(dir_path)
                
                # Add the AI Librarian server
                existing_config["mcpServers"][librarian_server_name] = librarian_config

            # Write config back with careful handling of JSON format
            with open(config_path, 'w', encoding='utf-8') as f:
                # Use a compact JSON format to avoid any formatting issues
                json_str = json.dumps(existing_config, indent=2, ensure_ascii=False, separators=(',', ': '))
                f.write(json_str)
            
            # Create .ai_reference directories for enabled projects if AI Librarian is enabled
            if server_enabled and self.ai_librarian_enabled.get():
                for directory in enabled_directories:
                    ai_ref_path = os.path.join(directory, ".ai_reference")
                    if not os.path.exists(ai_ref_path):
                        try:
                            os.makedirs(ai_ref_path, exist_ok=True)
                            # Create a simple README.md file
                            readme_path = os.path.join(ai_ref_path, "README.md")
                            with open(readme_path, 'w', encoding='utf-8') as f:
                                f.write("# AI Librarian\n\nThis directory contains the AI Librarian context for this project.")
                        except Exception as e:
                            print(f"Error creating .ai_reference directory: {str(e)}")
            
            # Reset changes flag
            self.has_changes = False
            
            # Show confirmation with configuration type
            config_type = "NPM package" if self.server_config_type.get() == "npm" else "Python with uv"
            messagebox.showinfo("Success", 
                              f"Configuration updated successfully using {config_type}.\n\n"
                              "Please restart Claude Desktop for changes to take effect.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def apply_and_exit(self):
        """Apply changes and exit the application"""
        self.apply_claude_config()
        self.root.destroy()
        
    def discard_and_exit(self):
        """Discard all changes and exit the application"""
        if self.has_changes:
            if messagebox.askyesno("Confirm Discard", "Are you sure you want to discard all changes and exit?"):
                self.root.destroy()
        else:
            self.root.destroy()
        
    def on_closing(self):
        """Handle window close event"""
        if self.has_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                 "You have unsaved changes. Do you want to save them before exiting?")
            if response is True:  # Yes - save and exit
                self.apply_claude_config()
                self.root.destroy()
            elif response is False:  # No - discard and exit
                self.root.destroy()
            else:  # Cancel - return to application
                return
        else:
            self.root.destroy()
    
    #-----------------------------------------------------
    # Server Management Functions
    #-----------------------------------------------------
    def check_server_status(self):
        """Check if the MCP server is running"""
        # Simple check - in a production app we'd do proper process detection
        # This is just a placeholder implementation
        if self.server_process and self.server_process.poll() is None:
            self.server_status.set("Running")
            self.server_status_value_label.configure(style='Running.Status.TLabel') if hasattr(self, 'server_status_value_label') else None
            self.server_status_label.configure(style='Running.Status.TLabel')
            self.server_status_label.configure(text="MCP Server: Running")
        else:
            self.server_status.set("Stopped")
            self.server_status_value_label.configure(style='Stopped.Status.TLabel') if hasattr(self, 'server_status_value_label') else None
            self.server_status_label.configure(style='Stopped.Status.TLabel')
            self.server_status_label.configure(text="MCP Server: Stopped")
        
        # Schedule next check
        self.root.after(1000, self.check_server_status)
    
    def restart_server(self):
        """Restart the MCP server"""
        self.stop_server()
        # Wait a moment to ensure the server is fully stopped
        self.root.after(1000, self.start_server)
    
    def start_server(self):
        """Start the MCP server"""
        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Server Status", "Server is already running")
            return
        
        try:
            # Get the server script path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            repo_dir = os.path.dirname(script_dir)
            server_script = os.path.normpath(os.path.join(repo_dir, "src", "server.py"))
            
            # Check if the file exists
            if not os.path.exists(server_script):
                messagebox.showerror("Error", f"Server script not found at {server_script}\n\nMake sure you have installed the AI Dev Toolkit correctly.")
                return
            
            # Print status information for debugging
            print(f"Starting server from: {server_script}")
            
            # Command based on configuration type
            if self.server_config_type.get() == "npm":
                try:
                    # Try to run using npx
                    print("Starting server using npm package...")
                    self.server_process = subprocess.Popen(
                        ["npx", "@modelcontextprotocol/server-filesystem"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )
                except Exception as npm_err:
                    print(f"Error starting npm package: {str(npm_err)}")
                    # Fall back to Python directly
                    print(f"Falling back to Python directly: {sys.executable}")
                    self.server_process = subprocess.Popen(
                        [sys.executable, server_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )
            else:  # uv
                try:
                    # Try to run using uv
                    print("Starting server using uv...")
                    self.server_process = subprocess.Popen(
                        ["uv", "run", server_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1,
                        env={"PYTHONPATH": repo_dir, **os.environ}
                    )
                except Exception as uv_err:
                    print(f"Error starting with uv: {str(uv_err)}")
                    # Fall back to Python directly
                    print(f"Falling back to Python directly: {sys.executable}")
                    self.server_process = subprocess.Popen(
                        [sys.executable, server_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )
            
            # Start reading the output
            self.start_log_reader()
            
            # Update status
            self.add_to_log("Server starting...\nWaiting for initialization to complete.")
            
            # Enable immediate visual feedback
            self.server_status.set("Starting...")
            self.server_status_label.configure(style='Warning.Status.TLabel')
            self.server_status_label.configure(text="MCP Server: Starting")
            
            messagebox.showinfo("Server Status", "MCP Server starting.\n\nThe server will be ready in a few moments.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop the MCP server"""
        if not self.server_process or self.server_process.poll() is not None:
            messagebox.showinfo("Server Status", "Server is not running")
            return
        
        try:
            # Terminate the process
            self.server_process.terminate()
            
            # Wait for it to end (with timeout)
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                self.server_process.kill()
            
            messagebox.showinfo("Server Status", "Server stopped successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
    
    def start_log_reader(self):
        """Start a thread to read the server output"""
        if not self.server_process:
            return
        
        def read_output():
            while self.server_process and self.server_process.poll() is None:
                try:
                    line = self.server_process.stdout.readline()
                    if line:
                        # Add to log
                        self.add_to_log(line.strip())
                except:
                    break
        
        # Start the thread
        log_thread = threading.Thread(target=read_output, daemon=True)
        log_thread.start()
    
    def add_to_log(self, line):
        """Add a line to the log displays"""
        # Add to dashboard log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_server_log(self):
        """Clear the server log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    #-----------------------------------------------------
    # Project Management Functions
    #-----------------------------------------------------
    def update_projects_list(self):
        """Update the projects list with checkboxes"""
        # Clear existing widgets
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        
        # Create a canvas and scrollbar for the projects list
        canvas = tk.Canvas(self.projects_container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.projects_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add the project entries
        for i, directory in enumerate(self.project_dirs):
            project_frame = ttk.Frame(scrollable_frame)
            project_frame.pack(fill=tk.X, pady=2)
            
            # Create variable for the checkbox
            var = tk.BooleanVar(value=self.project_enabled.get(directory, True))
            
            # Update project_enabled dictionary when checkbox changes
            def make_callback(path, variable):
                def callback():
                    self.project_enabled[path] = variable.get()
                    self.has_changes = True
                    # Show message about AI Librarian
                    if not variable.get() and self.ai_librarian_enabled.get():
                        self.show_project_message("AI Librarian will be disabled for non-accessible projects.")
                    self.update_directory_list()
                return callback
            
            # Create the checkbox
            checkbox = ttk.Checkbutton(project_frame, variable=var, command=make_callback(directory, var))
            checkbox.pack(side=tk.LEFT, padx=(5, 10))
            
            # Create the project path label
            path_label = ttk.Label(project_frame, text=directory)
            path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Create the "Open Location" button
            open_btn = ttk.Button(project_frame, text="Open Project Location", 
                              command=lambda d=directory: self.open_project_location(d))
            open_btn.pack(side=tk.RIGHT, padx=5)
            
            # Check for .ai_reference directory
            ai_ref_path = os.path.join(directory, ".ai_reference")
            if os.path.exists(ai_ref_path):
                ai_ref_label = ttk.Label(project_frame, text="AI Librarian Enabled", 
                                      foreground="green")
                ai_ref_label.pack(side=tk.RIGHT, padx=5)
        
        # Pack the canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ensure project_dirs is a list
        if self.project_dirs is None:
            self.project_dirs = []
                
        # Update message if no projects
        if not self.project_dirs:
            self.show_project_message("No project directories added. Add directories that Claude should have access to.")
    
    def toggle_create_project_area(self):
        """Toggle the visibility of the create project area"""
        if self.create_project_frame.winfo_ismapped():
            self.create_project_frame.pack_forget()
        else:
            self.create_project_frame.pack(fill=tk.X, pady=(15, 0))
    
    def browse_project_location(self):
        """Browse for new project location"""
        directory = filedialog.askdirectory(title="Select Project Location")
        if directory:
            self.new_project_location.set(directory)
    
    def create_new_project(self):
        """Create a new project"""
        # Get project details
        project_name = self.new_project_name.get().strip()
        project_type = self.new_project_type.get()
        project_location = self.new_project_location.get()
        
        # Validate inputs
        if not project_name:
            messagebox.showerror("Error", "Please enter a project name")
            return
        
        if not project_type:
            messagebox.showerror("Error", "Please select a project type")
            return
        
        if not project_location or not os.path.isdir(project_location):
            messagebox.showerror("Error", "Please select a valid project location")
            return
        
        # Create project directory
        project_dir = os.path.join(project_location, project_name.lower().replace(' ', '-'))
        
        try:
            os.makedirs(project_dir, exist_ok=True)
            
            # Create some basic directories
            os.makedirs(os.path.join(project_dir, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_dir, "tests"), exist_ok=True)
            
            # Create a simple README
            with open(os.path.join(project_dir, "README.md"), 'w') as f:
                f.write(f"# {project_name}\n\nA {project_type} project.\n")
            
            # Add to project directories
            if project_dir not in self.project_dirs:
                self.project_dirs.append(project_dir)
                self.project_enabled[project_dir] = True
                self.update_directory_list()
                self.update_projects_list()
            
            # Create .ai_reference directory if AI Librarian is enabled
            if self.ai_librarian_enabled.get():
                ai_ref_path = os.path.join(project_dir, ".ai_reference")
                os.makedirs(ai_ref_path, exist_ok=True)
                # Create a simple README.md file
                readme_path = os.path.join(ai_ref_path, "README.md")
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write("# AI Librarian\n\nThis directory contains the AI Librarian context for this project.")
            
            # Hide the create project frame
            self.create_project_frame.pack_forget()
            
            # Reset fields
            self.new_project_name.set("")
            self.new_project_location.set("")
            
            messagebox.showinfo("Project Created", f"Project {project_name} created at {project_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
    
    def open_project_location(self, directory):
        """Open the project location in file explorer"""
        if os.path.exists(directory):
            os.startfile(directory)
    
    def open_claude_directory(self):
        """Open the Claude Desktop directory in file explorer"""
        claude_path = os.path.dirname(self.config_path.get())
        if os.path.exists(claude_path):
            os.startfile(claude_path)
    
    def show_project_message(self, message):
        """Show a message in the project tab"""
        self.project_message_var.set(message)
        self.project_message_label.pack(fill=tk.X, pady=(10, 0))
        
    def hide_project_message(self):
        """Hide the project message - this is intentionally empty as messages should remain visible
        until the list is cleared or another message replaces it"""
        pass
    
    def apply_project_changes(self):
        """Apply project changes to Claude Desktop configuration"""
        self.apply_claude_config()

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = AIDevToolkitGUI(root)
    root.mainloop()

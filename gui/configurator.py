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
        
        # Variables
        self.claude_desktop_path = tk.StringVar()
        self.config_path = tk.StringVar()
        self.server_enabled = tk.BooleanVar(value=False)
        self.project_dirs = []
        self.project_enabled = {}  # Map of project path to enabled status
        self.server_status = tk.StringVar(value="Stopped")
        self.server_process = None
        self.server_log = tk.StringVar(value="")
        
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
        
        # Claude Desktop Configuration tab (first)
        self.claude_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.claude_frame, text="Claude Desktop Configuration")
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Project Management tab
        self.project_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.project_frame, text="Projects")
        
        # About tab
        self.about_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.about_frame, text="About")
        
        # Setup each tab
        self.setup_claude_tab()
        self.setup_dashboard()
        self.setup_project_tab()
        self.setup_about_tab()
    
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
        
        # Enable server checkbox
        self.enable_server_check = ttk.Checkbutton(server_config_frame, text="Enable AI Dev Toolkit MCP Server", 
                                                 variable=self.server_enabled,
                                                 command=self.toggle_server)
        self.enable_server_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Server status
        self.server_config_status_label = ttk.Label(server_config_frame, text="MCP Server is disabled", style='TLabel')
        self.server_config_status_label.pack(anchor=tk.W, pady=(0, 5))
        
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
                                                  variable=self.project_starter_tools_enabled)
        self.project_starter_check.pack(anchor=tk.W, pady=2)
        
        # AI Librarian checkbox
        self.ai_librarian_check = ttk.Checkbutton(tool_frame, 
                                               text="AI Librarian - Persistent code comprehension system", 
                                               variable=self.ai_librarian_enabled)
        self.ai_librarian_check.pack(anchor=tk.W, pady=2)
        
        # Think Tool checkbox
        think_tool_check = ttk.Checkbutton(tool_frame, 
                                         text="Think Tool - Structured reasoning for complex problems", 
                                         variable=self.think_tool_enabled)
        think_tool_check.pack(anchor=tk.W, pady=2)
        
        # Context Compression checkbox
        self.context_compression_check = ttk.Checkbutton(tool_frame, 
                                                      text="Context Compression - Store and retrieve conversation history (Recommended for longer project conversations)", 
                                                      variable=self.context_compression_enabled)
        self.context_compression_check.pack(anchor=tk.W, pady=2)
        
        # Project directories section
        dirs_frame = ttk.LabelFrame(self.claude_frame, text="Project Directories", padding="10 10 10 10")
        dirs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Directory controls
        dir_controls = ttk.Frame(dirs_frame)
        dir_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(dir_controls, text="Add Directory", command=self.add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dir_controls, text="Project Management", 
                 command=lambda: self.notebook.select(self.project_frame)).pack(side=tk.LEFT)
        
        # Directory label
        dir_label = ttk.Label(dirs_frame, 
                            text="Directories Claude can access:",
                            wraplength=600)
        dir_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Bottom buttons
        button_frame = ttk.Frame(self.claude_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Apply and Exit", command=self.apply_and_exit).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply Changes", command=self.apply_claude_config).pack(side=tk.RIGHT, padx=(5, 0))
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
        
        # Message area for project updates
        self.project_message_var = tk.StringVar()
        self.project_message_label = ttk.Label(projects_frame, textvariable=self.project_message_var, 
                                             style='Info.TLabel', wraplength=600)
        self.project_message_label.pack(fill=tk.X, pady=(10, 0))
        self.project_message_label.pack_forget()  # Hide initially
        
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
        github_link = ttk.Label(links_frame, text="GitHub Repository", 
                              foreground="blue", cursor="hand2")
        github_link.pack(anchor=tk.W, pady=2)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/modelcontextprotocol/python-sdk"))
    
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
            os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Programs/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Roaming/Claude/config.json"),  # Fallback to old name
            # Use normalized path.join for consistent separators
            os.path.join(os.path.expanduser("~/AppData/Roaming/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Local/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Local/Programs/Claude"), "claude_desktop_config.json"),
            os.path.join(os.path.expanduser("~/AppData/Roaming/Claude"), "config.json"),
            # Add potential alternative locations
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
            
            # Now MCP Server Configuration is accessible
            self.enable_server_check.configure(state=tk.NORMAL)
        else:
            self.claude_status_label.config(text="Claude Desktop not found. Please install it first.")
            self.claude_config_status_label.config(text="Claude Desktop not found. Please install it first.")
            
            # Disable MCP Server Configuration
            self.enable_server_check.configure(state=tk.DISABLED)
        
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
            # Now MCP Server Configuration is accessible
            self.enable_server_check.configure(state=tk.NORMAL)
    
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
                print(f"Config file size: {len(config_text)} bytes")
                print(f"First 100 chars: {config_text[:100]}")
                
                if not config_text:
                    print("Config file is empty!")
                    messagebox.showerror("Error", "Config file is empty")
                    return
                    
                config = json.loads(config_text)
            
            # Check if our MCP server is enabled
            print(f"Config keys: {list(config.keys())}")
            
            # Handle both camelCase and snake_case for backward compatibility
            mcp_servers = []
            if "mcp_servers" in config:
                mcp_servers = config.get("mcp_servers", [])
                print(f"Found {len(mcp_servers)} MCP servers in snake_case config")
            elif "mcpServers" in config:
                # Handle camelCase structure
                mcpServers = config.get("mcpServers", {})
                # Convert camelCase structure to expected list format
                if isinstance(mcpServers, dict):
                    mcp_servers = []
                    # If it's a dict with named servers, convert to list format
                    for name, server_config in mcpServers.items():
                        if isinstance(server_config, dict):
                            server_entry = {"name": name}
                            if "url" not in server_config and "command" in server_config:
                                # Local MCP server format
                                server_entry["url"] = "http://localhost:8000"
                            else:
                                server_entry["url"] = server_config.get("url", "")
                            
                            if "allowed_directories" not in server_config and "allowedDirectories" in server_config:
                                server_entry["allowed_directories"] = server_config.get("allowedDirectories", [])
                            else:  
                                server_entry["allowed_directories"] = server_config.get("allowed_directories", [])
                                
                            mcp_servers.append(server_entry)
                    print(f"Converted {len(mcp_servers)} servers from camelCase format")
                elif isinstance(mcpServers, list):
                    # It's already a list, just rename keys if needed
                    for server in mcpServers:
                        if "allowedDirectories" in server and "allowed_directories" not in server:
                            server["allowed_directories"] = server["allowedDirectories"]
                    mcp_servers = mcpServers
                    print(f"Found {len(mcp_servers)} MCP servers in camelCase list format")
            
            print(f"Final MCP servers count: {len(mcp_servers)}")
            
            server_enabled = False
            self.project_dirs = []
            
            for server in mcp_servers:
                print(f"Checking server: {server.get('name')}")
                if server.get("name") == "AI Dev Toolkit":
                    server_enabled = True
                    self.project_dirs = server.get("allowed_directories", [])
                    print(f"Found AI Dev Toolkit server with {len(self.project_dirs)} directories")
                    break
            
            self.server_enabled.set(server_enabled)
            self.update_server_status()
            
            # Initialize project enabled status
            for path in self.project_dirs:
                self.project_enabled[path] = True
            
            # Update directory lists
            self.update_directory_list()
            self.update_projects_list()
            
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {str(je)}")
            messagebox.showerror("Error", f"Failed to parse config file: {str(je)}\n\nThe file may be corrupted or not in JSON format.")
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
    
    def toggle_server(self):
        """Handle enabling/disabling the server"""
        self.update_server_status()
        
        # Update tool selection availability based on server status
        if self.server_enabled.get():
            self.file_system_tools_enabled.set(True)
            self.update_tool_dependencies()
        else:
            # If server is disabled, disable all tool checkboxes
            self.file_system_tools_enabled.set(False)
            self.project_starter_tools_enabled.set(False)
            self.ai_librarian_enabled.set(False)
            self.think_tool_enabled.set(False)
            self.context_compression_enabled.set(False)
            
            # Disable all tool checkboxes except for file system
            self.project_starter_check.configure(state=tk.DISABLED)
            self.ai_librarian_check.configure(state=tk.DISABLED)
            self.context_compression_check.configure(state=tk.DISABLED)
    
    def update_tool_dependencies(self):
        """Update tool dependencies based on file system tools status"""
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
    
    def update_server_status(self):
        """Update the server status label"""
        if self.server_enabled.get():
            self.server_config_status_label.config(text="MCP Server is enabled")
        else:
            self.server_config_status_label.config(text="MCP Server is disabled")
    
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
            # Read current config
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
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
            
            # Filter project directories to only include enabled ones
            enabled_directories = [path for path in self.project_dirs if self.project_enabled.get(path, True)]
            
            # Check if config uses camelCase or snake_case
            uses_camel_case = "mcpServers" in config
            uses_snake_case = "mcp_servers" in config
            
            if uses_camel_case:
                # Handle camelCase format (dict structure)
                if isinstance(config["mcpServers"], dict):
                    # Remove existing AI Dev Toolkit server if present
                    if "AI Dev Toolkit" in config["mcpServers"]:
                        del config["mcpServers"]["AI Dev Toolkit"]
                    
                    # Add our server if enabled
                    if self.server_enabled.get():
                        config["mcpServers"]["AI Dev Toolkit"] = {
                            "url": "http://localhost:8000",
                            "allowedDirectories": enabled_directories,
                            "enabledTools": enabled_tools  # Add enabled tools
                        }
                # Handle camelCase format (list structure)
                elif isinstance(config["mcpServers"], list):
                    # Remove existing AI Dev Toolkit server if present
                    config["mcpServers"] = [s for s in config["mcpServers"] if s.get("name") != "AI Dev Toolkit"]
                    
                    # Add our server if enabled
                    if self.server_enabled.get():
                        config["mcpServers"].append({
                            "name": "AI Dev Toolkit",
                            "url": "http://localhost:8000",
                            "allowedDirectories": enabled_directories,
                            "enabledTools": enabled_tools  # Add enabled tools
                        })
            elif uses_snake_case:
                # Update MCP servers configuration (snake_case)
                mcp_servers = config.get("mcp_servers", [])
                
                # Remove existing AI Dev Toolkit server if present
                mcp_servers = [s for s in mcp_servers if s.get("name") != "AI Dev Toolkit"]
                
                # Add our server if enabled
                if self.server_enabled.get():
                    mcp_servers.append({
                        "name": "AI Dev Toolkit",
                        "url": "http://localhost:8000",
                        "allowed_directories": enabled_directories,
                        "enabled_tools": enabled_tools  # Add enabled tools
                    })
                
                # Update config
                config["mcp_servers"] = mcp_servers
            else:
                # Neither format exists, create new using camelCase (current format)
                config["mcpServers"] = {}
                if self.server_enabled.get():
                    config["mcpServers"]["AI Dev Toolkit"] = {
                        "url": "http://localhost:8000",
                        "allowedDirectories": enabled_directories,
                        "enabledTools": enabled_tools  # Add enabled tools
                    }
            
            # Write config back
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Create .ai_reference directories for enabled projects if AI Librarian is enabled
            if self.server_enabled.get() and self.ai_librarian_enabled.get():
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
            
            # Verify the changes were saved correctly
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    verification_config = json.load(f)
                
                # Check if our changes are present
                verification_passed = False
                if uses_camel_case and "mcpServers" in verification_config:
                    if isinstance(verification_config["mcpServers"], dict):
                        verification_passed = ("AI Dev Toolkit" in verification_config["mcpServers"]) == self.server_enabled.get()
                    elif isinstance(verification_config["mcpServers"], list):
                        server_names = [s.get("name") for s in verification_config["mcpServers"]]
                        verification_passed = ("AI Dev Toolkit" in server_names) == self.server_enabled.get()
                elif uses_snake_case and "mcp_servers" in verification_config:
                    server_names = [s.get("name") for s in verification_config["mcp_servers"]]
                    verification_passed = ("AI Dev Toolkit" in server_names) == self.server_enabled.get()
                
                if verification_passed:
                    messagebox.showinfo("Success", "Configuration updated and verified successfully.\n\nPlease restart Claude Desktop for changes to take effect.")
                else:
                    messagebox.showwarning("Warning", "Configuration was saved, but verification failed.\n\nThe changes may not persist. Please check the file permissions.")
            
            except Exception as e:
                print(f"Verification error: {str(e)}")
                messagebox.showinfo("Success", "Configuration updated.\n\nPlease restart Claude Desktop for changes to take effect.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def apply_and_exit(self):
        """Apply changes and exit the application"""
        self.apply_claude_config()
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
            server_script = os.path.normpath(os.path.join(script_dir, "..", "src", "server.py"))
            
            # Check if the file exists
            if not os.path.exists(server_script):
                messagebox.showerror("Error", f"Server script not found at {server_script}\n\nMake sure you have installed the AI Dev Toolkit correctly.")
                return
            
            # Print status information for debugging
            print(f"Starting server from: {server_script}")
            print(f"Using Python: {sys.executable}")
            
            # Start the server
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
        
        # Auto-hide after 5 seconds
        self.root.after(5000, self.hide_project_message)
    
    def hide_project_message(self):
        """Hide the project message"""
        self.project_message_label.pack_forget()
    
    def apply_project_changes(self):
        """Apply project changes to Claude Desktop configuration"""
        self.apply_claude_config()

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = AIDevToolkitGUI(root)
    root.mainloop()

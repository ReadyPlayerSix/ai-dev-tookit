import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import time
from pathlib import Path

class AIDevToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Dev Toolkit Control Panel")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
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
        
        # Variables
        self.claude_desktop_path = tk.StringVar()
        self.config_path = tk.StringVar()
        self.server_enabled = tk.BooleanVar(value=False)
        self.project_dirs = []
        self.server_status = tk.StringVar(value="Stopped")
        self.server_process = None
        self.server_log = tk.StringVar(value="")
        
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
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Claude Configuration tab
        self.claude_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.claude_frame, text="Claude Desktop")
        
        # Server Management tab
        self.server_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.server_frame, text="Server Management")
        
        # Project Management tab
        self.project_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.project_frame, text="Projects")
        
        # AI Librarian tab
        self.librarian_frame = ttk.Frame(self.notebook, padding="20 20 20 20", style='TFrame')
        self.notebook.add(self.librarian_frame, text="AI Librarian")
        
        # Setup each tab
        self.setup_dashboard()
        self.setup_claude_tab()
        self.setup_server_tab()
        self.setup_project_tab()
        self.setup_librarian_tab()
    
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
        
        ttk.Button(actions_frame, text="Start MCP Server", command=self.start_server).grid(
            row=0, column=0, sticky="ew", pady=5, padx=5)
        
        ttk.Button(actions_frame, text="Stop MCP Server", command=self.stop_server).grid(
            row=1, column=0, sticky="ew", pady=5, padx=5)
        
        ttk.Button(actions_frame, text="Update Claude Config", command=self.apply_claude_config).grid(
            row=2, column=0, sticky="ew", pady=5, padx=5)
        
        ttk.Button(actions_frame, text="Add Project Directory", command=self.add_directory).grid(
            row=3, column=0, sticky="ew", pady=5, padx=5)
        
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
        
        # Project directories section
        dirs_frame = ttk.LabelFrame(self.claude_frame, text="Project Directories", padding="10 10 10 10")
        dirs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Directory controls
        dir_controls = ttk.Frame(dirs_frame)
        dir_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(dir_controls, text="Add Directory", command=self.add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dir_controls, text="Remove Selected", command=self.remove_directory).pack(side=tk.LEFT)
        
        # Directory list
        self.dir_listbox_frame = ttk.Frame(dirs_frame)
        self.dir_listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.dir_listbox = tk.Listbox(self.dir_listbox_frame, height=10)
        self.dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.dir_listbox_frame, orient=tk.VERTICAL, command=self.dir_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dir_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.claude_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Apply Changes", command=self.apply_claude_config).pack(side=tk.RIGHT, padx=(5, 0))
    
    #-----------------------------------------------------
    # Server Management Tab
    #-----------------------------------------------------
    def setup_server_tab(self):
        # Header
        header_label = ttk.Label(self.server_frame, text="MCP Server Management", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Server controls
        controls_frame = ttk.LabelFrame(self.server_frame, text="Server Controls", padding="10 10 10 10")
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status
        status_frame = ttk.Frame(controls_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Server Status:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.server_status_value_label = ttk.Label(status_frame, textvariable=self.server_status, 
                                                 style='Stopped.Status.TLabel')
        self.server_status_value_label.pack(side=tk.LEFT)
        
        # Control buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Start Server", command=self.start_server).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Stop Server", command=self.stop_server).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Restart Server", command=self.restart_server).pack(side=tk.LEFT)
        
        # Server log
        log_frame = ttk.LabelFrame(self.server_frame, text="Server Log", padding="10 10 10 10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.server_log_text = tk.Text(log_frame, height=20, width=80, wrap=tk.WORD)
        self.server_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.server_log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_log_text.config(yscrollcommand=log_scrollbar.set)
        self.server_log_text.insert(tk.END, "Server log will appear here when the server is started.")
        
        # Button to clear log
        ttk.Button(log_frame, text="Clear Log", command=self.clear_server_log).pack(anchor=tk.E, pady=(5, 0))
    
    #-----------------------------------------------------
    # Project Management Tab
    #-----------------------------------------------------
    def setup_project_tab(self):
        # Header
        header_label = ttk.Label(self.project_frame, text="Project Management", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Projects panel
        projects_paned = ttk.PanedWindow(self.project_frame, orient=tk.HORIZONTAL)
        projects_paned.pack(fill=tk.BOTH, expand=True)
        
        # Project list frame
        project_list_frame = ttk.LabelFrame(projects_paned, text="Project Directories", padding="10 10 10 10")
        projects_paned.add(project_list_frame, weight=1)
        
        # Project controls
        proj_controls = ttk.Frame(project_list_frame)
        proj_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(proj_controls, text="Add Project", command=self.add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(proj_controls, text="Remove Project", command=self.remove_directory).pack(side=tk.LEFT)
        
        # Project list
        self.project_listbox_frame = ttk.Frame(project_list_frame)
        self.project_listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.project_listbox = tk.Listbox(self.project_listbox_frame, height=15)
        self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.project_listbox.bind('<<ListboxSelect>>', self.on_project_select)
        
        proj_scrollbar = ttk.Scrollbar(self.project_listbox_frame, orient=tk.VERTICAL, command=self.project_listbox.yview)
        proj_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_listbox.config(yscrollcommand=proj_scrollbar.set)
        
        # Project details frame
        project_details_frame = ttk.LabelFrame(projects_paned, text="Project Details", padding="10 10 10 10")
        projects_paned.add(project_details_frame, weight=2)
        
        # Project info
        self.project_info_frame = ttk.Frame(project_details_frame)
        self.project_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.project_info_frame, text="No project selected", style='TLabel').pack(anchor=tk.W)
        
        # Project actions frame
        actions_frame = ttk.LabelFrame(project_details_frame, text="Actions", padding="10 10 10 10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(actions_frame, text="Initialize AI Librarian", command=self.init_ai_librarian).pack(anchor=tk.W, pady=5)
        ttk.Button(actions_frame, text="Update AI Librarian", command=self.update_ai_librarian).pack(anchor=tk.W, pady=5)
        ttk.Button(actions_frame, text="Open in Explorer", command=self.open_project_in_explorer).pack(anchor=tk.W, pady=5)
        
        # Create new project section
        new_project_frame = ttk.LabelFrame(self.project_frame, text="Create New Project", padding="10 10 10 10")
        new_project_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Project name
        name_frame = ttk.Frame(new_project_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Project Name:", width=15).pack(side=tk.LEFT)
        self.new_project_name = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.new_project_name).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Project type
        type_frame = ttk.Frame(new_project_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Project Type:", width=15).pack(side=tk.LEFT)
        self.new_project_type = tk.StringVar(value="web")
        type_combo = ttk.Combobox(type_frame, textvariable=self.new_project_type, 
                                 values=["web", "cli", "library", "api"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Project location
        location_frame = ttk.Frame(new_project_frame)
        location_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(location_frame, text="Location:", width=15).pack(side=tk.LEFT)
        self.new_project_location = tk.StringVar()
        ttk.Entry(location_frame, textvariable=self.new_project_location).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(location_frame, text="Browse...", command=self.browse_project_location).pack(side=tk.LEFT)
        
        # Create button
        ttk.Button(new_project_frame, text="Create Project", command=self.create_new_project).pack(anchor=tk.E, pady=(10, 0))
    
    #-----------------------------------------------------
    # AI Librarian Tab
    #-----------------------------------------------------
    def setup_librarian_tab(self):
        # Header
        header_label = ttk.Label(self.librarian_frame, text="AI Librarian Management", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Librarian panel
        librarian_paned = ttk.PanedWindow(self.librarian_frame, orient=tk.HORIZONTAL)
        librarian_paned.pack(fill=tk.BOTH, expand=True)
        
        # Project list frame
        lib_projects_frame = ttk.LabelFrame(librarian_paned, text="Projects", padding="10 10 10 10")
        librarian_paned.add(lib_projects_frame, weight=1)
        
        # Project list
        self.lib_projects_listbox_frame = ttk.Frame(lib_projects_frame)
        self.lib_projects_listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.lib_projects_listbox = tk.Listbox(self.lib_projects_listbox_frame, height=15)
        self.lib_projects_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lib_projects_listbox.bind('<<ListboxSelect>>', self.on_lib_project_select)
        
        lib_proj_scrollbar = ttk.Scrollbar(self.lib_projects_listbox_frame, orient=tk.VERTICAL, 
                                          command=self.lib_projects_listbox.yview)
        lib_proj_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lib_projects_listbox.config(yscrollcommand=lib_proj_scrollbar.set)
        
        # Librarian details frame
        lib_details_frame = ttk.LabelFrame(librarian_paned, text="Librarian Details", padding="10 10 10 10")
        librarian_paned.add(lib_details_frame, weight=2)
        
        # Librarian info
        self.lib_info_frame = ttk.Frame(lib_details_frame)
        self.lib_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.lib_info_frame, text="No project selected", style='TLabel').pack(anchor=tk.W)
        
        # Librarian actions frame
        lib_actions_frame = ttk.LabelFrame(lib_details_frame, text="Actions", padding="10 10 10 10")
        lib_actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(lib_actions_frame, text="Initialize AI Librarian", command=self.init_ai_librarian_from_lib).pack(anchor=tk.W, pady=5)
        ttk.Button(lib_actions_frame, text="Update AI Librarian", command=self.update_ai_librarian_from_lib).pack(anchor=tk.W, pady=5)
        ttk.Button(lib_actions_frame, text="View Component Registry", command=self.view_component_registry).pack(anchor=tk.W, pady=5)
        
        # Component details
        self.lib_components_frame = ttk.LabelFrame(lib_details_frame, text="Components", padding="10 10 10 10")
        self.lib_components_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Components list
        self.components_listbox = tk.Listbox(self.lib_components_frame, height=10)
        self.components_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        components_scrollbar = ttk.Scrollbar(self.lib_components_frame, orient=tk.VERTICAL, 
                                           command=self.components_listbox.yview)
        components_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.components_listbox.config(yscrollcommand=components_scrollbar.set)
    
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
            "C:/Program Files (x86)/Claude"
        ]
        
        # Common configuration paths
        possible_config_paths = [
            os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Local/Programs/Claude/claude_desktop_config.json"),
            os.path.expanduser("~/AppData/Roaming/Claude/config.json")  # Fallback to old name
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
                if os.path.exists(os.path.join(path, "Claude.exe")):
                    self.claude_desktop_path.set(path)
                    found_installation = True
                    print(f"\nFound Claude Desktop installation at: {path}")
                    break
        
        # Now try to find the config file
        for config_path in possible_config_paths:
            if os.path.exists(config_path):
                self.config_path.set(config_path)
                found_config = True
                print(f"Found Claude Desktop config at: {config_path}")
                break
        
        # Update UI based on what we found
        if found_installation and found_config:
            self.claude_status_label.config(text=f"Claude Desktop: Installed")
            self.claude_config_status_label.config(text=f"Config found: {os.path.basename(self.config_path.get())}")
        elif found_installation:
            self.claude_status_label.config(text=f"Claude Desktop: Installed")
            self.claude_config_status_label.config(text="Config file not found. Please browse for it manually.")
        else:
            self.claude_status_label.config(text="Claude Desktop not found. Please install it first.")
            self.claude_config_status_label.config(text="Claude Desktop not found. Please install it first.")
        
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
    
    def load_config(self):
        """Load current configuration from config file"""
        config_path = self.config_path.get()
        if not config_path or not os.path.exists(config_path):
            return
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if our MCP server is enabled
            mcp_servers = config.get("mcp_servers", [])
            server_enabled = False
            self.project_dirs = []
            
            for server in mcp_servers:
                if server.get("name") == "AI Dev Toolkit":
                    server_enabled = True
                    self.project_dirs = server.get("allowed_directories", [])
                    break
            
            self.server_enabled.set(server_enabled)
            self.update_server_status()
            
            # Update directory list
            self.update_directory_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
    
    def toggle_server(self):
        """Handle enabling/disabling the server"""
        self.update_server_status()
    
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
                self.update_directory_list()
    
    def remove_directory(self):
        """Remove selected directory from the list"""
        selection = self.dir_listbox.curselection()
        if selection:
            index = selection[0]
            del self.project_dirs[index]
            self.update_directory_list()
    
    def update_directory_list(self):
        """Update the directory listbox"""
        self.dir_listbox.delete(0, tk.END)
        self.project_listbox.delete(0, tk.END)
        self.lib_projects_listbox.delete(0, tk.END)
        
        for directory in self.project_dirs:
            self.dir_listbox.insert(tk.END, directory)
            self.project_listbox.insert(tk.END, directory)
            self.lib_projects_listbox.insert(tk.END, directory)
    
    def apply_claude_config(self):
        """Save changes to the config file"""
        config_path = self.config_path.get()
        if not config_path:
            messagebox.showerror("Error", "Please select Claude Desktop configuration file")
            return
        
        try:
            # Read current config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update MCP servers configuration
            mcp_servers = config.get("mcp_servers", [])
            
            # Remove existing AI Dev Toolkit server if present
            mcp_servers = [s for s in mcp_servers if s.get("name") != "AI Dev Toolkit"]
            
            # Add our server if enabled
            if self.server_enabled.get():
                mcp_servers.append({
                    "name": "AI Dev Toolkit",
                    "url": "http://localhost:8000",
                    "allowed_directories": self.project_dirs
                })
            
            # Update config
            config["mcp_servers"] = mcp_servers
            
            # Write config back
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", "Configuration updated successfully.\n\nPlease restart Claude Desktop for changes to take effect.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    #-----------------------------------------------------
    # Server Management Functions
    #-----------------------------------------------------
    def check_server_status(self):
        """Check if the MCP server is running"""
        # Simple check - in a production app we'd do proper process detection
        # This is just a placeholder implementation
        if self.server_process and self.server_process.poll() is None:
            self.server_status.set("Running")
            self.server_status_value_label.configure(style='Running.Status.TLabel')
            self.server_status_label.configure(style='Running.Status.TLabel')
            self.server_status_label.configure(text="MCP Server: Running")
        else:
            self.server_status.set("Stopped")
            self.server_status_value_label.configure(style='Stopped.Status.TLabel')
            self.server_status_label.configure(style='Stopped.Status.TLabel')
            self.server_status_label.configure(text="MCP Server: Stopped")
        
        # Schedule next check
        self.root.after(1000, self.check_server_status)
    
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
            self.server_status_value_label.configure(style='Warning.Status.TLabel')
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
    
    def restart_server(self):
        """Restart the MCP server"""
        self.stop_server()
        # Wait a moment to ensure the server is fully stopped
        self.root.after(1000, self.start_server)
    
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
        # Add to server tab log
        self.server_log_text.config(state=tk.NORMAL)
        self.server_log_text.insert(tk.END, line + "\n")
        self.server_log_text.see(tk.END)
        self.server_log_text.config(state=tk.DISABLED)
        
        # Add to dashboard log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_server_log(self):
        """Clear the server log"""
        self.server_log_text.config(state=tk.NORMAL)
        self.server_log_text.delete(1.0, tk.END)
        self.server_log_text.config(state=tk.DISABLED)
    
    #-----------------------------------------------------
    # Project Management Functions
    #-----------------------------------------------------
    def on_project_select(self, event):
        """Handle project selection in the projects tab"""
        selection = self.project_listbox.curselection()
        if not selection:
            return
        
        # Get the selected project path
        index = selection[0]
        project_path = self.project_dirs[index]
        
        # Update project info display
        for widget in self.project_info_frame.winfo_children():
            widget.destroy()
        
        # Show project details
        ttk.Label(self.project_info_frame, text=f"Project Path: {project_path}", style='TLabel').pack(anchor=tk.W)
        
        # Check if AI Librarian is initialized
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if os.path.exists(ai_ref_path):
            ttk.Label(self.project_info_frame, text="AI Librarian: Initialized", style='TLabel').pack(anchor=tk.W, pady=(5, 0))
            
            # Try to get component count
            component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
            if os.path.exists(component_registry_path):
                try:
                    with open(component_registry_path, 'r') as f:
                        registry = json.load(f)
                    component_count = len(registry.get("components", {}))
                    ttk.Label(self.project_info_frame, text=f"Registered Components: {component_count}", 
                            style='TLabel').pack(anchor=tk.W)
                except:
                    pass
        else:
            ttk.Label(self.project_info_frame, text="AI Librarian: Not initialized", style='TLabel').pack(anchor=tk.W, pady=(5, 0))
    
    def init_ai_librarian(self):
        """Initialize AI Librarian for the selected project"""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showinfo("AI Librarian", "Please select a project first")
            return
        
        # Get the selected project path
        index = selection[0]
        project_path = self.project_dirs[index]
        
        # Check if AI Librarian already exists
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if os.path.exists(ai_ref_path):
            response = messagebox.askyesno("AI Librarian", 
                                         "AI Librarian is already initialized for this project. Reinitialize?")
            if not response:
                return
        
        # TODO: Actually initialize the librarian
        # For now, let's simulate it
        messagebox.showinfo("AI Librarian", f"Initializing AI Librarian for {project_path}\n\n" +
                          "Please start the MCP server and use the initialize_librarian tool in Claude to complete setup.")
    
    def update_ai_librarian(self):
        """Update AI Librarian for the selected project"""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showinfo("AI Librarian", "Please select a project first")
            return
        
        # Get the selected project path
        index = selection[0]
        project_path = self.project_dirs[index]
        
        # Check if AI Librarian exists
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            messagebox.showinfo("AI Librarian", "AI Librarian is not initialized for this project. " +
                              "Please initialize it first.")
            return
        
        # TODO: Actually update the librarian
        # For now, let's simulate it
        messagebox.showinfo("AI Librarian", f"Updating AI Librarian for {project_path}\n\n" +
                          "Please start the MCP server and use the generate_librarian tool in Claude to update.")
    
    def open_project_in_explorer(self):
        """Open the selected project in file explorer"""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showinfo("Project", "Please select a project first")
            return
        
        # Get the selected project path
        index = selection[0]
        project_path = self.project_dirs[index]
        
        # Open in explorer
        if os.path.exists(project_path):
            os.startfile(project_path)
    
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
            
            # TODO: Implement actual project creation
            # For now, let's just create some directories
            os.makedirs(os.path.join(project_dir, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_dir, "tests"), exist_ok=True)
            
            # Create a simple README
            with open(os.path.join(project_dir, "README.md"), 'w') as f:
                f.write(f"# {project_name}\n\nA {project_type} project.\n")
            
            # Add to project directories
            if project_dir not in self.project_dirs:
                self.project_dirs.append(project_dir)
                self.update_directory_list()
            
            messagebox.showinfo("Project Created", f"Project {project_name} created at {project_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
    
    #-----------------------------------------------------
    # AI Librarian Tab Functions
    #-----------------------------------------------------
    def on_lib_project_select(self, event):
        """Handle project selection in the librarian tab"""
        selection = self.lib_projects_listbox.curselection()
        if not selection:
            return
        
        # Get the selected project path
        index = selection[0]
        project_path = self.project_dirs[index]
        
        # Update librarian info display
        for widget in self.lib_info_frame.winfo_children():
            widget.destroy()
        
        # Show project details
        ttk.Label(self.lib_info_frame, text=f"Project Path: {project_path}", style='TLabel').pack(anchor=tk.W)
        
        # Check if AI Librarian is initialized
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if os.path.exists(ai_ref_path):
            ttk.Label(self.lib_info_frame, text="AI Librarian: Initialized", style='TLabel').pack(anchor=tk.W, pady=(5, 0))
            
            # Try to get component registry info
            self.components_listbox.delete(0, tk.END)
            component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
            if os.path.exists(component_registry_path):
                try:
                    with open(component_registry_path, 'r') as f:
                        registry = json.load(f)
                    component_count = len(registry.get("components", {}))
                    ttk.Label(self.lib_info_frame, text=f"Registered Components: {component_count}", 
                            style='TLabel').pack(anchor=tk.W)
                    
                    # Display components
                    for component_name in registry.get("components", {}):
                        self.components_listbox.insert(tk.END, component_name)
                except:
                    pass
        else:
            ttk.Label(self.lib_info_frame, text="AI Librarian: Not initialized", style='TLabel').pack(anchor=tk.W, pady=(5, 0))
    
    def init_ai_librarian_from_lib(self):
        """Initialize AI Librarian from the librarian tab"""
        selection = self.lib_projects_listbox.curselection()
        if not selection:
            messagebox.showinfo("AI Librarian", "Please select a project first")
            return
        
        self.init_ai_librarian()
    
    def update_ai_librarian_from_lib(self):
        """Update AI Librarian from the librarian tab"""
        selection = self.lib_projects_listbox.curselection()
        if not selection:
            messagebox.showinfo("AI Librarian", "Please select a project first")
            return
        
        self.update_ai_librarian()
    
    def view_component_registry(self):
        """View the component registry in detail"""
        selection = self.lib_projects_listbox.curselection()
        if not selection:
            messagebox.showinfo("AI Librarian", "Please select a project first")
            return
        
        # Get the selected project path
        index = selection[0]
        project_path = self.project_dirs[index]
        
        # Check if AI Librarian exists
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            messagebox.showinfo("AI Librarian", "AI Librarian is not initialized for this project. " +
                              "Please initialize it first.")
            return
        
        # Check for component registry
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        if not os.path.exists(component_registry_path):
            messagebox.showinfo("AI Librarian", "Component registry not found. Please update the AI Librarian first.")
            return
        
        # Open component registry viewer
        try:
            with open(component_registry_path, 'r') as f:
                registry = json.load(f)
            
            # Create a viewer window
            viewer = tk.Toplevel(self.root)
            viewer.title(f"Component Registry - {os.path.basename(project_path)}")
            viewer.geometry("800x600")
            
            # Create a text widget to display the JSON
            text = tk.Text(viewer, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True)
            
            # Add a scrollbar
            scrollbar = ttk.Scrollbar(text, orient=tk.VERTICAL, command=text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text.config(yscrollcommand=scrollbar.set)
            
            # Insert formatted JSON
            formatted_json = json.dumps(registry, indent=2)
            text.insert(tk.END, formatted_json)
            
            # Make it read-only
            text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view component registry: {str(e)}")

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = AIDevToolkitGUI(root)
    root.mainloop()

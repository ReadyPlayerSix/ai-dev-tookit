import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess
import sys

class AIDevToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Dev Toolkit Settings")
        self.root.geometry("750x550")
        self.root.resizable(True, True)
        
        # Set theme and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TLabel', font=('Segoe UI', 10), background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), background='#f0f0f0')
        
        # Variables
        self.claude_desktop_path = tk.StringVar()
        self.config_path = tk.StringVar()
        self.server_enabled = tk.BooleanVar(value=False)
        self.project_dirs = []
        
        # Build UI
        self.create_widgets()
        
        # Initial checks
        self.detect_claude_desktop()
        self.load_config()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="AI Dev Toolkit Settings", style='Header.TLabel')
        header_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Claude Desktop section
        claude_frame = ttk.LabelFrame(main_frame, text="Claude Desktop", padding="10 10 10 10")
        claude_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Claude Desktop status
        self.claude_status_label = ttk.Label(claude_frame, text="Checking Claude Desktop installation...", style='TLabel')
        self.claude_status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Claude Desktop path
        path_frame = ttk.Frame(claude_frame)
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(path_frame, text="Config Path:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.config_path, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse...", command=self.browse_config).pack(side=tk.LEFT)
        
        # MCP Server section
        server_frame = ttk.LabelFrame(main_frame, text="MCP Server Configuration", padding="10 10 10 10")
        server_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Enable server checkbox
        self.enable_server_check = ttk.Checkbutton(server_frame, text="Enable AI Dev Toolkit MCP Server", 
                                                 variable=self.server_enabled,
                                                 command=self.toggle_server)
        self.enable_server_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Server status
        self.server_status_label = ttk.Label(server_frame, text="MCP Server is disabled", style='TLabel')
        self.server_status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Project directories section
        dirs_frame = ttk.LabelFrame(main_frame, text="Project Directories", padding="10 10 10 10")
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
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Close", command=self.root.destroy).pack(side=tk.RIGHT)
    
    def detect_claude_desktop(self):
        """Try to locate Claude Desktop installation"""
        # Common installation paths
        possible_paths = [
            os.path.expanduser("~/AppData/Local/Programs/Claude"),
            os.path.expanduser("~/AppData/Local/Claude"),
            os.path.expanduser("~/AppData/Roaming/Claude"),
            "C:/Program Files/Claude",
            "C:/Program Files (x86)/Claude"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Look for executable or config
                if os.path.exists(os.path.join(path, "Claude.exe")):
                    self.claude_desktop_path.set(path)
                    self.claude_status_label.config(text="Claude Desktop is installed")
                    
                    # Try to find config in subdirectories
                    for root, dirs, files in os.walk(path):
                        if "claude_desktop_config.json" in files:
                            config_path = os.path.join(root, "claude_desktop_config.json")
                            self.config_path.set(config_path)
                            return
        
        # Not found
        self.claude_status_label.config(text="Claude Desktop not found. Please install it first.")
    
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
            self.server_status_label.config(text="MCP Server is enabled")
        else:
            self.server_status_label.config(text="MCP Server is disabled")
    
    def add_directory(self):
        """Open directory selection dialog to add a project directory"""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
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
        for directory in self.project_dirs:
            self.dir_listbox.insert(tk.END, directory)
    
    def apply_changes(self):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = AIDevToolkitGUI(root)
    root.mainloop()
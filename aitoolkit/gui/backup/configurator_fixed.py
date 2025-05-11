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
            fixed_text = re.sub(r',\s*([\]\}])', r'\1', config_text)
            
            try:
                existing_config = json.loads(fixed_text)
                print("Successfully fixed and loaded JSON")
            except json.JSONDecodeError:
                # Create backup of the original file
                import shutil
                backup_path = config_path + ".backup"
                shutil.copyfile(config_path, backup_path)
                print(f"Created backup at {backup_path}")
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
        if self.ai_librarian_enabled.get():
            enabled_tools.append("ai_librarian")
        if self.context_compression_enabled.get():
            enabled_tools.append("context_compression")
        
        # Determine server status based on tools and servers
        server_enabled = len(enabled_tools) > 0 or self.ai_librarian_server_enabled.get() or self.file_system_server_enabled.get()
        
        # Filter project directories to only include enabled ones
        enabled_directories = [path for path in self.project_dirs if self.project_enabled.get(path, True)]
        
        # Get absolute path to this script's directory for Python configuration
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_dir = os.path.dirname(os.path.dirname(script_dir))
        
        # Remove existing AI Dev Toolkit and AI Librarian servers if present
        toolkit_server_names = ["AI Dev Toolkit", "aidevtoolkit", "ai-dev-toolkit", "file-system-tools"]
        librarian_server_names = ["AI Librarian", "ailibrarian", "ai-librarian"]
        
        for name in toolkit_server_names + librarian_server_names:
            if name in existing_config["mcpServers"]:
                del existing_config["mcpServers"][name]
        
        # File System Tools Server Configuration
        if self.file_system_server_enabled.get():
            toolkit_server_name = "file-system-tools"
            
            # Path to the FileSystem Tools server
            filesystem_server_path = os.path.join(repo_dir, "src", "mcp", "filesystem_server.py")
            
            # Create configuration
            toolkit_config = {
                "command": "python",
                "args": [
                    filesystem_server_path
                ],
                "env": {}
            }
            
            # Add directories as environment variables
            if enabled_directories:
                toolkit_config["env"]["FILE_SYSTEM_ALLOWED_DIRS"] = ",".join(enabled_directories)
            
            # Add the File System Tools server
            existing_config["mcpServers"][toolkit_server_name] = toolkit_config
        
        # AI Librarian Server Configuration
        if self.ai_librarian_server_enabled.get():
            librarian_server_name = "ai-librarian"
            
            # Path to the AI Librarian server
            librarian_server_path = os.path.join(repo_dir, "aitoolkit", "librarian", "server.py")
            
            # Create configuration
            librarian_config = {
                "command": "python",
                "args": [
                    librarian_server_path
                ],
                "env": {}
            }
            
            # Add directories as environment variables
            if enabled_directories:
                librarian_config["env"]["AI_LIBRARIAN_ALLOWED_DIRS"] = ",".join(enabled_directories)
            
            # Add the AI Librarian server
            existing_config["mcpServers"][librarian_server_name] = librarian_config

        # Write config back with careful handling of JSON format
        with open(config_path, 'w', encoding='utf-8') as f:
            # Use a compact JSON format to avoid any formatting issues
            json_str = json.dumps(existing_config, indent=2, ensure_ascii=False)
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
                            f.write("# AI Librarian\n\nThis directory contains the AI Librarian context for this project.\n\n## Features\n\n- Analyzes code structure and tracks components\n- Runs startup checks to verify tool functionality\n- Maintains context memory across conversations with Claude\n- Monitors project in real-time to detect code changes")
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
        traceback.print_exc()
        messagebox.showerror("Error", f"Failed to save config: {str(e)}")

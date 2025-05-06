"""
Helper functions for the AI Dev Toolkit.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

def ensure_dir_exists(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: The directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)

def format_path(path: str) -> str:
    """
    Format a path with consistent separators.
    
    Args:
        path: The path to format
        
    Returns:
        Formatted path
    """
    return str(Path(path))

def read_json_file(path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        Parsed JSON content
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {path}: {e}")
        return {}

def write_json_file(path: str, data: Dict[str, Any]) -> bool:
    """
    Write data to a JSON file.
    
    Args:
        path: Path to the JSON file
        data: Data to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing JSON file {path}: {e}")
        return False

def get_file_extension(path: str) -> str:
    """
    Get the file extension from a path.
    
    Args:
        path: The file path
        
    Returns:
        The file extension (with dot)
    """
    return os.path.splitext(path)[1]

def is_text_file(path: str) -> bool:
    """
    Check if a file is a text file based on its extension.
    
    Args:
        path: The file path
        
    Returns:
        True if the file is a text file, False otherwise
    """
    text_extensions = [
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
        '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bat',
        '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rs', '.rb', '.php'
    ]
    
    return get_file_extension(path).lower() in text_extensions

def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to a human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size
    """
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            break
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} {unit}" if unit != 'bytes' else f"{size_bytes} bytes"

def create_file_from_template(template: str, output_path: str, replacements: Dict[str, str]) -> bool:
    """
    Create a file from a template with replacements.
    
    Args:
        template: Template content
        output_path: Path to write the file
        replacements: Dictionary of replacements (key is replaced with value)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error creating file from template {output_path}: {e}")
        return False

def get_project_type_from_extensions(directory: str) -> str:
    """
    Try to determine the project type from file extensions in a directory.
    
    Args:
        directory: Directory to analyze
        
    Returns:
        Project type guess ("web", "python", "java", etc.) or "unknown"
    """
    extensions = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common excluded directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                  d not in ['venv', 'env', 'node_modules', '__pycache__', '.git']]
        
        for file in files:
            ext = get_file_extension(file).lower()
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
    
    # Logic to determine project type
    if '.py' in extensions and extensions['.py'] > 5:
        if os.path.exists(os.path.join(directory, 'manage.py')):
            return "django"
        if os.path.exists(os.path.join(directory, 'app.py')) or os.path.exists(os.path.join(directory, 'wsgi.py')):
            return "flask"
        return "python"
    
    if '.js' in extensions and '.html' in extensions and '.css' in extensions:
        if os.path.exists(os.path.join(directory, 'package.json')):
            with open(os.path.join(directory, 'package.json'), 'r') as f:
                try:
                    data = json.load(f)
                    if 'react' in str(data.get('dependencies', {})):
                        return "react"
                    if 'vue' in str(data.get('dependencies', {})):
                        return "vue"
                    if 'angular' in str(data.get('dependencies', {})):
                        return "angular"
                except:
                    pass
        return "web"
    
    if '.java' in extensions:
        if os.path.exists(os.path.join(directory, 'pom.xml')):
            return "maven"
        if os.path.exists(os.path.join(directory, 'build.gradle')):
            return "gradle"
        return "java"
    
    if '.go' in extensions:
        return "go"
    
    if '.rs' in extensions:
        return "rust"
    
    if '.rb' in extensions:
        return "ruby"
    
    if '.php' in extensions:
        return "php"
    
    if '.cs' in extensions:
        return "csharp"
    
    return "unknown"

def search_file_content(directory: str, text: str, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for text in file contents.
    
    Args:
        directory: Directory to search in
        text: Text to search for
        file_pattern: Optional pattern to filter files
        
    Returns:
        List of matching results with context
    """
    results = []
    search_text = text.lower()
    
    # Determine which extensions to search based on file_pattern
    extensions = []
    if file_pattern:
        if "*." in file_pattern:
            ext = file_pattern.split("*.")[-1]
            extensions.append(f".{ext}")
        elif "." in file_pattern:
            extensions.append(file_pattern)
    
    # Function to check if a file should be searched
    def should_search_file(filename):
        if not extensions:
            return is_text_file(filename)
        return any(filename.endswith(ext) for ext in extensions)
    
    # Walk the directory tree
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common excluded directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                  d not in ['venv', 'env', 'node_modules', '__pycache__', '.git']]
        
        # Search files
        for filename in files:
            if should_search_file(filename):
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, directory)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Search for the text
                    if search_text in content.lower():
                        # Find matching lines with context
                        lines = content.splitlines()
                        matches = []
                        
                        for i, line in enumerate(lines):
                            if search_text in line.lower():
                                # Get context (3 lines before and after)
                                start = max(0, i - 3)
                                end = min(len(lines), i + 4)
                                
                                # Format the context
                                context = []
                                for j in range(start, end):
                                    context.append({
                                        "line": j + 1,
                                        "text": lines[j],
                                        "match": j == i
                                    })
                                
                                matches.append(context)
                        
                        if matches:
                            results.append({
                                "file": rel_path,
                                "matches": matches
                            })
                except UnicodeDecodeError:
                    # Skip binary files
                    pass
                except Exception as e:
                    results.append({
                        "file": rel_path,
                        "error": str(e)
                    })
    
    return results

if __name__ == "__main__":
    # Example usage
    print(format_size(1024 * 1024))  # 1.00 MB

"""
To-Do List Manager for AI Librarian

This module provides tools for managing a persistent to-do list
that remembers tasks across conversations.
"""

import os
import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Union


class TodoManager:
    """Manages the AI Librarian to-do list."""

    def __init__(self, project_path: str):
        """
        Initialize the TodoManager for a specific project.
        
        Args:
            project_path: Path to the project root
        """
        self.project_path = os.path.abspath(project_path)
        self.ai_ref_path = os.path.join(self.project_path, ".ai_reference")
        self.todos_dir = os.path.join(self.ai_ref_path, "todos")
        self.todo_file = os.path.join(self.todos_dir, "todo_list.json")
        
        # Ensure directories exist
        os.makedirs(self.todos_dir, exist_ok=True)
        
        # Initialize empty to-do list if it doesn't exist
        if not os.path.exists(self.todo_file):
            self._init_todo_file()
    
    def _init_todo_file(self) -> None:
        """Initialize an empty to-do list file."""
        empty_todo_list = {
            "version": "0.1.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "items": []
        }
        
        with open(self.todo_file, 'w', encoding='utf-8') as f:
            json.dump(empty_todo_list, f, indent=2)
    
    def _load_todos(self) -> Dict[str, Any]:
        """
        Load the to-do list from file.
        
        Returns:
            Dict containing the to-do list
        """
        try:
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file is missing or corrupted, create a new one
            self._init_todo_file()
            return self._load_todos()
    
    def _save_todos(self, todos: Dict[str, Any]) -> None:
        """
        Save the to-do list to file.
        
        Args:
            todos: Dict containing the to-do list
        """
        # Update the last_updated timestamp
        todos["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(self.todo_file, 'w', encoding='utf-8') as f:
            json.dump(todos, f, indent=2)
    
    def add_todo(self, title: str, description: str = "", priority: str = "medium", 
                 tags: List[str] = None, subtasks: List[Dict[str, str]] = None,
                 context_prompt: str = None) -> str:
        """
        Add a new to-do item.
        
        Args:
            title: Title of the to-do item
            description: Detailed description
            priority: Priority level (low, medium, high)
            tags: List of tags
            subtasks: List of subtask dictionaries with title and status
            context_prompt: Optional prompt for Claude to retrieve context
            
        Returns:
            ID of the created to-do item
        """
        todos = self._load_todos()
        
        # Generate a unique ID
        todo_id = f"todo-{uuid.uuid4().hex[:8]}"
        
        # Check if this is a "quick view" todo (with long description but no context prompt)
        if len(description) > 250 and not context_prompt:
            # Create a context prompt from the description
            context_prompt = f"Claude, use current context. Ask user about '{title}' details."
            
            # Store a concise version of the description
            # Get the first paragraph or first two sentences
            summary = ""
            if "\n\n" in description:
                summary = description.split("\n\n")[0].strip()
            else:
                sentences = description.split(". ")
                if len(sentences) > 1:
                    summary = ". ".join(sentences[:2]) + "."
                else:
                    summary = sentences[0]
                    
            # Keep summary under 250 characters
            if len(summary) > 250:
                summary = summary[:247] + "..."
                
            # Store the full description in a separate field for reference
            full_description = description
            # Use the summary as the visible description
            description = summary
        else:
            full_description = None
        
        # Create the new to-do item
        new_todo = {
            "id": todo_id,
            "title": title,
            "description": description,
            "status": "active",
            "priority": priority,
            "tags": tags or [],
            "created": datetime.datetime.now().isoformat(),
            "subtasks": [],
            "context_prompt": context_prompt,
            "full_description": full_description
        }
        
        # Add subtasks if provided
        if subtasks:
            for i, subtask in enumerate(subtasks):
                subtask_id = f"subtask-{uuid.uuid4().hex[:8]}"
                new_todo["subtasks"].append({
                    "id": subtask_id,
                    "title": subtask.get("title", f"Subtask {i+1}"),
                    "status": subtask.get("status", "active")
                })
        
        # Add to the list
        todos["items"].append(new_todo)
        
        # Save the updated list
        self._save_todos(todos)
        
        return todo_id
    
    def update_todo(self, todo_id: str, **kwargs) -> bool:
        """
        Update an existing to-do item.
        
        Args:
            todo_id: ID of the to-do item to update
            **kwargs: Fields to update
            
        Returns:
            True if successful, False if not found
        """
        todos = self._load_todos()
        
        # Find the to-do item
        for i, todo in enumerate(todos["items"]):
            if todo["id"] == todo_id:
                # Update the specified fields
                for key, value in kwargs.items():
                    if key in todo:
                        todo[key] = value
                
                # Save the updated list
                self._save_todos(todos)
                return True
        
        return False
    
    def update_subtask(self, todo_id: str, subtask_id: str, 
                      title: Optional[str] = None, status: Optional[str] = None) -> bool:
        """
        Update a subtask.
        
        Args:
            todo_id: ID of the parent to-do item
            subtask_id: ID of the subtask to update
            title: New title (if None, don't update)
            status: New status (if None, don't update)
            
        Returns:
            True if successful, False if not found
        """
        todos = self._load_todos()
        
        # Find the to-do item
        for todo in todos["items"]:
            if todo["id"] == todo_id:
                # Find the subtask
                for subtask in todo.get("subtasks", []):
                    if subtask["id"] == subtask_id:
                        # Update the specified fields
                        if title is not None:
                            subtask["title"] = title
                        if status is not None:
                            subtask["status"] = status
                        
                        # Save the updated list
                        self._save_todos(todos)
                        return True
        
        return False
    
    def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a to-do item.
        
        Args:
            todo_id: ID of the to-do item to delete
            
        Returns:
            True if successful, False if not found
        """
        todos = self._load_todos()
        
        # Find the to-do item
        for i, todo in enumerate(todos["items"]):
            if todo["id"] == todo_id:
                # Remove the item
                todos["items"].pop(i)
                
                # Save the updated list
                self._save_todos(todos)
                return True
        
        return False
    
    def get_todos(self, status: Optional[str] = None, 
                 priority: Optional[str] = None, 
                 tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get to-do items with optional filtering.
        
        Args:
            status: Filter by status (active, completed, etc.)
            priority: Filter by priority (low, medium, high)
            tag: Filter by tag
            
        Returns:
            List of matching to-do items
        """
        todos = self._load_todos()
        
        # Start with all items
        result = todos["items"]
        
        # Apply filters
        if status:
            result = [todo for todo in result if todo["status"] == status]
        
        if priority:
            result = [todo for todo in result if todo["priority"] == priority]
        
        if tag:
            result = [todo for todo in result if tag in todo["tags"]]
        
        return result

    def get_todo(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific to-do item by ID.
        
        Args:
            todo_id: ID of the to-do item
            
        Returns:
            The to-do item, or None if not found
        """
        todos = self._load_todos()
        
        # Find the to-do item
        for todo in todos["items"]:
            if todo["id"] == todo_id:
                return todo
        
        return None
    
    def search_todos(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for to-do items by text in title or description.
        
        Args:
            query: Search text
            
        Returns:
            List of matching to-do items
        """
        todos = self._load_todos()
        query = query.lower()
        
        # Search in title and description
        result = []
        for todo in todos["items"]:
            if (query in todo["title"].lower() or 
                query in todo["description"].lower()):
                result.append(todo)
        
        return result
    
    def add_subtask(self, todo_id: str, title: str) -> Optional[str]:
        """
        Add a subtask to an existing to-do item.
        
        Args:
            todo_id: ID of the parent to-do item
            title: Title of the subtask
            
        Returns:
            ID of the created subtask, or None if parent not found
        """
        todos = self._load_todos()
        
        # Find the to-do item
        for todo in todos["items"]:
            if todo["id"] == todo_id:
                # Generate a unique ID
                subtask_id = f"subtask-{uuid.uuid4().hex[:8]}"
                
                # Create the subtask
                subtask = {
                    "id": subtask_id,
                    "title": title,
                    "status": "active"
                }
                
                # Add to the list
                if "subtasks" not in todo:
                    todo["subtasks"] = []
                
                todo["subtasks"].append(subtask)
                
                # Save the updated list
                self._save_todos(todos)
                
                return subtask_id
        
        return None
    
    def delete_subtask(self, todo_id: str, subtask_id: str) -> bool:
        """
        Delete a subtask.
        
        Args:
            todo_id: ID of the parent to-do item
            subtask_id: ID of the subtask to delete
            
        Returns:
            True if successful, False if not found
        """
        todos = self._load_todos()
        
        # Find the to-do item
        for todo in todos["items"]:
            if todo["id"] == todo_id and "subtasks" in todo:
                # Find the subtask
                for i, subtask in enumerate(todo["subtasks"]):
                    if subtask["id"] == subtask_id:
                        # Remove the subtask
                        todo["subtasks"].pop(i)
                        
                        # Save the updated list
                        self._save_todos(todos)
                        return True
        
        return False

    def infer_todo_item(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Infer a to-do item from text by looking for common patterns.
        
        Args:
            text: Text to analyze for to-do items
            
        Returns:
            Dict with title and optionally description, or None if no to-do found
        """
        # Common markers for to-dos
        markers = [
            "todo:", "to-do:", "task:", "don't forget", "don't forget to", 
            "remind me to", "need to", "should", "must", "have to",
            "remember to", "later,", "later:", "note:", "remember:",
            "i'll need to", "we'll need to"
        ]
        
        text = text.lower()
        result = None
        
        # Check for markers
        for marker in markers:
            if marker in text:
                # Extract the part after the marker
                parts = text.split(marker, 1)
                if len(parts) > 1:
                    todo_text = parts[1].strip()
                    
                    # Split into title and description if there's a newline or period
                    title_parts = todo_text.split("\n", 1)
                    if len(title_parts) > 1:
                        title = title_parts[0].strip()
                        description = title_parts[1].strip()
                    else:
                        # Try splitting by period
                        title_parts = todo_text.split(".", 1)
                        if len(title_parts) > 1:
                            title = title_parts[0].strip()
                            description = title_parts[1].strip()
                        else:
                            title = todo_text
                            description = ""
                    
                    result = {
                        "title": title,
                        "description": description
                    }
                    break
        
        return result


# Example usage:
# todo_manager = TodoManager("/path/to/your/project")
# todo_manager.add_todo("Implement feature X", "This feature will...")
# todos = todo_manager.get_todos(status="active")

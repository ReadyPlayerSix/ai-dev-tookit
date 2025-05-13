#!/usr/bin/env python3
"""
Edit Bookmark Module

This module provides the EditBookmark class, which allows for creating bookmarks
for sections of files, making edits to those sections, and applying the changes
back to the original files. This provides a more reliable way to edit complex
code sections compared to direct file editing.
"""

import os
import uuid
import json
import logging
import datetime
from typing import Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

class EditBookmark:
    """
    EditBookmark class for managing bookmarks of file sections.
    
    This class allows for creating bookmarks for sections of files, making edits to
    those sections, and applying the changes back to the original files.
    """

    def __init__(self, project_path: str):
        """
        Initialize an EditBookmark instance.
        
        Args:
            project_path: The root directory of the project
        """
        self.project_path = project_path
        self.bookmarks_dir = os.path.join(project_path, ".ai_reference", "edit_bookmarks")
        os.makedirs(self.bookmarks_dir, exist_ok=True)

        # Path to the metadata file that stores active bookmarks
        self.metadata_path = os.path.join(self.bookmarks_dir, "bookmarks_metadata.json")

        # Load active bookmarks from metadata file
        self.active_bookmarks = self._load_bookmarks()

    def create_bookmark(self, file_path: str, start_line: int, end_line: int,
                        bookmark_name: Optional[str] = None) -> str:
        """
        Create a bookmark for a section of a file.
        
        Args:
            file_path: Path to the file to bookmark
            start_line: First line of the section to bookmark (1-based)
            end_line: Last line of the section to bookmark (inclusive)
            bookmark_name: Optional name for the bookmark
            
        Returns:
            The bookmark ID
        """
        try:
            # Generate unique ID if no name provided
            bookmark_id = bookmark_name or f"bookmark_{uuid.uuid4().hex[:8]}"

            # Ensure file path is absolute
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.project_path, file_path)

            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # Validate line numbers
            if start_line < 1 or end_line > len(content) or start_line > end_line:
                raise ValueError(f"Invalid line range: {start_line}-{end_line} for file with {len(content)} lines")

            # Extract the section
            section = content[start_line-1:end_line]

            # Create a bookmark file
            bookmark_path = os.path.join(self.bookmarks_dir, f"{bookmark_id}_{end_line-start_line+1}.edit")
            with open(bookmark_path, 'w', encoding='utf-8') as f:
                f.writelines(section)

            # Store bookmark metadata
            self.active_bookmarks[bookmark_id] = {
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "bookmark_path": bookmark_path,
                "created": datetime.datetime.now().isoformat()
            }

            # Save bookmarks to disk
            self._save_bookmarks()

            logger.info(f"Created bookmark '{bookmark_id}' for {file_path}, lines {start_line}-{end_line}")
            return bookmark_id
        except Exception as e:
            logger.error(f"Error creating bookmark: {str(e)}")
            raise

    def get_bookmark_content(self, bookmark_id: str) -> Optional[str]:
        """
        Get the content of a bookmark.
        
        Args:
            bookmark_id: The ID of the bookmark
            
        Returns:
            The content of the bookmark or None if not found
        """
        try:
            if bookmark_id not in self.active_bookmarks:
                logger.warning(f"Bookmark not found: {bookmark_id}")
                return None

            bookmark_path = self.active_bookmarks[bookmark_id]["bookmark_path"]
            if not os.path.exists(bookmark_path):
                logger.warning(f"Bookmark file not found: {bookmark_path}")
                return None

            with open(bookmark_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error getting bookmark content: {str(e)}")
            return None

    def list_bookmarks(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active bookmarks.
        
        Returns:
            Dictionary mapping bookmark IDs to their metadata
        """
        return self.active_bookmarks

    def update_bookmark(self, bookmark_id: str, new_content: str) -> bool:
        """
        Update the content of a bookmark.
        
        Args:
            bookmark_id: The ID of the bookmark
            new_content: The new content for the bookmark
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if bookmark_id not in self.active_bookmarks:
                logger.warning(f"Bookmark not found: {bookmark_id}")
                return False

            bookmark_path = self.active_bookmarks[bookmark_id]["bookmark_path"]
            with open(bookmark_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Save bookmarks to disk
            self._save_bookmarks()

            logger.info(f"Updated bookmark: {bookmark_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating bookmark: {str(e)}")
            return False

    def apply_bookmark(self, bookmark_id: str) -> bool:
        """
        Apply a bookmark to the original file.
        
        Args:
            bookmark_id: The ID of the bookmark
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if bookmark_id not in self.active_bookmarks:
                logger.warning(f"Bookmark not found: {bookmark_id}")
                return False

            bookmark = self.active_bookmarks[bookmark_id]
            file_path = bookmark["file_path"]
            start_line = bookmark["start_line"]
            end_line = bookmark["end_line"]

            # Read the original file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # Read the bookmark content
            with open(bookmark["bookmark_path"], 'r', encoding='utf-8') as f:
                new_section = f.readlines()

            # Replace the section
            new_content = content[:start_line-1] + new_section + content[end_line:]
            # Write back to the original file atomically
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_content)

            logger.info(f"Applied bookmark {bookmark_id} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error applying bookmark: {str(e)}")
            return False

    def remove_bookmark(self, bookmark_id: str) -> bool:
        """
        Remove a bookmark from the system.
        
        Args:
            bookmark_id: The ID of the bookmark to remove
            
        Returns:
            True if successfully removed, False if not found or error occurred
        """
        try:
            if bookmark_id not in self.active_bookmarks:
                logger.warning(f"Bookmark not found: {bookmark_id}")
                return False

            bookmark_path = self.active_bookmarks[bookmark_id]["bookmark_path"]
            if os.path.exists(bookmark_path):
                os.remove(bookmark_path)

            del self.active_bookmarks[bookmark_id]

            # Save bookmarks to disk
            self._save_bookmarks()

            logger.info(f"Removed bookmark: {bookmark_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing bookmark: {str(e)}")
            return False

    def get_bookmark_diff(self, bookmark_id: str) -> Optional[str]:
        """
        Get a diff of the changes made to a bookmark.
        
        Args:
            bookmark_id: The ID of the bookmark
            
        Returns:
            A string representing the diff, or None if the bookmark is not found
        """
        try:
            if bookmark_id not in self.active_bookmarks:
                return None

            bookmark = self.active_bookmarks[bookmark_id]
            file_path = bookmark["file_path"]
            start_line = bookmark["start_line"]
            end_line = bookmark["end_line"]

            # Read the original file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()

            # Extract the original section
            original_section = content[start_line-1:end_line]

            # Read the bookmark content
            with open(bookmark["bookmark_path"], 'r', encoding='utf-8') as f:
                new_section = f.readlines()

            # Create a simple diff
            diff_lines = []
            diff_lines.append(f"Diff for bookmark {bookmark_id} ({file_path}, lines {start_line}-{end_line}):")
            diff_lines.append("=" * 80)

            # Show side-by-side diff
            max_lines = max(len(original_section), len(new_section))
            for i in range(max_lines):
                orig_line = original_section[i].rstrip() if i < len(original_section) else ""
                new_line = new_section[i].rstrip() if i < len(new_section) else ""

                if i < len(original_section) and i < len(new_section) and original_section[i] == new_section[i]:
                    # Unchanged line
                    diff_lines.append(f"  {start_line+i}: {orig_line}")
                else:
                    # Changed line
                    if i < len(original_section):
                        diff_lines.append(f"- {start_line+i}: {orig_line}")
                    if i < len(new_section):
                        diff_lines.append(f"+ {start_line+i}: {new_line}")

            return "\n".join(diff_lines)
        except Exception as e:
            logger.error(f"Error generating diff: {str(e)}")
            return None

    def cleanup_old_bookmarks(self, max_age_hours: int = 24) -> int:
        """
        Clean up old bookmarks.
        
        Args:
            max_age_hours: Maximum age of bookmarks to keep, in hours
            
        Returns:
            Number of bookmarks removed
        """
        try:
            now = datetime.datetime.now()
            bookmarks_to_remove = []

            for bookmark_id, metadata in self.active_bookmarks.items():
                created = datetime.datetime.fromisoformat(metadata["created"])
                age = now - created

                if age.total_seconds() > max_age_hours * 3600:
                    bookmarks_to_remove.append(bookmark_id)

            for bookmark_id in bookmarks_to_remove:
                self.remove_bookmark(bookmark_id)

            # Save bookmarks to disk after cleanup
            self._save_bookmarks()

            logger.info(f"Cleaned up {len(bookmarks_to_remove)} old bookmarks")
            return len(bookmarks_to_remove)
        except Exception as e:
            logger.error(f"Error cleaning up bookmarks: {str(e)}")
            return 0

    def _load_bookmarks(self) -> Dict[str, Dict[str, Any]]:
        """
        Load bookmarks from the metadata file.
        
        Returns:
            Dictionary of active bookmarks
        """
        try:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading bookmarks metadata: {str(e)}")
            return {}

    def _save_bookmarks(self) -> bool:
        """
        Save bookmarks to the metadata file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.active_bookmarks, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving bookmarks metadata: {str(e)}")
            return False

#!/usr/bin/env python3
"""
Enhanced Edit File Fix Implementation

This module contains a fixed implementation of the enhanced_edit_file function
to address issues with timeouts, lag, and internal errors.
"""

import os
import logging
import time
import shutil
import tempfile
import hashlib

def enhanced_edit_file_fixed(path, old_text, new_text, encoding="utf-8", ALLOWED_DIRECTORIES=None, logger=None):
    """
    Fixed implementation of enhanced_edit_file with improved error handling and performance.
    
    Args:
        path: Path to the file to edit
        old_text: The text segment to be replaced (must match exactly)
        new_text: The new text to replace with
        encoding: File encoding (default: utf-8)
        ALLOWED_DIRECTORIES: List of allowed directories (required)
        logger: Logger instance for reporting (required)
        
    Returns:
        Dictionary with the result of the edit operation, including a git-style diff
    """
    # Setup default logger if none provided
    if logger is None:
        logger = logging.getLogger("enhanced_edit_file")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    # Log start of operation with timestamp
    start_time = time.time()
    logger.info(f"Starting enhanced_edit_file for {path}")
    
    try:
        # Normalize the path
        path = os.path.abspath(path)
        logger.debug(f"Normalized path: {path}")
        
        # Check if path is within allowed directories
        if not any(path.startswith(allowed_dir) for allowed_dir in ALLOWED_DIRECTORIES):
            logger.warning(f"Access denied: {path} is not within allowed directories")
            return {
                "status": "error",
                "message": f"Access denied: {path} is not within allowed directories"
            }
        
        # Check if file exists
        if not os.path.isfile(path):
            logger.warning(f"File not found: {path}")
            return {
                "status": "error",
                "message": f"File not found: {path}"
            }
        
        # Check if we have read and write permission
        if not os.access(path, os.R_OK | os.W_OK):
            logger.warning(f"Permission denied: Cannot modify {path}")
            return {
                "status": "error",
                "message": f"Permission denied: Cannot modify {path}"
            }
        
        # Get file size before trying to read (for logging and potential size limits)
        try:
            file_size = os.path.getsize(path)
            logger.info(f"File size: {file_size} bytes")
            
            # Implement a size limit for very large files
            MAX_SIZE = 50 * 1024 * 1024  # 50 MB
            if file_size > MAX_SIZE:
                logger.warning(f"File too large: {file_size} bytes exceeds limit of {MAX_SIZE} bytes")
                return {
                    "status": "error",
                    "message": f"File too large: {file_size / 1024 / 1024:.2f} MB exceeds limit of {MAX_SIZE / 1024 / 1024} MB"
                }
        except Exception as e:
            logger.error(f"Error checking file size: {str(e)}")
        
        # Read the current content of the file
        try:
            logger.info("Reading file content")
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            logger.info(f"File content read, length: {len(content)} characters")
        except UnicodeDecodeError as ude:
            logger.error(f"Unicode decode error: {str(ude)}")
            return {
                "status": "error",
                "message": f"Cannot edit binary file or file with encoding different from {encoding}"
            }
        except PermissionError as pe:
            logger.error(f"Permission error reading file: {str(pe)}")
            return {
                "status": "error",
                "message": f"Permission denied: Cannot read {path}"
            }
        except FileNotFoundError as fnf:
            logger.error(f"File not found: {str(fnf)}")
            return {
                "status": "error",
                "message": f"File not found: {path}"
            }
        except Exception as e:
            logger.error(f"Error reading file: {str(e)} (Type: {type(e).__name__})")
            return {
                "status": "error",
                "message": f"Error reading file: {str(e)}"
            }
        
        # Check if content is unchanged to avoid unnecessary work
        if not old_text:
            logger.warning("Empty old_text provided, nothing to replace")
            return {
                "status": "error",
                "message": "Empty old_text provided, nothing to replace"
            }
            
        # Check if the old_text exists in the content
        if old_text not in content:
            logger.warning("The specified text segment was not found in the file")
            return {
                "status": "error",
                "message": "The specified text segment was not found in the file"
            }
        
        # Check if the old text occurs multiple times (ambiguous replacement)
        occurrences = content.count(old_text)
        if occurrences > 1:
            logger.warning(f"Text segment appears multiple times in file ({occurrences} occurrences)")
            return {
                "status": "error",
                "message": f"The specified text segment appears {occurrences} times in the file. Please provide a more specific text segment."
            }
        
        # Calculate hash of the content for verification
        content_hash_before = hashlib.md5(content.encode()).hexdigest()
        
        # Replace the text
        logger.info("Performing text replacement")
        new_content = content.replace(old_text, new_text)
        
        # Check if content was actually modified
        if content == new_content:
            logger.info("No changes made to file content")
            return {
                "status": "success",
                "message": "No changes needed, content is identical after replacement",
                "path": path
            }
            
        # Calculate hash of the new content for verification
        content_hash_after = hashlib.md5(new_content.encode()).hexdigest()
        
        # Calculate a descriptive diff for the response
        logger.info("Generating diff")
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        
        # Generate a unified diff-like output
        diff = ["Changes:"]
        diff.append(f"--- {path} (original)")
        diff.append(f"+++ {path} (modified)")
        
        # Add the changed lines with line numbers if possible
        try:
            # Find where in the file the old_text is located
            lines_before = content.split(old_text, 1)[0].count('\n') + 1
            
            # Add a better header for the diff
            diff.append(f"@@ -{lines_before},{len(old_lines)} +{lines_before},{len(new_lines)} @@")
            
            for line in old_lines:
                diff.append(f"- {line}")
            for line in new_lines:
                diff.append(f"+ {line}")
        except Exception as e:
            logger.error(f"Error generating diff: {str(e)}")
            diff.append("Error generating detailed diff")
        
        # Create the directory if it doesn't exist
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            try:
                logger.info(f"Creating directory: {dir_name}")
                os.makedirs(dir_name, exist_ok=True)
            except OSError as e:
                logger.error(f"Cannot create directory {dir_name}: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Cannot create directory {dir_name}: {str(e)}"
                }
        
        # Create the temporary directory in the same directory as the target file if possible
        # If not, fall back to system default temp directory
        temp_dir = None
        try:
            if os.path.exists(dir_name) and os.access(dir_name, os.W_OK):
                temp_dir = dir_name
            else:
                temp_dir = tempfile.gettempdir()
            logger.info(f"Using temp directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Error determining temp directory: {str(e)}")
            temp_dir = tempfile.gettempdir()
        
        # Write the modified content to a temp file first, then move it
        logger.info("Writing content to temporary file")
        temp_path = None
        
        try:
            # Create a temporary file with a unique name in the appropriate directory
            temp_file_handle, temp_path = tempfile.mkstemp(dir=temp_dir, suffix='.tmp')
            
            # Close the file descriptor returned by mkstemp
            os.close(temp_file_handle)
            
            # Write content to the temp file
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(new_content)
                
            logger.info(f"Temporary file created: {temp_path}")
                
            # Verify the temp file was written correctly
            if not os.path.exists(temp_path):
                logger.error("Temporary file not created properly")
                return {
                    "status": "error",
                    "message": "Error in atomic write: temporary file not created properly"
                }
                
            try:
                # Use copy followed by removal instead of move for better cross-filesystem compatibility
                logger.info(f"Copying {temp_path} to {path}")
                shutil.copy2(temp_path, path)
                
                # Remove temp file after successful copy
                logger.info(f"Removing temporary file: {temp_path}")
                os.unlink(temp_path)
            except Exception as copy_error:
                logger.error(f"Error during final copy operation: {str(copy_error)}")
                # Clean up the temporary file if it exists
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                return {
                    "status": "error",
                    "message": f"Error writing file: {str(copy_error)}"
                }
                
            # Calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Operation completed successfully in {execution_time:.2f} seconds")
            
            # Calculate the character and line differences for better reporting
            chars_removed = len(old_text)
            chars_added = len(new_text)
            lines_removed = len(old_lines)
            lines_added = len(new_lines)
            
            return {
                "status": "success",
                "message": f"Successfully edited file: {path}",
                "diff": "\n".join(diff),
                "path": path,
                "encoding": encoding,
                "stats": {
                    "chars_removed": chars_removed,
                    "chars_added": chars_added,
                    "chars_net_change": chars_added - chars_removed,
                    "lines_removed": lines_removed,
                    "lines_added": lines_added,
                    "lines_net_change": lines_added - lines_removed,
                    "execution_time_seconds": execution_time
                },
                "content_hash_before": content_hash_before,
                "content_hash_after": content_hash_after
            }
            
        except Exception as e:
            logger.error(f"Error in write operation: {str(e)}")
            # Clean up the temporary file if it exists
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temp file: {str(cleanup_error)}")
            
            return {
                "status": "error",
                "message": f"Error writing file: {str(e)}"
            }
    except Exception as outer_e:
        # Catch any other exceptions that might occur
        logger.error(f"Unexpected error in enhanced_edit_file: {str(outer_e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(outer_e)}"
        }

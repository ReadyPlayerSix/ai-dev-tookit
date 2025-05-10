"""
Centralized Logging Manager

This module provides a unified logging system for the AI Dev Toolkit.
It ensures consistent logging across all components with configurable levels,
formatters, and handlers.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Default log directory 
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")

# Global dictionary to track registered loggers
_registered_loggers = {}

def configure_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    console_level: int = logging.WARNING,
    file_level: int = logging.INFO,
    clear_existing_handlers: bool = True
) -> logging.Logger:
    """
    Configure a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_level: Overall logger level
        log_file: Log file name (optional)
        log_dir: Directory to store logs (optional)
        console_level: Level for console output
        file_level: Level for file output
        clear_existing_handlers: Whether to clear existing handlers
        
    Returns:
        Configured logger
    """
    # Get or create the logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Store in global registry
    _registered_loggers[name] = logger
    
    # Clear any existing handlers if requested
    if clear_existing_handlers and logger.handlers:
        logger.handlers.clear()
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Set up file handler if log_file is provided
    if log_file:
        # Create log directory if it doesn't exist
        log_directory = log_dir or DEFAULT_LOG_DIR
        os.makedirs(log_directory, exist_ok=True)
        
        file_path = os.path.join(log_directory, log_file)
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a registered logger or create a new one with default settings.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    if name in _registered_loggers:
        return _registered_loggers[name]
    
    # Create new logger with default settings
    return configure_logger(
        name=name,
        log_file=f"{name.replace('.', '_')}.log"
    )

def set_all_loggers_level(level: int) -> None:
    """
    Set the level for all registered loggers.
    
    Args:
        level: Logging level to set
    """
    for logger in _registered_loggers.values():
        logger.setLevel(level)

def get_all_loggers() -> Dict[str, logging.Logger]:
    """
    Get all registered loggers.
    
    Returns:
        Dictionary of logger names to logger objects
    """
    return _registered_loggers.copy()

def set_handler_levels(console_level: Optional[int] = None, file_level: Optional[int] = None) -> None:
    """
    Set the levels for all handlers of registered loggers.
    
    Args:
        console_level: Level for console handlers
        file_level: Level for file handlers
    """
    for logger in _registered_loggers.values():
        for handler in logger.handlers:
            if console_level is not None and isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(console_level)
            elif file_level is not None and isinstance(handler, logging.FileHandler):
                handler.setLevel(file_level)

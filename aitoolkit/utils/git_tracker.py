#!/usr/bin/env python3
"""
Git History Tracker for Claude

This module provides functionality to track git repository history and 
maintain files that Claude can use to understand the repository state.

It records detailed information about commits, tags, branches, and remotes,
making it easier for Claude to provide accurate git commands.
"""

import os
import subprocess
import json
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger("git-tracker")

def run_git_command(command, cwd=None):
    """
    Run a git command and return the output.
    
    Args:
        command: Git command to run (list of args)
        cwd: Directory to run the command in (default: current directory)
        
    Returns:
        String output of the command
    """
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running git command: {e}")
        logger.error(f"stderr: {e.stderr}")
        return ""

def get_commit_history(num_commits=30, repo_path=None):
    """
    Get the recent commit history.
    
    Args:
        num_commits: Number of commits to retrieve
        repo_path: Path to the repository (default: current directory)
        
    Returns:
        List of commit dictionaries
    """
    format_string = "--pretty=format:%H|%an|%at|%ar|%s"
    command = ["git", "log", f"-n{num_commits}", format_string]
    output = run_git_command(command, cwd=repo_path)
    
    commits = []
    for line in output.split('\n'):
        if not line.strip():
            continue
            
        parts = line.split('|')
        if len(parts) < 5:
            continue
            
        commit = {
            "hash": parts[0],
            "author": parts[1],
            "timestamp": int(parts[2]),
            "date": datetime.fromtimestamp(int(parts[2])).isoformat(),
            "relative_date": parts[3],
            "message": parts[4]
        }
        commits.append(commit)
    
    return commits

def get_tags(repo_path=None):
    """
    Get all tags with their annotations.
    
    Args:
        repo_path: Path to the repository (default: current directory)
        
    Returns:
        Dictionary mapping tag names to info dictionaries
    """
    # Get all tags
    command = ["git", "tag"]
    tag_list = run_git_command(command, cwd=repo_path).split('\n')
    
    tags = {}
    for tag in tag_list:
        if not tag.strip():
            continue
            
        # Get tag message
        message_command = ["git", "tag", "-l", "-n99", tag]
        message_output = run_git_command(message_command, cwd=repo_path)
        
        # Get tag commit hash
        hash_command = ["git", "rev-list", "-n", "1", tag]
        commit_hash = run_git_command(hash_command, cwd=repo_path)
        
        # Get tag date
        date_command = ["git", "show", "--format=%at", tag, "-s"]
        date_output = run_git_command(date_command, cwd=repo_path)
        tag_date = datetime.fromtimestamp(int(date_output)).isoformat() if date_output else None
        
        # Extract message removing the tag name
        parts = message_output.split('\t')
        message = parts[1] if len(parts) > 1 else ""
        
        tags[tag] = {
            "name": tag,
            "message": message.strip(),
            "commit": commit_hash,
            "date": tag_date
        }
    
    # Sort tags by date
    return dict(sorted(tags.items(), key=lambda x: x[1]["date"] if x[1]["date"] else ""))

def get_branches(repo_path=None):
    """
    Get all branches and their latest commits.
    
    Args:
        repo_path: Path to the repository (default: current directory)
        
    Returns:
        List of branch dictionaries
    """
    command = ["git", "branch", "-v", "--no-abbrev"]
    output = run_git_command(command, cwd=repo_path)
    
    branches = []
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if this is the current branch
        is_current = line.startswith('*')
        line = line[2:] if is_current else line
        
        # Split into branch name and rest of the information
        parts = line.split(maxsplit=2)
        if len(parts) < 3:
            continue
            
        branch_name, commit_hash, commit_message = parts
        
        branches.append({
            "name": branch_name,
            "hash": commit_hash,
            "message": commit_message,
            "current": is_current
        })
    
    return branches

def get_remotes(repo_path=None):
    """
    Get remote repository information.
    
    Args:
        repo_path: Path to the repository (default: current directory)
        
    Returns:
        Dictionary mapping remote names to their URLs
    """
    command = ["git", "remote", "-v"]
    output = run_git_command(command, cwd=repo_path)
    
    remotes = {}
    for line in output.split('\n'):
        if not line.strip():
            continue
            
        parts = line.split()
        if len(parts) < 3:
            continue
            
        name, url, type_info = parts[0], parts[1], parts[2]
        if type_info == "(fetch)" and name not in remotes:
            remotes[name] = url
    
    return remotes

def get_repository_status(repo_path=None):
    """
    Get information about the current state of the repository.
    
    Args:
        repo_path: Path to the repository (default: current directory)
        
    Returns:
        Dictionary with repository status information
    """
    # Is the repo clean?
    command = ["git", "status", "--porcelain"]
    status_output = run_git_command(command, cwd=repo_path)
    is_clean = status_output.strip() == ""
    
    # Get current branch
    command = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    current_branch = run_git_command(command, cwd=repo_path)
    
    # Get latest commit
    command = ["git", "rev-parse", "HEAD"]
    current_commit = run_git_command(command, cwd=repo_path)
    
    # Get commit message
    command = ["git", "log", "-1", "--pretty=%B"]
    commit_message = run_git_command(command, cwd=repo_path)
    
    return {
        "is_clean": is_clean,
        "current_branch": current_branch,
        "current_commit": current_commit,
        "latest_commit_message": commit_message.strip()
    }

def update_git_history_files(repo_path=None, history_dir=None):
    """
    Update all git history files with current repository information.
    
    Args:
        repo_path: Path to the repository (default: current directory)
        history_dir: Directory where to store history files (default: .git_history in repo_path)
        
    Returns:
        Dictionary with results of the operation
    """
    # Determine paths
    if repo_path is None:
        repo_path = os.getcwd()
    
    if history_dir is None:
        history_dir = os.path.join(repo_path, ".git_history")
    
    # Create directory for git history if it doesn't exist
    os.makedirs(history_dir, exist_ok=True)
    
    try:
        # Get git information
        commits = get_commit_history(repo_path=repo_path)
        tags = get_tags(repo_path=repo_path)
        branches = get_branches(repo_path=repo_path)
        remotes = get_remotes(repo_path=repo_path)
        status = get_repository_status(repo_path=repo_path)
        
        # Create structured git info
        git_info = {
            "last_updated": datetime.now().isoformat(),
            "repository_status": status,
            "commits": commits,
            "tags": tags,
            "branches": branches,
            "remotes": remotes
        }
        
        # Save JSON file
        json_path = os.path.join(history_dir, "git_info.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(git_info, f, indent=2)
        
        # Save human-readable text file
        text_path = os.path.join(history_dir, "git_info.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write("GIT REPOSITORY INFORMATION\n")
            f.write("=========================\n")
            f.write(f"Last Updated: {datetime.now().isoformat()}\n\n")
            
            f.write("REPOSITORY STATUS\n")
            f.write("-----------------\n")
            f.write(f"Current Branch: {status['current_branch']}\n")
            f.write(f"Current Commit: {status['current_commit'][:8]}\n")
            f.write(f"Clean Working Directory: {'Yes' if status['is_clean'] else 'No'}\n")
            f.write(f"Latest Commit Message: {status['latest_commit_message']}\n\n")
            
            f.write("RECENT COMMITS\n")
            f.write("-------------\n")
            for commit in commits:
                f.write(f"{commit['hash'][:8]} - {commit['author']}, {commit['relative_date']} : {commit['message']}\n")
            f.write("\n")
            
            f.write("TAGS\n")
            f.write("----\n")
            for tag_name, tag_info in tags.items():
                f.write(f"{tag_name:<20} {tag_info['message']}\n")
            f.write("\n")
            
            f.write("BRANCHES\n")
            f.write("--------\n")
            for branch in branches:
                current_marker = "* " if branch["current"] else "  "
                f.write(f"{current_marker}{branch['name']:<20} {branch['hash'][:8]} {branch['message']}\n")
            f.write("\n")
            
            f.write("REMOTES\n")
            f.write("-------\n")
            for name, url in remotes.items():
                f.write(f"{name:<10} {url}\n")
        
        # Create a latest version file for quick reference
        latest_tag = list(tags.keys())[-1] if tags else "No tags found"
        latest_commit = commits[0]["hash"][:8] if commits else "No commits found"
        latest_commit_msg = commits[0]["message"] if commits else ""
        
        version_path = os.path.join(history_dir, "latest_version.txt")
        with open(version_path, "w", encoding="utf-8") as f:
            f.write(f"Latest tag: {latest_tag}\n")
            f.write(f"Latest commit: {latest_commit} - {latest_commit_msg}\n")
            f.write(f"Current branch: {status['current_branch']}\n")
            f.write(f"Working directory clean: {'Yes' if status['is_clean'] else 'No'}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
        
        logger.info(f"Git history files updated in {history_dir}")
        
        return {
            "status": "success",
            "message": f"Git history files updated in {history_dir}",
            "files": {
                "json": json_path,
                "text": text_path,
                "version": version_path
            },
            "latest_tag": latest_tag,
            "latest_commit": latest_commit,
            "latest_commit_msg": latest_commit_msg
        }
    
    except Exception as e:
        logger.error(f"Error updating git history: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error updating git history: {str(e)}",
            "exception": str(e)
        }

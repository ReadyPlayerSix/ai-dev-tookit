#!/usr/bin/env python3
"""
Context Compression Tool

This tool compresses and stores conversation history in a format optimized for
AI language models, making it easier to maintain context between sessions.

Usage:
    python context-compressor.py save "conversation_title" conversation.json
    python context-compressor.py load "conversation_title"
"""

import os
import sys
import json
import datetime
import argparse
import re
from typing import Dict, List, Any, Optional, Set, Tuple

# Constants
DEFAULT_CONTEXT_DIR = os.path.join(".ai_reference", "context")
DEFAULT_IMPORTANCE_THRESHOLD = 0.6
VERSION = "1.0.0"

class ConversationCompressor:
    """Compresses and stores conversation history."""
    
    def __init__(self, context_dir: str = DEFAULT_CONTEXT_DIR):
        """Initialize with context directory."""
        self.context_dir = context_dir
        os.makedirs(context_dir, exist_ok=True)
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        # Simple implementation - in real use, this would use NLP
        # Extract key phrases based on common patterns
        topics = set()
        
        # Look for phrases after "about", "regarding", "concerning"
        pattern = r'(?:about|regarding|concerning|discussing|explaining) ([a-zA-Z0-9, _-]+)'
        matches = re.findall(pattern, text.lower())
        for match in matches:
            topics.update([t.strip() for t in match.split(',')])
            
        # Extract code-related topics
        code_pattern = r'(?:code|function|class|method|module|file) (?:for|named|called) ([a-zA-Z0-9_-]+)'
        code_matches = re.findall(code_pattern, text.lower())
        for match in code_matches:
            topics.add(match.strip())
            
        # Add general topics based on keywords
        keywords = {
            "project structure": ["structure", "organization", "layout", "directory"],
            "file system tools": ["file", "directory", "read", "write", "file system"],
            "ai dev toolkit": ["ai dev toolkit", "toolkit", "mcp", "server"],
            "librarian": ["librarian", "code comprehension", "code navigation"],
            "project generator": ["generator", "scaffolding", "project creation"],
            "claude integration": ["claude", "integration", "connection", "desktop"],
            "context compression": ["context", "compression", "conversation history"],
            "batch files": ["batch", "script", "bat", "automation"],
            "github": ["github", "repository", "git"],
            "installation": ["install", "setup", "configuration"]
        }
        
        for topic, words in keywords.items():
            if any(word in text.lower() for word in words):
                topics.add(topic)
        
        return list(topics) if topics else ["general"]
    
    def extract_files_referenced(self, text: str) -> List[str]:
        """Extract file paths that were referenced."""
        # Look for file extensions and paths
        file_pattern = r'[A-Za-z0-9_\-\.\/\\]+\.(py|md|bat|sh|json|txt)'
        return list(set(re.findall(file_pattern, text)))
    
    def extract_tools_used(self, text: str) -> List[str]:
        """Extract tools that were used."""
        tool_pattern = r'`([a-zA-Z_]+)`|read_file|write_file|list_directory|search_files|create_directory|directory_tree|get_file_info|move_file|edit_file|initialize_librarian|query_component|find_implementation|generate_librarian|create_project_plan|generate_project_structure|create_starter_files|setup_github_repo|think'
        return list(set(re.findall(tool_pattern, text)))
    
    def calculate_importance(self, message: Dict[str, Any]) -> float:
        """Calculate importance score for a message."""
        # Simple heuristic based on content
        content = message.get("content", "")
        
        # Base importance
        importance = 0.5
        
        # Adjust based on length (longer often more important)
        content_length = len(content)
        if content_length > 1000:
            importance += 0.2
        elif content_length > 500:
            importance += 0.1
        
        # Code snippets are important
        if "```" in content:
            importance += 0.2
        
        # Lists often contain important info
        if re.search(r'\n[*-] ', content):
            importance += 0.1
        
        # Questions are often important
        if "?" in content:
            importance += 0.1
        
        # Tool usage indicates importance
        tools_used = message.get("tools_used", [])
        if tools_used:
            importance += 0.1
        
        # File references indicate importance
        files_referenced = message.get("files_referenced", [])
        if files_referenced:
            importance += 0.1
            
        # Cap at 0.9 - nothing is fully 1.0 important
        return min(importance, 0.9)

    def preprocess_conversation(self, conversation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess the conversation to add metadata."""
        processed = []
        
        for i, message in enumerate(conversation):
            # Create unique ID for the message
            msg_id = f"msg{i+1}"
            
            # Get message role and content
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            # Extract metadata
            topics = self.extract_topics(content)
            tools_used = self.extract_tools_used(content)
            files_referenced = self.extract_files_referenced(content)
            
            # Calculate importance
            importance = self.calculate_importance(message)
            
            # Create references to previous messages (simplified)
            references = [f"msg{i}"] if i > 0 else []
            
            # Create processed message
            processed_message = {
                "id": msg_id,
                "role": role,
                "content": content,
                "timestamp": message.get("timestamp", datetime.datetime.now().isoformat()),
                "topics": topics,
                "importance": importance,
                "references": references,
                "tools_used": tools_used,
                "files_referenced": files_referenced
            }
            
            processed.append(processed_message)
            
        return processed
    
    def compress_conversation(self, conversation: List[Dict[str, Any]], importance_threshold: float = DEFAULT_IMPORTANCE_THRESHOLD) -> Dict[str, Any]:
        """Compress a conversation."""
        # Preprocess to add metadata
        processed = self.preprocess_conversation(conversation)
        
        # Step 1: Sort messages by importance
        sorted_by_importance = sorted(processed, key=lambda msg: msg.get("importance", 0), reverse=True)
        
        # Step 2: Take top important messages verbatim
        cutoff_index = int(len(processed) * importance_threshold)
        high_importance_messages = sorted_by_importance[:cutoff_index]
        high_importance_ids = {msg["id"] for msg in high_importance_messages}
        
        # Step 3: Summarize the rest
        low_importance_messages = [msg for msg in sorted_by_importance if msg["id"] not in high_importance_ids]
        
        # Step 4: Group by topics
        topic_groups = {}
        for msg in processed:
            for topic in msg.get("topics", []):
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(msg["id"])
        
        # Step 5: Create the compressed representation
        global_tools = set()
        global_files = set()
        
        for msg in processed:
            tools = msg.get("tools_used", [])
            files = msg.get("files_referenced", [])
            global_tools.update(tools)
            global_files.update(files)
        
        compressed = {
            "metadata": {
                "totalMessages": len(processed),
                "compressedDate": datetime.datetime.now().isoformat(),
                "topicGroups": topic_groups,
                "globalTools": list(global_tools),
                "globalFiles": list(global_files),
            },
            "highImportanceMessages": high_importance_messages,
            "summaries": [{
                "id": msg["id"],
                "role": msg["role"],
                "summary": f"{msg['role'].capitalize()} {'asked about' if msg['role'] == 'human' else 'explained'} {', '.join(msg.get('topics', ['general']))}",
                "references": msg.get("references", []),
                "importance": msg.get("importance", 0)
            } for msg in low_importance_messages]
        }
        
        return compressed
    
    def summarize_compressed(self, compressed: Dict[str, Any]) -> str:
        """Create a summary of the compressed conversation."""
        metadata = compressed.get("metadata", {})
        
        summary = f"Conversation with {metadata.get('totalMessages', 0)} messages.\n\n"
        
        # Add topic overview
        topic_groups = metadata.get("topicGroups", {})
        if topic_groups:
            summary += "Topics discussed:\n"
            for topic, _ in sorted(topic_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
                summary += f"- {topic}\n"
            summary += "\n"
        
        # Add tools used
        tools = metadata.get("globalTools", [])
        if tools:
            summary += "Tools used: " + ", ".join(tools) + "\n\n"
        
        # Add files referenced
        files = metadata.get("globalFiles", [])
        if files:
            summary += "Files referenced: " + ", ".join(files) + "\n\n"
        
        # Add key messages
        high_importance = compressed.get("highImportanceMessages", [])
        if high_importance:
            summary += "Key points:\n"
            for msg in high_importance[:3]:  # Just show top 3
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                preview = content[:100] + "..." if len(content) > 100 else content
                summary += f"- {role.capitalize()}: {preview}\n"
        
        return summary
    
    def save_conversation(self, title: str, conversation: List[Dict[str, Any]], compressed: Optional[Dict[str, Any]] = None) -> str:
        """Save a conversation to disk."""
        if compressed is None:
            compressed = self.compress_conversation(conversation)
        
        # Create the metadata structure
        conversation_store = {
            "version": VERSION,
            "projectId": "ai-dev-toolkit",
            "conversations": [
                {
                    "id": title.lower().replace(" ", "-"),
                    "title": title,
                    "startDate": datetime.datetime.now().isoformat(),
                    "endDate": datetime.datetime.now().isoformat(),
                    "compressed": compressed
                }
            ]
        }
        
        # Create filename
        safe_title = title.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = os.path.join(self.context_dir, f"{safe_title}.json")
        
        # Save to disk
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_store, f, indent=2)
        
        return filename
    
    def load_conversation(self, title: str) -> Dict[str, Any]:
        """Load a conversation from disk."""
        # Create filename
        safe_title = title.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = os.path.join(self.context_dir, f"{safe_title}.json")
        
        # Load from disk
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Return the first conversation
            return data
        except FileNotFoundError:
            return {"error": f"Conversation '{title}' not found"}
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON in conversation file '{filename}'"}
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations."""
        conversations = []
        
        for filename in os.listdir(self.context_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.context_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for conv in data.get("conversations", []):
                        conversations.append({
                            "id": conv.get("id", "unknown"),
                            "title": conv.get("title", "Unnamed"),
                            "startDate": conv.get("startDate", ""),
                            "messageCount": conv.get("compressed", {}).get("metadata", {}).get("totalMessages", 0)
                        })
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
                    
        return conversations

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Context Compression Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save a conversation")
    save_parser.add_argument("title", help="Title of the conversation")
    save_parser.add_argument("input_file", help="JSON file containing conversation")
    save_parser.add_argument("--dir", default=DEFAULT_CONTEXT_DIR, help="Context directory")
    save_parser.add_argument("--threshold", type=float, default=DEFAULT_IMPORTANCE_THRESHOLD, 
                            help="Importance threshold (0-1)")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load a conversation")
    load_parser.add_argument("title", help="Title of the conversation")
    load_parser.add_argument("--dir", default=DEFAULT_CONTEXT_DIR, help="Context directory")
    load_parser.add_argument("--summary", action="store_true", help="Print summary instead of full data")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all conversations")
    list_parser.add_argument("--dir", default=DEFAULT_CONTEXT_DIR, help="Context directory")
    
    args = parser.parse_args()
    
    compressor = ConversationCompressor(args.dir if hasattr(args, "dir") else DEFAULT_CONTEXT_DIR)
    
    if args.command == "save":
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
                
            # Validate the conversation format
            if not isinstance(conversation, list):
                print("Error: Conversation must be a list of messages")
                return 1
                
            # Compress and save
            compressed = compressor.compress_conversation(conversation, args.threshold)
            filename = compressor.save_conversation(args.title, conversation, compressed)
            
            print(f"Conversation saved to {filename}")
            print(compressor.summarize_compressed(compressed))
            
        except FileNotFoundError:
            print(f"Error: Input file {args.input_file} not found")
            return 1
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {args.input_file}")
            return 1
            
    elif args.command == "load":
        data = compressor.load_conversation(args.title)
        
        if "error" in data:
            print(data["error"])
            return 1
            
        if args.summary:
            for conv in data.get("conversations", []):
                print(f"Title: {conv.get('title')}")
                print(f"Date: {conv.get('startDate')}")
                print()
                compressed = conv.get("compressed", {})
                print(compressor.summarize_compressed(compressed))
        else:
            print(json.dumps(data, indent=2))
            
    elif args.command == "list":
        conversations = compressor.list_conversations()
        
        if not conversations:
            print("No conversations found")
            return 0
            
        print(f"Found {len(conversations)} conversations:")
        for i, conv in enumerate(conversations, 1):
            print(f"{i}. {conv.get('title')} ({conv.get('messageCount')} messages) - {conv.get('startDate')}")
            
    else:
        parser.print_help()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())

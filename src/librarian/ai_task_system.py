"""
AI-Optimized Todo System for Claude's task tracking
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class TaskReference:
    """Reference to another task, code component, or conversation segment"""
    ref_type: str  # "task", "code", "conversation"
    ref_id: str    # ID of the referenced item
    context: str   # Why this reference exists
    
    
@dataclass
class CodeContext:
    """Information about code related to a task"""
    files: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    
    
@dataclass
class Subtask:
    """Smaller unit of work within a task"""
    id: str
    description: str
    status: str = "pending"  # pending, completed, blocked
    dependencies: List[str] = field(default_factory=list)
    completion_criteria: str = ""
    

@dataclass
class AiTask:
    """
    AI-optimized task structure with rich context and relationships
    """
    # Core identification
    id: str
    title: str
    description: str
    
    # Classification and status
    task_type: str  # "implementation", "refactor", "bugfix", "enhancement", etc.
    status: str     # "active", "completed", "blocked", "deferred"
    priority: int   # Numeric priority (1-5, with 1 being highest)
    urgency: int    # Time-sensitivity (1-5, with 1 being most urgent)
    complexity: int  # Estimated complexity (1-5)
    
    # Organization
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Rich context
    context: str = ""  # Detailed context about why this task exists
    code_context: CodeContext = field(default_factory=CodeContext)
    conversation_refs: List[str] = field(default_factory=list)  # Conversation IDs where this was discussed
    
    # Relationships
    subtasks: List[Subtask] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks that must be completed first
    blockers: List[str] = field(default_factory=list)      # IDs of tasks blocking this one
    related_tasks: List[TaskReference] = field(default_factory=list)
    
    # Temporal information
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    modified: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    estimated_time: Optional[int] = None  # In minutes
    
    # Execution tracking
    progress: int = 0  # 0-100 percent
    notes: List[str] = field(default_factory=list)
    
    def update_modified(self):
        """Update the modified timestamp"""
        self.modified = datetime.now().isoformat()
    
    def add_subtask(self, description: str, completion_criteria: str = "") -> str:
        """Add a subtask and return its ID"""
        subtask_id = f"subtask-{uuid.uuid4().hex[:8]}"
        self.subtasks.append(Subtask(
            id=subtask_id,
            description=description,
            completion_criteria=completion_criteria
        ))
        self.update_modified()
        return subtask_id
    
    def calculate_progress(self) -> int:
        """Calculate progress based on subtasks"""
        if not self.subtasks:
            return self.progress
        
        completed = sum(1 for subtask in self.subtasks if subtask.status == "completed")
        return int((completed / len(self.subtasks)) * 100)
    
    def update_progress(self, progress: Optional[int] = None):
        """Update progress manually or based on subtasks"""
        if progress is not None:
            self.progress = max(0, min(100, progress))
        else:
            self.progress = self.calculate_progress()
        self.update_modified()
        
    def add_code_context(self, 
                        files: Optional[List[str]] = None,
                        components: Optional[List[str]] = None,
                        functions: Optional[List[str]] = None,
                        classes: Optional[List[str]] = None):
        """Add code context to the task"""
        if files:
            self.code_context.files.extend(files)
        if components:
            self.code_context.components.extend(components)
        if functions:
            self.code_context.functions.extend(functions)
        if classes:
            self.code_context.classes.extend(classes)
        self.update_modified()
    
    def add_related_task(self, task_id: str, context: str):
        """Add a related task reference"""
        self.related_tasks.append(TaskReference(
            ref_type="task",
            ref_id=task_id,
            context=context
        ))
        self.update_modified()
    
    def add_conversation_ref(self, conversation_id: str):
        """Add a reference to a conversation"""
        if conversation_id not in self.conversation_refs:
            self.conversation_refs.append(conversation_id)
            self.update_modified()


@dataclass
class AITaskManager:
    """Manager for AI-optimized tasks"""
    storage_path: str
    tasks: Dict[str, AiTask] = field(default_factory=dict)
    indices: Dict[str, Dict[str, Set[str]]] = field(default_factory=lambda: {
        "tags": {},
        "categories": {},
        "status": {},
        "priority": {},
        "task_type": {},
    })
    vector_index: Dict[str, Any] = field(default_factory=dict)  # For semantic search
    last_accessed: Dict[str, float] = field(default_factory=dict)  # Track when tasks were last accessed
    
    def __post_init__(self):
        """Initialize the task manager"""
        self.load_tasks()
        
    def load_tasks(self):
        """Load tasks from storage"""
        storage_dir = Path(self.storage_path)
        if not storage_dir.exists():
            os.makedirs(storage_dir, exist_ok=True)
            return
            
        task_file = storage_dir / "ai_tasks.json"
        if task_file.exists():
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load tasks
                for task_data in data.get("tasks", []):
                    # Convert raw dicts to proper dataclasses
                    if "code_context" in task_data and isinstance(task_data["code_context"], dict):
                        task_data["code_context"] = CodeContext(**task_data["code_context"])
                    
                    if "subtasks" in task_data:
                        subtasks = []
                        for subtask_data in task_data["subtasks"]:
                            subtasks.append(Subtask(**subtask_data))
                        task_data["subtasks"] = subtasks
                    
                    if "related_tasks" in task_data:
                        related_tasks = []
                        for ref_data in task_data["related_tasks"]:
                            related_tasks.append(TaskReference(**ref_data))
                        task_data["related_tasks"] = related_tasks
                    
                    task = AiTask(**task_data)
                    self.tasks[task.id] = task
                    self._index_task(task)
                    
            except Exception as e:
                print(f"Error loading tasks: {e}")
    
    def save_tasks(self):
        """Save tasks to storage"""
        storage_dir = Path(self.storage_path)
        os.makedirs(storage_dir, exist_ok=True)
        
        # Convert tasks to serializable format
        task_list = []
        for task in self.tasks.values():
            task_dict = asdict(task)
            task_list.append(task_dict)
            
        data = {
            "version": "0.2.0",
            "last_updated": datetime.now().isoformat(),
            "tasks": task_list
        }
        
        # Save to file
        task_file = storage_dir / "ai_tasks.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _index_task(self, task: AiTask):
        """Index a task for faster retrieval"""
        # Index by tags
        for tag in task.tags:
            if tag not in self.indices["tags"]:
                self.indices["tags"][tag] = set()
            self.indices["tags"][tag].add(task.id)
        
        # Index by categories
        for category in task.categories:
            if category not in self.indices["categories"]:
                self.indices["categories"][category] = set()
            self.indices["categories"][category].add(task.id)
        
        # Index by status
        if task.status not in self.indices["status"]:
            self.indices["status"][task.status] = set()
        self.indices["status"][task.status].add(task.id)
        
        # Index by priority
        priority_key = str(task.priority)
        if priority_key not in self.indices["priority"]:
            self.indices["priority"][priority_key] = set()
        self.indices["priority"][priority_key].add(task.id)
        
        # Index by task type
        if task.task_type not in self.indices["task_type"]:
            self.indices["task_type"][task.task_type] = set()
        self.indices["task_type"][task.task_type].add(task.id)
        
        # TODO: Add vector indexing for semantic search
    
    def _remove_from_indices(self, task: AiTask):
        """Remove a task from indices"""
        # Remove from tag indices
        for tag in task.tags:
            if tag in self.indices["tags"] and task.id in self.indices["tags"][tag]:
                self.indices["tags"][tag].remove(task.id)
        
        # Remove from category indices
        for category in task.categories:
            if category in self.indices["categories"] and task.id in self.indices["categories"][category]:
                self.indices["categories"][category].remove(task.id)
        
        # Remove from status index
        if task.status in self.indices["status"] and task.id in self.indices["status"][task.status]:
            self.indices["status"][task.status].remove(task.id)
        
        # Remove from priority index
        priority_key = str(task.priority)
        if priority_key in self.indices["priority"] and task.id in self.indices["priority"][priority_key]:
            self.indices["priority"][priority_key].remove(task.id)
        
        # Remove from task type index
        if task.task_type in self.indices["task_type"] and task.id in self.indices["task_type"][task.task_type]:
            self.indices["task_type"][task.task_type].remove(task.id)
        
        # TODO: Remove from vector index
    
    def create_task(self, 
                   title: str, 
                   description: str, 
                   task_type: str = "enhancement",
                   priority: int = 3,
                   urgency: int = 3,
                   complexity: int = 3,
                   tags: Optional[List[str]] = None,
                   categories: Optional[List[str]] = None,
                   context: str = "") -> str:
        """Create a new task and return its ID"""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        task = AiTask(
            id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            status="active",
            priority=priority,
            urgency=urgency,
            complexity=complexity,
            tags=tags or [],
            categories=categories or [],
            context=context
        )
        
        self.tasks[task_id] = task
        self._index_task(task)
        self.last_accessed[task_id] = time.time()
        self.save_tasks()
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[AiTask]:
        """Get a task by ID"""
        task = self.tasks.get(task_id)
        if task:
            self.last_accessed[task_id] = time.time()
        return task
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task with new values"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        # Remove from indices before updating
        self._remove_from_indices(task)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Update modified timestamp
        task.update_modified()
        
        # Re-index the task
        self._index_task(task)
        self.last_accessed[task_id] = time.time()
        self.save_tasks()
        
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id not in self.tasks:
            return False
        
        # Remove from indices
        self._remove_from_indices(self.tasks[task_id])
        
        # Remove from tasks dictionary
        del self.tasks[task_id]
        if task_id in self.last_accessed:
            del self.last_accessed[task_id]
        
        self.save_tasks()
        return True
    
    def list_tasks(self, 
                  status: Optional[str] = None,
                  priority: Optional[int] = None,
                  task_type: Optional[str] = None,
                  tags: Optional[List[str]] = None,
                  categories: Optional[List[str]] = None) -> List[AiTask]:
        """List tasks with optional filtering"""
        # Start with all task IDs
        task_ids = set(self.tasks.keys())
        
        # Apply filters using indices for efficiency
        if status:
            status_ids = self.indices["status"].get(status, set())
            task_ids = task_ids.intersection(status_ids)
        
        if priority is not None:
            priority_key = str(priority)
            priority_ids = self.indices["priority"].get(priority_key, set())
            task_ids = task_ids.intersection(priority_ids)
        
        if task_type:
            type_ids = self.indices["task_type"].get(task_type, set())
            task_ids = task_ids.intersection(type_ids)
        
        if tags:
            tag_ids = set()
            for tag in tags:
                tag_ids = tag_ids.union(self.indices["tags"].get(tag, set()))
            task_ids = task_ids.intersection(tag_ids)
        
        if categories:
            category_ids = set()
            for category in categories:
                category_ids = category_ids.union(self.indices["categories"].get(category, set()))
            task_ids = task_ids.intersection(category_ids)
        
        # Convert IDs to tasks
        tasks = [self.tasks[task_id] for task_id in task_ids]
        
        # Sort by priority (highest first) and then by urgency
        tasks.sort(key=lambda t: (t.priority, t.urgency))
        
        # Update last accessed
        for task in tasks:
            self.last_accessed[task.id] = time.time()
        
        return tasks
    
    def search_tasks(self, query: str) -> List[AiTask]:
        """Search tasks by text (basic implementation)"""
        query = query.lower()
        results = []
        
        for task in self.tasks.values():
            # Check title, description, and context
            if (query in task.title.lower() or 
                query in task.description.lower() or 
                query in task.context.lower()):
                results.append(task)
                self.last_accessed[task.id] = time.time()
        
        # Sort by relevance (simple implementation)
        results.sort(key=lambda t: (
            # Exact title match is best
            0 if query == t.title.lower() else
            # Title contains query is next best
            1 if query in t.title.lower() else
            # Description/context contains query is last
            2
        ))
        
        return results
    
    def get_task_with_dependencies(self, task_id: str) -> Tuple[Optional[AiTask], List[AiTask]]:
        """Get a task and its dependencies"""
        task = self.get_task(task_id)
        if not task:
            return None, []
        
        # Get dependencies
        dependencies = []
        for dep_id in task.dependencies:
            dep_task = self.get_task(dep_id)
            if dep_task:
                dependencies.append(dep_task)
        
        return task, dependencies
    
    def get_dependent_tasks(self, task_id: str) -> List[AiTask]:
        """Get tasks that depend on this task"""
        dependent_tasks = []
        
        for task in self.tasks.values():
            if task_id in task.dependencies:
                dependent_tasks.append(task)
                self.last_accessed[task.id] = time.time()
        
        return dependent_tasks
    
    def get_related_tasks(self, task_id: str) -> List[AiTask]:
        """Get tasks related to this task"""
        task = self.get_task(task_id)
        if not task:
            return []
        
        related_tasks = []
        for ref in task.related_tasks:
            if ref.ref_type == "task":
                related_task = self.get_task(ref.ref_id)
                if related_task:
                    related_tasks.append(related_task)
        
        return related_tasks


def initialize_ai_task_manager(project_path: str) -> AITaskManager:
    """Initialize the AI task manager for a project"""
    storage_path = os.path.join(project_path, ".ai_reference", "todos")
    return AITaskManager(storage_path=storage_path)


# MCP Tool Functions
def add_ai_task(project_path: str, 
               title: str, 
               description: str, 
               task_type: str = "enhancement", 
               priority: int = 3,
               tags: str = "") -> str:
    """Add a new AI-optimized task"""
    manager = initialize_ai_task_manager(project_path)
    
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    # Create the task
    task_id = manager.create_task(
        title=title,
        description=description,
        task_type=task_type,
        priority=priority,
        tags=tag_list
    )
    
    return f"✅ AI-Task added with ID: {task_id}\n\nTitle: {title}\nPriority: {priority}\nType: {task_type}"


def list_ai_tasks(project_path: str, 
                 status: str = "active", 
                 priority: Optional[int] = None, 
                 task_type: Optional[str] = None,
                 tag: Optional[str] = None) -> str:
    """List AI-optimized tasks with filtering"""
    manager = initialize_ai_task_manager(project_path)
    
    # Parse tag filter
    tags = None
    if tag:
        tags = [tag]
    
    # Get filtered tasks
    tasks = manager.list_tasks(
        status=status,
        priority=priority,
        task_type=task_type,
        tags=tags
    )
    
    if not tasks:
        return f"No AI-tasks found with the specified filters.\n\nStatus: {status}\nPriority: {priority if priority is not None else 'any'}\nType: {task_type if task_type else 'any'}\nTag: {tag if tag else 'any'}"
    
    # Format output
    # Using a compact format designed for AI processing
    output = []
    
    for task in tasks:
        # Format tags
        tags_str = ", ".join(task.tags)
        
        # Format subtasks
        subtasks_str = ""
        if task.subtasks:
            completed = sum(1 for st in task.subtasks if st.status == "completed")
            subtasks_str = f" [{completed}/{len(task.subtasks)} subtasks]"
        
        # Build task summary line
        line = f"ID:{task.id} | P{task.priority}U{task.urgency}C{task.complexity} | {task.status.upper()} | {task.task_type} | {task.title}{subtasks_str}"
        
        # Add tags if present
        if tags_str:
            line += f" | Tags: {tags_str}"
            
        output.append(line)
    
    return "\n".join(output)


def search_ai_tasks(project_path: str, query: str) -> str:
    """Search AI-optimized tasks by text"""
    manager = initialize_ai_task_manager(project_path)
    
    # Search tasks
    tasks = manager.search_tasks(query)
    
    if not tasks:
        return f"No AI-tasks found matching query: {query}"
    
    # Format output
    output = []
    
    for task in tasks:
        # Format tags
        tags_str = ", ".join(task.tags)
        
        # Build task summary line
        line = f"ID:{task.id} | P{task.priority}U{task.urgency} | {task.status.upper()} | {task.task_type} | {task.title}"
        
        # Add tags if present
        if tags_str:
            line += f" | Tags: {tags_str}"
            
        # Add snippet of matching context
        snippets = []
        query_lower = query.lower()
        
        # Check title
        if query_lower in task.title.lower():
            title_ctx = task.title
            snippets.append(f"Title: {title_ctx}")
        
        # Check description
        if query_lower in task.description.lower():
            desc_parts = task.description.split("\n")
            for part in desc_parts:
                if query_lower in part.lower():
                    snippets.append(f"Desc: {part[:100]}...")
                    break
        
        # Add snippets if found
        if snippets:
            line += f"\n  > {' | '.join(snippets)}"
            
        output.append(line)
    
    return "\n".join(output)


def get_ai_task(project_path: str, task_id: str) -> str:
    """Get detailed information about an AI-optimized task"""
    manager = initialize_ai_task_manager(project_path)
    
    # Get task
    task = manager.get_task(task_id)
    
    if not task:
        return f"❌ AI-Task not found: {task_id}"
    
    # Format output
    output = [
        f"ID: {task.id}",
        f"Title: {task.title}",
        f"Status: {task.status}",
        f"Type: {task.task_type}",
        f"Priority: {task.priority}",
        f"Urgency: {task.urgency}",
        f"Complexity: {task.complexity}",
        f"Progress: {task.progress}%",
        f"Created: {task.created}",
        f"Modified: {task.modified}"
    ]
    
    if task.due_date:
        output.append(f"Due Date: {task.due_date}")
    
    if task.estimated_time:
        output.append(f"Estimated Time: {task.estimated_time} minutes")
    
    if task.tags:
        output.append(f"Tags: {', '.join(task.tags)}")
    
    if task.categories:
        output.append(f"Categories: {', '.join(task.categories)}")
    
    # Add description
    output.append("\nDescription:")
    output.append(task.description)
    
    # Add context if present
    if task.context:
        output.append("\nContext:")
        output.append(task.context)
    
    # Add subtasks if present
    if task.subtasks:
        output.append("\nSubtasks:")
        for subtask in task.subtasks:
            status_marker = "✅" if subtask.status == "completed" else "⬜"
            output.append(f"{status_marker} {subtask.id}: {subtask.description}")
    
    # Add dependencies if present
    if task.dependencies:
        output.append("\nDependencies:")
        for dep_id in task.dependencies:
            dep_task = manager.get_task(dep_id)
            if dep_task:
                output.append(f"- {dep_id}: {dep_task.title}")
            else:
                output.append(f"- {dep_id}: [Not found]")
    
    # Add code context if present
    if (task.code_context.files or task.code_context.components or 
        task.code_context.functions or task.code_context.classes):
        output.append("\nCode Context:")
        
        if task.code_context.files:
            output.append("Files:")
            for file in task.code_context.files:
                output.append(f"- {file}")
        
        if task.code_context.components:
            output.append("Components:")
            for comp in task.code_context.components:
                output.append(f"- {comp}")
        
        if task.code_context.functions:
            output.append("Functions:")
            for func in task.code_context.functions:
                output.append(f"- {func}")
        
        if task.code_context.classes:
            output.append("Classes:")
            for cls in task.code_context.classes:
                output.append(f"- {cls}")
    
    return "\n".join(output)


def update_ai_task_status(project_path: str, task_id: str, status: str) -> str:
    """Update the status of an AI-optimized task"""
    manager = initialize_ai_task_manager(project_path)
    
    # Validate status
    valid_statuses = ["active", "completed", "blocked", "deferred"]
    if status not in valid_statuses:
        return f"❌ Invalid status: {status}. Valid values are: {', '.join(valid_statuses)}"
    
    # Update task
    result = manager.update_task(task_id, status=status)
    
    if not result:
        return f"❌ AI-Task not found: {task_id}"
    
    return f"✅ Updated status of AI-Task {task_id} to {status}"


def add_subtask(project_path: str, task_id: str, title: str, criteria: str = "") -> str:
    """Add a subtask to an AI-optimized task"""
    manager = initialize_ai_task_manager(project_path)
    
    # Get task
    task = manager.get_task(task_id)
    
    if not task:
        return f"❌ AI-Task not found: {task_id}"
    
    # Add subtask
    subtask_id = task.add_subtask(description=title, completion_criteria=criteria)
    
    # Update task
    manager.save_tasks()
    
    return f"✅ Added subtask {subtask_id} to AI-Task {task_id}"


def update_subtask_status(project_path: str, task_id: str, subtask_id: str, status: str) -> str:
    """Update the status of a subtask"""
    manager = initialize_ai_task_manager(project_path)
    
    # Get task
    task = manager.get_task(task_id)
    
    if not task:
        return f"❌ AI-Task not found: {task_id}"
    
    # Find subtask
    subtask = next((st for st in task.subtasks if st.id == subtask_id), None)
    
    if not subtask:
        return f"❌ Subtask not found: {subtask_id}"
    
    # Validate status
    valid_statuses = ["pending", "completed", "blocked"]
    if status not in valid_statuses:
        return f"❌ Invalid status: {status}. Valid values are: {', '.join(valid_statuses)}"
    
    # Update subtask
    subtask.status = status
    task.update_modified()
    task.update_progress()
    
    # Save changes
    manager.save_tasks()
    
    return f"✅ Updated status of subtask {subtask_id} to {status}"


def infer_tasks(project_path: str, text: str) -> str:
    """Analyze text and extract potential AI-optimized tasks"""
    from collections import namedtuple
    
    # Define patterns for task identification
    TaskPattern = namedtuple('TaskPattern', ['regex', 'task_type', 'priority'])
    import re
    
    patterns = [
        # High priority implementation tasks
        TaskPattern(
            regex=re.compile(r"(?:need|must|should|important|urgent).*(?:implement|create|build|develop)", re.I),
            task_type="implementation",
            priority=1
        ),
        # Medium priority implementation tasks
        TaskPattern(
            regex=re.compile(r"(?:let's|we should|would be good to).*(?:implement|create|build|develop)", re.I),
            task_type="implementation",
            priority=2
        ),
        # Bug fixes (high priority)
        TaskPattern(
            regex=re.compile(r"(?:bug|issue|problem|error|fix|broken).*(?:needs|requires|should be|must be).*(?:fixed|addressed|resolved)", re.I),
            task_type="bugfix",
            priority=1
        ),
        # Enhancements (medium priority)
        TaskPattern(
            regex=re.compile(r"(?:enhance|improve|optimize|refine|extend).*(?:functionality|feature|component|system|performance)", re.I),
            task_type="enhancement",
            priority=2
        ),
        # Refactoring tasks (medium priority)
        TaskPattern(
            regex=re.compile(r"(?:refactor|restructure|reorganize|clean up|rewrite).*(?:code|module|class|function)", re.I),
            task_type="refactor",
            priority=2
        ),
        # Documentation tasks (lower priority)
        TaskPattern(
            regex=re.compile(r"(?:document|add docs|explain|write up).*(?:functionality|usage|api|method|class)", re.I),
            task_type="documentation",
            priority=3
        ),
        # Research tasks
        TaskPattern(
            regex=re.compile(r"(?:research|investigate|look into|explore|study).*(?:approach|solution|technology|framework|library)", re.I),
            task_type="research",
            priority=2
        ),
        # Review tasks
        TaskPattern(
            regex=re.compile(r"(?:review|evaluate|assess|analyze).*(?:code|implementation|design|approach|solution)", re.I),
            task_type="review",
            priority=2
        ),
        # Todo marker
        TaskPattern(
            regex=re.compile(r"(?:TODO|FIXME|HACK|XXX)[:;\-\s]+(.*?)(?:\n|$)", re.I),
            task_type="enhancement",
            priority=2
        )
    ]
    
    # Split text into sentences/paragraphs for analysis
    lines = text.split('\n')
    sentences = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Split longer lines into sentences
        line_sentences = re.split(r'(?<=[.!?])\s+', line)
        sentences.extend([s for s in line_sentences if s.strip()])
    
    # Initialize task manager
    manager = initialize_ai_task_manager(project_path)
    
    # Extract tasks
    extracted_tasks = []
    
    for sentence in sentences:
        for pattern in patterns:
            match = pattern.regex.search(sentence)
            if match:
                # Create a task from this match
                task_id = manager.create_task(
                    title=sentence.strip(),
                    description=f"Automatically extracted from conversation:\n\n{text[:500]}...",
                    task_type=pattern.task_type,
                    priority=pattern.priority,
                    tags=["auto-extracted"],
                    context=f"Extracted from conversation context. Full sentence: {sentence}"
                )
                
                extracted_tasks.append((task_id, sentence.strip(), pattern.task_type, pattern.priority))
                break  # Only extract one task per sentence
    
    # Generate response
    if not extracted_tasks:
        return "No tasks were automatically identified in the provided text."
    
    output = [f"Extracted {len(extracted_tasks)} AI-Tasks:"]
    
    for task_id, title, task_type, priority in extracted_tasks:
        output.append(f"- {task_id}: [{task_type} P{priority}] {title}")
    
    return "\n".join(output)


# Initializing the system when setting up an AI Librarian for a project
def setup_ai_task_system(project_path: str):
    """Set up the AI-optimized task system for a project"""
    # Create task directory
    task_dir = os.path.join(project_path, ".ai_reference", "todos")
    os.makedirs(task_dir, exist_ok=True)
    
    # Initialize the task manager
    manager = initialize_ai_task_manager(project_path)
    
    # Save initial state
    manager.save_tasks()
    
    return f"AI-optimized task system initialized at {task_dir}"


# Migration script to upgrade from old todo system
def migrate_old_todos(project_path: str):
    """Migrate from the old todo system to the new AI-optimized task system"""
    old_todo_file = os.path.join(project_path, ".ai_reference", "todos", "todo_list.json")
    
    if not os.path.exists(old_todo_file):
        return "No old todo list found, nothing to migrate."
    
    try:
        # Load old todos
        with open(old_todo_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        # Initialize new task manager
        manager = initialize_ai_task_manager(project_path)
        
        # Convert old todos to new format
        migrated_count = 0
        
        for old_todo in old_data.get("items", []):
            # Map old status to new status
            status_map = {
                "active": "active",
                "completed": "completed",
                "deferred": "deferred"
            }
            status = status_map.get(old_todo.get("status", "active"), "active")
            
            # Map old priority to new priority
            priority_map = {
                "high": 1,
                "medium": 2,
                "low": 3
            }
            priority = priority_map.get(old_todo.get("priority", "medium"), 2)
            
            # Determine task type based on tags
            tags = old_todo.get("tags", [])
            task_type = "enhancement"  # Default
            
            if "bugfix" in tags:
                task_type = "bugfix"
            elif "implementation" in tags:
                task_type = "implementation"
            elif "documentation" in tags:
                task_type = "documentation"
            elif "refactor" in tags:
                task_type = "refactor"
            
            # Create new task
            task_id = manager.create_task(
                title=old_todo.get("title", "Untitled Task"),
                description=old_todo.get("description", ""),
                task_type=task_type,
                status=status,
                priority=priority,
                tags=tags,
                context=f"Migrated from old todo system. Original ID: {old_todo.get('id', 'unknown')}"
            )
            
            # Migrate subtasks if present
            for subtask in old_todo.get("subtasks", []):
                subtask_status = "completed" if subtask.get("completed", False) else "pending"
                manager.get_task(task_id).add_subtask(
                    description=subtask.get("title", "Untitled Subtask"),
                    completion_criteria=""
                )
            
            migrated_count += 1
        
        # Backup old todo file
        backup_file = old_todo_file + ".bak"
        import shutil
        shutil.copy2(old_todo_file, backup_file)
        
        return f"Successfully migrated {migrated_count} todos to the new AI-optimized task system. Old todos backed up to {backup_file}"
        
    except Exception as e:
        return f"Error migrating old todos: {str(e)}"

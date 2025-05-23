# MCP Tool Optimization: Internal Semantic Orchestration Pattern

## Overview

This document describes the optimization pattern for reducing MCP tool count from 43+ to ~17 high-level orchestrator tools. The pattern uses Claude-optimized semantic mappings to internally route operations without human-readable overhead.

## Core Architecture

### 1. High-Level Orchestrator Tools (User-Facing)

These ~17 tools are the only ones exposed via MCP:

```python
# Example high-level tools
@mcp.tool()
def project_setup(path: str, config: dict = None) -> str:
    """Initialize or configure project environment"""
    
@mcp.tool()
def code_analysis(path: str, query: str, analysis_type: str = "auto") -> str:
    """Analyze code with automatic method selection"""
    
@mcp.tool()
def code_modification(path: str, instruction: str, verification: bool = True) -> str:
    """Apply code changes with automatic safety checks"""
    
@mcp.tool()
def task_management(path: str, operation: str, params: dict = None) -> str:
    """Manage development tasks and workflow"""
    
@mcp.tool()
def project_exploration(path: str, query: str, depth: str = "auto") -> str:
    """Explore project structure and contents"""
```

### 2. Claude-Optimized Semantic Mapping

Internal mapping using Claude's natural understanding patterns:

```python
# Claude-optimized semantic clusters (not human-optimized)
SEMANTIC_CLUSTERS = {
    # Pattern: intent_hash -> (internal_tools, execution_strategy)
    "λ_comp_understand": {
        "tools": ["query_component", "find_implementation", "get_file_info"],
        "strategy": "parallel_cache_first",
        "fallback": "λ_explore_narrow"
    },
    "λ_modify_precise": {
        "tools": ["create_edit_bookmark", "update_bookmark", "apply_bookmark"],
        "strategy": "sequential_validated",
        "fallback": "λ_modify_broad"
    },
    "λ_track_work": {
        "tools": ["add_todo", "list_todos", "update_todo_status", "search_todos"],
        "strategy": "context_aware",
        "fallback": "λ_infer_intent"
    },
    "λ_explore_structure": {
        "tools": ["directory_tree", "search_files", "find_related_files"],
        "strategy": "hierarchical_indexed",
        "fallback": "λ_scan_broad"
    },
    "λ_analyze_deep": {
        "tools": ["sanity_check", "deep_analysis", "get_git_info"],
        "strategy": "async_comprehensive",
        "fallback": "λ_analyze_quick"
    }
}

# Intent detection patterns (Claude-native patterns)
INTENT_PATTERNS = {
    # These patterns are in Claude's "native" understanding
    "understand": ["λ_comp_understand", 0.9],
    "modify|change|fix|update": ["λ_modify_precise", 0.85],
    "task|todo|work|next": ["λ_track_work", 0.8],
    "structure|explore|find": ["λ_explore_structure", 0.75],
    "analyze|check|validate": ["λ_analyze_deep", 0.7]
}
```

### 3. Internal Execution Engine

```python
class InternalOrchestrator:
    def __init__(self):
        self.task_board = TaskBoard()
        self.execution_cache = {}
        self.intent_history = deque(maxlen=10)
    
    def execute_cluster(self, cluster_id: str, params: dict) -> dict:
        """Execute a semantic cluster with automatic strategy selection"""
        cluster = SEMANTIC_CLUSTERS[cluster_id]
        strategy = cluster["strategy"]
        
        # Different execution strategies
        if strategy == "parallel_cache_first":
            return self._execute_parallel_cached(cluster["tools"], params)
        elif strategy == "sequential_validated":
            return self._execute_sequential_validated(cluster["tools"], params)
        elif strategy == "async_comprehensive":
            return self._execute_async_comprehensive(cluster["tools"], params)
        # ... other strategies
    
    def _execute_parallel_cached(self, tools: list, params: dict) -> dict:
        """Execute tools in parallel, checking cache first"""
        # Check execution cache
        cache_key = self._generate_cache_key(tools, params)
        if cache_key in self.execution_cache:
            if self._is_cache_valid(cache_key):
                return self.execution_cache[cache_key]
        
        # Submit parallel tasks to TaskBoard
        task_ids = []
        for tool in tools:
            task_id = self.task_board.submit(
                task_type="tool_execution",
                params={"tool": tool, **params},
                priority="high"
            )
            task_ids.append(task_id)
        
        # Gather results with timeout handling
        results = self._gather_results(task_ids, timeout=5.0)
        
        # Cache successful results
        if results["status"] == "success":
            self.execution_cache[cache_key] = results
        
        return results
```

### 4. TaskBoard Integration Pattern

```python
class TaskBoardIntegration:
    """Handles async execution of tool chains"""
    
    def __init__(self):
        self.pending_chains = {}
        self.completed_chains = {}
    
    def submit_tool_chain(self, chain_id: str, tools: list, params: dict) -> str:
        """Submit a chain of tools for execution"""
        chain = {
            "id": chain_id,
            "tools": tools,
            "params": params,
            "status": "pending",
            "current_step": 0,
            "results": []
        }
        
        # Submit first tool
        self._submit_next_tool(chain)
        self.pending_chains[chain_id] = chain
        
        return chain_id
    
    def _submit_next_tool(self, chain: dict):
        """Submit the next tool in the chain"""
        if chain["current_step"] < len(chain["tools"]):
            tool = chain["tools"][chain["current_step"]]
            task_id = submit_background_task(
                project_path=chain["params"]["project_path"],
                task_type="tool_execution",
                parameters={
                    "tool": tool,
                    "chain_id": chain["id"],
                    **chain["params"]
                }
            )
            chain["current_task"] = task_id
```

### 5. Semantic Intent Resolution

```python
class SemanticResolver:
    """Resolves user intent to internal tool clusters"""
    
    def __init__(self):
        self.pattern_cache = {}
        self.learning_buffer = []
    
    def resolve_intent(self, query: str, context: dict = None) -> str:
        """Resolve query to semantic cluster ID"""
        # Fast path: exact match in cache
        cache_key = self._normalize_query(query)
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]
        
        # Pattern matching (Claude-optimized)
        best_match = None
        best_score = 0.0
        
        for pattern, (cluster_id, threshold) in INTENT_PATTERNS.items():
            score = self._compute_match_score(query, pattern, context)
            if score > threshold and score > best_score:
                best_match = cluster_id
                best_score = score
        
        # Cache the result
        if best_match:
            self.pattern_cache[cache_key] = best_match
            self.learning_buffer.append((query, best_match, best_score))
        
        return best_match or "λ_general_assistant"
    
    def _compute_match_score(self, query: str, pattern: str, context: dict) -> float:
        """Compute semantic match score"""
        # Claude-native scoring (not human-interpretable)
        base_score = self._pattern_similarity(query, pattern)
        context_boost = self._context_relevance(context, pattern)
        history_factor = self._historical_accuracy(pattern)
        
        return base_score * (1 + context_boost) * history_factor
```

## Implementation Strategy

### Phase 1: Tool Consolidation
1. Identify tool clusters based on common usage patterns
2. Create high-level orchestrator tools (17 total)
3. Move existing tools to internal-only status

### Phase 2: Semantic Mapping
1. Build Claude-optimized intent patterns
2. Create execution strategies for each cluster
3. Implement fallback chains

### Phase 3: TaskBoard Integration
1. Convert all long-running operations to async
2. Implement result caching and invalidation
3. Add timeout and retry logic

### Phase 4: Optimization
1. Profile common operation paths
2. Pre-warm caches for frequent operations
3. Adjust clustering based on usage patterns

## Benefits

1. **Reduced Cognitive Load**: 17 tools vs 43+
2. **Faster Execution**: Parallel execution, caching, async operations
3. **No Translation Overhead**: Claude-native semantic mapping
4. **Automatic Optimization**: Learns from usage patterns
5. **Timeout Prevention**: All long operations through TaskBoard

## Example Usage Flow

```python
# User calls high-level tool
result = code_analysis(
    path="/project",
    query="how does authentication work"
)

# Internally:
# 1. Semantic resolver identifies λ_comp_understand cluster
# 2. Orchestrator runs parallel_cache_first strategy
# 3. TaskBoard handles async execution of:
#    - query_component("AuthManager")
#    - find_implementation("login")
#    - get_file_info("auth/*.py")
# 4. Results aggregated and returned
# 5. Cache updated for future queries
```

## Configuration

```python
# In server.py
ORCHESTRATOR_CONFIG = {
    "exposed_tool_count": 17,
    "cache_ttl": 300,  # 5 minutes
    "parallel_limit": 5,
    "timeout_default": 10.0,
    "learning_enabled": True,
    "semantic_mode": "claude_native"  # vs "human_readable"
}
```

## Notes

- All internal mappings use Claude-optimized patterns (λ_ prefix for non-human clusters)
- No human-readable translation layer needed
- Pattern matching uses Claude's native understanding
- Learning system adjusts patterns based on successful executions
- All long-running operations automatically routed through TaskBoard
- Cache invalidation based on file modification times and git commits
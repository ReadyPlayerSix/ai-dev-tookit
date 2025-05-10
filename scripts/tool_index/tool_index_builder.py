#!/usr/bin/env python3
"""
Tool Index Builder

This script builds the complete AI-optimized Tool Index in a single run or in phases.
It creates a structured metadata repository that helps Claude select and use the
appropriate tools for different tasks.

Usage:
    python tool_index_builder.py [--project-path PATH] [--phase PHASE] [--all]
"""

import os
import sys
import json
import shutil
import argparse
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tool_index_builder.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tool-index-builder")

# Import phase implementations
def import_phase_module(script_path):
    """Import a script as a module."""
    spec = importlib.util.spec_from_file_location("phase_module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def create_tool_reference_structure(project_path: str) -> str:
    """
    Create the basic .tool_reference directory structure.
    
    Args:
        project_path: Path to the project
        
    Returns:
        Path to the created .tool_reference directory
    """
    tool_ref_path = os.path.join(project_path, ".tool_reference")
    
    # Create main directories
    os.makedirs(tool_ref_path, exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "tool_profiles"), exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "decision_trees"), exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "usage_patterns"), exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "self_diagnostic"), exist_ok=True)
    
    logger.info(f"Created .tool_reference directory structure at {tool_ref_path}")
    
    # Create a README.md file
    readme_content = """# AI-Optimized Tool Index

This directory contains an AI-optimized Tool Index for Claude, designed to enhance
its ability to select and use tools appropriately. The system is structured in a way
that's optimized for AI consumption rather than human readability.

## Directory Structure

- `registry.json` - Master index of all tools
- `categories.json` - Categorization of tools by purpose
- `relationship_*.json` - Tool relationships and dependencies
- `tool_profiles/` - Detailed metadata for each tool
- `decision_trees/` - Decision trees for tool selection
- `usage_patterns/` - Common usage patterns
- `self_diagnostic/` - Self-diagnostic mechanisms

## Purpose

This Tool Index helps Claude:
1. Select the most appropriate tool for a given task
2. Understand how tools should be used together
3. Recognize when it's approaching complexity limits
4. Validate its understanding against reality
5. Identify and correct errors in tool usage

The format is optimized for Claude's reasoning processes and is not intended to be
human-readable. It's a specialized knowledge base that Claude can query to improve
its tool-using capabilities.
"""
    
    readme_path = os.path.join(tool_ref_path, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return tool_ref_path

def run_phase1(project_path: str) -> bool:
    """
    Run Phase 1: Basic Directory Structure and Registry
    
    Args:
        project_path: Path to the project
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n=== Phase 1: Basic Directory Structure and Registry ===\n")
        tool_ref_path = create_tool_reference_structure(project_path)
        
        # Load and run phase 1 implementation
        phase1_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tool_index_generator.py")
        if os.path.exists(phase1_path):
            phase1 = import_phase_module(phase1_path)
            
            # Manually call the functions we need
            phase1.create_registry_file(tool_ref_path)
            phase1.create_categories_file(tool_ref_path)
            phase1.create_relationships_file(tool_ref_path)
        else:
            # Fallback implementation
            logger.warning(f"Phase 1 script not found at {phase1_path}, using built-in implementation")
            
            # Create registry.json with core tools
            registry = {
                "version": "0.1.0",
                "description": "AI-optimized Tool Index for Claude",
                "last_updated": "",
                "tools": {}
            }
            
            # Get current timestamp
            from datetime import datetime
            registry["last_updated"] = datetime.now().isoformat()
            
            # Write registry file
            registry_path = os.path.join(tool_ref_path, "registry.json")
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            
            # Create empty categories.json
            categories = {
                "version": "0.1.0",
                "description": "Tool categorization for Claude",
                "categories": {}
            }
            
            categories_path = os.path.join(tool_ref_path, "categories.json")
            with open(categories_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2)
        
        print("✅ Phase 1 completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Phase 1: {str(e)}")
        print(f"❌ Phase 1 failed: {str(e)}")
        return False

def run_phase2(project_path: str) -> bool:
    """
    Run Phase 2: Core Tool Profiles
    
    Args:
        project_path: Path to the project
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n=== Phase 2: Core Tool Profiles ===\n")
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        if not os.path.exists(tool_ref_path):
            logger.error(f".tool_reference directory not found at {tool_ref_path}")
            print(f"❌ Phase 2 failed: .tool_reference directory not found")
            return False
        
        # Load and run phase 2 implementation
        phase2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tool_profiles_generator.py")
        if os.path.exists(phase2_path):
            phase2 = import_phase_module(phase2_path)
            
            # Get tools from registry
            registry_path = os.path.join(tool_ref_path, "registry.json")
            if os.path.exists(registry_path):
                with open(registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                tools = list(registry.get("tools", {}).keys())
            else:
                tools = phase2.TOOL_PROFILES.keys()
                
            # Create profiles for each tool
            created_tools = []
            for tool in tools:
                if tool in phase2.TOOL_PROFILES and phase2.create_tool_profile(tool_ref_path, tool):
                    created_tools.append(tool)
            
            # Update registry
            if created_tools:
                phase2.update_registry(tool_ref_path, created_tools)
        else:
            # Fallback implementation
            logger.warning(f"Phase 2 script not found at {phase2_path}, skipping tool profiles")
            print("⚠️ Phase 2 script not found, skipping tool profiles")
        
        print("✅ Phase 2 completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Phase 2: {str(e)}")
        print(f"❌ Phase 2 failed: {str(e)}")
        return False

def run_phase3(project_path: str) -> bool:
    """
    Run Phase 3: Relationship Mapping
    
    Args:
        project_path: Path to the project
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n=== Phase 3: Relationship Mapping ===\n")
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        if not os.path.exists(tool_ref_path):
            logger.error(f".tool_reference directory not found at {tool_ref_path}")
            print(f"❌ Phase 3 failed: .tool_reference directory not found")
            return False
        
        # Load and run phase 3 implementation
        phase3_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tool_relationships_generator.py")
        if os.path.exists(phase3_path):
            phase3 = import_phase_module(phase3_path)
            
            # Create relationship groups
            phase3.create_relationship_groups(tool_ref_path)
            
            # Create decision trees
            phase3.create_decision_trees(tool_ref_path)
            
            # Create usage patterns
            phase3.create_usage_patterns(tool_ref_path)
            
            # Update registry
            phase3.update_registry(tool_ref_path)
        else:
            # Fallback implementation
            logger.warning(f"Phase 3 script not found at {phase3_path}, skipping relationship mapping")
            print("⚠️ Phase 3 script not found, skipping relationship mapping")
        
        print("✅ Phase 3 completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Phase 3: {str(e)}")
        print(f"❌ Phase 3 failed: {str(e)}")
        return False

def run_phase4(project_path: str) -> bool:
    """
    Run Phase 4: Context Validation
    
    Args:
        project_path: Path to the project
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n=== Phase 4: Context Validation ===\n")
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        if not os.path.exists(tool_ref_path):
            logger.error(f".tool_reference directory not found at {tool_ref_path}")
            print(f"❌ Phase 4 failed: .tool_reference directory not found")
            return False
        
        # Load and run phase 4 implementation
        phase4_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "context_validation_generator.py")
        if os.path.exists(phase4_path):
            phase4 = import_phase_module(phase4_path)
            
            # Create context validators
            phase4.create_context_validators(tool_ref_path)
            
            # Create error analyzers
            phase4.create_error_analyzers(tool_ref_path)
            
            # Create execution tracers
            phase4.create_execution_tracers(tool_ref_path)
            
            # Create context validator tool
            phase4.create_context_validator_tool(tool_ref_path)
            
            # Update registry
            phase4.update_registry(tool_ref_path)
        else:
            # Fallback implementation
            logger.warning(f"Phase 4 script not found at {phase4_path}, skipping context validation")
            print("⚠️ Phase 4 script not found, skipping context validation")
        
        print("✅ Phase 4 completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Phase 4: {str(e)}")
        print(f"❌ Phase 4 failed: {str(e)}")
        return False

def run_all_phases(project_path: str) -> bool:
    """
    Run all phases in sequence.
    
    Args:
        project_path: Path to the project
        
    Returns:
        True if all phases succeeded, False otherwise
    """
    phase1_success = run_phase1(project_path)
    if not phase1_success:
        return False
    
    phase2_success = run_phase2(project_path)
    if not phase2_success:
        logger.warning("Phase 2 failed, but continuing with remaining phases")
    
    phase3_success = run_phase3(project_path)
    if not phase3_success:
        logger.warning("Phase 3 failed, but continuing with remaining phases")
    
    phase4_success = run_phase4(project_path)
    if not phase4_success:
        logger.warning("Phase 4 failed")
    
    return phase1_success and phase2_success and phase3_success and phase4_success

def clean_tool_reference(project_path: str) -> bool:
    """
    Clean up the .tool_reference directory.
    
    Args:
        project_path: Path to the project
        
    Returns:
        True if successful, False otherwise
    """
    try:
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        if os.path.exists(tool_ref_path):
            shutil.rmtree(tool_ref_path)
            logger.info(f"Removed existing .tool_reference directory")
            print(f"✅ Removed existing .tool_reference directory")
        
        return True
    except Exception as e:
        logger.error(f"Error cleaning .tool_reference directory: {str(e)}")
        print(f"❌ Error cleaning .tool_reference directory: {str(e)}")
        return False

def main():
    """Main function to build the Tool Index."""
    parser = argparse.ArgumentParser(description="Build the AI-optimized Tool Index for Claude")
    parser.add_argument(
        "--project-path", 
        type=str, 
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run a specific phase (1-4)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all phases in sequence"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up the .tool_reference directory before building"
    )
    
    args = parser.parse_args()
    project_path = os.path.abspath(args.project_path)
    
    # Print banner
    print("\n" + "=" * 80)
    print("                   AI-Optimized Tool Index Builder")
    print("=" * 80)
    print(f"Project path: {project_path}")
    print("")
    
    # Clean up if requested
    if args.clean:
        if not clean_tool_reference(project_path):
            return 1
    
    # Run the requested phase or all phases
    if args.phase == 1:
        success = run_phase1(project_path)
    elif args.phase == 2:
        success = run_phase2(project_path)
    elif args.phase == 3:
        success = run_phase3(project_path)
    elif args.phase == 4:
        success = run_phase4(project_path)
    elif args.all:
        success = run_all_phases(project_path)
    else:
        # Default to running all phases
        print("No specific phase selected, running all phases...\n")
        success = run_all_phases(project_path)
    
    # Print summary
    print("\n" + "=" * 80)
    if success:
        print("✅ Tool Index build completed successfully!")
    else:
        print("⚠️ Tool Index build completed with errors.")
    print("=" * 80)
    
    # Next steps
    print("\nNext steps:")
    print("1. Review the Tool Index at: " + os.path.join(project_path, ".tool_reference"))
    print("2. Test the context validator: python context_validator.py --check all")
    print("3. Explore the tool profiles to understand how Claude will use tools")
    print("\nThis Tool Index will help Claude select and use tools more effectively,")
    print("understand tool relationships, recognize complexity limits, and validate")
    print("its context against reality.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

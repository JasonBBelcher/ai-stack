#!/usr/bin/env python3
"""
Workflow Runner - Run example workflows with the AI Stack.

This script demonstrates how to use the example workflows with the AI Stack.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_workflow(workflow_name):
    """Load a workflow from the examples/workflows directory."""
    workflow_path = Path(__file__).parent / "workflows" / f"{workflow_name}.json"
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow '{workflow_name}' not found")
    
    with open(workflow_path, 'r') as f:
        return json.load(f)

def run_workflow_step(step, variables=None):
    """Run a single workflow step."""
    if variables is None:
        variables = {}
    
    # Replace variables in parameters
    parameters = step.get("parameters", {})
    for key, value in parameters.items():
        if isinstance(value, str):
            for var_name, var_value in variables.items():
                value = value.replace(f"{{{{{var_name}}}}}", str(var_value))
            parameters[key] = value
    
    print(f"Executing step: {step['name']}")
    print(f"  Type: {step['type']}")
    print(f"  Description: {step['description']}")
    print(f"  Parameters: {parameters}")
    
    # In a real implementation, this would actually execute the step
    # For now, we'll just simulate the execution
    if step['type'] == 'rag_index':
        print(f"  📂 Indexing codebase at {parameters.get('path', './src')}")
        print("  ✅ Indexing completed successfully")
    elif step['type'] == 'rag_query':
        print(f"  🔍 Querying: {parameters.get('query', 'default query')}")
        print("  ✅ Query completed successfully")
    elif step['type'] == 'cascade_request':
        print(f"  🔄 Processing cascade request")
        print("  ✅ Cascade processing completed successfully")
    else:
        print(f"  ⚠️ Unknown step type: {step['type']}")
    
    print()
    return True

def run_workflow(workflow_name, input_path=None, variables=None):
    """Run a complete workflow."""
    if variables is None:
        variables = {}
    
    # Add input path to variables if provided
    if input_path:
        variables['input_path'] = input_path
    
    try:
        # Load workflow
        workflow = load_workflow(workflow_name)
        print(f"🚀 Running workflow: {workflow['workflow_name']}")
        print(f"📝 Description: {workflow['description']}")
        print(f"🔖 Version: {workflow['version']}")
        print()
        
        # Run each step
        for step in workflow['steps']:
            success = run_workflow_step(step, variables)
            if not success:
                print(f"❌ Workflow failed at step: {step['name']}")
                return False
        
        print(f"🎉 Workflow '{workflow_name}' completed successfully!")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        return False

def list_workflows():
    """List all available workflows."""
    workflows_dir = Path(__file__).parent / "workflows"
    if not workflows_dir.exists():
        print("❌ Workflows directory not found")
        return
    
    print("Available workflows:")
    for workflow_file in workflows_dir.glob("*.json"):
        workflow_name = workflow_file.stem
        try:
            workflow = load_workflow(workflow_name)
            print(f"  - {workflow_name}: {workflow.get('description', 'No description')}")
        except Exception as e:
            print(f"  - {workflow_name}: Error loading workflow - {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run example workflows with the AI Stack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s code_analysis /path/to/project    # Run code analysis workflow
  %(prog)s document_qa /path/to/documents     # Run document QA workflow
  %(prog)s --list                            # List available workflows
  %(prog)s bug_fixing --variables "error=TypeError,path=./src/main.py"  # Run with variables
        """
    )
    
    parser.add_argument("workflow", nargs="?", help="Workflow name to run")
    parser.add_argument("input_path", nargs="?", help="Input path for the workflow")
    parser.add_argument("--list", "-l", action="store_true", help="List available workflows")
    parser.add_argument("--variables", "-v", help="Variables in key=value,key2=value2 format")
    
    args = parser.parse_args()
    
    # Parse variables if provided
    variables = {}
    if args.variables:
        for pair in args.variables.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                variables[key.strip()] = value.strip()
    
    # Handle list command
    if args.list:
        list_workflows()
        return
    
    # Handle workflow execution
    if not args.workflow:
        parser.print_help()
        return
    
    success = run_workflow(args.workflow, args.input_path, variables)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
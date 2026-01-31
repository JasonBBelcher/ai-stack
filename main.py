#!/usr/bin/env python3
"""
AI Stack - Local multi-model AI system
Main entry point for the AI stack application
"""
import argparse
import json
import sys
import os
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.controller import AIStackController
from src.config import AIStackConfig


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Local AI Stack - Claude-like multi-model system")
    parser.add_argument("input", nargs="?", help="Input prompt or request")
    parser.add_argument("--context", default="", help="Additional context for the request")
    parser.add_argument("--additional-context", default="", help="Additional context for execution")
    parser.add_argument("--health-check", action="store_true", help="Perform system health check")
    parser.add_argument("--status", action="store_true", help="Show detailed system status")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()
    
    # Initialize controller
    config = AIStackConfig()
    controller = AIStackController(config)
    
    # Handle different modes
    if args.health_check:
        health = controller.health_check()
        print(json.dumps(health, indent=2))
        return
    
    if args.status:
        status = controller.get_system_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.config:
        print(json.dumps(config.to_dict(), indent=2))
        return
    
    if args.interactive:
        interactive_mode(controller)
        return
    
    if not args.input:
        print("Error: No input provided. Use --interactive mode or provide input as argument.")
        parser.print_help()
        sys.exit(1)
    
    # Process the request
    result = controller.process_request(
        user_input=args.input,
        context=args.context,
        additional_context=args.additional_context
    )
    
    # Output results
    if args.json:
        output_data = {
            "success": result.success,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "plan": result.plan,
            "output": result.output,
            "error": result.error
        }
        output = json.dumps(output_data, indent=2)
    else:
        if result.success:
            output = f"""=== AI Stack Result ===
Execution Time: {result.execution_time:.2f}s
Memory Used: {result.memory_used:.2f}GB

=== Output ===
{result.output}"""
        else:
            output = f"Error: {result.error}"
    
    # Write to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


def interactive_mode(controller: AIStackController):
    """Interactive mode for continuous requests"""
    print("=== AI Stack Interactive Mode ===")
    print("Type 'exit' to quit, 'status' for system status, 'health' for health check")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'status':
                status = controller.get_system_status()
                print(json.dumps(status, indent=2))
                continue
            
            if user_input.lower() == 'health':
                health = controller.health_check()
                print(json.dumps(health, indent=2))
                continue
            
            if not user_input:
                continue
            
            print("Processing...")
            result = controller.process_request(user_input)
            
            if result.success:
                print(f"\nAI: {result.output}")
                print(f"(Time: {result.execution_time:.2f}s, Memory: {result.memory_used:.2f}GB)")
            else:
                print(f"Error: {result.error}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
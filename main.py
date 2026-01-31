#!/usr/bin/env python3
"""
AI Stack - Enhanced local multi-model AI system with generic model swappability
Main entry point for the AI stack application
"""
import argparse
import json
import sys
import os
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_controller import EnhancedAIStackController
from src.api_keys_manager import get_api_keys_manager
from src.profile_manager import ProfileManager


def create_enhanced_parser():
    """Create enhanced argument parser with new options"""
    parser = argparse.ArgumentParser(
        description="Local AI Stack - Enhanced multi-model system with generic model swappability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Write a Python function"                    # Basic request
  %(prog)s "Debug this code" --profile coding       # Use coding profile
  %(prog)s --interactive                                   # Interactive mode
  %(prog)s --models list                                  # List available models
  %(prog)s --profile create coding "Optimized for Python"  # Create profile
  %(prog)s --models planner=mistral:latest              # Specify models
  %(prog)s --cloud setup                                   # Setup cloud providers
        """
    )
    
    # Core arguments
    parser.add_argument("input", nargs="?", help="Input prompt or request")
    parser.add_argument("--context", default="", help="Additional context for the request")
    parser.add_argument("--additional-context", default="", help="Additional context for execution phase")
    
    # System information
    parser.add_argument("--health-check", action="store_true", help="Perform system health check")
    parser.add_argument("--status", action="store_true", help="Show detailed system status")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    
    # Model management
    parser.add_argument("--models", choices=["list", "validate", "discover"], help="Model management operations")
    parser.add_argument("--model-info", help="Show detailed information about a specific model")
    
    # Profile management
    parser.add_argument("--profile", nargs="?", const="list", help="Profile management (list, create, load, save, delete)")
    parser.add_argument("--profile-name", help="Name for profile operations")
    parser.add_argument("--profile-description", help="Description for new profile")
    
    # Model selection overrides
    parser.add_argument("--models-override", help="Override models for specific roles (e.g., planner=mistral:latest,critic=qwen2.5:7b)")
    parser.add_argument("--temperature", help="Override temperature for all roles (e.g., 0.2)")
    parser.add_argument("--max-memory", type=float, help="Override maximum memory usage in GB")
    parser.add_argument("--enable-cloud", action="store_true", help="Enable cloud model fallbacks")
    
    # Cloud provider management
    parser.add_argument("--cloud", choices=["setup", "status", "test"], help="Cloud provider operations")
    
    # Output options
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    # Interactive mode
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    
    return parser


def handle_models_command(controller, args):
    """Handle model management commands"""
    if args.models == "list":
        models = controller.get_available_models()
        if args.json:
            print(json.dumps(models, indent=2))
        else:
            print("=== Available Models ===")
            for name, info in models.items():
                capabilities = info.get('capabilities', {})
                status = "✓" if info.get('validated', True) else "⚠"
                source_icon = "🏠" if info.get('source', 'unknown') == "ollama" else "☁️"
                print(f"{status} {source_icon} {name} ({info.get('source', 'unknown')})")
                if args.verbose:
                    caps = info.get('capabilities', {})
                    if hasattr(caps, 'context_length'):
                        print(f"  Context: {caps.context_length}")
                    else:
                        print(f"  Context: {caps.get('context_length', 'N/A')}")
                    if hasattr(caps, 'recommended_memory_gb'):
                        print(f"  Memory: {caps.recommended_memory_gb}GB")
                    else:
                        print(f"  Memory: {info.get('memory_gb', 'N/A')}GB")
    
    elif args.models == "validate":
        print("=== Validating Models ===")
        # Implementation would go here
        print("Model validation not yet implemented")
    
    elif args.models == "discover":
        print("=== Discovering Models ===")
        controller.refresh_models()
        summary = controller.get_system_status()["config"]["models"]
        print(f"Total models: {summary['total_models']}")
        print(f"Validated: {summary['validated_models']}")


def handle_profile_command(controller, args):
    """Handle profile management commands"""
    profile_manager = controller.config.profile_manager
    
    if args.profile == "list":
        profiles = controller.get_available_profiles()
        if args.json:
            print(json.dumps(profiles, indent=2))
        else:
            print("=== Available Profiles ===")
            for profile in profiles:
                active = " (ACTIVE)" if profile["is_active"] else ""
                print(f"• {profile['name']}{active}")
                print(f"  {profile['description']}")
                print(f"  Created: {profile['created_at']}")
    
    elif args.profile == "create":
        if not args.profile_name:
            print("Error: --profile-name required for create operation")
            return False
        
        description = args.profile_description or f"Profile {args.profile_name}"
        success = controller.create_profile(args.profile_name, description)
        if success:
            print(f"✓ Profile '{args.profile_name}' created successfully")
        else:
            print(f"✗ Failed to create profile '{args.profile_name}'")
    
    elif args.profile == "load":
        if not args.profile_name:
            print("Error: --profile-name required for load operation")
            return False
        
        success = controller.switch_profile(args.profile_name)
        if success:
            print(f"✓ Switched to profile '{args.profile_name}'")
        else:
            print(f"✗ Failed to switch to profile '{args.profile_name}'")
    
    elif args.profile == "save":
        if not args.profile_name:
            # Save current configuration as a profile
            name = input("Enter profile name: ").strip()
            if not name:
                print("Error: Profile name cannot be empty")
                return False
            
            description = input("Enter profile description: ").strip()
            success = controller.create_profile(name, description)
            if success:
                print(f"✓ Current configuration saved as profile '{name}'")
            else:
                print(f"✗ Failed to save profile '{name}'")
        else:
            # Save existing profile
            profile = profile_manager.load_profile(args.profile_name)
            if profile:
                print(f"✓ Profile '{args.profile_name}' already exists")
            else:
                print(f"✗ Profile '{args.profile_name}' not found")
    
    elif args.profile == "delete":
        if not args.profile_name:
            print("Error: --profile-name required for delete operation")
            return False
        
        success = profile_manager.delete_profile(args.profile_name)
        if success:
            print(f"✓ Profile '{args.profile_name}' deleted successfully")
        else:
            print(f"✗ Failed to delete profile '{args.profile_name}'")
    
    else:
        print("Error: Unknown profile command")
        return False


def handle_cloud_command(controller, args):
    """Handle cloud provider operations"""
    api_manager = get_api_keys_manager()
    
    if args.cloud == "setup":
        print("=== Cloud Provider Setup ===")
        results = api_manager.setup_interactive()
        print(f"Configured providers: {sum(results.values())}/{len(results)}")
    
    elif args.cloud == "status":
        print("=== Cloud Provider Status ===")
        status = api_manager.get_status()
        for provider, info in status.items():
            configured = "✓" if info["configured"] else "✗"
            valid = "✓" if info["valid"] else "✗"
            print(f"{configured} {valid} {info['info']['name'] if info['info'] else provider}")
            if args.verbose and info["configured"]:
                print(f"  Last updated: {info.get('last_updated', 'N/A')}")
    
    elif args.cloud == "test":
        print("=== Testing Cloud Providers ===")
        for provider in ["openai", "anthropic"]:
            if api_manager.has_key(provider):
                is_valid = api_manager.validate_key(provider)
                status = "✓" if is_valid else "✗"
                print(f"{status} {provider}: API key is {'valid' if is_valid else 'invalid'}")
            else:
                print(f"⚠️ {provider}: No API key configured")


def parse_model_override(override_string):
    """Parse model override string into dictionary"""
    if not override_string:
        return {}
    
    overrides = {}
    for assignment in override_string.split(","):
        if "=" not in assignment:
            continue
        
        role, model = assignment.split("=", 1)
        overrides[role.strip()] = model.strip()
    
    return overrides


def main():
    """Main entry point"""
    parser = create_enhanced_parser()
    args = parser.parse_args()
    
    # Initialize enhanced controller
    controller = EnhancedAIStackController(
        config_path="config/models.json",
        profile_name=None  # Will use active profile or default
    )
    
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
        status = controller.get_system_status()
        config_data = status["config"]
        print(json.dumps(config_data, indent=2))
        return
    
    if args.models:
        handle_models_command(controller, args)
        return
    
    if args.profile:
        success = handle_profile_command(controller, args)
        if not success:
            sys.exit(1)
        return
    
    if args.cloud:
        handle_cloud_command(controller, args)
        return
    
    if args.model_info:
        model_info = controller.get_model_info(args.model_info)
        if model_info:
            print(json.dumps(model_info, indent=2))
        else:
            print(f"Error: Model '{args.model_info}' not found")
            sys.exit(1)
        return
    
    if args.interactive:
        interactive_mode(controller)
        return
    
    # Process request if input provided
    if args.input:
        process_request(controller, args)
    else:
        parser.print_help()


def process_request(controller, args):
    """Process user request with enhanced features"""
    # Apply model overrides if specified
    model_overrides = parse_model_override(args.models_override) if args.models_override else {}
    
    # Apply temperature override if specified
    temp_overrides = {}
    if args.temperature:
        try:
            temp = float(args.temperature)
            temp_overrides = {
                "planner": temp,
                "critic": temp,
                "executor": temp
            }
        except ValueError:
            print(f"Error: Invalid temperature value: {args.temperature}")
            return
    
    # Apply memory override if specified
    memory_override = None
    if args.max_memory:
        memory_override = {"max_memory_usage_gb": args.max_memory}
    
    # Apply cloud enable override if specified
    if args.enable_cloud:
        cloud_override = {"enable_cloud_fallbacks": True}
        if not memory_override:
            memory_override = {}
        memory_override.update(cloud_override)
    
    # Process the request
    print(f"Processing request with enhanced model system...")
    if args.verbose:
        print(f"Model overrides: {model_overrides}")
        print(f"Temperature override: {args.temperature}")
        print(f"Memory override: {args.max_memory}")
        print(f"Cloud enabled: {args.enable_cloud}")
    
    result = controller.process_request(
        user_input=args.input,
        context=args.context,
        additional_context=args.additional_context,
        model_overrides=model_overrides,
        temp_overrides=temp_overrides,
        config_overrides=memory_override
    )
    
    # Output results
    if args.json:
        output_data = {
            "success": result.success,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "plan": result.plan,
            "output": result.output,
            "error": result.error,
            "models_used": {
                "planner": result.plan.get("selected_model") if result.plan else None,
                "critic": result.critique.get("selected_model") if result.critique else None,
                "executor": result.output.get("selected_model") if result.output else None
            }
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
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


def interactive_mode(controller):
    """Interactive mode for enhanced model system"""
    print("=== AI Stack Interactive Mode (Enhanced) ===")
    print("Type 'help' for commands, 'exit' to quit")
    print()
    
    while True:
        try:
            user_input = input("ai-stack> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                show_interactive_help()
                continue
            
            if not user_input:
                continue
            
            # Parse interactive commands
            if user_input.startswith('/'):
                handle_interactive_command(controller, user_input[1:])
            else:
                # Process as regular request
                result = controller.process_request(user_input)
                if result.success:
                    print(f"\n{result.output}")
                else:
                    print(f"\nError: {result.error}")
            
            print("-" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def show_interactive_help():
    """Show help for interactive mode"""
    print("""
Available Commands:
  /models list                    - List available models
  /models info <model>           - Show model details
  /profile list                   - List profiles
  /profile switch <name>          - Switch profile
  /profile create <name> <desc>  - Create new profile
  /cloud status                  - Check cloud provider status
  /cloud setup                   - Setup cloud providers
  /health                         - System health check
  /status                         - System status
  /help                           - Show this help
  
Regular text will be processed as an AI request.
    """)


def handle_interactive_command(controller, command):
    """Handle interactive commands"""
    parts = command.split()
    if not parts:
        return
    
    cmd = parts[0].lower()
    
    if cmd == 'models':
        if len(parts) >= 2 and parts[1].lower() == 'list':
            handle_models_command(controller, type('Args', models='list', json=False, verbose=False)())
        elif len(parts) >= 2 and parts[1].lower() == 'info':
            if len(parts) >= 3:
                handle_models_command(controller, type('Args', model_info=parts[2], json=True, verbose=False)())
        else:
            print("Usage: /models info <model_name>")
    
    elif cmd == 'profile':
        if len(parts) >= 2:
            action = parts[1].lower()
            if action == 'list':
                handle_profile_command(controller, type('Args', profile='list', json=False)())
            elif action == 'switch':
                if len(parts) >= 3:
                    handle_profile_command(controller, type('Args', profile='load', profile_name=parts[2])())
                else:
                    print("Usage: /profile switch <name>")
            elif action == 'create':
                if len(parts) >= 4:
                    name = parts[2]
                    desc = ' '.join(parts[3:])
                    handle_profile_command(controller, type('Args', profile='create', profile_name=name, profile_description=desc)())
                else:
                    print("Usage: /profile create <name> <description>")
        else:
            print("Usage: /profile <list|switch|create> [args]")
    
    elif cmd == 'cloud':
        if len(parts) >= 2:
            action = parts[1].lower()
            if action == 'status':
                handle_cloud_command(controller, type('Args', cloud='status', verbose=True)())
            elif action == 'setup':
                handle_cloud_command(controller, type('Args', cloud='setup')())
        else:
            print("Usage: /cloud <status|setup>")
    
    elif cmd == 'health':
        health = controller.health_check()
        print(json.dumps(health, indent=2))
    
    elif cmd == 'status':
        status = controller.get_system_status()
        print(json.dumps(status, indent=2))
    
    elif cmd == 'help':
        show_interactive_help()
    
    else:
        print(f"Unknown command: {cmd}")
        print("Type '/help' for available commands")


if __name__ == "__main__":
    main()
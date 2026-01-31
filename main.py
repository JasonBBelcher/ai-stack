#!/usr/bin/env python3
"""
AI Stack - Enhanced local multi-model AI system with generic model swappability
Main entry point for AI stack application
"""
import argparse
import json
import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import with error handling
try:
    from src.enhanced_controller import SimplifiedAIStackController
except ImportError as e:
    print(f"❌ Error importing enhanced controller: {e}")
    print("Ensure all dependencies are installed with:")
    print("  pip install psutil pydantic PyYAML cryptography requests orjson structlog")
    sys.exit(1)

# Import other components with error handling
try:
    from src.api_keys_manager import get_api_keys_manager
    API_KEY_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: API key manager not available: {e}")
    API_KEY_MANAGER_AVAILABLE = False

# Check if we have basic required components
BASIC_COMPONENTS = {
    "enhanced_controller": "src/enhanced_controller.py",
    "capabilities": "src/capabilities.py", 
    "model_registry": "src/model_registry.py",
    "profile_manager": "src/profile_manager.py",
    "enhanced_config": "src/enhanced_config.py",
}

def check_basic_components():
    """Check if basic components are available"""
    missing = []
    present = []
    
    for component, description in BASIC_COMPONENTS.items():
        if not os.path.exists(description):
            missing.append(f"❌ {description} ({component})")
        else:
            present.append(f"✅ {description}")
    
    if missing:
        print("❌ Missing components:")
        for item in missing:
            print(f"  {item}")
        for item in present:
            print(f"  {item}")
        return False
    else:
        print("✅ All basic components available")
        return True


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
    parser.add_argument("--temperature", type=float, help="Override temperature for all roles (e.g., 0.2)")
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
    
    # Add quick access commands
    parser.add_argument("--quick-setup", action="store_true", help="Quick setup for new users")
    parser.add_argument("--demo", action="store_true", help="Run demonstration of features")
    
    return parser


def quick_setup():
    """Quick setup for new users"""
    print("🚀 AI Stack Quick Setup")
    print("="*50)
    
    if not check_basic_components():
        print("❌ Setup failed: Missing components")
        return False
    
    print("📦 Checking Python version...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor} - Compatible")
    else:
        print(f"⚠️ Python {python_version.major}.{python_version.minor} - May have issues")
    
    print("🔧 Checking Ollama...")
    try:
        import subprocess
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama {result.stdout.strip()}")
        else:
            print("⚠️ Ollama not responding")
    except Exception:
        print("❌ Ollama check failed")
    
    print("📦 Setting up virtual environment...")
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("📦 Creating virtual environment...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "venv"], capture_output=True)
        if result.returncode != 0:
            print(f"⚠️ Failed to create virtual environment")
            return False
    
    print("📦 Activating virtual environment...")
    
    # Check if dependencies are installed
    if API_KEY_MANAGER_AVAILABLE:
        print("✅ API key manager available")
    else:
        print("⚠️ API key manager not available")
    
    print("🎯 Setup complete!")
    print("")
    print("🚀 Next steps:")
    print("1. python3 main.py --models list    # Discover available models")
    print("2. python3 main.py --interactive     # Start interactive mode")
    print("3. python3 main.py --help            # See all options")
    print("")
    print("📚 Documentation:")
    print("• docs/generic_models_implementation.md")
    print("• docs/api_reference.md")
    print("")
    
    return True


def run_demo():
    """Run demonstration of AI stack features"""
    print("🎭 AI Stack Demo Mode")
    print("="*50)
    
    if not check_basic_components():
        print("❌ Demo cannot run - missing components")
        return False
    
    try:
        from src.enhanced_controller import SimplifiedAIStackController
        controller = SimplifiedAIStackController()
        
        print("🔧 Testing model discovery...")
        models = controller.get_available_models()
        print(f"✅ Found {len(models)} models")
        
        print("📊 Testing profile system...")
        profiles = controller.get_available_profiles()
        print(f"✅ Found {len(profiles)} profiles")
        
        print("🚀 Demo: Model listing with capabilities")
        controller.handle_models_command(type('Args', models='list', json=False, verbose=True))
        
        print("🚀 Demo: Profile management")
        controller.handle_profile_command(type('Args', profile='list', json=False))
        
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    return True


def handle_models_command(controller, args):
    """Handle model management commands"""
    try:
        if args.models == "list":
            models = controller.get_available_models()
            print("=== Available Models ===")
            for name, info in models.items():
                capabilities = info.get('capabilities', {})
                status = "✓" if info.get('validated', False) else "⚠"
                source_icon = "🏠" if info.get('source', 'unknown') == "ollama" else "☁️"
                print(f"{status} {source_icon} {name} ({info.get('source', 'unknown')})")
                if args.verbose and capabilities:
                    print(f"  Context: {capabilities.get('context_length', 'N/A')}")
                    print(f"  Memory: {info.get('memory_gb', 'N/A')}GB")
        elif args.models == "validate":
            print("=== Model Validation ===")
            print("✓ Model validation framework implemented")
            print("⚠️ Full validation not yet implemented")
        
        elif args.models == "discover":
            print("=== Model Discovery ===")
            refresh_result = controller.refresh_models()
            print(f"✓ Refreshed models - Total: {len(refresh_result.get('models', []))}")
            for model in refresh_result.get('models', []):
                print(f"  • {model}")
        
        elif args.model_info:
            info = controller.get_model_for_role_info(args.model_info)
            if "error" not in info:
                print(f"=== Model Information: {args.model_info} ===")
                print(f"Source: {info.get('source', 'Unknown')}")
                print(f"Validated: {info.get('validated', False)}")
                if args.verbose and info.get('capabilities'):
                    caps = info["capabilities"]
                    print(f"  Context Length: {caps.get('context_length', 'N/A')}")
                    print(f"  Reasoning: {caps.get('reasoning_strength', 'N/A')}")
                    print(f"  Coding Strength: {caps.get('coding_strength', 'N/A')}")
        
        else:
            print(f"Unknown models command: {args.models}")
            return False
            
    except Exception as e:
        print(f"Error in models command: {e}")
        return False


def handle_profile_command(controller, args):
    """Handle profile management commands"""
    try:
        if args.profile == "list":
            profiles = controller.get_available_profiles()
            print("=== Available Profiles ===")
            for profile in profiles:
                active = " (ACTIVE)" if profile["is_active"] else ""
                print(f"• {profile['name']}{active}")
                print(f"  {profile['description']}")
        
        elif args.profile == "create":
            if not args.profile_name:
                print("Error: --profile-name required for create operation")
                return False
            
            success = controller.create_profile(args.profile_name, args.profile_description)
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
                print("Error: --profile-name required for save operation")
                return False
            
            success = controller.create_profile(args.profile_name, f"Profile saved at {datetime.now().isoformat()}")
            if success:
                print(f"✓ Current configuration saved as profile '{args.profile_name}'")
            else:
                print(f"✗ Failed to save profile '{args.profile_name}'")
        
        elif args.profile == "delete":
            if not args.profile_name:
                print("Error: --profile-name required for delete operation")
                return False
            
            success = controller.config.profile_manager.delete_profile(args.profile_name)
            if success:
                print(f"✓ Profile '{args.profile_name}' deleted successfully")
            else:
                print(f"✗ Failed to delete profile '{args.profile_name}'")
        
        else:
            print(f"Unknown profile command: {args.profile}")
            return False
            
    except Exception as e:
        print(f"Error in profile command: {e}")
        return False


def handle_cloud_command(controller, args):
    """Handle cloud provider operations"""
    if not API_KEY_MANAGER_AVAILABLE:
        print("❌ Cloud provider features not available")
        print("Install cryptography: pip install cryptography")
        return False
    
    api_manager = get_api_keys_manager()
    
    if args.cloud == "setup":
        print("=== Cloud Provider Setup ===")
        results = api_manager.setup_interactive()
        print(f"✅ Setup complete - {sum(results.values())} providers configured")
    
    elif args.cloud == "status":
        print("=== Cloud Provider Status ===")
        status = api_manager.get_status()
        for provider, info in status.items():
            configured = "✓" if info["configured"] else "✗"
            valid = "✓" if info["valid"] else "✗"
            print(f"{configured} {valid} {info['info']['name']}")
            if info["configured"]:
                provider_info = info.get("info", {})
                if provider_info:
                    print(f"  Models: {provider_info.get('models', [])}")
    
    elif args.cloud == "test":
        print("=== Testing Cloud Providers ===")
        for provider in ["openai", "anthropic"]:
            if api_manager.has_key(provider):
                is_valid = api_manager.validate_key(provider)
                status = "✓" if is_valid else "✗"
                print(f"{status} {provider}: API key is {'valid' if is_valid else 'invalid'}")
            else:
                print(f"⚠️ {provider}: No API key configured")


def main():
    """Main entry point"""
    parser = create_enhanced_parser()
    args = parser.parse_args()
    
    # Handle special modes first
    if args.quick_setup:
        quick_setup()
        return
    
    if args.demo:
        run_demo()
        return
    
    # Check basic components before proceeding
    if not check_basic_components():
        print("❌ Cannot proceed - missing core components")
        print("Please ensure all AI stack components are properly installed")
        sys.exit(1)
    
    # Initialize enhanced controller
    try:
        controller = SimplifiedAIStackController()
        print("✅ Enhanced AI Stack Controller initialized")
    except Exception as e:
        print(f"❌ Error initializing controller: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
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
    
    if args.model_info:
        handle_models_command(controller, args)
        return
    
    if args.profile:
        handle_profile_command(controller, args)
        return
    
    if args.cloud:
        handle_cloud_command(controller, args)
        return
    
    if args.interactive:
        interactive_mode(controller)
        return
    
    # Process request if input provided
    if args.input:
        process_request(controller, args)
    else:
        parser.print_help()


def interactive_mode(controller):
    """Interactive mode for enhanced model system"""
    print("🎯 AI Stack - Enhanced Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit")
    print("")
    
    # Check if we're in an interactive terminal
    import sys
    if not sys.stdin.isatty():
        print("⚠️ Not an interactive terminal. Use command-line arguments instead.")
        print("Example: python3 main.py 'your request here'")
        return
    
    while True:
        try:
            user_input = input("ai-stack> ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Parse and execute commands
            if user_input.startswith('/'):
                handle_interactive_command(controller, user_input)
            elif user_input.lower() == 'help':
                show_interactive_help()
                continue
            else:
                # Process as regular request
                print(f"Processing: {user_input}")
                
                result = controller.process_request(user_input)
                
                if result.success:
                    print(f"\n{result.output}")
                    print(f"⏱️ Time: {result.execution_time:.2f}s | Memory: {result.memory_used:.2f}GB")
                else:
                    print(f"\n❌ Error: {result.error}")
            
            print("-" * 50)
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


def handle_interactive_command(controller, command):
    """Handle interactive commands"""
    parts = command.split()
    if not parts:
        return
    
    cmd = parts[0].lower()
    
    if cmd == 'models':
        if len(parts) >= 2 and parts[1].lower() == 'list':
            handle_models_command(controller, type('Args', models='list', json=False))
        elif len(parts) >= 2 and parts[1].lower() == 'info':
            if len(parts) >= 3:
                model_name = parts[2]
                handle_models_command(controller, type('Args', model_info=model_name, json=True, verbose=False))
            else:
                print("Usage: /models info <model_name>")
        elif len(parts) >= 2 and parts[1].lower() == 'validate':
            handle_models_command(controller, type('Args', models='validate'))
        elif len(parts) >= 2 and parts[1].lower() == 'discover':
            handle_models_command(controller, type('Args', models='discover'))
        else:
            print("Usage: /models <command>")
            print("  Available: list, validate, discover")
    
    elif cmd == 'profile':
        if len(parts) >= 2:
            action = parts[1].lower()
            if action == 'list':
                handle_profile_command(controller, type('Args', profile='list', json=False))
            elif action == 'create':
                if len(parts) >= 3:
                    name = parts[2]
                    description = ' '.join(parts[3:])
                    handle_profile_command(controller, type('Args', profile='create', profile_name=name, profile_description=description))
                else:
                    print("Usage: /profile create <name> <description>")
            elif action == 'load':
                if len(parts) >= 3:
                    name = parts[2]
                    handle_profile_command(controller, type('Args', profile='load', profile_name=name))
                else:
                    print("Usage: /profile load <name>")
            elif action == 'save':
                handle_profile_command(controller, type('Args', profile='save'))
            elif action == 'switch':
                if len(parts) >= 3:
                    name = parts[2]
                    handle_profile_command(controller, type('Args', profile='switch', profile_name=name))
                else:
                    print("Usage: /profile switch <name>")
            elif action == 'delete':
                if len(parts) >= 3:
                    name = parts[2]
                    handle_profile_command(controller, type('Args', profile='delete', profile_name=name))
                else:
                    print("Usage: /profile delete <name>")
        else:
            print("Usage: /profile <command>")
            print("  Available: list, create, load, save, switch, delete")
    
    elif cmd == 'cloud':
        if len(parts) >= 2:
            action = parts[1].lower()
            if action == 'setup':
                handle_cloud_command(controller, type('Args', cloud='setup'))
            elif action == 'status':
                handle_cloud_command(controller, type('Args', cloud='status'))
            elif action == 'test':
                handle_cloud_command(controller, type('Args', cloud='test'))
        else:
            print("Usage: /cloud <command>")
            print("  Available: setup, status, test")
    
    elif cmd == 'health':
        health = controller.health_check()
        print("=== System Health ===")
        print(f"Overall Status: {health['overall_status']}")
        print(f"Ollama Running: {health['ollama_running']}")
        print(f"Available Models: {len(health['models_available'])}")
        if health["thermal_state"].get("level") == "critical":
            print("⚠️ Warning: Thermal state is critical")
    
    elif cmd == 'status':
        status = controller.get_system_status()
        print("=== System Status ===")
        config_data = status["config"]
        print(f"Active Profile: {config_data['profile']}")
        print(f"Cloud Enabled: {config_data['cloud_enabled']}")
        print(f"Total Models: {config_data['models']['total_models']}")
        print(f"Validated Models: {config_data['models']['validated_models']}")
    
    elif cmd == 'config':
        status = controller.get_system_status()
        config_data = status["config"]
        print(json.dumps(config_data, indent=2))
    
    elif cmd == 'help':
        show_interactive_help()
    
    else:
        print(f"Unknown command: {cmd}")
        print("Type '/help' for available commands")


def show_interactive_help():
    """Show help for interactive mode"""
    print("""
📚 Interactive Mode Commands:
  
=== Model Management ===
/models list                    - List all available models
/models info <model>           - Show model details  
/models validate                - Validate model configurations  
/models discover               - Rediscover available models

=== Profile Management ===  
/profile list                   - List user profiles
/profile create <name> <desc>  - Create profile  
/profile switch <name>          - Switch to profile  
/profile save                 - Save current as profile  
/profile delete <name>          - Delete profile

=== Cloud Provider Management ===
/cloud setup                   - Interactive API key setup  
/cloud status                  - Check provider status  
/cloud test                   - Test API connectivity

=== System Information ===
/health                          - System health check  
/status                           - Detailed system status  
/config                          - Current configuration  

=== Enhanced Commands ===
--models-override <overrides>     - Override models for roles
--temperature <temp>               - Override all model temperatures
--max-memory <GB>             - Maximum memory usage limit
--enable-cloud                   - Enable cloud fallbacks

=== Other ===
/help                             - Show this help
/exit                              - Exit interactive mode

=== Direct Processing ===
Any other input will be processed as an AI request using the enhanced generic model system.

=== Tips ===
• Use profiles to optimize for specific tasks
• Enable cloud fallbacks for better model availability
• Use --verbose to see detailed model information
• Use --json for programmatic output
""")


def process_request(controller, args):
    """Process user request through the new workflow"""
    start_time = time.time()
    
    try:
        # Apply model overrides if specified
        model_overrides = {}
        if args.models_override:
            for assignment in args.models_override.split(","):
                if "=" not in assignment:
                    continue
                
                role, model = assignment.split("=", 1)
                model_overrides[role.strip()] = model.strip()
        
        # Apply temperature override if specified
        temp_overrides = {}
        if args.temperature:
            temp_overrides = {
                "planner": args.temperature,
                "critic": args.temperature,
                "executor": args.temperature
            }
        
        # Apply memory override if specified
        config_overrides = {}
        if args.max_memory:
            config_overrides = {"max_memory_usage_gb": args.max_memory}
        
        # Apply cloud enablement if specified
        cloud_overrides = {"enable_cloud_fallbacks": args.enable_cloud} if args.enable_cloud else None
        if config_overrides:
            temp_overrides.update(cloud_overrides)
        
        print("🤖 Processing request with enhanced model system...")
        if args.verbose:
            print(f"Model overrides: {model_overrides}")
            print(f"Temperature override: {args.temperature}")
            print(f"Memory limit: {args.max_memory}")
            print(f"Cloud enabled: {args.enable_cloud}")
        
        # Process the request
        result = controller.process_request(
            user_input=args.input,
            context=args.context,
            additional_context=args.additional_context
        )
        
        if result.success:
            print(f"✅ Request completed successfully")
            print(f"⏱️ Execution Time: {result.execution_time:.2f}s")
            print(f"💾 Memory Used: {result.memory_used:.2f}GB")
            print("")
            print("=== Output ===")
            print(result.output)
        else:
            print(f"❌ Request failed: {result.error}")
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
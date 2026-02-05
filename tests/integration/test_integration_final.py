"""
Test script for enhanced controller and CLI system
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_basic_functionality():
    """Test basic functionality without hanging"""
    print("🧪 Testing Basic Functionality...")
    
    try:
        from capabilities import ModelCapabilities
        print("✅ Capabilities import")
        
        # Test basic model creation
        caps = ModelCapabilities(
            context_length=32000,
            reasoning_strength=0.7,
            memory_gb_estimate=5.0
        )
        print(f"✅ ModelCapabilities: context={caps.context_length}")
        
    except Exception as e:
        print(f"❌ Capabilities failed: {e}")
        return False
    
    try:
        from model_registry import ModelRegistry
        print("✅ ModelRegistry import")
        
        # Test configuration loading only (no subprocess)
        registry = ModelRegistry()
        models_count = len(registry.models)
        print(f"✅ ModelRegistry: {models_count} models loaded")
        
    except Exception as e:
        print(f"❌ ModelRegistry failed: {e}")
        return False
    
    try:
        from profile_manager import ProfileManager
        print("✅ ProfileManager import")
        
        profile_mgr = ProfileManager()
        profiles = profile_mgr.list_profiles()
        print(f"✅ ProfileManager: {len(profiles)} profiles")
        
    except Exception as e:
        print(f"❌ ProfileManager failed: {e}")
        return False
    
    try:
        from enhanced_config import AIStackConfig
        print("✅ EnhancedConfig import")
        
        config = AIStackConfig()
        print("✅ EnhancedConfig created")
        
    except Exception as e:
        print(f"❌ EnhancedConfig failed: {e}")
        return False
    
    try:
        from enhanced_controller import EnhancedAIStackController
        print("✅ EnhancedController import")
        
        controller = EnhancedAIStackController()
        print("✅ EnhancedController created")
        
    except Exception as e:
        print(f"❌ EnhancedController failed: {e}")
        return False
    
    try:
        from api_keys_manager import get_api_keys_manager
        print("✅ APIKeysManager import")
        
        api_mgr = get_api_keys_manager()
        print("✅ APIKeysManager created")
        
    except Exception as e:
        print(f"❌ APIKeysManager failed: {e}")
        return False
    
    return True

def test_cli_integration():
    """Test CLI without hanging on subprocess calls"""
    print("\n🔧 Testing CLI Integration...")
    
    try:
        from enhanced_controller import EnhancedAIStackController
        controller = EnhancedAIStackController()
        
        # Test models list (this should work)
        print("Testing --models list...")
        try:
            # Simulate args for models list
            class MockArgs:
                def __init__(self):
                    self.models = "list"
                    self.json = False
                    self.verbose = False
            
            args = MockArgs()
            from main import handle_models_command
            handle_models_command(controller, args)
            print("✅ Models list command works")
        except Exception as e:
            print(f"❌ Models list command failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False
    
    return True

def test_model_discovery():
    """Test model discovery without hanging"""
    print("\n🤖 Testing Model Discovery...")
    
    try:
        from enhanced_controller import EnhancedAIStackController
        controller = EnhancedAIStackController()
        
        # Test model info for each role
        for role in ["planner", "critic", "executor"]:
            print(f"Testing model for role: {role}...")
            try:
                info = controller.get_model_for_role_info(role)
                if "error" not in info:
                    print(f"✅ {role}: {info.get('model_name', 'None')}")
                    if info.get("capabilities"):
                        caps = info["capabilities"]
                        print(f"  Context: {caps.get('context_length', 'N/A')}")
                        print(f"  Memory: {caps.get('memory_gb', 'N/A')}GB")
                else:
                    print(f"⚠️ {role}: {info.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ {role} info failed: {e}")
        
    except Exception as e:
        print(f"❌ Model discovery test failed: {e}")
        return False
    
    return True

def test_health_system():
    """Test health checking system"""
    print("\n🏥 Testing Health System...")
    
    try:
        from enhanced_controller import EnhancedAIStackController
        controller = EnhancedAIStackController()
        
        health = controller.health_check()
        print("✅ Health check completed")
        print(f"  Overall status: {health['overall_status']}")
        print(f"  Ollama running: {health['ollama_running']}")
        print(f"  Models available: {len(health['models_available'])}")
        
    except Exception as e:
        print(f"❌ Health system test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🎯 Testing Enhanced AI Stack - CLI Integration")
    print("="*50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("CLI Integration", test_cli_integration),
        ("Model Discovery", test_model_discovery),
        ("Health System", test_health_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"🧪 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System Ready!")
        print("\n🚀 Ready for Phase 2:")
        print("• CLI integration with enhanced generic model system")
        print("• Model discovery and validation")
        print("• Profile management and user customization")
        print("• Cloud provider framework")
        print("• Health monitoring and status reporting")
        print("\n📋 Next Steps:")
        print("1. Test full workflow with model selection")
        print("2. Implement cloud API integration")
        print("3. Performance optimization and benchmarking")
    else:
        print("⚠️ SOME TESTS FAILED - Issues to Address")
        print("\n🔧 Troubleshooting:")
        print("1. Check Python version >= 3.8")
        print("2. Verify all dependencies installed")
        print("3. Ensure Ollama is running: ollama serve")
        print("4. Check virtual environment activation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
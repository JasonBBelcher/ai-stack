"""
Test the enhanced controller with new generic system
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_enhanced_controller():
    """Test the enhanced controller"""
    print("=== Testing Enhanced Controller ===")
    
    try:
        from enhanced_controller import EnhancedAIStackController
        
        # Create controller
        controller = EnhancedAIStackController()
        print("✓ Enhanced controller created")
        
        # Test health check
        print("\n--- Health Check ---")
        health = controller.health_check()
        print(f"Overall status: {health['overall_status']}")
        print(f"Models available: {len(health['models_available'])}")
        print(f"Ollama running: {health['ollama_running']}")
        
        # Test model for role
        print("\n--- Model for Role ---")
        for role in ['planner', 'critic', 'executor']:
            model_info = controller.get_model_for_role_info(role)
            print(f"{role}: {model_info.get('model_name', 'None')} ({model_info.get('source', 'Unknown')})")
            
            capabilities = model_info.get('capabilities')
            if capabilities:
                print(f"  Context: {capabilities.context_length}")
                print(f"  Memory: {capabilities.recommended_memory_gb}GB")
        
        # Test system status
        print("\n--- System Status ---")
        status = controller.get_system_status()
        print(f"Config path: {status['config']['path']}")
        print(f"Active profile: {status['config']['profile']}")
        print(f"Cloud enabled: {status['config']['cloud_enabled']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced controller test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_controller()
    if success:
        print("\n✓ Enhanced controller test completed successfully!")
        print("✓ New generic model system is ready!")
    else:
        print("\n✗ Enhanced controller test failed!")
        print("✗ Need to debug issues before proceeding")
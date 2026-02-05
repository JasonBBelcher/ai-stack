"""
Quick test of enhanced controller methods
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def main():
    try:
        from enhanced_controller import EnhancedAIStackController
        
        # Create controller
        controller = EnhancedAIStackController()
        
        # Check available methods
        methods = [attr for attr in dir(controller) if not attr.startswith('_')]
        print("Available methods:", [m for m in methods if 'model' in m])
        
        # Test the problematic method
        if hasattr(controller, 'get_all_models'):
            print("✓ get_all_models method exists")
            models = controller.get_all_models()
            print(f"✓ get_all_models() returned {len(models)} models")
        else:
            print("✗ get_all_models method not found")
        
        # Test get_available_models
        if hasattr(controller, 'get_available_models'):
            print("✓ get_available_models method exists")
            models = controller.get_available_models()
            print(f"✓ get_available_models() returned {len(models)} models")
        else:
            print("✗ get_available_models method not found")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
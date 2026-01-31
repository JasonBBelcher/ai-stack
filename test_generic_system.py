"""
Test script for new generic model system
"""
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_basic_imports():
    """Test basic module imports"""
    try:
        from capabilities import ModelCapabilities, RoleRequirements
        print("✓ capabilities module imported")
        
        from profile_manager import ProfileManager
        print("✓ profile_manager module imported")
        
        from enhanced_config import AIStackConfig
        print("✓ enhanced_config module imported")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_capabilities():
    """Test capabilities system"""
    try:
        from capabilities import ModelCapabilities, create_capabilities_from_dict
        
        # Create test capabilities
        caps_data = {
            'context_length': 32000,
            'reasoning_strength': 0.7,
            'coding_strength': 0.6,
            'memory_gb_estimate': 5.0
        }
        
        caps = create_capabilities_from_dict(caps_data)
        print(f"✓ Created capabilities: context={caps.context_length}, reasoning={caps.reasoning_strength}")
        return True
    except Exception as e:
        print(f"✗ Capabilities error: {e}")
        return False

def test_profile_manager():
    """Test profile manager without file operations"""
    try:
        from profile_manager import ProfileManager, UserProfile
        from datetime import datetime
        
        # Create test profile
        test_profile = UserProfile(
            name='test',
            description='Test profile',
            created_at=datetime.now(),
            modified_at=datetime.now(),
            role_mappings={},
            system_settings={},
            selection_preferences={},
            cloud_settings={}
        )
        
        print(f"✓ Created test profile: {test_profile.name}")
        return True
    except Exception as e:
        print(f"✗ Profile manager error: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    try:
        from enhanced_config import AIStackConfig
        
        # Check if config file exists
        if os.path.exists('config/models.json'):
            print("✓ models.json found")
            
            # Try to load config (this might be slow)
            config = AIStackConfig()
            print("✓ AIStackConfig created")
            return True
        else:
            print("⚠ models.json not found")
            return False
            
    except Exception as e:
        print(f"✗ Config loading error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Testing Generic Model System ===\n")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Capabilities System", test_capabilities),
        ("Profile Manager", test_profile_manager),
        ("Config Loading", test_config_loading)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Unexpected error in {test_name}: {e}")
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return True
    else:
        print("⚠ Some tests failed")
        return False

if __name__ == "__main__":
    main()
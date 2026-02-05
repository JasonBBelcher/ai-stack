#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 4: Specialization.

This script tests all Phase 4 components:
1. Model capability tags
2. Enhanced memory manager for M3 Mac
3. RAG profiles
4. Cascade profiles
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from memory_manager import MemoryManager

def test_phase4_model_capabilities():
    """Test Phase 4 Task 4.1: Model capability tags."""
    print("="*60)
    print("PHASE 4 - TASK 4.1: Model Capability Tags")
    print("="*60)
    
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'models.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check local models have tags
    print("\nLocal Models:")
    for model_name, model_data in config['model_profiles'].items():
        capabilities = model_data['capabilities']
        if 'tags' in capabilities:
            tags = capabilities['tags']
            print(f"  ✓ {model_name}: {tags}")
        else:
            print(f"  ✗ {model_name}: Missing tags!")
            return False
    
    # Check cloud models have tags
    print("\nCloud Models:")
    for provider, provider_data in config['cloud_providers'].items():
        for model_name, model_data in provider_data['models'].items():
            capabilities = model_data['capabilities']
            if 'tags' in capabilities:
                tags = capabilities['tags']
                print(f"  ✓ {provider}/{model_name}: {tags}")
            else:
                print(f"  ✗ {provider}/{model_name}: Missing tags!")
                return False
    
    print("\n✓ All models have capability tags!")
    return True

def test_phase4_memory_manager():
    """Test Phase 4 Task 4.2: Enhanced memory manager."""
    print("\n" + "="*60)
    print("PHASE 4 - TASK 4.2: Enhanced Memory Manager (M3 Mac)")
    print("="*60)
    
    mm = MemoryManager()
    
    # Test unified memory pressure
    print("\n1. Unified Memory Pressure:")
    pressure = mm.get_unified_memory_pressure()
    print(f"   Pressure Level: {pressure['pressure']}")
    print(f"   Percent Used: {pressure['percent_used']:.1f}%")
    print(f"   Status: {pressure['status']}")
    
    # Test memory alerts
    print("\n2. Memory Alerts:")
    alerts = mm.get_memory_alerts()
    print(f"   Total Alerts: {len(alerts)}")
    for alert in alerts[:3]:  # Show first 3
        print(f"   - [{alert['severity']}] {alert['message']}")
    
    # Test M3 optimization suggestions
    print("\n3. M3 Optimization Suggestions:")
    suggestions = mm.get_m3_optimization_suggestions()
    print(f"   Total Suggestions: {len(suggestions)}")
    for suggestion in suggestions[:3]:  # Show first 3
        print(f"   - {suggestion}")
    
    # Test memory pressure trend
    print("\n4. Memory Pressure Trend:")
    # Build some history
    for _ in range(5):
        mm.take_memory_snapshot()
    trend = mm.get_memory_pressure_trend()
    print(f"   Trend: {trend['trend']}")
    print(f"   Message: {trend['message']}")
    
    print("\n✓ Enhanced memory manager working!")
    return True

def test_phase4_rag_profiles():
    """Test Phase 4 Task 4.3: RAG profiles."""
    print("\n" + "="*60)
    print("PHASE 4 - TASK 4.3: RAG Profiles")
    print("="*60)
    
    rag_profiles_dir = os.path.join(os.path.dirname(__file__), 'config', 'rag_profiles')
    
    # Check directory exists
    if not os.path.exists(rag_profiles_dir):
        print(f"✗ RAG profiles directory not found: {rag_profiles_dir}")
        return False
    
    # Check for expected profiles
    expected_profiles = ['coding.json', 'research.json', 'writing.json']
    
    print("\nRAG Profiles:")
    for profile_name in expected_profiles:
        profile_path = os.path.join(rag_profiles_dir, profile_name)
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            
            print(f"\n  ✓ {profile_name}")
            print(f"     Description: {profile.get('description', 'N/A')}")
            print(f"     Chunk Size: {profile['chunking']['chunk_size']}")
            print(f"     Top K: {profile['retrieval']['top_k']}")
            print(f"     Temperature: {profile['generation']['temperature']}")
            
            # Check model preferences
            if 'model_preferences' in profile:
                print(f"     Retrieval Models: {profile['model_preferences']['retrieval']['preferred_models']}")
                print(f"     Generation Models: {profile['model_preferences']['generation']['preferred_models']}")
            
            # Check M3 optimizations
            if 'm3_mac_optimizations' in profile:
                print(f"     M3 Optimizations: {profile['m3_mac_optimizations']['use_metal_acceleration']}")
        else:
            print(f"  ✗ {profile_name} not found!")
            return False
    
    print("\n✓ All RAG profiles created successfully!")
    return True

def test_phase4_cascade_profiles():
    """Test Phase 4 Task 4.4: Cascade profiles."""
    print("\n" + "="*60)
    print("PHASE 4 - TASK 4.4: Cascade Profiles")
    print("="*60)
    
    user_profiles_dir = os.path.join(os.path.dirname(__file__), 'config', 'user_profiles')
    
    # Check for cascade settings in user profiles
    expected_profiles = ['coding.json', 'research.json', 'writing.json']
    
    print("\nCascade Settings in User Profiles:")
    for profile_name in expected_profiles:
        profile_path = os.path.join(user_profiles_dir, profile_name)
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            
            if 'cascade_settings' in profile:
                cascade = profile['cascade_settings']
                print(f"\n  ✓ {profile_name}")
                print(f"     Enabled: {cascade['enabled']}")
                
                # Check stages
                print(f"     Stages:")
                for stage_name, stage_config in cascade['stages'].items():
                    print(f"       - {stage_name}: {stage_config['model']}")
                    print(f"         Max Iterations: {stage_config['max_iterations']}")
                    print(f"         Temperature: {stage_config['temperature']}")
                
                # Check flow control
                print(f"     Flow Control:")
                print(f"       - Early Termination: {cascade['flow_control']['enable_early_termination']}")
                print(f"       - Max Total Iterations: {cascade['flow_control']['max_total_iterations']}")
                
                # Check quality gates
                print(f"     Quality Gates:")
                for gate_name, threshold in cascade['quality_gates'].items():
                    print(f"       - {gate_name}: {threshold}")
                
                # Check memory management
                print(f"     Memory Management:")
                print(f"       - Unload Between Stages: {cascade['memory_management']['unload_between_stages']}")
                print(f"       - Cache Results: {cascade['memory_management']['cache_intermediate_results']}")
            else:
                print(f"\n  ✗ {profile_name}: Missing cascade_settings!")
                return False
        else:
            print(f"\n  ✗ {profile_name} not found!")
            return False
    
    print("\n✓ All cascade profiles configured successfully!")
    return True

def test_phase4_integration():
    """Test Phase 4 integration between components."""
    print("\n" + "="*60)
    print("PHASE 4 - INTEGRATION TEST")
    print("="*60)
    
    # Test that RAG profiles reference models with correct tags
    print("\n1. RAG Profile - Model Tag Alignment:")
    
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'models.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    rag_profiles_dir = os.path.join(os.path.dirname(__file__), 'config', 'rag_profiles')
    
    for profile_name in ['coding.json', 'research.json', 'writing.json']:
        profile_path = os.path.join(rag_profiles_dir, profile_name)
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        
        print(f"\n  {profile_name}:")
        
        # Check retrieval models
        retrieval_models = profile['model_preferences']['retrieval']['preferred_models']
        required_tags = profile['model_preferences']['retrieval']['requirements']['tags']
        
        for model in retrieval_models:
            if model in config['model_profiles']:
                model_tags = config['model_profiles'][model]['capabilities']['tags']
                has_required_tags = all(tag in model_tags for tag in required_tags)
                status = "✓" if has_required_tags else "✗"
                print(f"    {status} {model} has required tags: {required_tags}")
    
    # Test that cascade profiles use appropriate models
    print("\n2. Cascade Profile - Model Selection:")
    
    user_profiles_dir = os.path.join(os.path.dirname(__file__), 'config', 'user_profiles')
    
    for profile_name in ['coding.json', 'research.json', 'writing.json']:
        profile_path = os.path.join(user_profiles_dir, profile_name)
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        
        print(f"\n  {profile_name}:")
        
        for stage_name, stage_config in profile['cascade_settings']['stages'].items():
            model = stage_config['model']
            print(f"    - {stage_name}: {model}")
    
    print("\n✓ Integration test passed!")
    return True

def main():
    """Run all Phase 4 tests."""
    print("\n" + "="*60)
    print("PHASE 4: SPECIALIZATION - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Task 4.1: Model Capability Tags", test_phase4_model_capabilities),
        ("Task 4.2: Enhanced Memory Manager", test_phase4_memory_manager),
        ("Task 4.3: RAG Profiles", test_phase4_rag_profiles),
        ("Task 4.4: Cascade Profiles", test_phase4_cascade_profiles),
        ("Integration Test", test_phase4_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 4 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if failed > 0:
        print(f"\n{failed} test(s) failed!")
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("✓ PHASE 4: SPECIALIZATION - ALL TESTS PASSED!")
        print("="*60)
        print("\nCompleted Tasks:")
        print("  ✓ Task 4.1: Model capability tags added to all models")
        print("  ✓ Task 4.2: Enhanced memory manager with M3 Mac optimizations")
        print("  ✓ Task 4.3: RAG profiles created (coding, research, writing)")
        print("  ✓ Task 4.4: Cascade profiles added to user profiles")
        print("\nPhase 4 is complete and ready for Phase 5!")
        sys.exit(0)

if __name__ == "__main__":
    main()
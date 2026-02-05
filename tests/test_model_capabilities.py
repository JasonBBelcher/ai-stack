#!/usr/bin/env python3
"""
Test script to verify model capability tags and selection logic.

This script tests the new capability tags added to models.json
and verifies that models can be selected based on their tags.
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def load_models_config():
    """Load the models.json configuration."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'models.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def test_capability_tags():
    """Test that all models have capability tags."""
    config = load_models_config()
    
    print("="*60)
    print("TEST 1: Verify Capability Tags")
    print("="*60)
    
    # Check local models
    print("\nLocal Models:")
    for model_name, model_data in config['model_profiles'].items():
        capabilities = model_data['capabilities']
        if 'tags' in capabilities:
            tags = capabilities['tags']
            print(f"  ✓ {model_name}: {tags}")
        else:
            print(f"  ✗ {model_name}: Missing tags!")
            return False
    
    # Check cloud models
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

def test_model_selection_by_tag():
    """Test selecting models based on capability tags."""
    config = load_models_config()
    
    print("\n" + "="*60)
    print("TEST 2: Model Selection by Tag")
    print("="*60)
    
    # Define test scenarios
    scenarios = [
        ("coding", "Find best coding model"),
        ("reasoning", "Find best reasoning model"),
        ("generation", "Find best generation model"),
        ("function-calling", "Find best function-calling model"),
        ("long-context", "Find best long-context model"),
    ]
    
    for tag, description in scenarios:
        print(f"\n{description} (tag: {tag}):")
        
        # Find models with this tag
        matching_models = []
        
        # Check local models
        for model_name, model_data in config['model_profiles'].items():
            capabilities = model_data['capabilities']
            if 'tags' in capabilities and tag in capabilities['tags']:
                strength = capabilities.get(f"{tag.split('-')[0]}_strength", 0.5)
                matching_models.append((model_name, strength, 'local'))
        
        # Check cloud models
        for provider, provider_data in config['cloud_providers'].items():
            for model_name, model_data in provider_data['models'].items():
                capabilities = model_data['capabilities']
                if 'tags' in capabilities and tag in capabilities['tags']:
                    strength = capabilities.get(f"{tag.split('-')[0]}_strength", 0.5)
                    matching_models.append((f"{provider}/{model_name}", strength, 'cloud'))
        
        # Sort by strength
        matching_models.sort(key=lambda x: x[1], reverse=True)
        
        if matching_models:
            print(f"  Found {len(matching_models)} matching models:")
            for model_name, strength, model_type in matching_models[:3]:  # Show top 3
                print(f"    - {model_name} ({model_type}, strength: {strength:.2f})")
        else:
            print(f"  ✗ No models found with tag '{tag}'")
            return False
    
    print("\n✓ Model selection by tag working!")
    return True

def test_model_ranking():
    """Test ranking models by multiple criteria."""
    config = load_models_config()
    
    print("\n" + "="*60)
    print("TEST 3: Model Ranking")
    print("="*60)
    
    # Test scenario: Find best coding model with function calling
    print("\nScenario: Best coding model with function calling:")
    
    candidates = []
    for model_name, model_data in config['model_profiles'].items():
        capabilities = model_data['capabilities']
        
        # Check if model has required tags
        has_coding = 'tags' in capabilities and 'coding' in capabilities['tags']
        has_function_calling = capabilities.get('supports_function_calling', False)
        
        if has_coding and has_function_calling:
            # Calculate score based on multiple factors
            coding_strength = capabilities.get('coding_strength', 0)
            reasoning_strength = capabilities.get('reasoning_strength', 0)
            memory_efficiency = 1.0 / capabilities.get('recommended_memory_gb', 10)
            
            score = (coding_strength * 0.5 + 
                    reasoning_strength * 0.3 + 
                    memory_efficiency * 0.2)
            
            candidates.append({
                'name': model_name,
                'score': score,
                'coding_strength': coding_strength,
                'memory_gb': capabilities.get('recommended_memory_gb', 0)
            })
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    if candidates:
        print(f"  Found {len(candidates)} candidates:")
        for i, model in enumerate(candidates, 1):
            print(f"    {i}. {model['name']}")
            print(f"       Score: {model['score']:.3f}")
            print(f"       Coding strength: {model['coding_strength']:.2f}")
            print(f"       Memory: {model['memory_gb']} GB")
    else:
        print("  ✗ No models found matching criteria")
        return False
    
    print("\n✓ Model ranking working!")
    return True

def test_tag_coverage():
    """Test that all important tags are covered."""
    config = load_models_config()
    
    print("\n" + "="*60)
    print("TEST 4: Tag Coverage")
    print("="*60)
    
    # Collect all tags
    all_tags = set()
    for model_name, model_data in config['model_profiles'].items():
        capabilities = model_data['capabilities']
        if 'tags' in capabilities:
            all_tags.update(capabilities['tags'])
    
    for provider, provider_data in config['cloud_providers'].items():
        for model_name, model_data in provider_data['models'].items():
            capabilities = model_data['capabilities']
            if 'tags' in capabilities:
                all_tags.update(capabilities['tags'])
    
    # Expected tags
    expected_tags = {
        'coding', 'reasoning', 'generation', 'multilingual',
        'function-calling', 'vision', 'cloud', 'long-context', 'premium'
    }
    
    print(f"\nFound {len(all_tags)} unique tags:")
    for tag in sorted(all_tags):
        count = 0
        for model_name, model_data in config['model_profiles'].items():
            capabilities = model_data['capabilities']
            if 'tags' in capabilities and tag in capabilities['tags']:
                count += 1
        for provider, provider_data in config['cloud_providers'].items():
            for model_name, model_data in provider_data['models'].items():
                capabilities = model_data['capabilities']
                if 'tags' in capabilities and tag in capabilities['tags']:
                    count += 1
        print(f"  - {tag}: {count} models")
    
    # Check for missing expected tags
    missing_tags = expected_tags - all_tags
    if missing_tags:
        print(f"\n⚠ Warning: Missing expected tags: {missing_tags}")
    else:
        print(f"\n✓ All expected tags are covered!")
    
    return True

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MODEL CAPABILITY TAGS TEST SUITE")
    print("="*60)
    
    tests = [
        test_capability_tags,
        test_model_selection_by_tag,
        test_model_ranking,
        test_tag_coverage,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ {test.__name__} failed with error: {e}")
            results.append((test.__name__, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
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
        print("\n✓ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
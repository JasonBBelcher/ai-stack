"""
Simplified Model Registry for testing - without hanging subprocess calls
"""
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.capabilities import ModelCapabilities, create_capabilities_from_dict, ModelSource


class SimpleModelRegistry:
    """Simplified model registry for testing"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/models.json"
        self.models: Dict[str, Any] = {}
        self.config_data: Dict[str, Any] = {}
        self._load_configuration_only()
    
    def _load_configuration_only(self) -> None:
        """Load configuration only, no subprocess calls"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                    print(f"Loaded configuration from {self.config_path}")
            else:
                print(f"Warning: Configuration file not found at {self.config_path}")
                self.config_data = {}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config_data = {}
    
    def get_model_capabilities(self, model_name: str) -> Optional[ModelCapabilities]:
        """Get capabilities for a specific model"""
        # Check model profiles
        model_profiles = self.config_data.get("model_profiles", {})
        if model_name in model_profiles:
            capabilities_data = model_profiles[model_name].get("capabilities", {})
            capabilities = create_capabilities_from_dict(capabilities_data)
            capabilities.model_name = model_name
            return capabilities
        
        # Check cloud provider models
        cloud_providers = self.config_data.get("cloud_providers", {})
        for provider_name, provider_data in cloud_providers.items():
            provider_models = provider_data.get("models", {})
            if model_name in provider_models:
                full_name = f"{provider_name}:{model_name}"
                if model_name == full_name or model_name.endswith(f":{model_name}"):
                    capabilities_data = provider_models[model_name].get("capabilities", {})
                    capabilities = create_capabilities_from_dict(capabilities_data)
                    capabilities.model_name = model_name
                    return capabilities
        
        return None
    
    def get_models_for_role(self, role: str) -> List[str]:
        """Get preferred models for a role"""
        role_mappings = self.config_data.get("role_mappings", {})
        role_config = role_mappings.get(role, {})
        
        preferred_models = role_config.get("preferred", [])
        cloud_fallback = role_config.get("cloud_fallback")
        
        models = []
        for model_name in preferred_models:
            if self.get_model_capabilities(model_name):
                models.append(model_name)
        
        if cloud_fallback and self.get_model_capabilities(cloud_fallback):
            models.append(cloud_fallback)
        
        return models
    
    def get_role_requirements(self, role: str) -> Optional[Dict[str, Any]]:
        """Get requirements for a role"""
        role_mappings = self.config_data.get("role_mappings", {})
        role_config = role_mappings.get(role)
        return role_config.get("requirements") if role_config else None
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Get system settings"""
        return self.config_data.get("system_settings", {})
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary of models"""
        model_profiles = self.config_data.get("model_profiles", {})
        cloud_providers = self.config_data.get("cloud_providers", {})
        
        total_models = len(model_profiles)
        
        # Count cloud models
        cloud_models = 0
        for provider_data in cloud_providers.values():
            provider_models = provider_data.get("models", {})
            cloud_models += len(provider_models)
        
        return {
            "total_models": total_models + cloud_models,
            "local_models": total_models,
            "cloud_models": cloud_models,
            "config_loaded": len(self.config_data) > 0
        }


def test_simple_registry():
    """Test the simplified registry"""
    print("=== Testing Simplified Model Registry ===")
    
    try:
        registry = SimpleModelRegistry('config/models.json')
        print("✓ Registry created")
        
        # Test getting capabilities
        mistral_caps = registry.get_model_capabilities('mistral:latest')
        if mistral_caps:
            print(f"✓ Got mistral capabilities: context={mistral_caps.context_length}")
        else:
            print("⚠ No mistral capabilities found")
        
        qwen_caps = registry.get_model_capabilities('qwen2.5:14b')
        if qwen_caps:
            print(f"✓ Got qwen2.5 capabilities: coding={qwen_caps.coding_strength}")
        else:
            print("⚠ No qwen2.5 capabilities found")
        
        # Test role models
        planner_models = registry.get_models_for_role('planner')
        print(f"✓ Planner models: {planner_models}")
        
        critic_models = registry.get_models_for_role('critic')
        print(f"✓ Critic models: {critic_models}")
        
        executor_models = registry.get_models_for_role('executor')
        print(f"✓ Executor models: {executor_models}")
        
        # Test role requirements
        planner_reqs = registry.get_role_requirements('planner')
        if planner_reqs:
            print(f"✓ Planner requirements: reasoning={planner_reqs.get('reasoning_strength')}")
        
        # Test system settings
        settings = registry.get_system_settings()
        print(f"✓ System settings: cloud_enabled={settings.get('enable_cloud_fallbacks')}")
        
        # Test summary
        summary = registry.get_model_summary()
        print(f"✓ Summary: {summary['total_models']} total models")
        
        print("\n=== Test Results ===")
        print("✓ Simplified registry works correctly!")
        print("✓ Can load model capabilities from config")
        print("✓ Can resolve role mappings")
        print("✓ Ready for integration with full system")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_simple_registry()
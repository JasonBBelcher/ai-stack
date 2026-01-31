"""
Enhanced Configuration System - Dynamic model configuration with generic swappability
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.model_registry import ModelRegistry
from src.profile_manager import ProfileManager
from src.role_mapper import RoleMapper, SystemConstraints, SelectionCriteria
from src.capabilities import ModelCapabilities, create_capabilities_from_dict
from src.memory_manager import MemoryManager


class ModelType:
    """Model role types"""
    PLANNER = "planner"
    CRITIC = "critic"
    EXECUTOR = "executor"


@dataclass
class ModelConfig:
    """Configuration for a specific model instance"""
    name: str
    ollama_name: Optional[str]  # None for cloud models
    type: str
    temperature: float
    max_tokens: int
    memory_gb: float
    capabilities: Optional[ModelCapabilities] = None
    source: str = "ollama"  # ollama, openai, anthropic, etc.


@dataclass
class SystemConfig:
    """System-wide configuration"""
    enable_cloud_fallbacks: bool = False
    max_memory_usage_gb: float = 14.0
    thermal_threshold: float = 0.8
    auto_discover_models: bool = True
    validation_timeout_seconds: int = 60
    default_temperature: Dict[str, float] = None
    
    def __post_init__(self):
        if self.default_temperature is None:
            self.default_temperature = {
                ModelType.PLANNER: 0.2,
                ModelType.CRITIC: 0.1,
                ModelType.EXECUTOR: 0.3
            }


class AIStackConfig:
    """Enhanced configuration system with generic model support"""
    
    def __init__(self, config_path: Optional[str] = None, profile_name: Optional[str] = None):
        self.config_path = config_path or "config/models.json"
        self.profile_name = profile_name
        
        # Initialize core components
        self.model_registry = ModelRegistry(self.config_path)
        self.profile_manager = ProfileManager()
        self.memory_manager = MemoryManager()
        
        # Load configuration
        self._load_configuration()
        
        # Create default profiles if needed
        if not self.profile_manager.list_profiles():
            self.profile_manager.create_default_profiles()
        
        # Set active profile if specified
        if profile_name:
            self.profile_manager.set_active_profile(profile_name)
    
    def _load_configuration(self) -> None:
        """Load and merge configuration from multiple sources"""
        # Base configuration from file
        base_config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    base_config = json.load(f)
            except Exception as e:
                print(f"Error loading base configuration: {e}")
        
        # User profile overrides
        profile_config = {}
        if self.profile_name:
            profile = self.profile_manager.load_profile(self.profile_name)
            if profile:
                profile_config = {
                    'role_mappings': profile.role_mappings,
                    'system_settings': profile.system_settings,
                    'selection_preferences': profile.selection_preferences,
                    'cloud_settings': profile.cloud_settings
                }
        elif self.profile_manager.get_active_profile():
            active_profile = self.profile_manager.get_active_profile()
            profile_config = {
                'role_mappings': active_profile.role_mappings,
                'system_settings': active_profile.system_settings,
                'selection_preferences': active_profile.selection_preferences,
                'cloud_settings': active_profile.cloud_settings
            }
        
        # User global overrides
        user_config = {}
        user_config_path = "config/user_models.json"
        if os.path.exists(user_config_path):
            try:
                with open(user_config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
            except Exception as e:
                print(f"Error loading user configuration: {e}")
        
        # Merge configurations (priority: user > profile > base)
        self.merged_config = self._merge_configs(base_config, profile_config, user_config)
        
        # Update registry with merged config
        self.model_registry.config_data = self.merged_config
        
        # Refresh model discovery
        self.model_registry.refresh()
    
    def _merge_configs(self, base: Dict[str, Any], profile: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configurations with user overrides"""
        merged = {}
        
        # Start with base config
        merged.update(base)
        
        # Apply profile overrides
        for key, value in profile.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        # Apply user overrides
        for key, value in user.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        return merged
    
    def get_model_for_role(
        self, 
        role: str, 
        system_constraints: Optional[SystemConstraints] = None,
        selection_criteria: Optional[SelectionCriteria] = None
    ) -> Optional[ModelConfig]:
        """Get the best model configuration for a specific role"""
        
        if not isinstance(role, str):
            role = role.value if hasattr(role, 'value') else str(role)
        
        # Create role mapper
        role_mapper = RoleMapper(self.model_registry)
        
        # Get system constraints
        if system_constraints is None:
            system_constraints = SystemConstraints.from_memory_manager(
                self.memory_manager, 
                self.model_registry
            )
        
        # Get user preferences from active profile
        user_preferences = None
        active_profile = self.profile_manager.get_active_profile()
        if active_profile:
            user_preferences = active_profile.selection_preferences
        
        # Select best model
        selection = role_mapper.select_model_for_role(
            ModelType.PLANNER if role == "planner" else ModelType.CRITIC if role == "critic" else ModelType.EXECUTOR,
            system_constraints,
            selection_criteria,
            user_preferences
        )
        
        if not selection.is_valid:
            print(f"Warning: No valid model found for role {role}: {selection.validation.issues}")
            return None
        
        # Create model config
        return self._create_model_config_from_selection(selection, role)
    
    def _create_model_config_from_selection(self, selection, role: str) -> ModelConfig:
        """Create ModelConfig from selection result"""
        capabilities = selection.capabilities
        
        # Get temperature defaults
        system_settings = self.merged_config.get("system_settings", {})
        default_temps = system_settings.get("default_temperature", {
            "planner": 0.2,
            "critic": 0.1,
            "executor": 0.3
        })
        
        # Check for role-specific overrides
        role_mappings = self.merged_config.get("role_mappings", {})
        role_config = role_mappings.get(role, {})
        
        # Start with default temperature
        temperature = default_temps.get(role, 0.2)
        
        # Apply role-specific temperature if available
        if "temperature" in role_config:
            temperature = role_config["temperature"]
        
        # Apply model-specific temperature overrides
        model_profiles = self.merged_config.get("model_profiles", {})
        model_name = selection.model_name
        
        # Handle cloud model names (provider:model)
        base_model_name = model_name
        if ":" in model_name:
            provider, model_id = model_name.split(":", 1)
            # Look in cloud provider models
            cloud_providers = self.merged_config.get("cloud_providers", {})
            if provider in cloud_providers:
                provider_models = cloud_providers[provider].get("models", {})
                if model_id in provider_models:
                    provider_config = provider_models[model_id]
                    if "temperature" in provider_config:
                        temperature = provider_config["temperature"]
        else:
            # Look in model profiles
            if model_name in model_profiles:
                model_profile = model_profiles[model_name]
                temp_overrides = model_profile.get("temperature_defaults", {})
                if role in temp_overrides:
                    temperature = temp_overrides[role]
        
        # Calculate max tokens
        max_tokens = self._calculate_max_tokens_for_model(capabilities)
        
        return ModelConfig(
            name=selection.model_name,
            ollama_name=selection.model_name if capabilities.model_source == "ollama" else None,
            type=role,
            temperature=temperature,
            max_tokens=max_tokens,
            memory_gb=capabilities.recommended_memory_gb,
            capabilities=capabilities,
            source=capabilities.model_source
        )
    
    def _calculate_max_tokens_for_model(self, capabilities: ModelCapabilities) -> int:
        """Calculate appropriate max tokens based on model capabilities"""
        context_tokens = capabilities.context_length
        
        if context_tokens >= 128000:
            return min(8000, context_tokens // 16)
        elif context_tokens >= 64000:
            return min(6000, context_tokens // 10)
        elif context_tokens >= 32000:
            return min(4000, context_tokens // 8)
        else:
            return min(2000, context_tokens // 4)
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        system_settings = self.merged_config.get("system_settings", {})
        return SystemConfig(
            enable_cloud_fallbacks=system_settings.get("enable_cloud_fallbacks", False),
            max_memory_usage_gb=system_settings.get("max_memory_usage_gb", 14.0),
            thermal_threshold=system_settings.get("thermal_threshold", 0.8),
            auto_discover_models=system_settings.get("auto_discover_models", True),
            validation_timeout_seconds=system_settings.get("validation_timeout_seconds", 30),
            default_temperature=system_settings.get("default_temperature", {
                ModelType.PLANNER: 0.2,
                ModelType.CRITIC: 0.1,
                ModelType.EXECUTOR: 0.3
            })
        )
    
    def refresh_models(self) -> None:
        """Refresh model discovery"""
        self.model_registry.refresh()
        self._load_configuration()  # Reload with new models
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile"""
        if self.profile_manager.set_active_profile(profile_name):
            self.profile_name = profile_name
            self._load_configuration()
            return True
        return False
    
    def create_profile_from_current(self, name: str, description: str) -> bool:
        """Create a new profile from current configuration"""
        from .profile_manager import UserProfile
        
        profile = self.profile_manager.create_profile_from_current_config(
            name, description, self.merged_config
        )
        
        return self.profile_manager.save_profile(profile)
    
    def get_available_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available profiles"""
        return self.profile_manager.list_profiles()
    
    def get_model_recommendations(self, role: str, max_count: int = 5) -> List[Dict[str, Any]]:
        """Get model recommendations for a role"""
        role_mapper = RoleMapper(self.model_registry)
        system_constraints = SystemConstraints.from_memory_manager(
            self.memory_manager, 
            self.model_registry
        )
        
        model_type = (ModelType.PLANNER if role == "planner" else 
                     ModelType.CRITIC if role == "critic" else 
                     ModelType.EXECUTOR)
        
        recommendations = role_mapper.get_model_recommendations(
            model_type, system_constraints, max_count
        )
        
        return [
            {
                'model_name': selection.model_name,
                'score': selection.validation.score,
                'capabilities': selection.capabilities,
                'source': selection.source,
                'validation': selection.validation
            }
            for selection in recommendations
        ]
    
    def validate_model_for_role(self, model_name: str, role: str) -> Dict[str, Any]:
        """Validate if a model is suitable for a role"""
        role_mapper = RoleMapper(self.model_registry)
        system_constraints = SystemConstraints.from_memory_manager(
            self.memory_manager, 
            self.model_registry
        )
        
        model_type = (ModelType.PLANNER if role == "planner" else 
                     ModelType.CRITIC if role == "critic" else 
                     ModelType.EXECUTOR)
        
        validation = role_mapper.validate_model_for_role(
            model_name, model_type, system_constraints
        )
        
        return {
            'is_valid': validation.is_valid,
            'score': validation.score,
            'issues': validation.issues,
            'warnings': validation.warnings
        }
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model"""
        capabilities = self.model_registry.get_model_capabilities(model_name)
        if not capabilities:
            return None
        
        return {
            'name': model_name,
            'capabilities': capabilities,
            'source': capabilities.model_source,
            'is_validated': self.model_registry.validate_model_exists(model_name),
            'memory_gb': capabilities.recommended_memory_gb
        }
    
    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available models"""
        models_info = {}
        
        for model_name, model_info in self.model_registry.models.items():
            if model_info.capabilities:
                models_info[model_name] = {
                    'name': model_name,
                    'source': model_info.source,
                    'validated': model_info.validated,
                    'capabilities': model_info.capabilities.to_dict(),
                    'memory_gb': model_info.capabilities.recommended_memory_gb
                }
        
        return models_info
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all available models with information"""
        return self.get_all_models()
    
    def export_configuration(self, export_path: str, include_profiles: bool = True) -> bool:
        """Export current configuration to file"""
        try:
            export_data = {
                'base_config': self.merged_config,
                'active_profile': self.profile_manager.get_active_profile_name()
            }
            
            if include_profiles:
                export_data['profiles'] = {}
                for profile in self.profile_manager.list_profiles():
                    profile_name = profile['name']
                    profile_obj = self.profile_manager.load_profile(profile_name)
                    if profile_obj:
                        export_data['profiles'][profile_name] = profile_obj.to_dict()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting configuration: {e}")
            return False
    
    def import_configuration(self, import_path: str) -> bool:
        """Import configuration from file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import base configuration
            if 'base_config' in import_data:
                # Save to user_models.json
                user_config_path = "config/user_models.json"
                with open(user_config_path, 'w', encoding='utf-8') as f:
                    json.dump(import_data['base_config'], f, indent=2)
            
            # Import profiles
            if 'profiles' in import_data:
                for profile_name, profile_data in import_data['profiles'].items():
                    from .profile_manager import UserProfile
                    profile = UserProfile.from_dict(profile_data)
                    self.profile_manager.save_profile(profile, overwrite=True)
            
            # Set active profile
            if 'active_profile' in import_data:
                self.profile_manager.set_active_profile(import_data['active_profile'])
            
            # Reload configuration
            self._load_configuration()
            
            return True
            
        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False
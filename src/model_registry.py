"""
Model Registry - Central model discovery, registration, and validation system
"""
import subprocess
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from src.capabilities import ModelCapabilities, create_capabilities_from_dict, ModelSource


class ModelInfo:
    """Information about a discovered model"""
    
    def __init__(self, name: str, source: str = "ollama", capabilities: Optional[ModelCapabilities] = None):
        self.name = name
        self.source = source
        self.capabilities = capabilities
        self.discovered_at = time.time()
        self.validated = False
        self.last_validation = None
    
    def __repr__(self) -> str:
        return f"ModelInfo(name='{self.name}', source='{self.source}', validated={self.validated})"


class ModelRegistry:
    """Central registry for model discovery and management"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/models.json"
        self.models: Dict[str, ModelInfo] = {}
        self.config_data: Dict[str, Any] = {}
        self.last_discovery = 0.0
        
        # Load configuration and discover models
        self._load_configuration()
        self.discover_models()
    
    def _load_configuration(self) -> None:
        """Load model configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                print(f"Warning: Configuration file not found at {self.config_path}")
                self.config_data = {}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config_data = {}
    
    def discover_models(self, force_rediscovery: bool = False) -> Dict[str, ModelInfo]:
        """Discover available models from Ollama and configuration"""
        current_time = time.time()
        
        # Skip rediscovery if done recently (within last 60 seconds)
        if not force_rediscovery and current_time - self.last_discovery < 60:
            return self.models
        
        self.models.clear()
        
        # Discover Ollama models
        ollama_models = self._discover_ollama_models()
        for model_name in ollama_models:
            self.models[model_name] = ModelInfo(model_name, source="ollama")
        
        # Add configured models (including cloud models)
        configured_models = self._load_configured_models()
        for model_name, capabilities in configured_models.items():
            if model_name in self.models:
                # Update existing model with capabilities from config
                self.models[model_name].capabilities = capabilities
            else:
                # Add new model (could be cloud model)
                source = capabilities.model_source if capabilities else "configured"
                self.models[model_name] = ModelInfo(model_name, source=source, capabilities=capabilities)
        
        # Validate models
        self._validate_models()
        self.last_discovery = current_time
        
        return self.models
    
    def _discover_ollama_models(self) -> List[str]:
        """Discover models available in Ollama"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            else:
                print(f"Error discovering Ollama models: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Exception discovering Ollama models: {e}")
            return []
    
    def _load_configured_models(self) -> Dict[str, ModelCapabilities]:
        """Load model capabilities from configuration"""
        models = {}
        
        # Load model profiles from config
        model_profiles = self.config_data.get("model_profiles", {})
        for model_name, model_data in model_profiles.items():
            capabilities_data = model_data.get("capabilities", {})
            capabilities = create_capabilities_from_dict(capabilities_data)
            capabilities.model_name = model_name
            models[model_name] = capabilities
        
        # Load cloud provider models
        cloud_providers = self.config_data.get("cloud_providers", {})
        for provider_name, provider_data in cloud_providers.items():
            provider_models = provider_data.get("models", {})
            for model_name, model_data in provider_models.items():
                full_model_name = f"{provider_name}:{model_name}"
                capabilities_data = model_data.get("capabilities", {})
                capabilities = create_capabilities_from_dict(capabilities_data)
                capabilities.model_name = full_model_name
                capabilities.display_name = model_name
                models[full_model_name] = capabilities
        
        return models
    
    def _validate_models(self) -> None:
        """Validate that models are accessible and working"""
        validation_timeout = self.config_data.get("system_settings", {}).get("validation_timeout_seconds", 60)
        
        for model_name, model_info in self.models.items():
            if model_info.source == "ollama":
                # Validate Ollama models
                is_valid = self._validate_ollama_model(model_name, validation_timeout)
                model_info.validated = is_valid
                model_info.last_validation = time.time()
            elif model_info.source in ["openai", "anthropic"]:
                # Cloud models require API key validation
                is_valid = self._validate_cloud_model(model_name, model_info.source)
                model_info.validated = is_valid
                model_info.last_validation = time.time()
            else:
                # Configured models are assumed valid
                model_info.validated = True
                model_info.last_validation = time.time()
    
    def _validate_ollama_model(self, model_name: str, timeout: int) -> bool:
        """Validate that an Ollama model is accessible"""
        try:
            # Fast validation: just check if model info is accessible via ollama show
            result = subprocess.run(
                ["ollama", "show", model_name],
                capture_output=True,
                text=True,
                timeout=5  # Short timeout for show command
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"Timeout validating model {model_name}")
            return False
        except Exception as e:
            print(f"Error validating model {model_name}: {e}")
            return False
    
    def _validate_cloud_model(self, model_name: str, provider: str) -> bool:
        """Validate that cloud model API is accessible (placeholder for now)"""
        # TODO: Implement actual API key validation
        # For now, assume valid if we have API keys configured
        return self._check_api_key_exists(provider)
    
    def _check_api_key_exists(self, provider: str) -> bool:
        """Check if API key exists for provider"""
        try:
            api_keys_file = Path("config/api_keys.json")
            if not api_keys_file.exists():
                return False
            
            with open(api_keys_file, 'r', encoding='utf-8') as f:
                api_keys = json.load(f)
            
            return provider in api_keys and api_keys[provider]
        except Exception:
            return False
    
    def get_model_capabilities(self, model_name: str) -> Optional[ModelCapabilities]:
        """Get capabilities for a specific model"""
        model_info = self.models.get(model_name)
        if model_info:
            return model_info.capabilities
        return None
    
    def get_available_models(self, source_filter: Optional[str] = None, 
                          validated_only: bool = False) -> Dict[str, ModelInfo]:
        """Get available models with optional filtering"""
        filtered_models = {}
        
        for model_name, model_info in self.models.items():
            # Apply source filter
            if source_filter and model_info.source != source_filter:
                continue
            
            # Apply validation filter
            if validated_only and not model_info.validated:
                continue
            
            filtered_models[model_name] = model_info
        
        return filtered_models
    
    def get_models_by_source(self) -> Dict[str, List[str]]:
        """Get models grouped by source"""
        source_groups = {}
        
        for model_name, model_info in self.models.items():
            source = model_info.source
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(model_name)
        
        return source_groups
    
    def get_models_for_role(self, role: str) -> List[str]:
        """Get preferred models for a specific role"""
        role_mappings = self.config_data.get("role_mappings", {})
        role_config = role_mappings.get(role, {})
        
        preferred_models = role_config.get("preferred", [])
        cloud_fallback = role_config.get("cloud_fallback")
        
        # Filter to only available models
        available_models = []
        for model_name in preferred_models:
            if model_name in self.models:
                available_models.append(model_name)
        
        # Add cloud fallback if available
        if cloud_fallback and cloud_fallback in self.models:
            available_models.append(cloud_fallback)
        
        return available_models
    
    def validate_model_exists(self, model_name: str) -> bool:
        """Check if a model exists and is accessible"""
        model_info = self.models.get(model_name)
        if not model_info:
            return False
        
        return model_info.validated
    
    def get_model_source(self, model_name: str) -> Optional[str]:
        """Get the source of a model"""
        model_info = self.models.get(model_name)
        return model_info.source if model_info else None
    
    def get_role_requirements(self, role: str) -> Optional[Dict[str, Any]]:
        """Get requirements for a specific role from configuration"""
        role_mappings = self.config_data.get("role_mappings", {})
        role_config = role_mappings.get(role)
        return role_config.get("requirements") if role_config else None
    
    def get_cloud_fallback_for_role(self, role: str) -> Optional[str]:
        """Get cloud fallback model for a role"""
        role_mappings = self.config_data.get("role_mappings", {})
        role_config = role_mappings.get(role)
        return role_config.get("cloud_fallback") if role_config else None
    
    def refresh(self) -> None:
        """Force refresh of model discovery"""
        self.discover_models(force_rediscovery=True)
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Get system settings from configuration"""
        return self.config_data.get("system_settings", {})
    
    def is_cloud_enabled(self) -> bool:
        """Check if cloud fallbacks are enabled"""
        settings = self.get_system_settings()
        return settings.get("enable_cloud_fallbacks", False)
    
    def get_max_memory_usage(self) -> float:
        """Get maximum memory usage setting"""
        settings = self.get_system_settings()
        return settings.get("max_memory_usage_gb", 14.0)
    
    def get_thermal_threshold(self) -> float:
        """Get thermal threshold setting"""
        settings = self.get_system_settings()
        return settings.get("thermal_threshold", 0.8)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary of discovered models"""
        total_models = len(self.models)
        validated_models = sum(1 for m in self.models.values() if m.validated)
        
        sources = {}
        for model_info in self.models.values():
            source = model_info.source
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_models": total_models,
            "validated_models": validated_models,
            "sources": sources,
            "last_discovery": self.last_discovery
        }
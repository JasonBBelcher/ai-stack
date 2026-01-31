"""
Model Factory - Generic model instantiation and runtime switching
"""
import subprocess
import time
import json
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum

from src.model_registry import ModelRegistry
from src.capabilities import ModelCapabilities
from src.enhanced_config import ModelType, ModelConfig


class ModelState(Enum):
    """Model operational states"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    SWITCHING = "switching"


@dataclass
class ModelInstance:
    """Represents an active model instance"""
    name: str
    capabilities: ModelCapabilities
    config: ModelConfig
    state: ModelState = ModelState.UNLOADED
    load_time: Optional[float] = None
    memory_usage: float = 0.0
    last_used: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    def __post_init__(self):
        if self.capabilities and self.capabilities.model_name:
            self.name = self.capabilities.model_name


@dataclass
class SwitchResult:
    """Result of model switching operation"""
    success: bool
    old_model: Optional[str] = None
    new_model: Optional[str] = None
    switch_time: float = 0.0
    error_message: Optional[str] = None


class ModelFactory:
    """Factory for creating and managing model instances"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.active_models: Dict[str, ModelInstance] = {}
        self.hot_swap_enabled = False
        self.default_switch_timeout = 60  # seconds
    
    def create_model(
        self, 
        model_name: str, 
        role: ModelType,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> ModelInstance:
        """Create a model instance with configuration"""
        
        # Get model capabilities
        capabilities = self.registry.get_model_capabilities(model_name)
        if not capabilities:
            raise ValueError(f"Model {model_name} not found in registry")
        
        # Create base configuration
        config = self._create_model_config(model_name, role, capabilities)
        
        # Apply configuration overrides
        if config_overrides:
            config = self._apply_config_overrides(config, config_overrides)
        
        # Create model instance
        instance = ModelInstance(
            name=model_name,
            capabilities=capabilities,
            config=config
        )
        
        return instance
    
    def _create_model_config(
        self, 
        model_name: str, 
        role: ModelType,
        capabilities: ModelCapabilities
    ) -> ModelConfig:
        """Create base configuration for a model"""
        
        # Get default temperature for role
        system_settings = self.registry.get_system_settings()
        default_temps = system_settings.get("default_temperature", {})
        temperature = default_temps.get(role.value, 0.2)
        
        # Override with model-specific defaults if available
        # This would come from model profiles in the registry
        model_profile = self.registry.config_data.get("model_profiles", {}).get(model_name, {})
        temp_overrides = model_profile.get("temperature_defaults", {})
        temperature = temp_overrides.get(role.value, temperature)
        
        return ModelConfig(
            name=model_name,
            ollama_name=model_name if capabilities.model_source == "ollama" else None,
            type=role,
            temperature=temperature,
            max_tokens=self._calculate_max_tokens(capabilities),
            memory_gb=capabilities.recommended_memory_gb
        )
    
    def _calculate_max_tokens(self, capabilities: ModelCapabilities) -> int:
        """Calculate appropriate max tokens based on model capabilities"""
        # Base on context length, but leave room for system messages
        context_tokens = capabilities.context_length
        
        # Conservative estimate to leave room for prompts and system messages
        if context_tokens >= 128000:
            return min(8000, context_tokens // 16)
        elif context_tokens >= 64000:
            return min(6000, context_tokens // 10)
        elif context_tokens >= 32000:
            return min(4000, context_tokens // 8)
        else:
            return min(2000, context_tokens // 4)
    
    def _apply_config_overrides(
        self, 
        config: ModelConfig, 
        overrides: Dict[str, Any]
    ) -> ModelConfig:
        """Apply configuration overrides to model config"""
        
        if 'temperature' in overrides:
            config.temperature = overrides['temperature']
        
        if 'max_tokens' in overrides:
            config.max_tokens = overrides['max_tokens']
        
        if 'memory_gb' in overrides:
            config.memory_gb = overrides['memory_gb']
        
        return config
    
    def load_model(
        self, 
        instance: ModelInstance, 
        timeout: Optional[int] = None
    ) -> bool:
        """Load a model instance into memory"""
        
        if instance.state == ModelState.LOADED:
            return True
        
        if instance.state == ModelState.LOADING:
            # Wait for current loading to complete
            return self._wait_for_loading(instance, timeout or self.default_switch_timeout)
        
        timeout = timeout or self.default_switch_timeout
        instance.state = ModelState.LOADING
        start_time = time.time()
        
        try:
            if instance.config.ollama_name:  # Ollama model
                success = self._load_ollama_model(instance, timeout)
            else:  # Cloud model
                success = self._load_cloud_model(instance, timeout)
            
            if success:
                instance.state = ModelState.LOADED
                instance.load_time = time.time() - start_time
                instance.last_used = time.time()
                instance.error_count = 0
                instance.last_error = None
                return True
            else:
                instance.state = ModelState.ERROR
                instance.error_count += 1
                return False
                
        except Exception as e:
            instance.state = ModelState.ERROR
            instance.error_count += 1
            instance.last_error = str(e)
            return False
    
    def _load_ollama_model(self, instance: ModelInstance, timeout: int) -> bool:
        """Load an Ollama model"""
        try:
            # Pre-warm the model with a minimal prompt
            result = subprocess.run(
                ["ollama", "run", instance.config.ollama_name, "test"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                # Track memory usage
                instance.memory_usage = instance.config.memory_gb
                return True
            else:
                instance.last_error = result.stderr
                return False
                
        except subprocess.TimeoutExpired:
            instance.last_error = "Model loading timeout"
            return False
        except Exception as e:
            instance.last_error = str(e)
            return False
    
    def _load_cloud_model(self, instance: ModelInstance, timeout: int) -> bool:
        """Load a cloud model (placeholder for now)"""
        # TODO: Implement cloud model loading
        # For now, assume success if API keys are available
        provider = instance.capabilities.model_source
        
        # Check if API key exists
        api_key_available = self.registry._check_api_key_exists(provider)
        
        if api_key_available:
            instance.memory_usage = instance.config.memory_gb
            return True
        else:
            instance.last_error = f"API key not available for {provider}"
            return False
    
    def unload_model(self, instance: ModelInstance) -> bool:
        """Unload a model instance from memory"""
        
        if instance.state == ModelState.UNLOADED:
            return True
        
        try:
            if instance.config.ollama_name:  # Ollama model
                success = self._unload_ollama_model(instance)
            else:  # Cloud model
                success = self._unload_cloud_model(instance)
            
            if success:
                instance.state = ModelState.UNLOADED
                instance.memory_usage = 0.0
                return True
            else:
                return False
                
        except Exception as e:
            instance.last_error = str(e)
            instance.state = ModelState.ERROR
            return False
    
    def _unload_ollama_model(self, instance: ModelInstance) -> bool:
        """Unload an Ollama model"""
        try:
            result = subprocess.run(
                ["ollama", "stop", instance.config.ollama_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            instance.last_error = str(e)
            return False
    
    def _unload_cloud_model(self, instance: ModelInstance) -> bool:
        """Unload a cloud model (placeholder for now)"""
        # Cloud models don't need explicit unloading
        return True
    
    def switch_model(
        self, 
        current_instance: Optional[ModelInstance],
        new_instance: ModelInstance,
        timeout: Optional[int] = None
    ) -> SwitchResult:
        """Switch from current model to new model"""
        
        start_time = time.time()
        old_model_name = current_instance.name if current_instance else None
        
        try:
            # Step 1: Unload current model if exists
            if current_instance:
                current_instance.state = ModelState.SWITCHING
                if not self.unload_model(current_instance):
                    return SwitchResult(
                        success=False,
                        old_model=old_model_name,
                        new_model=new_instance.name,
                        error_message=f"Failed to unload {old_model_name}"
                    )
            
            # Step 2: Load new model
            new_instance.state = ModelState.SWITCHING
            if not self.load_model(new_instance, timeout):
                return SwitchResult(
                    success=False,
                    old_model=old_model_name,
                    new_model=new_instance.name,
                    error_message=f"Failed to load {new_instance.name}: {new_instance.last_error}"
                )
            
            switch_time = time.time() - start_time
            
            # Step 3: Update active models registry
            if current_instance and current_instance.name in self.active_models:
                del self.active_models[current_instance.name]
            
            self.active_models[new_instance.name] = new_instance
            
            return SwitchResult(
                success=True,
                old_model=old_model_name,
                new_model=new_instance.name,
                switch_time=switch_time
            )
            
        except Exception as e:
            return SwitchResult(
                success=False,
                old_model=old_model_name,
                new_model=new_instance.name,
                switch_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def get_active_model(self, role: ModelType) -> Optional[ModelInstance]:
        """Get the currently active model for a role"""
        # For now, return the most recently loaded model
        # TODO: Implement proper role-to-instance mapping
        if not self.active_models:
            return None
        
        # Return the most recently used model
        latest_model = max(
            self.active_models.values(),
            key=lambda x: x.last_used or 0
        )
        return latest_model
    
    def get_loaded_models(self) -> Dict[str, ModelInstance]:
        """Get all currently loaded models"""
        return {
            name: instance for name, instance in self.active_models.items()
            if instance.state == ModelState.LOADED
        }
    
    def get_model_instance(self, model_name: str) -> Optional[ModelInstance]:
        """Get a specific model instance"""
        return self.active_models.get(model_name)
    
    def create_instance_for_role(
        self, 
        role: ModelType,
        model_name: Optional[str] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> ModelInstance:
        """Create and optionally load a model instance for a role"""
        
        if not model_name:
            # Auto-select model for role
            from .role_mapper import RoleMapper, SystemConstraints
            from .memory_manager import MemoryManager
            
            role_mapper = RoleMapper(self.registry)
            memory_manager = MemoryManager()
            constraints = SystemConstraints.from_memory_manager(memory_manager, self.registry)
            
            selection = role_mapper.select_model_for_role(role, constraints)
            
            if not selection.is_valid:
                raise ValueError(f"No valid model found for role {role.value}")
            
            model_name = selection.model_name
        
        # Create instance
        instance = self.create_model(model_name, role, config_overrides)
        
        return instance
    
    def enable_hot_swap(self, enabled: bool) -> None:
        """Enable or disable hot swapping"""
        self.hot_swap_enabled = enabled
    
    def cleanup_unused_models(self, max_idle_time: float = 300) -> int:
        """Unload models that haven't been used recently"""
        
        current_time = time.time()
        unloaded_count = 0
        
        for model_name, instance in list(self.active_models.items()):
            if (instance.state == ModelState.LOADED and 
                instance.last_used and 
                current_time - instance.last_used > max_idle_time):
                
                if self.unload_model(instance):
                    unloaded_count += 1
                    if model_name in self.active_models:
                        del self.active_models[model_name]
        
        return unloaded_count
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage by loaded models"""
        return {
            name: instance.memory_usage
            for name, instance in self.active_models.items()
            if instance.state == ModelState.LOADED
        }
    
    def get_total_memory_usage(self) -> float:
        """Get total memory usage by all loaded models"""
        return sum(self.get_memory_usage().values())
    
    def validate_memory_constraints(self, additional_memory_gb: float = 0) -> bool:
        """Validate if loading additional models would exceed memory constraints"""
        max_memory = self.registry.get_max_memory_usage()
        current_usage = self.get_total_memory_usage()
        
        return (current_usage + additional_memory_gb) <= max_memory
    
    def _wait_for_loading(self, instance: ModelInstance, timeout: float) -> bool:
        """Wait for a model to finish loading"""
        start_time = time.time()
        
        while (instance.state == ModelState.LOADING and 
               time.time() - start_time < timeout):
            time.sleep(0.1)
        
        return instance.state == ModelState.LOADED
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for loaded models"""
        stats = {
            'total_models': len(self.active_models),
            'loaded_models': len(self.get_loaded_models()),
            'total_memory_usage': self.get_total_memory_usage(),
            'models': {}
        }
        
        for name, instance in self.active_models.items():
            stats['models'][name] = {
                'state': instance.state.value,
                'load_time': instance.load_time,
                'memory_usage': instance.memory_usage,
                'last_used': instance.last_used,
                'error_count': instance.error_count,
                'last_error': instance.last_error
            }
        
        return stats
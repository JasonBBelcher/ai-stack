"""
Configuration - Centralized settings for the AI stack
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    PLANNER = "planner"
    CRITIC = "critic"
    EXECUTOR = "executor"


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    ollama_name: str
    type: ModelType
    temperature: float
    max_tokens: int
    memory_gb: float
    alternative: str = None


@dataclass
class MemoryConfig:
    """Memory management configuration"""
    safety_buffer_gb: float = 2.0
    thermal_threshold: float = 0.85
    max_retries: int = 3
    retry_delay: float = 3.0
    cleanup_on_failure: bool = True


@dataclass
class OllamaConfig:
    """Ollama connection configuration"""
    base_url: str = "http://localhost:11434"
    timeout: int = 120
    health_check_interval: int = 10


@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    thermal_adjustment_enabled: bool = True
    memory_pressure_threshold: float = 0.8
    auto_cleanup_enabled: bool = True
    performance_monitoring: bool = True


class AIStackConfig:
    """Main configuration class for the AI stack"""
    
    def __init__(self):
        self.models = self._init_models()
        self.memory = MemoryConfig()
        self.ollama = OllamaConfig()
        self.performance = PerformanceConfig()
        
        # System-specific settings for M3 Mac with 16GB RAM
        self.system_memory_gb = 16.0
        self.apple_silicon = True
        self.metal_acceleration = True
    
    def _init_models(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations"""
        return {
            "mistral": ModelConfig(
                name="mistral",
                ollama_name="mistral:latest",
                type=ModelType.PLANNER,
                temperature=0.2,
                max_tokens=2000,
                memory_gb=5.0,
                alternative="qwen2.5-7b"
            ),
            "qwen2.5-14b": ModelConfig(
                name="qwen2.5-14b",
                ollama_name="qwen2.5:14b",
                type=ModelType.EXECUTOR,
                temperature=0.3,
                max_tokens=4000,
                memory_gb=10.0
            ),
            "qwen2.5-7b": ModelConfig(
                name="qwen2.5-7b",
                ollama_name="qwen2.5:7b",  # If available
                type=ModelType.CRITIC,
                temperature=0.1,
                max_tokens=1500,
                memory_gb=5.5,
                alternative="mistral"
            )
        }
    
    def get_model_config(self, model_name: str) -> ModelConfig:
        """Get configuration for a specific model"""
        for config in self.models.values():
            if config.name in model_name or model_name in config.name:
                return config
        
        # Try partial match
        for config in self.models.values():
            if config.name.split("-")[0] in model_name.lower():
                return config
        
        raise ValueError(f"Model configuration not found for: {model_name}")
    
    def get_planner_config(self) -> ModelConfig:
        """Get planner model configuration"""
        return self.models["mistral"]
    
    def get_executor_config(self) -> ModelConfig:
        """Get executor model configuration"""
        return self.models["qwen2.5-14b"]
    
    def get_critic_config(self, use_alternative: bool = False) -> ModelConfig:
        """Get critic model configuration"""
        base_config = self.models["mistral"]
        if use_alternative and "qwen2.5-7b" in self.models:
            return self.models["qwen2.5-7b"]
        return base_config
    
    def get_all_model_configs(self) -> List[ModelConfig]:
        """Get all model configurations"""
        return list(self.models.values())
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration"""
        issues = []
        
        # Check memory constraints
        total_model_memory = sum(config.memory_gb for config in self.models.values())
        if total_model_memory > self.system_memory_gb - self.memory.safety_buffer_gb:
            issues.append(f"Total model memory ({total_model_memory}GB) exceeds system limits")
        
        # Check individual models
        for name, config in self.models.items():
            if config.memory_gb > self.system_memory_gb - self.memory.safety_buffer_gb:
                issues.append(f"Model {name} ({config.memory_gb}GB) may exceed memory limits")
        
        # Check temperatures
        for name, config in self.models.items():
            if not 0.0 <= config.temperature <= 2.0:
                issues.append(f"Invalid temperature for {name}: {config.temperature}")
        
        # Check Ollama settings
        if self.ollama.timeout < 30:
            issues.append("Ollama timeout may be too short for large models")
        
        return issues
    
    def get_optimization_settings(self) -> Dict[str, Any]:
        """Get performance optimization settings"""
        return {
            "apple_silicon_optimized": self.apple_silicon,
            "metal_acceleration": self.metal_acceleration,
            "thermal_management": {
                "enabled": self.performance.thermal_adjustment_enabled,
                "threshold": self.memory.thermal_threshold
            },
            "memory_management": {
                "safety_buffer_gb": self.memory.safety_buffer_gb,
                "auto_cleanup": self.performance.auto_cleanup_enabled,
                "pressure_threshold": self.performance.memory_pressure_threshold
            },
            "retry_logic": {
                "max_retries": self.memory.max_retries,
                "retry_delay": self.memory.retry_delay,
                "cleanup_on_failure": self.memory.cleanup_on_failure
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "models": {name: {
                "name": config.name,
                "ollama_name": config.ollama_name,
                "type": config.type.value,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "memory_gb": config.memory_gb,
                "alternative": config.alternative
            } for name, config in self.models.items()},
            "memory": {
                "safety_buffer_gb": self.memory.safety_buffer_gb,
                "thermal_threshold": self.memory.thermal_threshold,
                "max_retries": self.memory.max_retries,
                "retry_delay": self.memory.retry_delay,
                "cleanup_on_failure": self.memory.cleanup_on_failure
            },
            "ollama": {
                "base_url": self.ollama.base_url,
                "timeout": self.ollama.timeout,
                "health_check_interval": self.ollama.health_check_interval
            },
            "performance": {
                "thermal_adjustment_enabled": self.performance.thermal_adjustment_enabled,
                "memory_pressure_threshold": self.performance.memory_pressure_threshold,
                "auto_cleanup_enabled": self.performance.auto_cleanup_enabled,
                "performance_monitoring": self.performance.performance_monitoring
            },
            "system": {
                "system_memory_gb": self.system_memory_gb,
                "apple_silicon": self.apple_silicon,
                "metal_acceleration": self.metal_acceleration
            }
        }
    
    def update_setting(self, section: str, key: str, value: Any) -> None:
        """Update a specific configuration setting"""
        if section == "memory":
            setattr(self.memory, key, value)
        elif section == "ollama":
            setattr(self.ollama, key, value)
        elif section == "performance":
            setattr(self.performance, key, value)
        elif section == "system":
            setattr(self, key, value)
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.__init__()


# Global configuration instance
config = AIStackConfig()
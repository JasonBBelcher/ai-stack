"""
Model Capabilities System - Granular model capability definitions and validation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ModelSource(Enum):
    """Source of the model"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class QuantizationLevel(Enum):
    """Model quantization levels"""
    FP16 = "FP16"
    FP32 = "FP32"
    Q4_0 = "Q4_0"
    Q4_K_M = "Q4_K_M"
    Q5_K_M = "Q5_K_M"
    Q8_0 = "Q8_0"
    N_A = "N/A"


@dataclass
class ModelCapabilities:
    """Comprehensive model capability definition"""
    
    # Technical specifications
    context_length: int
    quantization_level: str
    model_size: int  # parameter count
    memory_gb_estimate: float
    
    # Performance characteristics (0-1 scales)
    reasoning_strength: float = 0.5
    coding_strength: float = 0.5
    creativity: float = 0.5
    multilingual_score: float = 0.5
    
    # Feature support
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_tools: bool = False
    
    # Resource requirements
    min_memory_gb: float = 4.0
    recommended_memory_gb: float = 6.0
    thermal_sensitivity: float = 0.5
    
    # Availability
    model_source: str = ModelSource.OLLAMA.value
    requires_api_key: bool = False
    
    # Metadata
    model_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize capabilities"""
        # Normalize scales to 0-1 range
        self.reasoning_strength = max(0.0, min(1.0, self.reasoning_strength))
        self.coding_strength = max(0.0, min(1.0, self.coding_strength))
        self.creativity = max(0.0, min(1.0, self.creativity))
        self.multilingual_score = max(0.0, min(1.0, self.multilingual_score))
        
        # Validate context length
        if self.context_length <= 0:
            raise ValueError("Context length must be positive")
        
        # Validate memory estimates
        if self.memory_gb_estimate <= 0:
            raise ValueError("Memory estimate must be positive")
        
        # Validate quantization
        if self.quantization_level not in [q.value for q in QuantizationLevel]:
            self.quantization_level = QuantizationLevel.N_A.value


@dataclass
class RoleRequirements:
    """Requirements for a specific role"""
    
    # Performance requirements (0-1 scales)
    reasoning_strength_min: float = 0.5
    coding_strength_min: float = 0.5
    creativity_min: float = 0.0
    multilingual_score_min: float = 0.0
    
    # Technical requirements
    context_length_min: int = 4000
    memory_gb_max: float = 16.0
    
    # Feature requirements
    supports_function_calling: bool = False
    supports_tools: bool = False
    supports_vision: bool = False
    
    # Constraints
    max_thermal_sensitivity: float = 0.8
    requires_local: bool = False  # If True, cloud models not allowed
    
    def validate_capabilities(self, capabilities: ModelCapabilities) -> 'ValidationReport':
        """Validate if a model meets role requirements"""
        issues = []
        warnings = []
        
        # Performance validation
        if capabilities.reasoning_strength < self.reasoning_strength_min:
            issues.append(f"Reasoning strength too low: {capabilities.reasoning_strength} < {self.reasoning_strength_min}")
        
        if capabilities.coding_strength < self.coding_strength_min:
            issues.append(f"Coding strength too low: {capabilities.coding_strength} < {self.coding_strength_min}")
        
        if capabilities.creativity < self.creativity_min:
            issues.append(f"Creativity too low: {capabilities.creativity} < {self.creativity_min}")
        
        if capabilities.multilingual_score < self.multilingual_score_min:
            issues.append(f"Multilingual score too low: {capabilities.multilingual_score} < {self.multilingual_score_min}")
        
        # Technical validation
        if capabilities.context_length < self.context_length_min:
            issues.append(f"Context length too short: {capabilities.context_length} < {self.context_length_min}")
        
        if capabilities.recommended_memory_gb > self.memory_gb_max:
            issues.append(f"Memory requirement too high: {capabilities.recommended_memory_gb}GB > {self.memory_gb_max}GB")
        
        # Feature validation
        if self.supports_function_calling and not capabilities.supports_function_calling:
            issues.append("Function calling support required but not available")
        
        if self.supports_tools and not capabilities.supports_tools:
            issues.append("Tools support required but not available")
        
        if self.supports_vision and not capabilities.supports_vision:
            issues.append("Vision support required but not available")
        
        # Constraints validation
        if capabilities.thermal_sensitivity > self.max_thermal_sensitivity:
            warnings.append(f"High thermal sensitivity: {capabilities.thermal_sensitivity} > {self.max_thermal_sensitivity}")
        
        if self.requires_local and capabilities.model_source != ModelSource.OLLAMA.value:
            issues.append("Local model required but this is a cloud model")
        
        # Performance warnings
        if capabilities.model_size < 1000000000:  # Less than 1B parameters
            warnings.append("Small model may have limited capabilities")
        
        return ValidationReport(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            score=self._calculate_score(capabilities)
        )
    
    def _calculate_score(self, capabilities: ModelCapabilities) -> float:
        """Calculate how well the model matches requirements (0-1)"""
        performance_score = (
            (capabilities.reasoning_strength + self.reasoning_strength_min) / 2 * 0.3 +
            (capabilities.coding_strength + self.coding_strength_min) / 2 * 0.3 +
            (capabilities.creativity + self.creativity_min) / 2 * 0.2 +
            (capabilities.multilingual_score + self.multilingual_score_min) / 2 * 0.2
        )
        
        tech_score = min(1.0, capabilities.context_length / self.context_length_min) * 0.5
        memory_score = 1.0 - max(0.0, (capabilities.recommended_memory_gb - self.memory_gb_max) / self.memory_gb_max) * 0.5
        
        return (performance_score + tech_score + memory_score) / 2


@dataclass
class ValidationReport:
    """Report from capability validation"""
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: float = 0.0
    
    def __str__(self) -> str:
        if self.is_valid:
            if self.warnings:
                return f"✓ Valid (score: {self.score:.2f}) with warnings: {'; '.join(self.warnings)}"
            return f"✓ Valid (score: {self.score:.2f})"
        else:
            return f"✗ Invalid (score: {self.score:.2f}): {'; '.join(self.issues)}"


class CapabilityMatcher:
    """Utility class for matching capabilities to requirements"""
    
    @staticmethod
    def find_best_match(
        models: Dict[str, ModelCapabilities],
        requirements: RoleRequirements,
        system_constraints: Optional[Dict[str, Any]] = None
    ) -> 'ModelSelection':
        """Find the best model matching requirements"""
        
        valid_models = []
        
        for model_name, capabilities in models.items():
            validation = requirements.validate_capabilities(capabilities)
            
            if validation.is_valid:
                # Apply system constraints
                if system_constraints:
                    if capabilities.recommended_memory_gb > system_constraints.get('max_memory_gb', float('inf')):
                        continue
                    
                    if capabilities.thermal_sensitivity > system_constraints.get('max_thermal_sensitivity', 1.0):
                        continue
                    
                    if system_constraints.get('local_only', False) and capabilities.model_source != ModelSource.OLLAMA.value:
                        continue
                
                valid_models.append(ModelSelection(
                    model_name=model_name,
                    capabilities=capabilities,
                    validation=validation,
                    source=capabilities.model_source
                ))
        
        if not valid_models:
            return ModelSelection(
                model_name=None,
                capabilities=None,
                validation=ValidationReport(is_valid=False, issues=["No valid models found"]),
                source=None
            )
        
        # Sort by validation score, then by model size (prefer larger models for ties)
        valid_models.sort(key=lambda x: (x.validation.score, x.capabilities.model_size), reverse=True)
        
        return valid_models[0]
    
    @staticmethod
    def get_models_by_capability(
        models: Dict[str, ModelCapabilities],
        capability: str,
        min_value: float = 0.7
    ) -> List[str]:
        """Get models that meet a minimum capability threshold"""
        
        matching_models = []
        for model_name, capabilities in models.items():
            capability_value = getattr(capabilities, capability, 0.0)
            if capability_value >= min_value:
                matching_models.append(model_name)
        
        return matching_models


@dataclass
class ModelSelection:
    """Result of model selection process"""
    model_name: Optional[str]
    capabilities: Optional[ModelCapabilities]
    validation: ValidationReport
    source: Optional[str]
    
    @property
    def is_valid(self) -> bool:
        return self.model_name is not None and self.validation.is_valid


# Predefined role requirements
DEFAULT_ROLE_REQUIREMENTS = {
    "planner": RoleRequirements(
        reasoning_strength_min=0.7,
        coding_strength_min=0.3,
        creativity_min=0.2,
        multilingual_score_min=0.5,
        context_length_min=8000,
        memory_gb_max=8.0,
        supports_function_calling=False,
        supports_tools=False,
        supports_vision=False,
        max_thermal_sensitivity=0.7,
        requires_local=True
    ),
    
    "critic": RoleRequirements(
        reasoning_strength_min=0.8,
        coding_strength_min=0.4,
        creativity_min=0.1,
        multilingual_score_min=0.6,
        context_length_min=16000,
        memory_gb_max=6.0,
        supports_function_calling=True,
        supports_tools=False,
        supports_vision=False,
        max_thermal_sensitivity=0.6,
        requires_local=True
    ),
    
    "executor": RoleRequirements(
        reasoning_strength_min=0.6,
        coding_strength_min=0.8,
        creativity_min=0.3,
        multilingual_score_min=0.4,
        context_length_min=16000,
        memory_gb_max=12.0,
        supports_function_calling=True,
        supports_tools=True,
        supports_vision=False,
        max_thermal_sensitivity=0.8,
        requires_local=True
    )
}


def create_capabilities_from_dict(data: Dict[str, Any]) -> ModelCapabilities:
    """Create ModelCapabilities from dictionary data"""
    return ModelCapabilities(
        context_length=data.get('context_length', 4000),
        quantization_level=data.get('quantization_level', 'N/A'),
        model_size=data.get('model_size', 0),
        memory_gb_estimate=data.get('memory_gb_estimate', 4.0),
        reasoning_strength=data.get('reasoning_strength', 0.5),
        coding_strength=data.get('coding_strength', 0.5),
        creativity=data.get('creativity', 0.5),
        multilingual_score=data.get('multilingual_score', 0.5),
        supports_function_calling=data.get('supports_function_calling', False),
        supports_vision=data.get('supports_vision', False),
        supports_tools=data.get('supports_tools', False),
        min_memory_gb=data.get('min_memory_gb', 4.0),
        recommended_memory_gb=data.get('recommended_memory_gb', 6.0),
        thermal_sensitivity=data.get('thermal_sensitivity', 0.5),
        model_source=data.get('model_source', ModelSource.OLLAMA.value),
        requires_api_key=data.get('requires_api_key', False),
        model_name=data.get('model_name'),
        display_name=data.get('display_name'),
        description=data.get('description'),
        tags=data.get('tags', [])
    )


def create_role_requirements_from_dict(data: Dict[str, Any]) -> RoleRequirements:
    """Create RoleRequirements from dictionary data"""
    return RoleRequirements(
        reasoning_strength_min=data.get('reasoning_strength', 0.5),
        coding_strength_min=data.get('coding_strength', 0.5),
        creativity_min=data.get('creativity', 0.0),
        multilingual_score_min=data.get('multilingual_score', 0.0),
        context_length_min=data.get('context_length_min', 4000),
        memory_gb_max=data.get('memory_gb_max', 16.0),
        supports_function_calling=data.get('supports_function_calling', False),
        supports_tools=data.get('supports_tools', False),
        supports_vision=data.get('supports_vision', False),
        max_thermal_sensitivity=data.get('max_thermal_sensitivity', 0.8),
        requires_local=data.get('requires_local', False)
    )
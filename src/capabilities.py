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
    """Comprehensive model capability definition with sensible defaults"""
    
    # Technical specifications
    context_length: int = 32768  # Default context length
    quantization_level: str = "N/A"
    model_size: int = 7000000  # Default estimate for 7B model
    memory_gb_estimate: float = 4.0  # Conservative estimate
    
    # Performance characteristics (0-1 scales)
    reasoning_strength: float = 0.5  # Balanced reasoning
    coding_strength: float = 0.5  # Practical coding ability
    creativity: float = 0.5  # Moderate creativity
    multilingual_score: float = 0.5  # Good multilingual support
    
    # Feature support
    supports_function_calling: bool = False  # Default
    supports_vision: bool = False     # Vision models
    supports_tools: bool = False      # Tool use (until implemented)
    
    # Resource requirements
    min_memory_gb: float = 4.0
    recommended_memory_gb: float = 6.0
    
    # Thermal and performance
    thermal_sensitivity: float = 0.5  # Medium thermal sensitivity
    model_size: int = 7000000  # 7B parameter estimate
    
    # Availability
    model_source: str = ModelSource.LOCAL  # Default
    requires_api_key: bool = False  # Local models don't need API keys
    
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
        
        # Normalize context length to reasonable range
        if self.context_length <= 0:
            self.context_length = max(1000, self.context_length)
        
        # Validate memory estimates
        if self.memory_gb_estimate <= 0:
            self.memory_gb_estimate = 4.0
        elif self.memory_gb_estimate > 20.0:
            self.memory_gb_estimate = 20.0  # Cap very large models
        elif self.model_size > 30000000000:  # >30B parameters
            self.memory_gb_estimate = min(self.model_size / 1000000000 * 20.0, 20.0)
        elif self.model_size > 7000000000:  # 7B parameters
            self.memory_gb_estimate = min(self.model_size / 1000000 * 8.0, 8.0)
        
        # Validate quantization level
        if self.quantization_level not in [q.value for q in QuantizationLevel]:
            self.quantization_level = QuantizationLevel.N_A
        
        # Validate thermal sensitivity
        self.thermal_sensitivity = max(0.1, min(1.0, self.thermal_sensitivity))
        
        # Validate performance characteristics
        all_positive = all(x >= 0 for x in [self.reasoning_strength, self.coding_strength, self.creativity, self.multilingual_score])
        if not all_positive:
            # Set minimal positive values if all are zero
            if self.reasoning_strength <= 0:
                self.reasoning_strength = 0.1
            if self.coding_strength <= 0:
                self.coding_strength = 0.1
            if self.creativity <= 0:
                self.creativity = 0.1
            self.multilingual_score = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "context_length": self.context_length,
            "quantization_level": self.quantization_level,
            "model_size": self.model_size,
            "reasoning_strength": self.reasoning_strength,
            "coding_strength": self.coding_strength,
            "creativity": self.creativity,
            "multilingual_score": self.multilingual_score,
            "supports_function_calling": self.supports_function_calling,
            "supports_vision": self.supports_vision,
            "supports_tools": self.supports_tools,
            "min_memory_gb": self.min_memory_gb,
            "recommended_memory_gb": self.recommended_memory_gb,
            "thermal_sensitivity": self.thermal_sensitivity,
            "model_source": self.model_source,
            "requires_api_key": self.requires_api_key,
            "model_name": self.model_name,
            "display_name": self.display_name,
            "description": self.description,
            "tags": self.tags
        }
    
    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'ModelCapabilities':
        """Create ModelCapabilities from dictionary"""
        return cls(
            context_length=data.get('context_length', 32768),
            quantization_level=data.get('quantization_level', 'N/A'),
            model_size=data.get('model_size', 7000000),
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
            model_source=data.get('model_source', ModelSource.LOCAL.value),
            requires_api_key=data.get('requires_api_key', False),
            model_name=data.get('model_name'),
            display_name=data.get('display_name'),
            description=data.get('description'),
            tags=data.get('tags', [])
        )


@dataclass
class RoleRequirements:
    """Requirements for a specific role/task type"""
    
    # Core requirements (0-1 scales)
    min_reasoning_strength: float = 0.5
    min_coding_strength: float = 0.0
    min_creativity: float = 0.0
    min_multilingual_score: float = 0.0
    
    # Feature requirements
    requires_function_calling: bool = False
    requires_vision: bool = False
    requires_tools: bool = False
    
    # Performance requirements
    max_thermal_sensitivity: float = 0.8
    min_context_length: int = 4096
    
    # Cost preferences (lower is more preferred)
    cost_preference: float = 0.5  # 0 = prefer cheapest, 1 = prefer best
    
    def __post_init__(self):
        """Validate role requirements"""
        # Validate scales
        self.min_reasoning_strength = max(0.0, min(1.0, self.min_reasoning_strength))
        self.min_coding_strength = max(0.0, min(1.0, self.min_coding_strength))
        self.min_creativity = max(0.0, min(1.0, self.min_creativity))
        self.min_multilingual_score = max(0.0, min(1.0, self.min_multilingual_score))
        
        self.max_thermal_sensitivity = max(0.1, min(1.0, self.max_thermal_sensitivity))
        self.cost_preference = max(0.0, min(1.0, self.cost_preference))
    
    def validate_capabilities(self, capabilities: ModelCapabilities) -> ValidationReport:
        """Validate if capabilities meet role requirements"""
        report = ValidationReport(
            model_name=capabilities.model_name or "Unknown",
            is_valid=True
        )
        
        # Check reasoning strength
        if capabilities.reasoning_strength < self.min_reasoning_strength:
            report.add_issue(f"Insufficient reasoning strength: {capabilities.reasoning_strength} < {self.min_reasoning_strength}")
        
        # Check coding strength
        if capabilities.coding_strength < self.min_coding_strength:
            report.add_issue(f"Insufficient coding strength: {capabilities.coding_strength} < {self.min_coding_strength}")
        
        # Check creativity
        if capabilities.creativity < self.min_creativity:
            report.add_issue(f"Insufficient creativity: {capabilities.creativity} < {self.min_creativity}")
        
        # Check multilingual support
        if capabilities.multilingual_score < self.min_multilingual_score:
            report.add_issue(f"Insufficient multilingual score: {capabilities.multilingual_score} < {self.min_multilingual_score}")
        
        # Check feature requirements
        if self.requires_function_calling and not capabilities.supports_function_calling:
            report.add_issue("Function calling required but not supported")
        
        if self.requires_vision and not capabilities.supports_vision:
            report.add_issue("Vision required but not supported")
        
        if self.requires_tools and not capabilities.supports_tools:
            report.add_issue("Tools required but not supported")
        
        # Check thermal sensitivity
        if capabilities.thermal_sensitivity > self.max_thermal_sensitivity:
            report.add_warning(f"High thermal sensitivity: {capabilities.thermal_sensitivity} > {self.max_thermal_sensitivity}")
        
        # Check context length
        if capabilities.context_length < self.min_context_length:
            report.add_issue(f"Insufficient context length: {capabilities.context_length} < {self.min_context_length}")
        
        return report


@dataclass
class ValidationReport:
    """Model validation report"""
    model_name: str
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: str):
        """Add a validation issue"""
        self.issues.append(issue)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning"""
        self.warnings.append(warning)
    
    def add_suggestion(self, suggestion: str):
        """Add a validation suggestion"""
        self.suggestions.append(suggestion)
    
    def has_issues(self) -> bool:
        """Check if there are any issues"""
        return len(self.issues) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0
    
    def __str__(self) -> str:
        """String representation of the validation report"""
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        result = f"{status}: {self.model_name}\n"
        
        if self.issues:
            result += "Issues:\n"
            for issue in self.issues:
                result += f"  • {issue}\n"
        
        if self.warnings:
            result += "Warnings:\n"
            for warning in self.warnings:
                result += f"  • {warning}\n"
        
        if self.suggestions:
            result += "Suggestions:\n"
            for suggestion in self.suggestions:
                result += f"  • {suggestion}\n"
        
        return result


@dataclass
class ModelSelection:
    """Model selection result with scoring"""
    model_name: str
    capabilities: ModelCapabilities
    score: float
    selection_reason: str
    cost_estimate: Optional[float] = None
    performance_estimate: Optional[float] = None
    thermal_impact: Optional[str] = None
    validation: Optional[ValidationReport] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if selection is valid"""
        if self.validation:
            return self.validation.is_valid
        return self.score > 0.0 and self.capabilities is not None
    
    def __str__(self) -> str:
        """String representation of model selection"""
        return f"{self.model_name} (Score: {self.score:.2f}): {self.selection_reason}"


class CapabilityMatcher:
    """Intelligent capability matching system"""
    
    def __init__(self):
        """Initialize capability matcher"""
        pass
    
    def match_requirements(self, capabilities: ModelCapabilities, requirements: RoleRequirements) -> float:
        """Calculate match score between model capabilities and role requirements"""
        score = 0.0
        factors = 0
        
        # Core capability matching
        if requirements.min_reasoning_strength > 0:
            if capabilities.reasoning_strength >= requirements.min_reasoning_strength:
                score += 1.0
            else:
                score += capabilities.reasoning_strength / requirements.min_reasoning_strength
            factors += 1
        
        if requirements.min_coding_strength > 0:
            if capabilities.coding_strength >= requirements.min_coding_strength:
                score += 1.0
            else:
                score += capabilities.coding_strength / requirements.min_coding_strength
            factors += 1
        
        if requirements.min_creativity > 0:
            if capabilities.creativity >= requirements.min_creativity:
                score += 1.0
            else:
                score += capabilities.creativity / requirements.min_creativity
            factors += 1
        
        if requirements.min_multilingual_score > 0:
            if capabilities.multilingual_score >= requirements.min_multilingual_score:
                score += 1.0
            else:
                score += capabilities.multilingual_score / requirements.min_multilingual_score
            factors += 1
        
        # Feature requirement matching
        if requirements.requires_function_calling and not capabilities.supports_function_calling:
            score -= 0.5
        if requirements.requires_vision and not capabilities.supports_vision:
            score -= 0.5
        if requirements.requires_tools and not capabilities.supports_tools:
            score -= 0.5
        
        # Thermal sensitivity matching
        if capabilities.thermal_sensitivity > requirements.max_thermal_sensitivity:
            score -= 0.3
        
        # Context length matching
        if capabilities.context_length < requirements.min_context_length:
            score -= 0.2
        
        # Normalize score
        if factors > 0:
            score = max(0.0, score / factors)
        
        return score
    
    def rank_models(self, models: List[ModelCapabilities], requirements: RoleRequirements) -> List[ModelSelection]:
        """Rank models by their match to requirements"""
        selections = []
        
        for capabilities in models:
            score = self.match_requirements(capabilities, requirements)
            
            # Generate selection reason
            reasons = []
            if score >= 0.8:
                reasons.append("Excellent match")
            elif score >= 0.6:
                reasons.append("Good match")
            elif score >= 0.4:
                reasons.append("Adequate match")
            else:
                reasons.append("Poor match")
            
            if capabilities.reasoning_strength >= requirements.min_reasoning_strength:
                reasons.append("meets reasoning requirements")
            if capabilities.coding_strength >= requirements.min_coding_strength:
                reasons.append("meets coding requirements")
            
            selection = ModelSelection(
                model_name=capabilities.model_name or "Unknown",
                capabilities=capabilities,
                score=score,
                selection_reason=", ".join(reasons)
            )
            
            selections.append(selection)
        
        # Sort by score (descending)
        selections.sort(key=lambda x: x.score, reverse=True)
        
        return selections
    
    def find_best_match(self, models: List[ModelCapabilities], requirements: RoleRequirements, constraints: Optional[Dict[str, Any]] = None) -> ModelSelection:
        """Find the best matching model"""
        selections = self.rank_models(models, requirements)
        return selections[0] if selections else None


# Default role requirements for common tasks
DEFAULT_ROLE_REQUIREMENTS = {
    "coding": RoleRequirements(
        min_reasoning_strength=0.6,
        min_coding_strength=0.7,
        min_creativity=0.3,
        requires_function_calling=True,
        min_context_length=8192,
        cost_preference=0.4
    ),
    "writing": RoleRequirements(
        min_reasoning_strength=0.5,
        min_coding_strength=0.0,
        min_creativity=0.8,
        min_context_length=4096,
        cost_preference=0.6
    ),
    "analysis": RoleRequirements(
        min_reasoning_strength=0.8,
        min_coding_strength=0.3,
        min_creativity=0.4,
        min_context_length=16384,
        cost_preference=0.3
    ),
    "chat": RoleRequirements(
        min_reasoning_strength=0.4,
        min_coding_strength=0.0,
        min_creativity=0.6,
        min_context_length=4096,
        cost_preference=0.7
    ),
    "research": RoleRequirements(
        min_reasoning_strength=0.7,
        min_coding_strength=0.2,
        min_creativity=0.5,
        min_context_length=32768,
        cost_preference=0.2
    )
}


def create_role_requirements_from_dict(data: Dict[str, Any]) -> RoleRequirements:
    """Factory function to create RoleRequirements from dictionary"""
    return RoleRequirements(
        min_reasoning_strength=data.get('min_reasoning_strength', 0.5),
        min_coding_strength=data.get('min_coding_strength', 0.0),
        min_creativity=data.get('min_creativity', 0.0),
        min_multilingual_score=data.get('min_multilingual_score', 0.0),
        requires_function_calling=data.get('requires_function_calling', False),
        requires_vision=data.get('requires_vision', False),
        requires_tools=data.get('requires_tools', False),
        max_thermal_sensitivity=data.get('max_thermal_sensitivity', 0.8),
        min_context_length=data.get('min_context_length', 4096),
        cost_preference=data.get('cost_preference', 0.5)
    )


def create_capabilities_from_dict(data: Dict[str, Any]) -> ModelCapabilities:
    """Factory function to create ModelCapabilities from dictionary"""
    return ModelCapabilities.create_from_dict(data)
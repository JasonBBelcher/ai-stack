"""
Role Mapper - Intelligent role-to-model mapping based on capabilities and constraints
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from src.model_registry import ModelRegistry
from src.capabilities import (
    ModelCapabilities, 
    RoleRequirements, 
    ValidationReport, 
    ModelSelection,
    CapabilityMatcher,
    DEFAULT_ROLE_REQUIREMENTS,
    create_role_requirements_from_dict
)


class ModelType:
    """Model role types"""
    PLANNER = "planner"
    CRITIC = "critic"
    EXECUTOR = "executor"


@dataclass
class SystemConstraints:
    """Current system constraints and resources"""
    max_memory_gb: float = 14.0
    max_thermal_sensitivity: float = 0.8
    thermal_state: str = "normal"
    available_memory_gb: float = 8.0
    local_only: bool = False
    enable_cloud_fallbacks: bool = False
    
    @classmethod
    def from_memory_manager(cls, memory_manager, registry: ModelRegistry) -> 'SystemConstraints':
        """Create SystemConstraints from memory manager and registry"""
        return cls(
            max_memory_gb=registry.get_max_memory_usage(),
            max_thermal_sensitivity=registry.get_thermal_threshold(),
            available_memory_gb=memory_manager.get_system_memory()["available_gb"],
            local_only=not registry.is_cloud_enabled(),
            enable_cloud_fallbacks=registry.is_cloud_enabled()
        )


@dataclass
class SelectionCriteria:
    """Criteria for model selection"""
    prefer_local: bool = True
    prefer_smaller: bool = False  # For resource-constrained environments
    prefer_faster: bool = False  # Based on thermal sensitivity
    max_response_time: Optional[float] = None
    
    def score_model(self, capabilities: ModelCapabilities, validation: ValidationReport) -> float:
        """Calculate a preference score for a model"""
        score = validation.score
        
        # Prefer local models
        if self.prefer_local and capabilities.model_source == "ollama":
            score += 0.1
        
        # Prefer smaller models for resource constraints
        if self.prefer_smaller and capabilities.model_size < 7000000000:  # < 7B
            score += 0.1
        
        # Prefer thermally efficient models
        if self.prefer_faster and capabilities.thermal_sensitivity < 0.5:
            score += 0.05
        
        return min(1.0, score)


class RoleMapper:
    """Intelligent role-to-model mapping with constraints and preferences"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.capability_matcher = CapabilityMatcher()
        self.default_criteria = SelectionCriteria()
    
    def select_model_for_role(
        self, 
        role: ModelType, 
        system_constraints: Optional[SystemConstraints] = None,
        selection_criteria: Optional[SelectionCriteria] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> ModelSelection:
        """Select the best model for a specific role"""
        
        role_str = role if isinstance(role, str) else role.value if hasattr(role, 'value') else str(role)
        system_constraints = system_constraints or SystemConstraints()
        selection_criteria = selection_criteria or self.default_criteria
        
        # Get role requirements
        role_requirements = self._get_role_requirements(role_str, user_preferences)
        
        # Get candidate models
        candidate_models = self._get_candidate_models(role_str, system_constraints)
        
        if not candidate_models:
            return ModelSelection(
                model_name=None,
                capabilities=None,
                validation=ValidationReport(
                    is_valid=False, 
                    issues=[f"No suitable models found for role: {role_str}"]
                ),
                source=None
            )
        
        # Apply capability matching and constraints
        constrained_models = self._apply_constraints(
            candidate_models, 
            role_requirements, 
            system_constraints
        )
        
        if not constrained_models:
            return ModelSelection(
                model_name=None,
                capabilities=None,
                validation=ValidationReport(
                    is_valid=False, 
                    issues=["No models meet system constraints"]
                ),
                source=None
            )
        
        # Find best match using capability matcher
        best_selection = self.capability_matcher.find_best_match(
            list(constrained_models.values()),
            role_requirements,
            self._constraints_to_dict(system_constraints)
        )
        
        # Apply selection criteria preferences
        if best_selection.is_valid:
            best_selection = self._apply_selection_preferences(
                best_selection,
                constrained_models,
                role_requirements,
                selection_criteria
            )
        
        return best_selection
    
    def _get_role_requirements(
        self, 
        role: str, 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> RoleRequirements:
        """Get role requirements, with user preference overrides"""
        
        # Get base requirements from config
        config_requirements = self.registry.get_role_requirements(role)
        
        if config_requirements:
            requirements = create_role_requirements_from_dict(config_requirements)
        else:
            requirements = DEFAULT_ROLE_REQUIREMENTS.get(role)
            if not requirements:
                requirements = RoleRequirements()  # Default minimal requirements
        
        # Apply user preferences if provided
        if user_preferences:
            if 'reasoning_strength_min' in user_preferences:
                requirements.reasoning_strength_min = user_preferences['reasoning_strength_min']
            if 'coding_strength_min' in user_preferences:
                requirements.coding_strength_min = user_preferences['coding_strength_min']
            if 'context_length_min' in user_preferences:
                requirements.context_length_min = user_preferences['context_length_min']
            if 'memory_gb_max' in user_preferences:
                requirements.memory_gb_max = user_preferences['memory_gb_max']
        
        return requirements
    
    def _get_candidate_models(
        self, 
        role: str, 
        system_constraints: SystemConstraints
    ) -> Dict[str, ModelCapabilities]:
        """Get candidate models for a role"""
        
        candidates = {}
        
        # Get preferred models from configuration
        preferred_models = self.registry.get_models_for_role(role)
        
        # Add only available and validated models
        for model_name in preferred_models:
            model_info = self.registry.models.get(model_name)
            if model_info and model_info.validated:
                if model_info.capabilities:
                    candidates[model_name] = model_info.capabilities
        
        # Add cloud fallbacks if enabled
        if system_constraints.enable_cloud_fallbacks:
            cloud_fallback = self.registry.get_cloud_fallback_for_role(role)
            if cloud_fallback:
                fallback_info = self.registry.models.get(cloud_fallback)
                if fallback_info and fallback_info.validated and fallback_info.capabilities:
                    candidates[cloud_fallback] = fallback_info.capabilities
        
        # If no specific candidates, add all validated models that could work
        if not candidates:
            all_models = self.registry.get_available_models(validated_only=True)
            for model_name, model_info in all_models.items():
                if model_info.capabilities:
                    candidates[model_name] = model_info.capabilities
        
        return candidates
    
    def _apply_constraints(
        self, 
        models: Dict[str, ModelCapabilities], 
        requirements: RoleRequirements,
        constraints: SystemConstraints
    ) -> Dict[str, ModelCapabilities]:
        """Apply system constraints to filter models"""
        
        constrained_models = {}
        
        for model_name, capabilities in models.items():
            # Check memory constraints
            if capabilities.recommended_memory_gb > constraints.max_memory_gb:
                continue
            
            # Check thermal constraints
            if capabilities.thermal_sensitivity > constraints.max_thermal_sensitivity:
                # Allow if thermal state is normal, skip if already hot
                if constraints.thermal_state not in ["normal", "moderate"]:
                    continue
            
            # Check local-only constraint
            if constraints.local_only and capabilities.model_source != "ollama":
                continue
            
            # Validate against role requirements
            validation = requirements.validate_capabilities(capabilities)
            if validation.is_valid:
                constrained_models[model_name] = capabilities
        
        return constrained_models
    
    def _constraints_to_dict(self, constraints: SystemConstraints) -> Dict[str, Any]:
        """Convert SystemConstraints to dictionary for capability matcher"""
        return {
            'max_memory_gb': constraints.max_memory_gb,
            'max_thermal_sensitivity': constraints.max_thermal_sensitivity,
            'local_only': constraints.local_only
        }
    
    def _apply_selection_preferences(
        self, 
        best_selection: ModelSelection,
        all_models: Dict[str, ModelCapabilities],
        requirements: RoleRequirements,
        criteria: SelectionCriteria
    ) -> ModelSelection:
        """Apply user selection preferences to potentially override best match"""
        
        # If no strong preferences, return the best match
        if criteria == self.default_criteria:
            return best_selection
        
        # Score all models with selection criteria
        scored_models = []
        for model_name, capabilities in all_models.items():
            validation = requirements.validate_capabilities(capabilities)
            if validation.is_valid:
                score = criteria.score_model(capabilities, validation)
                scored_models.append((score, model_name, capabilities, validation))
        
        if not scored_models:
            return best_selection
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[0], reverse=True)
        
        # Return highest scored model
        _, best_name, best_caps, best_valid = scored_models[0]
        return ModelSelection(
            model_name=best_name,
            capabilities=best_caps,
            validation=best_valid,
            source=best_caps.model_source
        )
    
    def get_model_recommendations(
        self, 
        role: ModelType,
        system_constraints: Optional[SystemConstraints] = None,
        max_recommendations: int = 5
    ) -> List[ModelSelection]:
        """Get multiple model recommendations for a role"""
        
        role_str = role.value
        system_constraints = system_constraints or SystemConstraints()
        
        # Get role requirements
        role_requirements = self._get_role_requirements(role_str)
        
        # Get all validated models
        all_models = self.registry.get_available_models(validated_only=True)
        candidate_models = {
            name: info.capabilities 
            for name, info in all_models.items() 
            if info.capabilities
        }
        
        # Apply constraints
        constrained_models = self._apply_constraints(
            candidate_models,
            role_requirements,
            system_constraints
        )
        
        # Score and rank all valid models
        recommendations = []
        for model_name, capabilities in constrained_models.items():
            validation = role_requirements.validate_capabilities(capabilities)
            if validation.is_valid:
                selection = ModelSelection(
                    model_name=model_name,
                    capabilities=capabilities,
                    validation=validation,
                    source=capabilities.model_source
                )
                recommendations.append(selection)
        
        # Sort by validation score
        recommendations.sort(key=lambda x: x.validation.score, reverse=True)
        
        return recommendations[:max_recommendations]
    
    def validate_model_for_role(
        self, 
        model_name: str, 
        role: ModelType,
        system_constraints: Optional[SystemConstraints] = None
    ) -> ValidationReport:
        """Validate if a specific model is suitable for a role"""
        
        role_str = role.value
        system_constraints = system_constraints or SystemConstraints()
        
        # Get model capabilities
        capabilities = self.registry.get_model_capabilities(model_name)
        if not capabilities:
            return ValidationReport(
                is_valid=False,
                issues=[f"Model {model_name} not found or no capabilities available"]
            )
        
        # Get role requirements
        role_requirements = self._get_role_requirements(role_str)
        
        # Apply system constraints first
        if capabilities.recommended_memory_gb > system_constraints.max_memory_gb:
            return ValidationReport(
                is_valid=False,
                issues=[f"Model requires {capabilities.recommended_memory_gb}GB, max available is {system_constraints.max_memory_gb}GB"]
            )
        
        if capabilities.thermal_sensitivity > system_constraints.max_thermal_sensitivity:
            return ValidationReport(
                is_valid=False,
                issues=[f"Model thermal sensitivity {capabilities.thermal_sensitivity} exceeds threshold {system_constraints.max_thermal_sensitivity}"]
            )
        
        # Validate against role requirements
        return role_requirements.validate_capabilities(capabilities)
    
    def suggest_model_upgrades(
        self, 
        current_model: str,
        role: ModelType
    ) -> List[ModelSelection]:
        """Suggest better models for the same role"""
        
        role_str = role.value
        role_requirements = self._get_role_requirements(role_str)
        
        # Get current model capabilities
        current_caps = self.registry.get_model_capabilities(current_model)
        if not current_caps:
            return []
        
        # Get all validated models better than current
        all_models = self.registry.get_available_models(validated_only=True)
        better_models = []
        
        for model_name, model_info in all_models.items():
            if not model_info.capabilities or model_name == current_model:
                continue
            
            # Check if significantly better
            if (model_info.capabilities.model_size > current_caps.model_size * 1.2 or
                model_info.capabilities.reasoning_strength > current_caps.reasoning_strength + 0.1):
                
                validation = role_requirements.validate_capabilities(model_info.capabilities)
                if validation.is_valid:
                    better_models.append(ModelSelection(
                        model_name=model_name,
                        capabilities=model_info.capabilities,
                        validation=validation,
                        source=model_info.capabilities.model_source
                    ))
        
        # Sort by improvement score
        better_models.sort(key=lambda x: x.validation.score, reverse=True)
        
        return better_models[:3]  # Top 3 suggestions
    
    def create_fallback_chain(
        self, 
        role: ModelType,
        system_constraints: Optional[SystemConstraints] = None
    ) -> List[str]:
        """Create a fallback chain of models for a role"""
        
        recommendations = self.get_model_recommendations(role, system_constraints)
        return [selection.model_name for selection in recommendations if selection.model_name]
    
    def get_selection_explanation(
        self, 
        selection: ModelSelection,
        role: ModelType
    ) -> str:
        """Generate explanation for why a model was selected"""
        
        if not selection.is_valid:
            return f"No valid model selected: {'; '.join(selection.validation.issues)}"
        
        explanation = f"Selected {selection.model_name} for {role.value} role.\n"
        explanation += f"Validation score: {selection.validation.score:.2f}\n"
        
        if selection.capabilities:
            explanation += f"Model characteristics:\n"
            explanation += f"  - Context length: {selection.capabilities.context_length:,}\n"
            explanation += f"  - Model size: {selection.capabilities.model_size/1e9:.1f}B parameters\n"
            explanation += f"  - Memory requirement: {selection.capabilities.recommended_memory_gb:.1f}GB\n"
            explanation += f"  - Reasoning strength: {selection.capabilities.reasoning_strength:.2f}\n"
            explanation += f"  - Coding strength: {selection.capabilities.coding_strength:.2f}\n"
            explanation += f"  - Source: {selection.capabilities.model_source}\n"
        
        if selection.validation.warnings:
            explanation += f"\nWarnings: {'; '.join(selection.validation.warnings)}"
        
        return explanation
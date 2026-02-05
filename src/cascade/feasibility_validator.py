"""
Feasibility Validator - Validates task feasibility within constraints.

This component checks if tasks can be completed within user constraints
and suggests alternative approaches when needed.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .constraint_extractor import Constraint, ConstraintType

logger = logging.getLogger(__name__)


class FeasibilityStatus(Enum):
    """Feasibility status of a task"""
    FEASIBLE = "feasible"
    MARGINALLY_FEASIBLE = "marginally_feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"


@dataclass
class FeasibilityResult:
    """Result of a feasibility check"""
    status: FeasibilityStatus
    confidence: float
    reasons: List[str]
    blockers: List[str]
    alternatives: List[str]
    suggestions: List[str]


class FeasibilityValidator:
    """Validates task feasibility within constraints."""
    
    def __init__(self):
        """Initialize the feasibility validator."""
        # Task complexity estimates (in hours)
        self.complexity_estimates = {
            'simple': {
                'minimal': 2,
                'standard': 4,
                'comprehensive': 8
            },
            'moderate': {
                'minimal': 8,
                'standard': 16,
                'comprehensive': 32
            },
            'complex': {
                'minimal': 16,
                'standard': 40,
                'comprehensive': 80
            }
        }
        
        # Quality multipliers
        self.quality_multipliers = {
            'mvp': 0.5,
            'production': 1.0,
            'polished': 1.5
        }
        
        # Maintainability multipliers
        self.maintainability_multipliers = {
            'quick_hack': 0.3,
            'maintainable': 1.0,
            'enterprise': 1.5
        }
    
    def validate(self, task_description: str, constraints: List[Constraint],
                context: Optional[Dict[str, Any]] = None) -> FeasibilityResult:
        """
        Validate if a task is feasible within constraints.
        
        Args:
            task_description: Description of the task
            constraints: List of user constraints
            context: Optional context (e.g., project info, available resources)
            
        Returns:
            FeasibilityResult with validation details
        """
        result = FeasibilityResult(
            status=FeasibilityStatus.UNKNOWN,
            confidence=0.0,
            reasons=[],
            blockers=[],
            alternatives=[],
            suggestions=[]
        )
        
        # Extract relevant constraints
        time_constraint = self._get_constraint_by_type(constraints, ConstraintType.TIME)
        complexity_constraint = self._get_constraint_by_type(constraints, ConstraintType.COMPLEXITY)
        scope_constraint = self._get_constraint_by_type(constraints, ConstraintType.SCOPE)
        quality_constraint = self._get_constraint_by_type(constraints, ConstraintType.QUALITY)
        maintainability_constraint = self._get_constraint_by_type(constraints, ConstraintType.MAINTAINABILITY)
        skill_constraint = self._get_constraint_by_type(constraints, ConstraintType.SKILL)
        
        # Estimate task complexity
        estimated_hours = self._estimate_task_hours(
            complexity_constraint, scope_constraint, 
            quality_constraint, maintainability_constraint
        )
        
        # Check time feasibility
        time_feasible = self._check_time_feasibility(time_constraint, estimated_hours)
        
        # Check skill feasibility
        skill_feasible = self._check_skill_feasibility(skill_constraint, complexity_constraint)
        
        # Check overall feasibility
        if time_feasible and skill_feasible:
            result.status = FeasibilityStatus.FEASIBLE
            result.confidence = 0.8
            result.reasons.append("Task appears feasible within constraints")
        elif time_feasible or skill_feasible:
            result.status = FeasibilityStatus.MARGINALLY_FEASIBLE
            result.confidence = 0.6
            result.reasons.append("Task may be feasible with adjustments")
        else:
            result.status = FeasibilityStatus.INFEASIBLE
            result.confidence = 0.7
            result.reasons.append("Task appears infeasible within current constraints")
        
        # Add blockers
        if not time_feasible:
            result.blockers.append(f"Time constraint ({time_constraint.description if time_constraint else 'none'}) "
                                  f"insufficient for estimated {estimated_hours} hours")
        
        if not skill_feasible:
            result.blockers.append(f"Skill level ({skill_constraint.value if skill_constraint else 'unknown'}) "
                                  f"may be insufficient for task complexity")
        
        # Generate alternatives
        result.alternatives = self._generate_alternatives(
            task_description, constraints, estimated_hours
        )
        
        # Generate suggestions
        result.suggestions = self._generate_suggestions(
            constraints, estimated_hours
        )
        
        logger.info(f"Feasibility check complete: {result.status.value} (confidence: {result.confidence:.2f})")
        return result
    
    def _get_constraint_by_type(self, constraints: List[Constraint], 
                                constraint_type: ConstraintType) -> Optional[Constraint]:
        """Get the first constraint of a given type."""
        for constraint in constraints:
            if constraint.type == constraint_type:
                return constraint
        return None
    
    def _estimate_task_hours(self, complexity_constraint: Optional[Constraint],
                            scope_constraint: Optional[Constraint],
                            quality_constraint: Optional[Constraint],
                            maintainability_constraint: Optional[Constraint]) -> float:
        """
        Estimate the hours required for a task based on constraints.
        
        Args:
            complexity_constraint: Complexity constraint
            scope_constraint: Scope constraint
            quality_constraint: Quality constraint
            maintainability_constraint: Maintainability constraint
            
        Returns:
            Estimated hours
        """
        # Get base estimate from complexity and scope
        complexity = complexity_constraint.value if complexity_constraint else 'moderate'
        scope = scope_constraint.value if scope_constraint else 'standard'
        
        base_hours = self.complexity_estimates.get(complexity, {}).get(scope, 16)
        
        # Apply quality multiplier
        quality = quality_constraint.value if quality_constraint else 'production'
        quality_multiplier = self.quality_multipliers.get(quality, 1.0)
        
        # Apply maintainability multiplier
        maintainability = maintainability_constraint.value if maintainability_constraint else 'maintainable'
        maintainability_multiplier = self.maintainability_multipliers.get(maintainability, 1.0)
        
        # Calculate final estimate
        estimated_hours = base_hours * quality_multiplier * maintainability_multiplier
        
        return estimated_hours
    
    def _check_time_feasibility(self, time_constraint: Optional[Constraint],
                                estimated_hours: float) -> bool:
        """
        Check if task is feasible within time constraint.
        
        Args:
            time_constraint: Time constraint
            estimated_hours: Estimated hours required
            
        Returns:
            True if feasible
        """
        if not time_constraint:
            # No time constraint, assume feasible
            return True
        
        if isinstance(time_constraint.value, str):
            # Qualitative time constraint
            if time_constraint.value == 'urgent':
                # Urgent means < 4 hours
                return estimated_hours <= 4
            elif time_constraint.value == 'thorough':
                # Thorough means plenty of time
                return True
            else:
                return True
        else:
            # Numeric time constraint (in hours)
            return estimated_hours <= time_constraint.value
    
    def _check_skill_feasibility(self, skill_constraint: Optional[Constraint],
                                 complexity_constraint: Optional[Constraint]) -> bool:
        """
        Check if task is feasible given skill level.
        
        Args:
            skill_constraint: Skill level constraint
            complexity_constraint: Complexity constraint
            
        Returns:
            True if feasible
        """
        if not skill_constraint:
            # No skill constraint, assume feasible
            return True
        
        if not complexity_constraint:
            # No complexity constraint, assume feasible
            return True
        
        skill = skill_constraint.value
        complexity = complexity_constraint.value
        
        # Define feasible combinations
        feasible_combinations = {
            'beginner': ['simple'],
            'intermediate': ['simple', 'moderate'],
            'expert': ['simple', 'moderate', 'complex']
        }
        
        return complexity in feasible_combinations.get(skill, [])
    
    def _generate_alternatives(self, task_description: str,
                               constraints: List[Constraint],
                               estimated_hours: float) -> List[str]:
        """
        Generate alternative approaches for infeasible tasks.
        
        Args:
            task_description: Task description
            constraints: User constraints
            estimated_hours: Estimated hours
            
        Returns:
            List of alternative approaches
        """
        alternatives = []
        
        # Get constraints
        time_constraint = self._get_constraint_by_type(constraints, ConstraintType.TIME)
        scope_constraint = self._get_constraint_by_type(constraints, ConstraintType.SCOPE)
        quality_constraint = self._get_constraint_by_type(constraints, ConstraintType.QUALITY)
        complexity_constraint = self._get_constraint_by_type(constraints, ConstraintType.COMPLEXITY)
        
        # Time-based alternatives
        if time_constraint and isinstance(time_constraint.value, (int, float)):
            if estimated_hours > time_constraint.value:
                # Reduce scope
                if scope_constraint and scope_constraint.value != 'minimal':
                    alternatives.append(
                        f"Reduce scope from {scope_constraint.value} to minimal "
                        f"(estimated {estimated_hours * 0.5:.1f} hours)"
                    )
                
                # Reduce quality
                if quality_constraint and quality_constraint.value != 'mvp':
                    alternatives.append(
                        f"Reduce quality from {quality_constraint.value} to MVP "
                        f"(estimated {estimated_hours * 0.5:.1f} hours)"
                    )
                
                # Reduce complexity
                if complexity_constraint and complexity_constraint.value != 'simple':
                    alternatives.append(
                        f"Simplify complexity from {complexity_constraint.value} to simple "
                        f"(estimated {estimated_hours * 0.25:.1f} hours)"
                    )
        
        # Skill-based alternatives
        skill_constraint = self._get_constraint_by_type(constraints, ConstraintType.SKILL)
        if skill_constraint and complexity_constraint:
            if skill_constraint.value == 'beginner' and complexity_constraint.value != 'simple':
                alternatives.append(
                    f"Simplify task complexity to match {skill_constraint.value} skill level"
                )
                alternatives.append(
                    f"Provide step-by-step guidance for {complexity_constraint.value} task"
                )
        
        # General alternatives
        if not alternatives:
            alternatives.append("Break task into smaller, manageable subtasks")
            alternatives.append("Consider using existing libraries or frameworks")
            alternatives.append("Seek assistance or pair programming")
        
        return alternatives
    
    def _generate_suggestions(self, constraints: List[Constraint],
                             estimated_hours: float) -> List[str]:
        """
        Generate suggestions for improving feasibility.
        
        Args:
            constraints: User constraints
            estimated_hours: Estimated hours
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Check for missing constraints
        constraint_types = [c.type for c in constraints]
        
        if ConstraintType.TIME not in constraint_types:
            suggestions.append(f"Specify a time constraint (estimated {estimated_hours:.1f} hours)")
        
        if ConstraintType.COMPLEXITY not in constraint_types:
            suggestions.append("Specify expected complexity (simple, moderate, complex)")
        
        if ConstraintType.SCOPE not in constraint_types:
            suggestions.append("Define scope (minimal, standard, comprehensive)")
        
        # Check for conflicting constraints
        time_constraint = self._get_constraint_by_type(constraints, ConstraintType.TIME)
        quality_constraint = self._get_constraint_by_type(constraints, ConstraintType.QUALITY)
        
        if time_constraint and quality_constraint:
            if isinstance(time_constraint.value, (int, float)):
                if time_constraint.value < 8 and quality_constraint.value == 'polished':
                    suggestions.append(
                        "Consider adjusting quality expectations for tight timeline"
                    )
        
        return suggestions
    
    def compare_alternatives(self, alternatives: List[str],
                            constraints: List[Constraint]) -> List[Dict[str, Any]]:
        """
        Compare alternative approaches and rank them.
        
        Args:
            alternatives: List of alternative approaches
            constraints: User constraints
            
        Returns:
            List of ranked alternatives with scores
        """
        ranked = []
        
        for i, alternative in enumerate(alternatives):
            score = self._score_alternative(alternative, constraints)
            ranked.append({
                "rank": i + 1,
                "alternative": alternative,
                "score": score,
                "pros": self._get_alternative_pros(alternative),
                "cons": self._get_alternative_cons(alternative)
            })
        
        # Sort by score (highest first)
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        # Update ranks
        for i, item in enumerate(ranked):
            item["rank"] = i + 1
        
        return ranked
    
    def _score_alternative(self, alternative: str, constraints: List[Constraint]) -> float:
        """
        Score an alternative based on how well it fits constraints.
        
        Args:
            alternative: Alternative approach
            constraints: User constraints
            
        Returns:
            Score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Check if alternative addresses time constraints
        time_constraint = self._get_constraint_by_type(constraints, ConstraintType.TIME)
        if time_constraint and "reduce" in alternative.lower():
            score += 0.2
        
        # Check if alternative addresses skill constraints
        skill_constraint = self._get_constraint_by_type(constraints, ConstraintType.SKILL)
        if skill_constraint and "simplify" in alternative.lower():
            score += 0.2
        
        # Check if alternative addresses quality constraints
        quality_constraint = self._get_constraint_by_type(constraints, ConstraintType.QUALITY)
        if quality_constraint and "mvp" in alternative.lower():
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_alternative_pros(self, alternative: str) -> List[str]:
        """Get pros of an alternative."""
        pros = []
        
        if "reduce scope" in alternative.lower():
            pros.append("Faster completion")
            pros.append("Lower complexity")
        
        if "reduce quality" in alternative.lower():
            pros.append("Quicker to implement")
            pros.append("Less effort required")
        
        if "simplify" in alternative.lower():
            pros.append("Easier to understand")
            pros.append("Less error-prone")
        
        if "break task" in alternative.lower():
            pros.append("More manageable")
            pros.append("Clearer progress")
        
        return pros
    
    def _get_alternative_cons(self, alternative: str) -> List[str]:
        """Get cons of an alternative."""
        cons = []
        
        if "reduce scope" in alternative.lower():
            cons.append("Fewer features")
            cons.append("May not meet all requirements")
        
        if "reduce quality" in alternative.lower():
            cons.append("Lower quality output")
            cons.append("May need refactoring later")
        
        if "simplify" in alternative.lower():
            cons.append("May not address all needs")
            cons.append("Limited functionality")
        
        if "break task" in alternative.lower():
            cons.append("More coordination needed")
            cons.append("May take longer overall")
        
        return cons
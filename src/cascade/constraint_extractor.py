"""
Constraint Extractor - Discovers user constraints and limitations.

This component identifies user constraints such as time, budget, skills,
and validates constraint combinations.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Types of constraints that can be extracted"""
    TIME = "time"  # Time constraints (hours, days, weeks)
    BUDGET = "budget"  # Budget constraints (dollars, resources)
    SKILL = "skill"  # Skill level constraints (beginner, intermediate, expert)
    COMPLEXITY = "complexity"  # Complexity constraints (simple, moderate, complex)
    SCOPE = "scope"  # Scope constraints (minimal, standard, comprehensive)
    QUALITY = "quality"  # Quality constraints (mvp, production-ready, polished)
    MAINTAINABILITY = "maintainability"  # Maintainability constraints (quick hack, maintainable, enterprise)


@dataclass
class Constraint:
    """Represents a user constraint"""
    type: ConstraintType
    value: Any
    confidence: float
    source: str  # Where the constraint was found (explicit, implicit, inferred)
    description: str


class ConstraintExtractor:
    """Extracts and validates user constraints from requests."""
    
    def __init__(self):
        """Initialize the constraint extractor with patterns."""
        # Time constraint patterns
        self.time_patterns = [
            (r'\b(\d+)\s*(hour|hr|h)\b', 'hours', 1),
            (r'\b(\d+)\s*(day|d)\b', 'days', 24),
            (r'\b(\d+)\s*(week|wk|w)\b', 'weeks', 168),
            (r'\b(\d+)\s*(month|mo|m)\b', 'months', 720),
            (r'\b(quick|fast|rapid|immediate|urgent|asap)\b', 'urgent', 1),
            (r'\b(slow|careful|thorough|detailed)\b', 'thorough', 168),
        ]
        
        # Budget constraint patterns
        self.budget_patterns = [
            (r'\$\s*(\d+(?:,\d+)*(?:\.\d{2})?)', 'dollars'),
            (r'\b(\d+)\s*(dollar|dollars|bucks)\b', 'dollars'),
            (r'\b(free|no cost|zero cost|budget|cheap|low cost)\b', 'low'),
            (r'\b(expensive|premium|high end|unlimited)\b', 'high'),
        ]
        
        # Skill level patterns
        self.skill_patterns = [
            (r'\b(beginner|novice|newbie|starter|learning)\b', 'beginner'),
            (r'\b(intermediate|moderate|some experience)\b', 'intermediate'),
            (r'\b(expert|advanced|professional|senior)\b', 'expert'),
            (r'\b(simple|easy|basic|straightforward)\b', 'beginner'),
            (r'\b(complex|advanced|sophisticated)\b', 'expert'),
        ]
        
        # Complexity patterns
        self.complexity_patterns = [
            (r'\b(simple|basic|minimal|quick|easy)\b', 'simple'),
            (r'\b(moderate|standard|normal|typical)\b', 'moderate'),
            (r'\b(complex|advanced|sophisticated|comprehensive)\b', 'complex'),
        ]
        
        # Scope patterns
        self.scope_patterns = [
            (r'\b(mvp|minimal|minimum|basic|core)\b', 'minimal'),
            (r'\b(standard|normal|typical|regular)\b', 'standard'),
            (r'\b(comprehensive|complete|full|entire|everything)\b', 'comprehensive'),
        ]
        
        # Quality patterns
        self.quality_patterns = [
            (r'\b(mvp|minimum viable|prototype|proof of concept|poc)\b', 'mvp'),
            (r'\b(production|prod|deployable|ready)\b', 'production'),
            (r'\b(polished|refined|professional|enterprise)\b', 'polished'),
        ]
        
        # Maintainability patterns
        self.maintainability_patterns = [
            (r'\b(quick|dirty|hack|temporary|throwaway)\b', 'quick_hack'),
            (r'\b(maintainable|clean|well-structured|organized)\b', 'maintainable'),
            (r'\b(enterprise|scalable|robust|long-term)\b', 'enterprise'),
        ]
        
        # Compile patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns."""
        self.time_patterns_compiled = [(re.compile(p, re.IGNORECASE), unit, mult) 
                                       for p, unit, mult in self.time_patterns]
        self.budget_patterns_compiled = [(re.compile(p, re.IGNORECASE), unit) 
                                         for p, unit in self.budget_patterns]
        self.skill_patterns_compiled = [(re.compile(p, re.IGNORECASE), level) 
                                        for p, level in self.skill_patterns]
        self.complexity_patterns_compiled = [(re.compile(p, re.IGNORECASE), level) 
                                             for p, level in self.complexity_patterns]
        self.scope_patterns_compiled = [(re.compile(p, re.IGNORECASE), level) 
                                        for p, level in self.scope_patterns]
        self.quality_patterns_compiled = [(re.compile(p, re.IGNORECASE), level) 
                                         for p, level in self.quality_patterns]
        self.maintainability_patterns_compiled = [(re.compile(p, re.IGNORECASE), level) 
                                                  for p, level in self.maintainability_patterns]
    
    def extract(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> List[Constraint]:
        """
        Extract constraints from user input.
        
        Args:
            user_input: The user's request string
            context: Optional context (e.g., project info, user profile)
            
        Returns:
            List of extracted constraints
        """
        constraints = []
        
        # Extract time constraints
        constraints.extend(self._extract_time_constraints(user_input))
        
        # Extract budget constraints
        constraints.extend(self._extract_budget_constraints(user_input))
        
        # Extract skill constraints
        constraints.extend(self._extract_skill_constraints(user_input))
        
        # Extract complexity constraints
        constraints.extend(self._extract_complexity_constraints(user_input))
        
        # Extract scope constraints
        constraints.extend(self._extract_scope_constraints(user_input))
        
        # Extract quality constraints
        constraints.extend(self._extract_quality_constraints(user_input))
        
        # Extract maintainability constraints
        constraints.extend(self._extract_maintainability_constraints(user_input))
        
        # Infer constraints from context if provided
        if context:
            constraints.extend(self._infer_constraints_from_context(context))
        
        logger.info(f"Extracted {len(constraints)} constraints from request")
        return constraints
    
    def _extract_time_constraints(self, text: str) -> List[Constraint]:
        """Extract time constraints from text."""
        constraints = []
        
        for pattern, unit, multiplier in self.time_patterns_compiled:
            match = pattern.search(text)
            if match:
                if unit in ['hours', 'days', 'weeks', 'months']:
                    value = int(match.group(1)) * multiplier
                    description = f"{match.group(0)} ({value} hours)"
                else:
                    value = unit
                    description = match.group(0)
                
                constraint = Constraint(
                    type=ConstraintType.TIME,
                    value=value,
                    confidence=0.8,
                    source="explicit",
                    description=description
                )
                constraints.append(constraint)
        
        return constraints
    
    def _extract_budget_constraints(self, text: str) -> List[Constraint]:
        """Extract budget constraints from text."""
        constraints = []
        
        for pattern, unit in self.budget_patterns_compiled:
            match = pattern.search(text)
            if match:
                if unit == 'dollars':
                    # Extract numeric value
                    value_str = match.group(1).replace(',', '')
                    try:
                        value = float(value_str)
                        description = f"${value}"
                    except ValueError:
                        value = "unknown"
                        description = match.group(0)
                else:
                    value = unit
                    description = match.group(0)
                
                constraint = Constraint(
                    type=ConstraintType.BUDGET,
                    value=value,
                    confidence=0.75,
                    source="explicit",
                    description=description
                )
                constraints.append(constraint)
        
        return constraints
    
    def _extract_skill_constraints(self, text: str) -> List[Constraint]:
        """Extract skill level constraints from text."""
        constraints = []
        
        for pattern, level in self.skill_patterns_compiled:
            match = pattern.search(text)
            if match:
                constraint = Constraint(
                    type=ConstraintType.SKILL,
                    value=level,
                    confidence=0.7,
                    source="explicit",
                    description=match.group(0)
                )
                constraints.append(constraint)
        
        return constraints
    
    def _extract_complexity_constraints(self, text: str) -> List[Constraint]:
        """Extract complexity constraints from text."""
        constraints = []
        
        for pattern, level in self.complexity_patterns_compiled:
            match = pattern.search(text)
            if match:
                constraint = Constraint(
                    type=ConstraintType.COMPLEXITY,
                    value=level,
                    confidence=0.75,
                    source="explicit",
                    description=match.group(0)
                )
                constraints.append(constraint)
        
        return constraints
    
    def _extract_scope_constraints(self, text: str) -> List[Constraint]:
        """Extract scope constraints from text."""
        constraints = []
        
        for pattern, level in self.scope_patterns_compiled:
            match = pattern.search(text)
            if match:
                constraint = Constraint(
                    type=ConstraintType.SCOPE,
                    value=level,
                    confidence=0.8,
                    source="explicit",
                    description=match.group(0)
                )
                constraints.append(constraint)
        
        return constraints
    
    def _extract_quality_constraints(self, text: str) -> List[Constraint]:
        """Extract quality constraints from text."""
        constraints = []
        
        for pattern, level in self.quality_patterns_compiled:
            match = pattern.search(text)
            if match:
                constraint = Constraint(
                    type=ConstraintType.QUALITY,
                    value=level,
                    confidence=0.85,
                    source="explicit",
                    description=match.group(0)
                )
                constraints.append(constraint)
        
        return constraints
    
    def _extract_maintainability_constraints(self, text: str) -> List[Constraint]:
        """Extract maintainability constraints from text."""
        constraints = []
        
        for pattern, level in self.maintainability_patterns_compiled:
            match = pattern.search(text)
            if match:
                constraint = Constraint(
                    type=ConstraintType.MAINTAINABILITY,
                    value=level,
                    confidence=0.75,
                    source="explicit",
                    description=match.group(0)
                )
                constraints.append(constraint)
        
        return constraints
    
    def _infer_constraints_from_context(self, context: Dict[str, Any]) -> List[Constraint]:
        """Infer constraints from context."""
        constraints = []
        
        # Infer from user profile
        if 'user_profile' in context:
            profile = context['user_profile']
            if profile.get('experience_level'):
                constraint = Constraint(
                    type=ConstraintType.SKILL,
                    value=profile['experience_level'],
                    confidence=0.6,
                    source="inferred",
                    description=f"Inferred from user profile"
                )
                constraints.append(constraint)
        
        # Infer from project type
        if 'project_type' in context:
            project_type = context['project_type']
            if project_type == 'prototype':
                constraint = Constraint(
                    type=ConstraintType.QUALITY,
                    value='mvp',
                    confidence=0.7,
                    source="inferred",
                    description=f"Inferred from project type: {project_type}"
                )
                constraints.append(constraint)
            elif project_type == 'production':
                constraint = Constraint(
                    type=ConstraintType.QUALITY,
                    value='production',
                    confidence=0.7,
                    source="inferred",
                    description=f"Inferred from project type: {project_type}"
                )
                constraints.append(constraint)
        
        return constraints
    
    def validate_constraints(self, constraints: List[Constraint]) -> Dict[str, Any]:
        """
        Validate constraint combinations for conflicts or issues.
        
        Args:
            constraints: List of constraints to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "conflicts": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Group constraints by type
        constraints_by_type = {}
        for constraint in constraints:
            if constraint.type not in constraints_by_type:
                constraints_by_type[constraint.type] = []
            constraints_by_type[constraint.type].append(constraint)
        
        # Check for conflicts
        validation["conflicts"].extend(self._check_time_complexity_conflict(constraints_by_type))
        validation["conflicts"].extend(self._check_quality_maintainability_conflict(constraints_by_type))
        validation["conflicts"].extend(self._check_scope_quality_conflict(constraints_by_type))
        
        # Check for warnings
        validation["warnings"].extend(self._check_time_warnings(constraints_by_type))
        validation["warnings"].extend(self._check_skill_complexity_warnings(constraints_by_type))
        
        # Generate suggestions
        validation["suggestions"].extend(self._generate_suggestions(constraints_by_type))
        
        # Set overall validity
        validation["valid"] = len(validation["conflicts"]) == 0
        
        return validation
    
    def _check_time_complexity_conflict(self, constraints_by_type: Dict[ConstraintType, List[Constraint]]) -> List[str]:
        """Check for conflicts between time and complexity constraints."""
        conflicts = []
        
        time_constraints = constraints_by_type.get(ConstraintType.TIME, [])
        complexity_constraints = constraints_by_type.get(ConstraintType.COMPLEXITY, [])
        
        for time_constraint in time_constraints:
            if isinstance(time_constraint.value, str) and time_constraint.value == 'urgent':
                for complexity_constraint in complexity_constraints:
                    if complexity_constraint.value == 'complex':
                        conflicts.append(
                            f"Urgent time constraint conflicts with complex complexity. "
                            f"Consider simplifying or extending timeline."
                        )
        
        return conflicts
    
    def _check_quality_maintainability_conflict(self, constraints_by_type: Dict[ConstraintType, List[Constraint]]) -> List[str]:
        """Check for conflicts between quality and maintainability constraints."""
        conflicts = []
        
        quality_constraints = constraints_by_type.get(ConstraintType.QUALITY, [])
        maintainability_constraints = constraints_by_type.get(ConstraintType.MAINTAINABILITY, [])
        
        for quality_constraint in quality_constraints:
            if quality_constraint.value == 'mvp':
                for maintainability_constraint in maintainability_constraints:
                    if maintainability_constraint.value == 'enterprise':
                        conflicts.append(
                            f"MVP quality conflicts with enterprise maintainability. "
                            f"Consider adjusting quality or maintainability expectations."
                        )
        
        return conflicts
    
    def _check_scope_quality_conflict(self, constraints_by_type: Dict[ConstraintType, List[Constraint]]) -> List[str]:
        """Check for conflicts between scope and quality constraints."""
        conflicts = []
        
        scope_constraints = constraints_by_type.get(ConstraintType.SCOPE, [])
        quality_constraints = constraints_by_type.get(ConstraintType.QUALITY, [])
        
        for scope_constraint in scope_constraints:
            if scope_constraint.value == 'minimal':
                for quality_constraint in quality_constraints:
                    if quality_constraint.value == 'polished':
                        conflicts.append(
                            f"Minimal scope conflicts with polished quality. "
                            f"Consider expanding scope or adjusting quality expectations."
                        )
        
        return conflicts
    
    def _check_time_warnings(self, constraints_by_type: Dict[ConstraintType, List[Constraint]]) -> List[str]:
        """Check for time-related warnings."""
        warnings = []
        
        time_constraints = constraints_by_type.get(ConstraintType.TIME, [])
        
        for time_constraint in time_constraints:
            if isinstance(time_constraint.value, (int, float)):
                if time_constraint.value < 4:  # Less than 4 hours
                    warnings.append(
                        f"Very tight time constraint ({time_constraint.value} hours). "
                        f"May limit what can be accomplished."
                    )
        
        return warnings
    
    def _check_skill_complexity_warnings(self, constraints_by_type: Dict[ConstraintType, List[Constraint]]) -> List[str]:
        """Check for skill-complexity warnings."""
        warnings = []
        
        skill_constraints = constraints_by_type.get(ConstraintType.SKILL, [])
        complexity_constraints = constraints_by_type.get(ConstraintType.COMPLEXITY, [])
        
        for skill_constraint in skill_constraints:
            if skill_constraint.value == 'beginner':
                for complexity_constraint in complexity_constraints:
                    if complexity_constraint.value == 'complex':
                        warnings.append(
                            f"Beginner skill level may struggle with complex complexity. "
                            f"Consider simplifying or providing more guidance."
                        )
        
        return warnings
    
    def _generate_suggestions(self, constraints_by_type: Dict[ConstraintType, List[Constraint]]) -> List[str]:
        """Generate suggestions based on constraints."""
        suggestions = []
        
        # Check for missing constraints
        if ConstraintType.TIME not in constraints_by_type:
            suggestions.append("Consider specifying a time constraint for better planning")
        
        if ConstraintType.QUALITY not in constraints_by_type:
            suggestions.append("Consider specifying quality expectations (mvp, production, polished)")
        
        if ConstraintType.SCOPE not in constraints_by_type:
            suggestions.append("Consider specifying scope (minimal, standard, comprehensive)")
        
        return suggestions
    
    def get_constraint_summary(self, constraints: List[Constraint]) -> Dict[str, Any]:
        """
        Get a summary of extracted constraints.
        
        Args:
            constraints: List of constraints
            
        Returns:
            Dictionary with constraint summary
        """
        if not constraints:
            return {
                "has_constraints": False,
                "count": 0,
                "types": []
            }
        
        # Count by type
        type_counts = {}
        for constraint in constraints:
            type_name = constraint.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "has_constraints": True,
            "count": len(constraints),
            "types": list(type_counts.keys()),
            "type_counts": type_counts,
            "average_confidence": sum(c.confidence for c in constraints) / len(constraints)
        }
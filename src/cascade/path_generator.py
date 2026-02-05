"""
Path Generator - Generates alternative execution paths when constraints limit options.

This component creates multiple approaches to completing tasks, allowing
the system to adapt when constraints prevent the optimal path.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .constraint_extractor import Constraint, ConstraintType
from .feasibility_validator import FeasibilityResult, FeasibilityStatus

logger = logging.getLogger(__name__)


class PathType(Enum):
    """Types of execution paths"""
    OPTIMAL = "optimal"
    FAST = "fast"
    THOROUGH = "thorough"
    MINIMAL = "minimal"
    ALTERNATIVE = "alternative"
    WORKAROUND = "workaround"


@dataclass
class ExecutionPath:
    """An execution path for completing a task"""
    path_type: PathType
    description: str
    steps: List[str]
    estimated_time: float
    estimated_cost: float
    required_skills: List[str]
    required_resources: List[str]
    pros: List[str]
    cons: List[str]
    confidence: float


class PathGenerator:
    """Generates alternative execution paths when constraints limit options."""
    
    def __init__(self):
        """Initialize the path generator."""
        # Path templates for different scenarios
        self.path_templates = {
            PathType.OPTIMAL: {
                'description': 'Balanced approach with optimal trade-offs',
                'time_multiplier': 1.0,
                'quality_multiplier': 1.0,
                'complexity_multiplier': 1.0
            },
            PathType.FAST: {
                'description': 'Quick completion with minimal features',
                'time_multiplier': 0.5,
                'quality_multiplier': 0.7,
                'complexity_multiplier': 0.5
            },
            PathType.THOROUGH: {
                'description': 'Comprehensive approach with maximum quality',
                'time_multiplier': 2.0,
                'quality_multiplier': 1.5,
                'complexity_multiplier': 1.5
            },
            PathType.MINIMAL: {
                'description': 'Minimum viable solution',
                'time_multiplier': 0.3,
                'quality_multiplier': 0.5,
                'complexity_multiplier': 0.3
            },
            PathType.ALTERNATIVE: {
                'description': 'Alternative approach using different methods',
                'time_multiplier': 1.2,
                'quality_multiplier': 0.9,
                'complexity_multiplier': 1.0
            },
            PathType.WORKAROUND: {
                'description': 'Workaround for specific constraints',
                'time_multiplier': 0.8,
                'quality_multiplier': 0.6,
                'complexity_multiplier': 0.7
            }
        }
        
        # Common task patterns
        self.task_patterns = {
            'coding': {
                'steps': [
                    'Analyze requirements',
                    'Design architecture',
                    'Implement core functionality',
                    'Add error handling',
                    'Write tests',
                    'Refactor and optimize',
                    'Document code'
                ],
                'skills': ['programming', 'problem-solving', 'debugging'],
                'resources': ['IDE', 'version control', 'testing framework']
            },
            'writing': {
                'steps': [
                    'Research topic',
                    'Outline structure',
                    'Draft content',
                    'Review and revise',
                    'Edit for clarity',
                    'Finalize and format'
                ],
                'skills': ['writing', 'research', 'editing'],
                'resources': ['word processor', 'research tools', 'style guide']
            },
            'analysis': {
                'steps': [
                    'Gather data',
                    'Clean and preprocess',
                    'Explore patterns',
                    'Apply analysis methods',
                    'Interpret results',
                    'Create visualizations',
                    'Document findings'
                ],
                'skills': ['data analysis', 'statistics', 'visualization'],
                'resources': ['analysis tools', 'data sources', 'visualization library']
            },
            'research': {
                'steps': [
                    'Define research question',
                    'Literature review',
                    'Design methodology',
                    'Collect data',
                    'Analyze results',
                    'Draw conclusions',
                    'Write report'
                ],
                'skills': ['research', 'critical thinking', 'writing'],
                'resources': ['databases', 'research tools', 'citation manager']
            }
        }
    
    def generate_paths(self, task_description: str, constraints: List[Constraint],
                      feasibility_result: Optional[FeasibilityResult] = None,
                      context: Optional[Dict[str, Any]] = None) -> List[ExecutionPath]:
        """
        Generate alternative execution paths for a task.
        
        Args:
            task_description: Description of the task
            constraints: List of user constraints
            feasibility_result: Optional feasibility check result
            context: Optional context (e.g., project info, available resources)
            
        Returns:
            List of execution paths
        """
        paths = []
        
        # Detect task type
        task_type = self._detect_task_type(task_description)
        
        # Get base steps for task type
        base_steps = self.task_patterns.get(task_type, {}).get('steps', [])
        base_skills = self.task_patterns.get(task_type, {}).get('skills', [])
        base_resources = self.task_patterns.get(task_type, {}).get('resources', [])
        
        # Generate different path types
        if feasibility_result and feasibility_result.status == FeasibilityStatus.FEASIBLE:
            # If feasible, generate optimal and thorough paths
            paths.append(self._generate_path(
                PathType.OPTIMAL, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
            paths.append(self._generate_path(
                PathType.THOROUGH, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
        elif feasibility_result and feasibility_result.status == FeasibilityStatus.MARGINALLY_FEASIBLE:
            # If marginally feasible, generate fast and minimal paths
            paths.append(self._generate_path(
                PathType.FAST, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
            paths.append(self._generate_path(
                PathType.MINIMAL, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
        else:
            # If infeasible, generate alternative and workaround paths
            paths.append(self._generate_path(
                PathType.ALTERNATIVE, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
            paths.append(self._generate_path(
                PathType.WORKAROUND, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
        
        # Always add a minimal path as fallback
        if not any(p.path_type == PathType.MINIMAL for p in paths):
            paths.append(self._generate_path(
                PathType.MINIMAL, task_description, constraints,
                base_steps, base_skills, base_resources, context
            ))
        
        logger.info(f"Generated {len(paths)} execution paths for task")
        return paths
    
    def _detect_task_type(self, task_description: str) -> str:
        """
        Detect the type of task from description.
        
        Args:
            task_description: Task description
            
        Returns:
            Task type (coding, writing, analysis, research)
        """
        task_lower = task_description.lower()
        
        coding_keywords = ['code', 'program', 'develop', 'implement', 'function', 'class', 'api', 'app']
        writing_keywords = ['write', 'document', 'article', 'blog', 'content', 'essay', 'report']
        analysis_keywords = ['analyze', 'data', 'statistics', 'metrics', 'trends', 'patterns']
        research_keywords = ['research', 'investigate', 'study', 'explore', 'find', 'discover']
        
        if any(keyword in task_lower for keyword in coding_keywords):
            return 'coding'
        elif any(keyword in task_lower for keyword in writing_keywords):
            return 'writing'
        elif any(keyword in task_lower for keyword in analysis_keywords):
            return 'analysis'
        elif any(keyword in task_lower for keyword in research_keywords):
            return 'research'
        else:
            return 'coding'  # Default to coding
    
    def _generate_path(self, path_type: PathType, task_description: str,
                      constraints: List[Constraint], base_steps: List[str],
                      base_skills: List[str], base_resources: List[str],
                      context: Optional[Dict[str, Any]] = None) -> ExecutionPath:
        """
        Generate a specific execution path.
        
        Args:
            path_type: Type of path to generate
            task_description: Task description
            constraints: User constraints
            base_steps: Base steps for task type
            base_skills: Base skills for task type
            base_resources: Base resources for task type
            context: Optional context
            
        Returns:
            ExecutionPath
        """
        template = self.path_templates[path_type]
        
        # Adjust steps based on path type
        steps = self._adjust_steps(base_steps, path_type)
        
        # Estimate time
        estimated_time = self._estimate_time(steps, constraints, template['time_multiplier'])
        
        # Estimate cost (simplified - could be more sophisticated)
        estimated_cost = self._estimate_cost(steps, constraints)
        
        # Adjust skills and resources
        required_skills = self._adjust_skills(base_skills, path_type)
        required_resources = self._adjust_resources(base_resources, path_type)
        
        # Generate pros and cons
        pros = self._generate_pros(path_type)
        cons = self._generate_cons(path_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(path_type, constraints)
        
        return ExecutionPath(
            path_type=path_type,
            description=template['description'],
            steps=steps,
            estimated_time=estimated_time,
            estimated_cost=estimated_cost,
            required_skills=required_skills,
            required_resources=required_resources,
            pros=pros,
            cons=cons,
            confidence=confidence
        )
    
    def _adjust_steps(self, base_steps: List[str], path_type: PathType) -> List[str]:
        """Adjust steps based on path type."""
        if path_type == PathType.MINIMAL:
            # Keep only essential steps
            essential_indices = [0, 2, 5]  # First, middle, last
            return [base_steps[i] for i in essential_indices if i < len(base_steps)]
        elif path_type == PathType.FAST:
            # Skip some steps
            skip_indices = [3, 5]  # Error handling, refactoring
            return [step for i, step in enumerate(base_steps) if i not in skip_indices]
        elif path_type == PathType.THOROUGH:
            # Add additional steps
            additional_steps = ['Add comprehensive tests', 'Performance optimization', 'Security review']
            return base_steps + additional_steps
        elif path_type == PathType.ALTERNATIVE:
            # Reorder steps
            return base_steps[2:4] + base_steps[0:2] + base_steps[4:]
        elif path_type == PathType.WORKAROUND:
            # Simplify steps
            simplified_steps = [step.split(' and')[0] for step in base_steps]
            return simplified_steps
        else:
            return base_steps
    
    def _estimate_time(self, steps: List[str], constraints: List[Constraint],
                      multiplier: float) -> float:
        """Estimate time for execution path."""
        # Base time per step (in hours)
        base_time_per_step = 2.0
        
        # Get time constraint
        time_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.TIME:
                time_constraint = constraint
                break
        
        # Calculate base time
        base_time = len(steps) * base_time_per_step
        
        # Apply multiplier
        estimated_time = base_time * multiplier
        
        # Adjust for time constraint
        if time_constraint and isinstance(time_constraint.value, (int, float)):
            # If constraint is tight, reduce estimate
            if estimated_time > time_constraint.value:
                estimated_time = time_constraint.value * 0.9
        
        return estimated_time
    
    def _estimate_cost(self, steps: List[str], constraints: List[Constraint]) -> float:
        """Estimate cost for execution path."""
        # Simplified cost model (could be more sophisticated)
        cost_per_step = 10.0  # Arbitrary cost unit
        
        # Get budget constraint
        budget_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.BUDGET:
                budget_constraint = constraint
                break
        
        # Calculate base cost
        base_cost = len(steps) * cost_per_step
        
        # Adjust for budget constraint
        if budget_constraint and isinstance(budget_constraint.value, (int, float)):
            if base_cost > budget_constraint.value:
                base_cost = budget_constraint.value * 0.9
        
        return base_cost
    
    def _adjust_skills(self, base_skills: List[str], path_type: PathType) -> List[str]:
        """Adjust required skills based on path type."""
        if path_type == PathType.MINIMAL:
            # Keep only essential skills
            return base_skills[:1]
        elif path_type == PathType.FAST:
            # Remove advanced skills
            return base_skills[:-1] if len(base_skills) > 1 else base_skills
        elif path_type == PathType.THOROUGH:
            # Add advanced skills
            additional_skills = ['optimization', 'security', 'scalability']
            return base_skills + additional_skills
        else:
            return base_skills
    
    def _adjust_resources(self, base_resources: List[str], path_type: PathType) -> List[str]:
        """Adjust required resources based on path type."""
        if path_type == PathType.MINIMAL:
            # Keep only essential resources
            return base_resources[:1]
        elif path_type == PathType.FAST:
            # Remove advanced resources
            return base_resources[:-1] if len(base_resources) > 1 else base_resources
        elif path_type == PathType.THOROUGH:
            # Add advanced resources
            additional_resources = ['profiling tools', 'security scanner', 'CI/CD']
            return base_resources + additional_resources
        else:
            return base_resources
    
    def _generate_pros(self, path_type: PathType) -> List[str]:
        """Generate pros for a path type."""
        pros_map = {
            PathType.OPTIMAL: [
                'Balanced approach',
                'Good quality and speed',
                'Meets most requirements'
            ],
            PathType.FAST: [
                'Quick completion',
                'Minimal time investment',
                'Fast feedback'
            ],
            PathType.THOROUGH: [
                'High quality output',
                'Comprehensive coverage',
                'Long-term maintainability'
            ],
            PathType.MINIMAL: [
                'Fastest completion',
                'Lowest cost',
                'Quick validation'
            ],
            PathType.ALTERNATIVE: [
                'Different perspective',
                'May avoid specific issues',
                'Creative approach'
            ],
            PathType.WORKAROUND: [
                'Bypasses constraints',
                'Practical solution',
                'Quick implementation'
            ]
        }
        return pros_map.get(path_type, [])
    
    def _generate_cons(self, path_type: PathType) -> List[str]:
        """Generate cons for a path type."""
        cons_map = {
            PathType.OPTIMAL: [
                'May not excel in any area',
                'Compromise on extremes'
            ],
            PathType.FAST: [
                'Lower quality',
                'May miss edge cases',
                'Limited features'
            ],
            PathType.THOROUGH: [
                'Time-consuming',
                'May be overkill',
                'Higher cost'
            ],
            PathType.MINIMAL: [
                'Limited functionality',
                'May not meet all needs',
                'Lower quality'
            ],
            PathType.ALTERNATIVE: [
                'Unproven approach',
                'May have unknown issues',
                'Learning curve'
            ],
            PathType.WORKAROUND: [
                'Not ideal solution',
                'May create technical debt',
                'Temporary fix'
            ]
        }
        return cons_map.get(path_type, [])
    
    def _calculate_confidence(self, path_type: PathType, constraints: List[Constraint]) -> float:
        """Calculate confidence score for a path."""
        base_confidence = 0.7
        
        # Adjust based on path type
        if path_type == PathType.OPTIMAL:
            base_confidence = 0.8
        elif path_type == PathType.MINIMAL:
            base_confidence = 0.9
        elif path_type == PathType.WORKAROUND:
            base_confidence = 0.6
        
        # Adjust based on constraints
        time_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.TIME:
                time_constraint = constraint
                break
        
        if time_constraint and path_type == PathType.THOROUGH:
            base_confidence -= 0.2  # Thorough path less confident with time constraints
        
        return max(0.0, min(1.0, base_confidence))
    
    def rank_paths(self, paths: List[ExecutionPath],
                  constraints: List[Constraint]) -> List[ExecutionPath]:
        """
        Rank paths based on constraints and preferences.
        
        Args:
            paths: List of execution paths
            constraints: User constraints
            
        Returns:
            Ranked list of paths
        """
        # Score each path
        scored_paths = []
        for path in paths:
            score = self._score_path(path, constraints)
            scored_paths.append((score, path))
        
        # Sort by score (highest first)
        scored_paths.sort(key=lambda x: x[0], reverse=True)
        
        # Return ranked paths
        return [path for score, path in scored_paths]
    
    def _score_path(self, path: ExecutionPath, constraints: List[Constraint]) -> float:
        """Score a path based on constraints."""
        score = path.confidence
        
        # Adjust for time constraint
        time_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.TIME:
                time_constraint = constraint
                break
        
        if time_constraint and isinstance(time_constraint.value, (int, float)):
            if path.estimated_time <= time_constraint.value:
                score += 0.2
            else:
                score -= 0.2
        
        # Adjust for budget constraint
        budget_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.BUDGET:
                budget_constraint = constraint
                break
        
        if budget_constraint and isinstance(budget_constraint.value, (int, float)):
            if path.estimated_cost <= budget_constraint.value:
                score += 0.1
            else:
                score -= 0.1
        
        # Adjust for skill constraint
        skill_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.SKILL:
                skill_constraint = constraint
                break
        
        if skill_constraint:
            # Check if required skills match constraint
            if skill_constraint.value == 'beginner' and len(path.required_skills) <= 2:
                score += 0.1
            elif skill_constraint.value == 'expert' and len(path.required_skills) >= 3:
                score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def select_best_path(self, paths: List[ExecutionPath],
                        constraints: List[Constraint]) -> Optional[ExecutionPath]:
        """
        Select the best path based on constraints.
        
        Args:
            paths: List of execution paths
            constraints: User constraints
            
        Returns:
            Best path or None if no paths available
        """
        if not paths:
            return None
        
        ranked_paths = self.rank_paths(paths, constraints)
        return ranked_paths[0]
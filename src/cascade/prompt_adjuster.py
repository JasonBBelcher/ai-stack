"""
Prompt Adjuster - Modifies prompts when obstacles are encountered and generates alternatives.

This component adapts prompts dynamically based on execution feedback,
obstacles, and performance metrics to improve task completion rates.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .execution_planner import Subtask, TaskStatus
from .progress_monitor import Obstacle, ObstacleType, AlertLevel

# Import test configuration if available
try:
    from .test_config import (
        TEST_MODE,
        TEST_MODEL_OPTIMIZATIONS,
        get_test_model_optimizations,
        is_test_mode
    )
except ImportError:
    TEST_MODE = False
    TEST_MODEL_OPTIMIZATIONS = {}

logger = logging.getLogger(__name__)


class AdjustmentType(Enum):
    """Types of prompt adjustments"""
    SIMPLIFY = "simplify"
    EXPAND = "expand"
    REFINE = "refine"
    RESTRUCTURE = "restructure"
    ADD_CONTEXT = "add_context"
    REDUCE_SCOPE = "reduce_scope"
    CHANGE_MODEL = "change_model"
    BREAK_DOWN = "break_down"


@dataclass
class PromptAdjustment:
    """A prompt adjustment suggestion"""
    adjustment_type: AdjustmentType
    original_prompt: str
    adjusted_prompt: str
    reason: str
    expected_improvement: str
    confidence: float


class PromptAdjuster:
    """Modifies prompts when obstacles are encountered and generates alternatives."""
    
    def __init__(self, test_mode: bool = False):
        """
        Initialize the prompt adjuster.
        
        Args:
            test_mode: If True, use test model optimizations
        """
        self.test_mode = test_mode or TEST_MODE
        
        # Adjustment strategies for different obstacle types
        self.adjustment_strategies = {
            ObstacleType.TIMEOUT: [
                AdjustmentType.SIMPLIFY,
                AdjustmentType.REDUCE_SCOPE,
                AdjustmentType.CHANGE_MODEL
            ],
            ObstacleType.ERROR: [
                AdjustmentType.REFINE,
                AdjustmentType.ADD_CONTEXT,
                AdjustmentType.RESTRUCTURE
            ],
            ObstacleType.RESOURCE_LIMIT: [
                AdjustmentType.SIMPLIFY,
                AdjustmentType.REDUCE_SCOPE,
                AdjustmentType.CHANGE_MODEL
            ],
            ObstacleType.DEPENDENCY_FAILURE: [
                AdjustmentType.ADD_CONTEXT,
                AdjustmentType.REFINE
            ],
            ObstacleType.QUALITY_ISSUE: [
                AdjustmentType.EXPAND,
                AdjustmentType.REFINE,
                AdjustmentType.ADD_CONTEXT
            ],
            ObstacleType.PERFORMANCE_ISSUE: [
                AdjustmentType.SIMPLIFY,
                AdjustmentType.REDUCE_SCOPE,
                AdjustmentType.CHANGE_MODEL
            ]
        }
        
        # Prompt templates for adjustments
        self.adjustment_templates = {
            AdjustmentType.SIMPLIFY: {
                'prefix': 'Simplified version: ',
                'suffix': ' Keep it brief and direct.',
                'instructions': 'Focus on the core requirement only'
            },
            AdjustmentType.EXPAND: {
                'prefix': 'Comprehensive version: ',
                'suffix': ' Provide detailed explanations and examples.',
                'instructions': 'Include thorough details and context'
            },
            AdjustmentType.REFINE: {
                'prefix': 'Refined version: ',
                'suffix': ' Ensure clarity and precision.',
                'instructions': 'Improve clarity and specificity'
            },
            AdjustmentType.RESTRUCTURE: {
                'prefix': 'Restructured version: ',
                'suffix': ' Organize logically.',
                'instructions': 'Reorganize for better flow'
            },
            AdjustmentType.ADD_CONTEXT: {
                'prefix': 'With additional context: ',
                'suffix': ' Consider the broader context.',
                'instructions': 'Add relevant background information'
            },
            AdjustmentType.REDUCE_SCOPE: {
                'prefix': 'Reduced scope version: ',
                'suffix': ' Focus on essential elements only.',
                'instructions': 'Limit to minimum viable output'
            },
            AdjustmentType.CHANGE_MODEL: {
                'prefix': 'Optimized for different model: ',
                'suffix': ' Use clear, unambiguous language.',
                'instructions': 'Optimize for model capabilities'
            },
            AdjustmentType.BREAK_DOWN: {
                'prefix': 'Broken down version: ',
                'suffix': ' Address one aspect at a time.',
                'instructions': 'Split into smaller, focused tasks'
            }
        }
        
        # Model-specific optimizations
        if self.test_mode:
            self.model_optimizations = TEST_MODEL_OPTIMIZATIONS
        else:
            self.model_optimizations = {
                'llama3.1:8b': {
                    'max_tokens': 2048,
                    'temperature': 0.7,
                    'style': 'concise',
                    'avoid': ['complex reasoning', 'multi-step logic']
                },
                'qwen2.5:14b': {
                    'max_tokens': 4096,
                    'temperature': 0.8,
                    'style': 'detailed',
                    'avoid': ['overly complex', 'ambiguous']
                }
            }
    
    def analyze_obstacle(self, obstacle: Obstacle, subtask: Subtask,
                        context: Optional[Dict[str, Any]] = None) -> List[PromptAdjustment]:
        """
        Analyze an obstacle and generate prompt adjustments.
        
        Args:
            obstacle: The obstacle encountered
            subtask: The subtask that encountered the obstacle
            context: Optional context
            
        Returns:
            List of prompt adjustments
        """
        adjustments = []
        
        # Get adjustment strategies for this obstacle type
        strategies = self.adjustment_strategies.get(obstacle.obstacle_type, [])
        
        # Generate adjustments for each strategy
        for strategy in strategies:
            adjustment = self._generate_adjustment(
                strategy, obstacle, subtask, context
            )
            if adjustment:
                adjustments.append(adjustment)
        
        logger.info(f"Generated {len(adjustments)} prompt adjustments for {obstacle.obstacle_type.value}")
        return adjustments
    
    def _generate_adjustment(self, adjustment_type: AdjustmentType,
                            obstacle: Obstacle, subtask: Subtask,
                            context: Optional[Dict[str, Any]] = None) -> Optional[PromptAdjustment]:
        """
        Generate a specific prompt adjustment.
        
        Args:
            adjustment_type: Type of adjustment to generate
            obstacle: The obstacle encountered
            subtask: The subtask
            context: Optional context
            
        Returns:
            PromptAdjustment or None
        """
        template = self.adjustment_templates.get(adjustment_type)
        if not template:
            return None
        
        original_prompt = subtask.prompt
        
        # Generate adjusted prompt
        adjusted_prompt = self._apply_adjustment(
            adjustment_type, original_prompt, template, obstacle, subtask, context
        )
        
        # Generate reason
        reason = self._generate_reason(adjustment_type, obstacle)
        
        # Generate expected improvement
        expected_improvement = self._generate_expected_improvement(adjustment_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(adjustment_type, obstacle, subtask)
        
        return PromptAdjustment(
            adjustment_type=adjustment_type,
            original_prompt=original_prompt,
            adjusted_prompt=adjusted_prompt,
            reason=reason,
            expected_improvement=expected_improvement,
            confidence=confidence
        )
    
    def _apply_adjustment(self, adjustment_type: AdjustmentType,
                         original_prompt: str, template: Dict[str, Any],
                         obstacle: Obstacle, subtask: Subtask,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Apply an adjustment to a prompt.
        
        Args:
            adjustment_type: Type of adjustment
            original_prompt: Original prompt
            template: Adjustment template
            obstacle: The obstacle
            subtask: The subtask
            context: Optional context
            
        Returns:
            Adjusted prompt
        """
        adjusted = original_prompt
        
        # Apply prefix
        if 'prefix' in template:
            adjusted = template['prefix'] + adjusted
        
        # Apply suffix
        if 'suffix' in template:
            adjusted = adjusted + template['suffix']
        
        # Add specific instructions based on adjustment type
        if adjustment_type == AdjustmentType.SIMPLIFY:
            adjusted = self._simplify_prompt(adjusted)
        elif adjustment_type == AdjustmentType.EXPAND:
            adjusted = self._expand_prompt(adjusted)
        elif adjustment_type == AdjustmentType.REFINE:
            adjusted = self._refine_prompt(adjusted, obstacle)
        elif adjustment_type == AdjustmentType.RESTRUCTURE:
            adjusted = self._restructure_prompt(adjusted)
        elif adjustment_type == AdjustmentType.ADD_CONTEXT:
            adjusted = self._add_context(adjusted, context)
        elif adjustment_type == AdjustmentType.REDUCE_SCOPE:
            adjusted = self._reduce_scope(adjusted)
        elif adjustment_type == AdjustmentType.CHANGE_MODEL:
            adjusted = self._optimize_for_model(adjusted, subtask.required_model)
        elif adjustment_type == AdjustmentType.BREAK_DOWN:
            adjusted = self._break_down(adjusted)
        
        return adjusted
    
    def _simplify_prompt(self, prompt: str) -> str:
        """Simplify a prompt by removing complexity."""
        # Remove redundant phrases
        simplified = prompt.replace('Please ensure that', '')
        simplified = simplified.replace('Make sure to', '')
        simplified = simplified.replace('It is important to', '')
        
        # Simplify instructions
        simplified = simplified.replace('Provide a comprehensive', 'Provide a')
        simplified = simplified.replace('Create a detailed', 'Create a')
        
        return simplified.strip()
    
    def _expand_prompt(self, prompt: str) -> str:
        """Expand a prompt by adding detail."""
        # Add expansion instructions
        expansion = "\n\nAdditional Requirements:\n"
        expansion += "- Provide detailed explanations\n"
        expansion += "- Include relevant examples\n"
        expansion += "- Consider edge cases\n"
        expansion += "- Explain your reasoning\n"
        
        return prompt + expansion
    
    def _refine_prompt(self, prompt: str, obstacle: Obstacle) -> str:
        """Refine a prompt based on obstacle."""
        refined = prompt
        
        # Add specific refinement based on obstacle
        if obstacle.obstacle_type == ObstacleType.ERROR:
            refined += "\n\nNote: Previous attempt encountered an error. Please ensure your output is valid and complete."
        elif obstacle.obstacle_type == ObstacleType.QUALITY_ISSUE:
            refined += "\n\nNote: Previous output had quality issues. Please focus on accuracy and completeness."
        
        return refined
    
    def _restructure_prompt(self, prompt: str) -> str:
        """Restructure a prompt for better flow."""
        # Split into sections
        lines = prompt.split('\n')
        
        # Identify sections
        sections = {
            'task': [],
            'context': [],
            'instructions': []
        }
        
        current_section = 'task'
        for line in lines:
            line_lower = line.lower()
            if 'task:' in line_lower or 'description:' in line_lower:
                current_section = 'task'
            elif 'context:' in line_lower or 'background:' in line_lower:
                current_section = 'context'
            elif 'instruction' in line_lower or 'requirement' in line_lower:
                current_section = 'instructions'
            
            sections[current_section].append(line)
        
        # Rebuild with clear structure
        restructured = "Task:\n" + "\n".join(sections['task']) + "\n\n"
        if sections['context']:
            restructured += "Context:\n" + "\n".join(sections['context']) + "\n\n"
        if sections['instructions']:
            restructured += "Instructions:\n" + "\n".join(sections['instructions'])
        
        return restructured
    
    def _add_context(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Add context to a prompt."""
        if not context:
            return prompt
        
        context_section = "\n\nAdditional Context:\n"
        for key, value in context.items():
            context_section += f"- {key}: {value}\n"
        
        return prompt + context_section
    
    def _reduce_scope(self, prompt: str) -> str:
        """Reduce the scope of a prompt."""
        # Add scope reduction instruction
        reduction = "\n\nScope Limitation:\n"
        reduction += "Focus only on the essential elements. "
        reduction += "Skip optional features and nice-to-have additions."
        
        return prompt + reduction
    
    def _optimize_for_model(self, prompt: str, model: str) -> str:
        """Optimize prompt for a specific model."""
        optimizations = self.model_optimizations.get(model, {})
        
        if not optimizations:
            return prompt
        
        optimized = prompt
        
        # Add model-specific instructions
        if 'style' in optimizations:
            optimized += f"\n\nStyle: {optimizations['style']}"
        
        if 'avoid' in optimizations:
            optimized += "\n\nAvoid: " + ", ".join(optimizations['avoid'])
        
        return optimized
    
    def _break_down(self, prompt: str) -> str:
        """Break down a complex prompt into steps."""
        breakdown = "\n\nStep-by-Step Approach:\n"
        breakdown += "1. Analyze the requirements\n"
        breakdown += "2. Plan your approach\n"
        breakdown += "3. Execute step by step\n"
        breakdown += "4. Review and refine\n"
        
        return prompt + breakdown
    
    def _generate_reason(self, adjustment_type: AdjustmentType,
                        obstacle: Obstacle) -> str:
        """Generate a reason for the adjustment."""
        reasons = {
            AdjustmentType.SIMPLIFY: f"Simplifying to address {obstacle.obstacle_type.value}",
            AdjustmentType.EXPAND: "Expanding to improve quality and completeness",
            AdjustmentType.REFINE: f"Refining to resolve {obstacle.obstacle_type.value}",
            AdjustmentType.RESTRUCTURE: "Restructuring for better clarity",
            AdjustmentType.ADD_CONTEXT: "Adding context to improve understanding",
            AdjustmentType.REDUCE_SCOPE: "Reducing scope to fit constraints",
            AdjustmentType.CHANGE_MODEL: "Optimizing for model capabilities",
            AdjustmentType.BREAK_DOWN: "Breaking down into manageable steps"
        }
        
        return reasons.get(adjustment_type, "Adjustment to improve execution")
    
    def _generate_expected_improvement(self, adjustment_type: AdjustmentType) -> str:
        """Generate expected improvement description."""
        improvements = {
            AdjustmentType.SIMPLIFY: "Faster execution, lower resource usage",
            AdjustmentType.EXPAND: "Higher quality, more comprehensive output",
            AdjustmentType.REFINE: "Better accuracy, fewer errors",
            AdjustmentType.RESTRUCTURE: "Improved clarity, better flow",
            AdjustmentType.ADD_CONTEXT: "Better understanding, more relevant output",
            AdjustmentType.REDUCE_SCOPE: "Faster completion, lower complexity",
            AdjustmentType.CHANGE_MODEL: "Better model fit, improved performance",
            AdjustmentType.BREAK_DOWN: "More manageable, better progress tracking"
        }
        
        return improvements.get(adjustment_type, "Improved execution")
    
    def _calculate_confidence(self, adjustment_type: AdjustmentType,
                             obstacle: Obstacle, subtask: Subtask) -> float:
        """Calculate confidence in the adjustment."""
        base_confidence = 0.7
        
        # Adjust based on obstacle type
        if obstacle.obstacle_type == ObstacleType.TIMEOUT:
            if adjustment_type in [AdjustmentType.SIMPLIFY, AdjustmentType.REDUCE_SCOPE]:
                base_confidence = 0.9
        elif obstacle.obstacle_type == ObstacleType.ERROR:
            if adjustment_type in [AdjustmentType.REFINE, AdjustmentType.ADD_CONTEXT]:
                base_confidence = 0.8
        elif obstacle.obstacle_type == ObstacleType.RESOURCE_LIMIT:
            if adjustment_type in [AdjustmentType.SIMPLIFY, AdjustmentType.CHANGE_MODEL]:
                base_confidence = 0.85
        
        return base_confidence
    
    def select_best_adjustment(self, adjustments: List[PromptAdjustment],
                              context: Optional[Dict[str, Any]] = None) -> Optional[PromptAdjustment]:
        """
        Select the best adjustment from a list.
        
        Args:
            adjustments: List of adjustments
            context: Optional context
            
        Returns:
            Best adjustment or None
        """
        if not adjustments:
            return None
        
        # Sort by confidence
        sorted_adjustments = sorted(adjustments, key=lambda x: x.confidence, reverse=True)
        
        return sorted_adjustments[0]
    
    def apply_adjustment(self, subtask: Subtask, adjustment: PromptAdjustment) -> Subtask:
        """
        Apply an adjustment to a subtask.
        
        Args:
            subtask: The subtask to adjust
            adjustment: The adjustment to apply
            
        Returns:
            Updated subtask
        """
        subtask.prompt = adjustment.adjusted_prompt
        return subtask
    
    def generate_alternative_prompts(self, subtask: Subtask,
                                    num_alternatives: int = 3) -> List[str]:
        """
        Generate alternative prompts for a subtask.
        
        Args:
            subtask: The subtask
            num_alternatives: Number of alternatives to generate
            
        Returns:
            List of alternative prompts
        """
        alternatives = []
        
        # Generate different variations
        variations = [
            AdjustmentType.SIMPLIFY,
            AdjustmentType.EXPAND,
            AdjustmentType.REFINE,
            AdjustmentType.RESTRUCTURE
        ]
        
        for i, variation in enumerate(variations[:num_alternatives]):
            template = self.adjustment_templates.get(variation)
            if template:
                alternative = self._apply_adjustment(
                    variation, subtask.prompt, template,
                    Obstacle(ObstacleType.UNKNOWN, "Generating alternative", 
                           subtask.id, None, AlertLevel.INFO, [], {}),
                    subtask
                )
                alternatives.append(alternative)
        
        return alternatives
    
    def evaluate_adjustment_effectiveness(self, original_prompt: str,
                                         adjusted_prompt: str,
                                         result: str) -> Dict[str, Any]:
        """
        Evaluate the effectiveness of a prompt adjustment.
        
        Args:
            original_prompt: Original prompt
            adjusted_prompt: Adjusted prompt
            result: Result from adjusted prompt
            
        Returns:
            Evaluation metrics
        """
        # Simple evaluation based on result length and quality indicators
        evaluation = {
            'result_length': len(result),
            'has_error': 'error' in result.lower() or 'failed' in result.lower(),
            'has_success': 'success' in result.lower() or 'completed' in result.lower(),
            'prompt_complexity_reduction': len(adjusted_prompt) / len(original_prompt) if original_prompt else 1.0
        }
        
        # Calculate overall score
        score = 0.5
        if not evaluation['has_error']:
            score += 0.3
        if evaluation['has_success']:
            score += 0.2
        
        evaluation['overall_score'] = score
        
        return evaluation
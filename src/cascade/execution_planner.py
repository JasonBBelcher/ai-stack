"""
Execution Planner - Breaks tasks into model-sized chunks with workflow planning.

This component decomposes complex tasks into manageable subtasks that can be
executed by AI models, with proper workflow orchestration.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .constraint_extractor import Constraint, ConstraintType
from .path_generator import ExecutionPath

# Import test configuration if available
try:
    from .test_config import (
        TEST_MODE,
        TEST_MODEL_CAPABILITIES,
        TEST_MODEL_OPTIMIZATIONS,
        TEST_SUBTASK_TEMPLATES,
        get_test_model,
        get_test_model_optimizations,
        get_test_subtask_template,
        is_test_mode
    )
except ImportError:
    TEST_MODE = False
    TEST_MODEL_CAPABILITIES = {}
    TEST_MODEL_OPTIMIZATIONS = {}
    TEST_SUBTASK_TEMPLATES = {}

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Priority of a task"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Subtask:
    """A subtask within an execution plan"""
    id: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    dependencies: List[str]
    estimated_time: float
    required_model: str
    prompt: str
    output_format: str
    context: Dict[str, Any]


@dataclass
class ExecutionPlan:
    """An execution plan for completing a task"""
    task_id: str
    task_description: str
    subtasks: List[Subtask]
    total_estimated_time: float
    workflow_type: str
    parallelizable: bool
    checkpoint_interval: int


class ExecutionPlanner:
    """Breaks tasks into model-sized chunks with workflow planning."""
    
    def __init__(self, test_mode: bool = False):
        """
        Initialize the execution planner.
        
        Args:
            test_mode: If True, use smaller/faster models for testing
        """
        self.test_mode = test_mode or TEST_MODE
        
        # Model capabilities for different task types
        if self.test_mode:
            self.model_capabilities = TEST_MODEL_CAPABILITIES
        else:
            self.model_capabilities = {
                'coding': {
                    'simple': 'llama3.1:8b',
                    'moderate': 'qwen2.5:14b',
                    'complex': 'qwen2.5:14b'
                },
                'writing': {
                    'simple': 'llama3.1:8b',
                    'moderate': 'llama3.1:8b',
                    'complex': 'qwen2.5:14b'
                },
                'analysis': {
                    'simple': 'llama3.1:8b',
                    'moderate': 'qwen2.5:14b',
                    'complex': 'qwen2.5:14b'
                },
                'research': {
                    'simple': 'llama3.1:8b',
                    'moderate': 'qwen2.5:14b',
                    'complex': 'qwen2.5:14b'
                }
            }
        
        # Workflow templates
        self.workflow_templates = {
            'sequential': {
                'description': 'Execute subtasks one after another',
                'parallelizable': False
            },
            'parallel': {
                'description': 'Execute independent subtasks in parallel',
                'parallelizable': True
            },
            'hierarchical': {
                'description': 'Execute subtasks in a hierarchical structure',
                'parallelizable': False
            },
            'iterative': {
                'description': 'Execute subtasks iteratively with feedback',
                'parallelizable': False
            }
        }
        
        # Subtask templates for different task types
        if self.test_mode:
            # Use simplified test templates
            self.subtask_templates = TEST_SUBTASK_TEMPLATES
        else:
            self.subtask_templates = {
                'coding': [
                    {
                        'description': 'Analyze requirements and design architecture',
                        'priority': TaskPriority.CRITICAL,
                        'estimated_time': 2.0,
                        'output_format': 'architecture document'
                    },
                    {
                        'description': 'Implement core functionality',
                        'priority': TaskPriority.HIGH,
                        'estimated_time': 4.0,
                        'output_format': 'code'
                    },
                    {
                        'description': 'Add error handling and validation',
                        'priority': TaskPriority.HIGH,
                        'estimated_time': 2.0,
                        'output_format': 'code'
                    },
                    {
                        'description': 'Write unit tests',
                        'priority': TaskPriority.MEDIUM,
                        'estimated_time': 2.0,
                        'output_format': 'test code'
                    },
                    {
                        'description': 'Refactor and optimize',
                        'priority': TaskPriority.MEDIUM,
                        'estimated_time': 2.0,
                        'output_format': 'code'
                    },
                    {
                        'description': 'Document code and API',
                        'priority': TaskPriority.LOW,
                        'estimated_time': 1.0,
                        'output_format': 'documentation'
                    }
                ],
            'writing': [
                {
                    'description': 'Research and gather information',
                    'priority': TaskPriority.CRITICAL,
                    'estimated_time': 2.0,
                    'output_format': 'notes'
                },
                {
                    'description': 'Create outline and structure',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 1.0,
                    'output_format': 'outline'
                },
                {
                    'description': 'Draft content',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 3.0,
                    'output_format': 'text'
                },
                {
                    'description': 'Review and revise',
                    'priority': TaskPriority.MEDIUM,
                    'estimated_time': 2.0,
                    'output_format': 'text'
                },
                {
                    'description': 'Finalize and format',
                    'priority': TaskPriority.LOW,
                    'estimated_time': 1.0,
                    'output_format': 'formatted text'
                }
            ],
            'analysis': [
                {
                    'description': 'Gather and load data',
                    'priority': TaskPriority.CRITICAL,
                    'estimated_time': 2.0,
                    'output_format': 'dataset'
                },
                {
                    'description': 'Clean and preprocess data',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 2.0,
                    'output_format': 'cleaned data'
                },
                {
                    'description': 'Explore and analyze patterns',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 3.0,
                    'output_format': 'analysis results'
                },
                {
                    'description': 'Create visualizations',
                    'priority': TaskPriority.MEDIUM,
                    'estimated_time': 2.0,
                    'output_format': 'charts'
                },
                {
                    'description': 'Document findings',
                    'priority': TaskPriority.LOW,
                    'estimated_time': 1.0,
                    'output_format': 'report'
                }
            ],
            'research': [
                {
                    'description': 'Define research question and objectives',
                    'priority': TaskPriority.CRITICAL,
                    'estimated_time': 1.0,
                    'output_format': 'research plan'
                },
                {
                    'description': 'Conduct literature review',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 3.0,
                    'output_format': 'literature summary'
                },
                {
                    'description': 'Design methodology',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 2.0,
                    'output_format': 'methodology'
                },
                {
                    'description': 'Collect and analyze data',
                    'priority': TaskPriority.HIGH,
                    'estimated_time': 4.0,
                    'output_format': 'data and analysis'
                },
                {
                    'description': 'Draw conclusions and write report',
                    'priority': TaskPriority.MEDIUM,
                    'estimated_time': 2.0,
                    'output_format': 'research report'
                }
            ]
        }
    
    def create_plan(self, task_description: str, constraints: List[Constraint],
                   execution_path: Optional[ExecutionPath] = None,
                   context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """
        Create an execution plan for a task.
        
        Args:
            task_description: Description of the task
            constraints: List of user constraints
            execution_path: Optional selected execution path
            context: Optional context
            
        Returns:
            ExecutionPlan
        """
        # Detect task type
        task_type = self._detect_task_type(task_description)
        
        # Determine complexity
        complexity = self._determine_complexity(task_description, constraints)
        
        # Get subtask template
        subtask_template = self.subtask_templates.get(task_type, [])
        
        # Create subtasks
        subtasks = self._create_subtasks(
            task_description, task_type, complexity,
            subtask_template, constraints, context
        )
        
        # Calculate total estimated time
        total_time = sum(subtask.estimated_time for subtask in subtasks)
        
        # Determine workflow type
        workflow_type = self._determine_workflow_type(subtasks, constraints)
        
        # Determine if parallelizable
        parallelizable = self.workflow_templates[workflow_type]['parallelizable']
        
        # Determine checkpoint interval
        checkpoint_interval = self._determine_checkpoint_interval(subtasks, constraints)
        
        # Generate task ID
        task_id = self._generate_task_id(task_description)
        
        plan = ExecutionPlan(
            task_id=task_id,
            task_description=task_description,
            subtasks=subtasks,
            total_estimated_time=total_time,
            workflow_type=workflow_type,
            parallelizable=parallelizable,
            checkpoint_interval=checkpoint_interval
        )
        
        logger.info(f"Created execution plan with {len(subtasks)} subtasks")
        return plan
    
    def _detect_task_type(self, task_description: str) -> str:
        """Detect the type of task from description."""
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
    
    def _determine_complexity(self, task_description: str,
                             constraints: List[Constraint]) -> str:
        """Determine task complexity from description and constraints."""
        # Check for complexity constraint
        for constraint in constraints:
            if constraint.type == ConstraintType.COMPLEXITY:
                return constraint.value
        
        # Infer from description
        task_lower = task_description.lower()
        
        complex_keywords = ['complex', 'advanced', 'sophisticated', 'comprehensive', 'enterprise']
        simple_keywords = ['simple', 'basic', 'minimal', 'quick', 'easy']
        
        if any(keyword in task_lower for keyword in complex_keywords):
            return 'complex'
        elif any(keyword in task_lower for keyword in simple_keywords):
            return 'simple'
        else:
            return 'moderate'  # Default
    
    def _create_subtasks(self, task_description: str, task_type: str,
                        complexity: str, subtask_template: List[Dict[str, Any]],
                        constraints: List[Constraint],
                        context: Optional[Dict[str, Any]] = None) -> List[Subtask]:
        """Create subtasks from template."""
        subtasks = []
        
        # Get model for task type and complexity
        model = self.model_capabilities.get(task_type, {}).get(complexity, 'llama3.1:8b')
        
        # Adjust template based on constraints
        adjusted_template = self._adjust_template(subtask_template, constraints)
        
        for i, template in enumerate(adjusted_template):
            subtask_id = f"{task_type}_{i+1}"
            
            # Generate prompt
            prompt = self._generate_prompt(
                task_description, template['description'],
                task_type, complexity, context
            )
            
            # Determine dependencies
            dependencies = []
            if i > 0:
                dependencies.append(f"{task_type}_{i}")
            
            subtask = Subtask(
                id=subtask_id,
                description=template['description'],
                status=TaskStatus.PENDING,
                priority=template['priority'],
                dependencies=dependencies,
                estimated_time=template['estimated_time'],
                required_model=model,
                prompt=prompt,
                output_format=template['output_format'],
                context=context or {}
            )
            
            subtasks.append(subtask)
        
        return subtasks
    
    def _adjust_template(self, template: List[Dict[str, Any]],
                        constraints: List[Constraint]) -> List[Dict[str, Any]]:
        """Adjust subtask template based on constraints."""
        adjusted = template.copy()
        
        # Check for scope constraint
        scope_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.SCOPE:
                scope_constraint = constraint
                break
        
        if scope_constraint:
            if scope_constraint.value == 'minimal':
                # Keep only critical and high priority subtasks
                adjusted = [t for t in adjusted if t['priority'] in [TaskPriority.CRITICAL, TaskPriority.HIGH]]
            elif scope_constraint.value == 'comprehensive':
                # Add additional subtasks
                additional = {
                    'description': 'Perform final review and quality assurance',
                    'priority': TaskPriority.MEDIUM,
                    'estimated_time': 1.0,
                    'output_format': 'review report'
                }
                adjusted.append(additional)
        
        return adjusted
    
    def _generate_prompt(self, task_description: str, subtask_description: str,
                        task_type: str, complexity: str,
                        context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a prompt for a subtask."""
        prompt = f"""Task: {task_description}

Subtask: {subtask_description}

Task Type: {task_type}
Complexity: {complexity}

Instructions:
1. Focus on the specific subtask described above
2. Ensure your output matches the expected format
3. Consider the overall task context
4. Provide clear and actionable results
"""
        
        if context:
            prompt += f"\nContext:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
        
        return prompt
    
    def _determine_workflow_type(self, subtasks: List[Subtask],
                                constraints: List[Constraint]) -> str:
        """Determine the best workflow type for the subtasks."""
        # Check if subtasks have dependencies
        has_dependencies = any(subtask.dependencies for subtask in subtasks)
        
        # Check for time constraint
        time_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.TIME:
                time_constraint = constraint
                break
        
        # Determine workflow type
        if not has_dependencies:
            return 'parallel'
        elif time_constraint and isinstance(time_constraint.value, (int, float)):
            if time_constraint.value < 10:
                return 'parallel'  # Prefer parallel for tight deadlines
            else:
                return 'sequential'
        else:
            return 'sequential'
    
    def _determine_checkpoint_interval(self, subtasks: List[Subtask],
                                      constraints: List[Constraint]) -> int:
        """Determine checkpoint interval for progress tracking."""
        # Default: checkpoint after every subtask
        interval = 1
        
        # Check for quality constraint
        quality_constraint = None
        for constraint in constraints:
            if constraint.type == ConstraintType.QUALITY:
                quality_constraint = constraint
                break
        
        if quality_constraint:
            if quality_constraint.value == 'polished':
                interval = 1  # Checkpoint after every subtask for high quality
            elif quality_constraint.value == 'mvp':
                interval = max(2, len(subtasks) // 2)  # Fewer checkpoints for MVP
        
        return interval
    
    def _generate_task_id(self, task_description: str) -> str:
        """Generate a unique task ID."""
        # Simple hash-based ID generation
        import hashlib
        hash_obj = hashlib.md5(task_description.encode())
        return f"task_{hash_obj.hexdigest()[:8]}"
    
    def get_next_subtask(self, plan: ExecutionPlan) -> Optional[Subtask]:
        """
        Get the next subtask to execute based on dependencies and status.
        
        Args:
            plan: Execution plan
            
        Returns:
            Next subtask or None if no more subtasks
        """
        # Get completed subtask IDs
        completed_ids = {subtask.id for subtask in plan.subtasks 
                        if subtask.status == TaskStatus.COMPLETED}
        
        # Find pending subtasks with all dependencies satisfied
        for subtask in plan.subtasks:
            if subtask.status == TaskStatus.PENDING:
                dependencies_satisfied = all(
                    dep_id in completed_ids for dep_id in subtask.dependencies
                )
                if dependencies_satisfied:
                    return subtask
        
        return None
    
    def update_subtask_status(self, plan: ExecutionPlan, subtask_id: str,
                             status: TaskStatus) -> ExecutionPlan:
        """
        Update the status of a subtask.
        
        Args:
            plan: Execution plan
            subtask_id: ID of subtask to update
            status: New status
            
        Returns:
            Updated execution plan
        """
        for subtask in plan.subtasks:
            if subtask.id == subtask_id:
                subtask.status = status
                break
        
        return plan
    
    def get_progress(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Get progress information for an execution plan.
        
        Args:
            plan: Execution plan
            
        Returns:
            Progress information
        """
        total = len(plan.subtasks)
        completed = sum(1 for subtask in plan.subtasks 
                       if subtask.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for subtask in plan.subtasks 
                         if subtask.status == TaskStatus.IN_PROGRESS)
        failed = sum(1 for subtask in plan.subtasks 
                    if subtask.status == TaskStatus.FAILED)
        
        progress_percentage = (completed / total * 100) if total > 0 else 0
        
        return {
            'total_subtasks': total,
            'completed': completed,
            'in_progress': in_progress,
            'failed': failed,
            'progress_percentage': progress_percentage,
            'estimated_time_remaining': sum(
                subtask.estimated_time for subtask in plan.subtasks
                if subtask.status == TaskStatus.PENDING
            )
        }
    
    def should_checkpoint(self, plan: ExecutionPlan) -> bool:
        """
        Determine if a checkpoint should be created.
        
        Args:
            plan: Execution plan
            
        Returns:
            True if checkpoint should be created
        """
        progress = self.get_progress(plan)
        completed = progress['completed']
        
        return completed > 0 and completed % plan.checkpoint_interval == 0
    
    def get_failed_subtasks(self, plan: ExecutionPlan) -> List[Subtask]:
        """
        Get all failed subtasks.
        
        Args:
            plan: Execution plan
            
        Returns:
            List of failed subtasks
        """
        return [subtask for subtask in plan.subtasks 
                if subtask.status == TaskStatus.FAILED]
    
    def retry_failed_subtasks(self, plan: ExecutionPlan) -> ExecutionPlan:
        """
        Reset failed subtasks to pending for retry.
        
        Args:
            plan: Execution plan
            
        Returns:
            Updated execution plan
        """
        for subtask in plan.subtasks:
            if subtask.status == TaskStatus.FAILED:
                subtask.status = TaskStatus.PENDING
        
        return plan
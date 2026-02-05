"""
Progress Monitor - Tracks task completion, detects obstacles, and reports progress.

This component monitors the execution of tasks, identifies obstacles,
and provides progress reporting and alerts.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from .execution_planner import ExecutionPlan, Subtask, TaskStatus

logger = logging.getLogger(__name__)


class ObstacleType(Enum):
    """Types of obstacles that can occur"""
    TIMEOUT = "timeout"
    ERROR = "error"
    RESOURCE_LIMIT = "resource_limit"
    DEPENDENCY_FAILURE = "dependency_failure"
    QUALITY_ISSUE = "quality_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    UNKNOWN = "unknown"


class AlertLevel(Enum):
    """Severity levels for alerts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Obstacle:
    """An obstacle encountered during execution"""
    obstacle_type: ObstacleType
    description: str
    subtask_id: str
    timestamp: datetime
    severity: AlertLevel
    suggested_actions: List[str]
    context: Dict[str, Any]


@dataclass
class ProgressReport:
    """A progress report for task execution"""
    task_id: str
    timestamp: datetime
    progress_percentage: float
    completed_subtasks: int
    total_subtasks: int
    current_subtask: Optional[str]
    elapsed_time: float
    estimated_time_remaining: float
    obstacles: List[Obstacle]
    alerts: List[Dict[str, Any]]


class ProgressMonitor:
    """Tracks task completion, detects obstacles, and reports progress."""
    
    def __init__(self):
        """Initialize the progress monitor."""
        self.obstacles: List[Obstacle] = []
        self.alerts: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.last_update_time: Optional[datetime] = None
        
        # Obstacle detection thresholds
        self.timeout_threshold = 300  # 5 minutes
        self.error_threshold = 3  # Max errors before critical
        self.performance_threshold = 2.0  # 2x slower than expected
        
        # Progress tracking
        self.subtask_start_times: Dict[str, datetime] = {}
        self.subtask_durations: Dict[str, float] = {}
    
    def start_monitoring(self, plan: ExecutionPlan) -> None:
        """
        Start monitoring an execution plan.
        
        Args:
            plan: Execution plan to monitor
        """
        self.start_time = datetime.now()
        self.last_update_time = self.start_time
        self.obstacles = []
        self.alerts = []
        self.subtask_start_times = {}
        self.subtask_durations = {}
        
        logger.info(f"Started monitoring task {plan.task_id}")
    
    def update_progress(self, plan: ExecutionPlan, subtask_id: str,
                       status: TaskStatus, output: Optional[str] = None,
                       error: Optional[str] = None) -> ProgressReport:
        """
        Update progress based on subtask status.
        
        Args:
            plan: Execution plan
            subtask_id: ID of subtask being updated
            status: New status of subtask
            output: Optional output from subtask
            error: Optional error message
            
        Returns:
            Progress report
        """
        self.last_update_time = datetime.now()
        
        # Track subtask timing
        if status == TaskStatus.IN_PROGRESS:
            if subtask_id not in self.subtask_start_times:
                self.subtask_start_times[subtask_id] = datetime.now()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            if subtask_id in self.subtask_start_times:
                duration = (datetime.now() - self.subtask_start_times[subtask_id]).total_seconds()
                self.subtask_durations[subtask_id] = duration
                del self.subtask_start_times[subtask_id]
        
        # Detect obstacles
        if status == TaskStatus.FAILED and error:
            obstacle = self._detect_error_obstacle(subtask_id, error, plan)
            if obstacle:
                self.obstacles.append(obstacle)
                self._generate_alert(obstacle)
        
        # Check for performance issues
        if status == TaskStatus.COMPLETED:
            self._check_performance(subtask_id, plan)
        
        # Generate progress report
        report = self.generate_report(plan)
        
        logger.info(f"Updated progress for task {plan.task_id}: {report.progress_percentage:.1f}%")
        return report
    
    def _detect_error_obstacle(self, subtask_id: str, error: str,
                              plan: ExecutionPlan) -> Optional[Obstacle]:
        """
        Detect and categorize an error obstacle.
        
        Args:
            subtask_id: ID of subtask with error
            error: Error message
            plan: Execution plan
            
        Returns:
            Obstacle or None
        """
        error_lower = error.lower()
        
        # Determine obstacle type
        if 'timeout' in error_lower or 'timed out' in error_lower:
            obstacle_type = ObstacleType.TIMEOUT
        elif 'memory' in error_lower or 'resource' in error_lower:
            obstacle_type = ObstacleType.RESOURCE_LIMIT
        elif 'dependency' in error_lower:
            obstacle_type = ObstacleType.DEPENDENCY_FAILURE
        else:
            obstacle_type = ObstacleType.ERROR
        
        # Determine severity
        severity = AlertLevel.ERROR
        if obstacle_type == ObstacleType.TIMEOUT:
            severity = AlertLevel.WARNING
        elif obstacle_type == ObstacleType.RESOURCE_LIMIT:
            severity = AlertLevel.CRITICAL
        
        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(obstacle_type, error)
        
        # Get subtask
        subtask = next((s for s in plan.subtasks if s.id == subtask_id), None)
        
        return Obstacle(
            obstacle_type=obstacle_type,
            description=error,
            subtask_id=subtask_id,
            timestamp=datetime.now(),
            severity=severity,
            suggested_actions=suggested_actions,
            context={
                'subtask_description': subtask.description if subtask else 'Unknown',
                'model': subtask.required_model if subtask else 'Unknown'
            }
        )
    
    def _generate_suggested_actions(self, obstacle_type: ObstacleType,
                                   error: str) -> List[str]:
        """Generate suggested actions for an obstacle."""
        actions = []
        
        if obstacle_type == ObstacleType.TIMEOUT:
            actions.append("Increase timeout threshold")
            actions.append("Break task into smaller chunks")
            actions.append("Use a faster model")
        elif obstacle_type == ObstacleType.RESOURCE_LIMIT:
            actions.append("Reduce model size")
            actions.append("Free up system resources")
            actions.append("Process data in batches")
        elif obstacle_type == ObstacleType.DEPENDENCY_FAILURE:
            actions.append("Check dependency status")
            actions.append("Retry failed dependencies")
            actions.append("Consider alternative approach")
        elif obstacle_type == ObstacleType.ERROR:
            actions.append("Review error details")
            actions.append("Check input data")
            actions.append("Retry with modified parameters")
        
        return actions
    
    def _check_performance(self, subtask_id: str, plan: ExecutionPlan) -> None:
        """
        Check for performance issues in a completed subtask.
        
        Args:
            subtask_id: ID of completed subtask
            plan: Execution plan
        """
        if subtask_id not in self.subtask_durations:
            return
        
        actual_duration = self.subtask_durations[subtask_id]
        subtask = next((s for s in plan.subtasks if s.id == subtask_id), None)
        
        if not subtask:
            return
        
        expected_duration = subtask.estimated_time * 3600  # Convert hours to seconds
        
        if actual_duration > expected_duration * self.performance_threshold:
            # Performance issue detected
            obstacle = Obstacle(
                obstacle_type=ObstacleType.PERFORMANCE_ISSUE,
                description=f"Subtask took {actual_duration:.1f}s, expected {expected_duration:.1f}s",
                subtask_id=subtask_id,
                timestamp=datetime.now(),
                severity=AlertLevel.WARNING,
                suggested_actions=[
                    "Consider using a faster model",
                    "Optimize prompt complexity",
                    "Reduce output requirements"
                ],
                context={
                    'actual_duration': actual_duration,
                    'expected_duration': expected_duration,
                    'ratio': actual_duration / expected_duration
                }
            )
            self.obstacles.append(obstacle)
            self._generate_alert(obstacle)
    
    def _generate_alert(self, obstacle: Obstacle) -> None:
        """Generate an alert for an obstacle."""
        alert = {
            'level': obstacle.severity.value,
            'type': obstacle.obstacle_type.value,
            'message': obstacle.description,
            'subtask_id': obstacle.subtask_id,
            'timestamp': obstacle.timestamp.isoformat(),
            'suggested_actions': obstacle.suggested_actions
        }
        self.alerts.append(alert)
        
        logger.warning(f"Alert generated: {alert['level']} - {alert['message']}")
    
    def generate_report(self, plan: ExecutionPlan) -> ProgressReport:
        """
        Generate a progress report for an execution plan.
        
        Args:
            plan: Execution plan
            
        Returns:
            Progress report
        """
        # Calculate progress
        total_subtasks = len(plan.subtasks)
        completed_subtasks = sum(1 for s in plan.subtasks 
                                if s.status == TaskStatus.COMPLETED)
        progress_percentage = (completed_subtasks / total_subtasks * 100) if total_subtasks > 0 else 0
        
        # Find current subtask
        current_subtask = next((s.id for s in plan.subtasks 
                               if s.status == TaskStatus.IN_PROGRESS), None)
        
        # Calculate elapsed time
        elapsed_time = 0.0
        if self.start_time:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Estimate time remaining
        estimated_time_remaining = sum(
            s.estimated_time * 3600 for s in plan.subtasks
            if s.status == TaskStatus.PENDING
        )
        
        # Adjust based on actual performance
        if self.subtask_durations:
            avg_performance_ratio = sum(
                self.subtask_durations[sid] / (s.estimated_time * 3600)
                for sid, s in [(sid, next((st for st in plan.subtasks if st.id == sid), None))
                              for sid in self.subtask_durations]
                if s
            ) / len(self.subtask_durations)
            estimated_time_remaining *= avg_performance_ratio
        
        return ProgressReport(
            task_id=plan.task_id,
            timestamp=datetime.now(),
            progress_percentage=progress_percentage,
            completed_subtasks=completed_subtasks,
            total_subtasks=total_subtasks,
            current_subtask=current_subtask,
            elapsed_time=elapsed_time,
            estimated_time_remaining=estimated_time_remaining,
            obstacles=self.obstacles.copy(),
            alerts=self.alerts.copy()
        )
    
    def get_obstacles(self, severity: Optional[AlertLevel] = None) -> List[Obstacle]:
        """
        Get obstacles, optionally filtered by severity.
        
        Args:
            severity: Optional severity filter
            
        Returns:
            List of obstacles
        """
        if severity:
            return [o for o in self.obstacles if o.severity == severity]
        return self.obstacles.copy()
    
    def get_alerts(self, level: Optional[AlertLevel] = None) -> List[Dict[str, Any]]:
        """
        Get alerts, optionally filtered by level.
        
        Args:
            level: Optional alert level filter
            
        Returns:
            List of alerts
        """
        if level:
            return [a for a in self.alerts if a['level'] == level.value]
        return self.alerts.copy()
    
    def has_critical_obstacles(self) -> bool:
        """
        Check if there are any critical obstacles.
        
        Returns:
            True if critical obstacles exist
        """
        return any(o.severity == AlertLevel.CRITICAL for o in self.obstacles)
    
    def should_stop_execution(self) -> bool:
        """
        Determine if execution should be stopped due to obstacles.
        
        Returns:
            True if execution should stop
        """
        # Stop if there are critical obstacles
        if self.has_critical_obstacles():
            return True
        
        # Stop if too many errors
        error_count = sum(1 for o in self.obstacles 
                         if o.obstacle_type == ObstacleType.ERROR)
        if error_count >= self.error_threshold:
            return True
        
        return False
    
    def get_recovery_suggestions(self) -> List[str]:
        """
        Get suggestions for recovering from obstacles.
        
        Returns:
            List of recovery suggestions
        """
        suggestions = []
        
        # Group obstacles by type
        obstacle_types = {}
        for obstacle in self.obstacles:
            if obstacle.obstacle_type not in obstacle_types:
                obstacle_types[obstacle.obstacle_type] = []
            obstacle_types[obstacle.obstacle_type].append(obstacle)
        
        # Generate suggestions for each type
        for obstacle_type, obstacles in obstacle_types.items():
            if obstacle_type == ObstacleType.TIMEOUT:
                suggestions.append("Consider increasing timeout thresholds")
                suggestions.append("Break complex tasks into smaller subtasks")
            elif obstacle_type == ObstacleType.RESOURCE_LIMIT:
                suggestions.append("Reduce model size or batch size")
                suggestions.append("Free up system memory")
            elif obstacle_type == ObstacleType.ERROR:
                suggestions.append("Review error messages and adjust approach")
                suggestions.append("Check input data for issues")
            elif obstacle_type == ObstacleType.PERFORMANCE_ISSUE:
                suggestions.append("Optimize prompts for faster execution")
                suggestions.append("Consider using faster models for simple tasks")
        
        return suggestions
    
    def reset(self) -> None:
        """Reset the progress monitor."""
        self.obstacles = []
        self.alerts = []
        self.start_time = None
        self.last_update_time = None
        self.subtask_start_times = {}
        self.subtask_durations = {}
        
        logger.info("Progress monitor reset")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of monitoring state.
        
        Returns:
            Summary dictionary
        """
        return {
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'total_obstacles': len(self.obstacles),
            'total_alerts': len(self.alerts),
            'critical_obstacles': sum(1 for o in self.obstacles if o.severity == AlertLevel.CRITICAL),
            'error_obstacles': sum(1 for o in self.obstacles if o.obstacle_type == ObstacleType.ERROR),
            'performance_obstacles': sum(1 for o in self.obstacles if o.obstacle_type == ObstacleType.PERFORMANCE_ISSUE),
            'completed_subtasks': len(self.subtask_durations),
            'in_progress_subtasks': len(self.subtask_start_times)
        }
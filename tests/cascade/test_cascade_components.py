"""
Comprehensive test suite for Cascade components.

This script tests all 8 cascade components to ensure they work correctly.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cascade.ambiguity_detector import AmbiguityDetector, AmbiguityType
from cascade.clarification_engine import ClarificationEngine, DialogueState
from cascade.constraint_extractor import ConstraintExtractor, ConstraintType
from cascade.feasibility_validator import FeasibilityValidator, FeasibilityStatus
from cascade.path_generator import PathGenerator, PathType
from cascade.execution_planner import ExecutionPlanner, TaskStatus
from cascade.progress_monitor import ProgressMonitor, ObstacleType, AlertLevel
from cascade.prompt_adjuster import PromptAdjuster, AdjustmentType

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_ambiguity_detector():
    """Test the AmbiguityDetector component."""
    print_section("TEST 1: Ambiguity Detector")
    
    detector = AmbiguityDetector()
    
    # Test cases with different ambiguity types
    test_requests = [
        "Make it faster",  # Vague quantifier
        "Improve the code",  # Undefined term
        "Fix the bug in the file",  # Missing context
        "Update that function",  # Ambiguous reference
        "Refactor everything",  # Unclear scope
        "Make it look good",  # Subjective criteria
        "Create a few functions to handle the data efficiently"  # Multiple ambiguities
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"Test {i}: {request}")
        ambiguities = detector.detect(request)
        
        print(f"  Detected {len(ambiguities)} ambiguities:")
        for ambiguity in ambiguities:
            print(f"    - Type: {ambiguity.type.value}")
            print(f"      Text: '{ambiguity.text}'")
            print(f"      Confidence: {ambiguity.confidence:.2f}")
            print(f"      Interpretations: {len(ambiguity.interpretations)}")
        print()
    
    print("✅ Ambiguity Detector test completed\n")


def test_clarification_engine():
    """Test the ClarificationEngine component."""
    print_section("TEST 2: Clarification Engine")
    
    detector = AmbiguityDetector()
    engine = ClarificationEngine(verbosity="normal")
    
    # Detect ambiguities
    request = "Make the code faster and better"
    ambiguities = detector.detect(request)
    
    print(f"Original request: {request}")
    print(f"Detected {len(ambiguities)} ambiguities\n")
    
    # Start clarification session
    session = engine.start_session(ambiguities)
    print(f"Started session: {session.session_id}")
    print(f"Session state: {session.state.value}\n")
    
    # Process each ambiguity
    while True:
        ambiguity = engine.get_next_ambiguity(session)
        if not ambiguity:
            break
        
        print(f"Clarifying: {ambiguity.text}")
        choices = engine.generate_choices(ambiguity)
        
        # Format and display choices
        formatted = engine.format_choices(choices, ambiguity)
        print(formatted)
        
        # Simulate user selection (select first non-skip choice)
        selected_choice = choices[0]
        print(f"Simulated selection: {selected_choice.text}")
        
        # Process choice
        engine.process_choice(session, selected_choice.id, "optimize algorithms")
        print(f"Session state: {session.state.value}\n")
    
    # Get session summary
    summary = engine.get_session_summary(session)
    print("Session Summary:")
    print(f"  Total ambiguities: {summary['total_ambiguities']}")
    print(f"  Clarified: {summary['clarified']}")
    print(f"  Skipped: {summary['skipped']}")
    print(f"  Completed: {summary['completed']}\n")
    
    # Apply clarifications
    clarified = engine.apply_clarifications(request, session)
    print(f"Original: {request}")
    print(f"Clarified: {clarified}\n")
    
    print("✅ Clarification Engine test completed\n")


def test_constraint_extractor():
    """Test the ConstraintExtractor component."""
    print_section("TEST 3: Constraint Extractor")
    
    extractor = ConstraintExtractor()
    
    # Test cases with different constraints
    test_requests = [
        "Complete this in 2 hours",
        "I have a budget of $100",
        "I'm a beginner programmer",
        "This is a simple task",
        "Keep it minimal scope",
        "Production quality required",
        "Make it maintainable for the long term",
        "Complete in 4 hours with high quality, I'm an intermediate developer"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"Test {i}: {request}")
        constraints = extractor.extract(request)
        
        print(f"  Extracted {len(constraints)} constraints:")
        for constraint in constraints:
            print(f"    - Type: {constraint.type.value}")
            print(f"      Value: {constraint.value}")
            print(f"      Description: {constraint.description}")
        
        # Validate constraints
        validation = extractor.validate_constraints(constraints)
        print(f"  Validation: {'Valid' if validation['valid'] else 'Invalid'}")
        if validation['conflicts']:
            print(f"  Conflicts: {validation['conflicts']}")
        if validation['suggestions']:
            print(f"  Suggestions: {validation['suggestions']}")
        print()
    
    print("✅ Constraint Extractor test completed\n")


def test_feasibility_validator():
    """Test the FeasibilityValidator component."""
    print_section("TEST 4: Feasibility Validator")
    
    extractor = ConstraintExtractor()
    validator = FeasibilityValidator()
    
    # Test task with constraints
    task_description = "Build a REST API with authentication"
    request = "Complete in 8 hours, production quality, I'm an intermediate developer"
    
    print(f"Task: {task_description}")
    print(f"Constraints: {request}\n")
    
    # Extract constraints
    constraints = extractor.extract(request)
    print(f"Extracted {len(constraints)} constraints:")
    for constraint in constraints:
        print(f"  - {constraint.type.value}: {constraint.value}")
    print()
    
    # Validate feasibility
    result = validator.validate(task_description, constraints)
    
    print("Feasibility Result:")
    print(f"  Status: {result.status.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reasons: {result.reasons}")
    
    if result.blockers:
        print(f"  Blockers:")
        for blocker in result.blockers:
            print(f"    - {blocker}")
    
    if result.alternatives:
        print(f"  Alternatives:")
        for i, alt in enumerate(result.alternatives[:3], 1):
            print(f"    {i}. {alt}")
    
    if result.suggestions:
        print(f"  Suggestions:")
        for i, suggestion in enumerate(result.suggestions[:3], 1):
            print(f"    {i}. {suggestion}")
    
    print()
    print("✅ Feasibility Validator test completed\n")


def test_path_generator():
    """Test the PathGenerator component."""
    print_section("TEST 5: Path Generator")
    
    extractor = ConstraintExtractor()
    validator = FeasibilityValidator()
    generator = PathGenerator()
    
    # Test task
    task_description = "Develop a web application with user authentication"
    request = "Complete in 16 hours, moderate complexity, standard scope"
    
    print(f"Task: {task_description}")
    print(f"Constraints: {request}\n")
    
    # Extract constraints
    constraints = extractor.extract(request)
    
    # Validate feasibility
    feasibility = validator.validate(task_description, constraints)
    
    # Generate paths
    paths = generator.generate_paths(task_description, constraints, feasibility)
    
    print(f"Generated {len(paths)} execution paths:\n")
    
    for i, path in enumerate(paths, 1):
        print(f"Path {i}: {path.path_type.value.upper()}")
        print(f"  Description: {path.description}")
        print(f"  Estimated time: {path.estimated_time:.1f} hours")
        print(f"  Estimated cost: {path.estimated_cost:.1f}")
        print(f"  Confidence: {path.confidence:.2f}")
        print(f"  Steps ({len(path.steps)}):")
        for j, step in enumerate(path.steps, 1):
            print(f"    {j}. {step}")
        print(f"  Required skills: {', '.join(path.required_skills)}")
        print(f"  Pros: {', '.join(path.pros[:2])}")
        print(f"  Cons: {', '.join(path.cons[:2])}")
        print()
    
    # Rank paths
    ranked = generator.rank_paths(paths, constraints)
    print(f"Best path: {ranked[0].path_type.value}")
    print(f"  Score: {generator._score_path(ranked[0], constraints):.2f}\n")
    
    print("✅ Path Generator test completed\n")


def test_execution_planner():
    """Test the ExecutionPlanner component."""
    print_section("TEST 6: Execution Planner")
    
    extractor = ConstraintExtractor()
    planner = ExecutionPlanner()
    
    # Test task
    task_description = "Create a Python script to process CSV files"
    request = "Complete in 6 hours, simple task, minimal scope"
    
    print(f"Task: {task_description}")
    print(f"Constraints: {request}\n")
    
    # Extract constraints
    constraints = extractor.extract(request)
    
    # Create execution plan
    plan = planner.create_plan(task_description, constraints)
    
    print(f"Execution Plan: {plan.task_id}")
    print(f"  Task: {plan.task_description}")
    print(f"  Total estimated time: {plan.total_estimated_time:.1f} hours")
    print(f"  Workflow type: {plan.workflow_type}")
    print(f"  Parallelizable: {plan.parallelizable}")
    print(f"  Checkpoint interval: {plan.checkpoint_interval}")
    print(f"\n  Subtasks ({len(plan.subtasks)}):")
    
    for i, subtask in enumerate(plan.subtasks, 1):
        print(f"    {i}. {subtask.id}: {subtask.description}")
        print(f"       Status: {subtask.status.value}")
        print(f"       Priority: {subtask.priority.value}")
        print(f"       Estimated time: {subtask.estimated_time:.1f} hours")
        print(f"       Model: {subtask.required_model}")
        print(f"       Dependencies: {subtask.dependencies}")
        print()
    
    # Test getting next subtask
    next_subtask = planner.get_next_subtask(plan)
    if next_subtask:
        print(f"Next subtask to execute: {next_subtask.id}")
        print(f"  Description: {next_subtask.description}\n")
    
    # Test progress tracking
    progress = planner.get_progress(plan)
    print("Progress:")
    print(f"  Total: {progress['total_subtasks']}")
    print(f"  Completed: {progress['completed']}")
    print(f"  In progress: {progress['in_progress']}")
    print(f"  Progress: {progress['progress_percentage']:.1f}%")
    print(f"  Estimated time remaining: {progress['estimated_time_remaining']:.1f} hours\n")
    
    print("✅ Execution Planner test completed\n")


def test_progress_monitor():
    """Test the ProgressMonitor component."""
    print_section("TEST 7: Progress Monitor")
    
    extractor = ConstraintExtractor()
    planner = ExecutionPlanner()
    monitor = ProgressMonitor()
    
    # Create a simple plan
    task_description = "Write a Python function"
    request = "Complete in 2 hours"
    constraints = extractor.extract(request)
    plan = planner.create_plan(task_description, constraints)
    
    print(f"Monitoring task: {plan.task_id}\n")
    
    # Start monitoring
    monitor.start_monitoring(plan)
    print("Started monitoring\n")
    
    # Simulate progress updates
    for i, subtask in enumerate(plan.subtasks[:3], 1):
        print(f"Updating subtask {i}: {subtask.description}")
        
        # Mark as in progress
        plan = planner.update_subtask_status(plan, subtask.id, TaskStatus.IN_PROGRESS)
        report = monitor.update_progress(plan, subtask.id, TaskStatus.IN_PROGRESS)
        print(f"  Progress: {report.progress_percentage:.1f}%")
        
        # Mark as completed
        plan = planner.update_subtask_status(plan, subtask.id, TaskStatus.COMPLETED)
        report = monitor.update_progress(plan, subtask.id, TaskStatus.COMPLETED)
        print(f"  Progress: {report.progress_percentage:.1f}%")
        print(f"  Elapsed time: {report.elapsed_time:.1f}s")
        print()
    
    # Simulate an error
    if len(plan.subtasks) > 3:
        error_subtask = plan.subtasks[3]
        print(f"Simulating error in subtask: {error_subtask.description}")
        plan = planner.update_subtask_status(plan, error_subtask.id, TaskStatus.FAILED)
        report = monitor.update_progress(
            plan, error_subtask.id, TaskStatus.FAILED,
            error="Timeout: Request took too long to complete"
        )
        print(f"  Progress: {report.progress_percentage:.1f}%")
        print(f"  Obstacles detected: {len(report.obstacles)}")
        
        if report.obstacles:
            obstacle = report.obstacles[0]
            print(f"  Obstacle type: {obstacle.obstacle_type.value}")
            print(f"  Severity: {obstacle.severity.value}")
            print(f"  Suggested actions: {obstacle.suggested_actions}")
        print()
    
    # Get final report
    final_report = monitor.generate_report(plan)
    print("Final Report:")
    print(f"  Progress: {final_report.progress_percentage:.1f}%")
    print(f"  Completed: {final_report.completed_subtasks}/{final_report.total_subtasks}")
    print(f"  Elapsed time: {final_report.elapsed_time:.1f}s")
    print(f"  Total obstacles: {len(final_report.obstacles)}")
    print(f"  Total alerts: {len(final_report.alerts)}\n")
    
    # Check if should stop
    should_stop = monitor.should_stop_execution()
    print(f"Should stop execution: {should_stop}\n")
    
    # Get recovery suggestions
    suggestions = monitor.get_recovery_suggestions()
    if suggestions:
        print("Recovery suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        print()
    
    print("✅ Progress Monitor test completed\n")


def test_prompt_adjuster():
    """Test the PromptAdjuster component."""
    print_section("TEST 8: Prompt Adjuster")
    
    extractor = ConstraintExtractor()
    planner = ExecutionPlanner()
    adjuster = PromptAdjuster()
    
    # Create a plan
    task_description = "Analyze the dataset"
    request = "Complete in 4 hours"
    constraints = extractor.extract(request)
    plan = planner.create_plan(task_description, constraints)
    
    # Get a subtask
    subtask = plan.subtasks[0]
    print(f"Subtask: {subtask.description}")
    print(f"Original prompt length: {len(subtask.prompt)} characters\n")
    
    # Create an obstacle
    from cascade.progress_monitor import Obstacle, AlertLevel
    obstacle = Obstacle(
        obstacle_type=ObstacleType.TIMEOUT,
        description="Request timed out after 60 seconds",
        subtask_id=subtask.id,
        timestamp=None,
        severity=AlertLevel.WARNING,
        suggested_actions=[],
        context={}
    )
    
    print(f"Obstacle: {obstacle.obstacle_type.value}")
    print(f"Description: {obstacle.description}\n")
    
    # Analyze obstacle and generate adjustments
    adjustments = adjuster.analyze_obstacle(obstacle, subtask)
    
    print(f"Generated {len(adjustments)} prompt adjustments:\n")
    
    for i, adjustment in enumerate(adjustments, 1):
        print(f"Adjustment {i}: {adjustment.adjustment_type.value}")
        print(f"  Reason: {adjustment.reason}")
        print(f"  Expected improvement: {adjustment.expected_improvement}")
        print(f"  Confidence: {adjustment.confidence:.2f}")
        print(f"  Original prompt length: {len(adjustment.original_prompt)}")
        print(f"  Adjusted prompt length: {len(adjustment.adjusted_prompt)}")
        print(f"  Reduction: {(1 - len(adjustment.adjusted_prompt) / len(adjustment.original_prompt)) * 100:.1f}%")
        print()
    
    # Select best adjustment
    best = adjuster.select_best_adjustment(adjustments)
    if best:
        print(f"Best adjustment: {best.adjustment_type.value}")
        print(f"  Confidence: {best.confidence:.2f}\n")
    
    # Generate alternative prompts
    alternatives = adjuster.generate_alternative_prompts(subtask, num_alternatives=3)
    print(f"Generated {len(alternatives)} alternative prompts:\n")
    
    for i, alt in enumerate(alternatives, 1):
        print(f"Alternative {i}:")
        print(f"  Length: {len(alt)} characters")
        print(f"  Preview: {alt[:100]}...")
        print()
    
    print("✅ Prompt Adjuster test completed\n")


def test_integration():
    """Test integration of all cascade components."""
    print_section("TEST 9: Integration Test")
    
    # Initialize all components
    detector = AmbiguityDetector()
    engine = ClarificationEngine(verbosity="minimal")
    extractor = ConstraintExtractor()
    validator = FeasibilityValidator()
    generator = PathGenerator()
    planner = ExecutionPlanner()
    monitor = ProgressMonitor()
    adjuster = PromptAdjuster()
    
    # Test request
    request = "Make the code faster and better, complete in 8 hours with high quality"
    task_description = "Optimize the existing codebase"
    
    print(f"Original request: {request}\n")
    
    # Step 1: Detect ambiguities
    print("Step 1: Detecting ambiguities...")
    ambiguities = detector.detect(request)
    print(f"  Found {len(ambiguities)} ambiguities\n")
    
    # Step 2: Clarify ambiguities (simulate)
    print("Step 2: Clarifying ambiguities...")
    if ambiguities:
        session = engine.start_session(ambiguities)
        # Simulate user skipping all ambiguities for this test
        for ambiguity in session.ambiguities:
            engine.process_choice(session, "skip")
        clarified_request = engine.apply_clarifications(request, session)
        print(f"  Clarified request: {clarified_request}\n")
    else:
        clarified_request = request
        print("  No ambiguities to clarify\n")
    
    # Step 3: Extract constraints
    print("Step 3: Extracting constraints...")
    constraints = extractor.extract(request)
    print(f"  Extracted {len(constraints)} constraints:")
    for constraint in constraints:
        print(f"    - {constraint.type.value}: {constraint.value}")
    print()
    
    # Step 4: Validate feasibility
    print("Step 4: Validating feasibility...")
    feasibility = validator.validate(task_description, constraints)
    print(f"  Status: {feasibility.status.value}")
    print(f"  Confidence: {feasibility.confidence:.2f}\n")
    
    # Step 5: Generate execution paths
    print("Step 5: Generating execution paths...")
    paths = generator.generate_paths(task_description, constraints, feasibility)
    print(f"  Generated {len(paths)} paths")
    best_path = generator.select_best_path(paths, constraints)
    if best_path:
        print(f"  Best path: {best_path.path_type.value} ({best_path.description})\n")
    
    # Step 6: Create execution plan
    print("Step 6: Creating execution plan...")
    plan = planner.create_plan(task_description, constraints, best_path)
    print(f"  Plan ID: {plan.task_id}")
    print(f"  Subtasks: {len(plan.subtasks)}")
    print(f"  Estimated time: {plan.total_estimated_time:.1f} hours\n")
    
    # Step 7: Start monitoring
    print("Step 7: Starting progress monitoring...")
    monitor.start_monitoring(plan)
    print("  Monitoring started\n")
    
    # Step 8: Simulate execution
    print("Step 8: Simulating execution...")
    completed = 0
    for subtask in plan.subtasks[:3]:  # Simulate first 3 subtasks
        print(f"  Executing: {subtask.description}")
        
        # Mark as in progress
        plan = planner.update_subtask_status(plan, subtask.id, TaskStatus.IN_PROGRESS)
        monitor.update_progress(plan, subtask.id, TaskStatus.IN_PROGRESS)
        
        # Mark as completed
        plan = planner.update_subtask_status(plan, subtask.id, TaskStatus.COMPLETED)
        report = monitor.update_progress(plan, subtask.id, TaskStatus.COMPLETED)
        completed += 1
        
        print(f"    Completed ({completed}/{len(plan.subtasks)})")
    
    print()
    
    # Step 9: Get final progress
    print("Step 9: Getting final progress...")
    final_report = monitor.generate_report(plan)
    print(f"  Progress: {final_report.progress_percentage:.1f}%")
    print(f"  Completed: {final_report.completed_subtasks}/{final_report.total_subtasks}")
    print(f"  Elapsed time: {final_report.elapsed_time:.1f}s\n")
    
    # Step 10: Simulate obstacle and adjustment
    print("Step 10: Simulating obstacle and prompt adjustment...")
    if len(plan.subtasks) > 3:
        next_subtask = plan.subtasks[3]
        from cascade.progress_monitor import Obstacle, AlertLevel
        obstacle = Obstacle(
            obstacle_type=ObstacleType.TIMEOUT,
            description="Subtask timed out",
            subtask_id=next_subtask.id,
            timestamp=None,
            severity=AlertLevel.WARNING,
            suggested_actions=[],
            context={}
        )
        
        adjustments = adjuster.analyze_obstacle(obstacle, next_subtask)
        print(f"  Generated {len(adjustments)} adjustments")
        if adjustments:
            best = adjuster.select_best_adjustment(adjustments)
            print(f"  Best adjustment: {best.adjustment_type.value}\n")
    
    print("✅ Integration test completed successfully\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  CASCADE COMPONENTS TEST SUITE")
    print("=" * 70)
    
    try:
        # Run individual component tests
        test_ambiguity_detector()
        test_clarification_engine()
        test_constraint_extractor()
        test_feasibility_validator()
        test_path_generator()
        test_execution_planner()
        test_progress_monitor()
        test_prompt_adjuster()
        
        # Run integration test
        test_integration()
        
        # Final summary
        print_section("TEST SUMMARY")
        print("✅ All tests completed successfully!")
        print("\nComponents tested:")
        print("  1. AmbiguityDetector - Detects ambiguities in user requests")
        print("  2. ClarificationEngine - Manages clarification dialogues")
        print("  3. ConstraintExtractor - Extracts user constraints")
        print("  4. FeasibilityValidator - Validates task feasibility")
        print("  5. PathGenerator - Generates execution paths")
        print("  6. ExecutionPlanner - Creates execution plans")
        print("  7. ProgressMonitor - Tracks progress and detects obstacles")
        print("  8. PromptAdjuster - Adjusts prompts based on obstacles")
        print("  9. Integration - End-to-end workflow test")
        print("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
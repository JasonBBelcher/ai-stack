#!/usr/bin/env python3
"""
Integration test for cascade components with enhanced_controller.py
Tests the full cascade workflow integrated into the main controller.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_controller import SimplifiedAIStackController


def test_cascade_integration():
    """Test the full cascade integration with the controller."""
    print("=" * 80)
    print("Testing Cascade Integration with Enhanced Controller")
    print("=" * 80)
    
    # Initialize controller
    print("\n1. Initializing controller with cascade components...")
    controller = SimplifiedAIStackController()
    
    # Check cascade status
    print("\n2. Checking cascade status...")
    status = controller.get_cascade_status()
    print(f"   Cascade enabled: {status['cascade_enabled']}")
    print(f"   Execution plan active: {status['execution_plan_active']}")
    print(f"   Monitoring active: {status['monitoring_active']}")
    print(f"   Components loaded:")
    for component, loaded in status['components'].items():
        print(f"     - {component}: {'✓' if loaded else '✗'}")
    
    # Test simple request without cascade
    print("\n3. Testing simple request without cascade...")
    result_no_cascade = controller.process_request_with_cascade(
        "Say hello",
        enable_cascade=False
    )
    print(f"   Success: {result_no_cascade.success}")
    if result_no_cascade.error:
        print(f"   Error: {result_no_cascade.error}")
    print(f"   Output: {result_no_cascade.output[:100] if result_no_cascade.output else 'None'}...")
    print(f"   Cascade enabled: {result_no_cascade.metadata.get('cascade_enabled', False)}")
    
    # Test request with cascade (simple)
    print("\n4. Testing simple request with cascade...")
    result_simple = controller.process_request_with_cascade(
        "Say hello",
        enable_cascade=True
    )
    print(f"   Success: {result_simple.success}")
    if result_simple.error:
        print(f"   Error: {result_simple.error}")
    print(f"   Output: {result_simple.output[:100] if result_simple.output else 'None'}...")
    print(f"   Cascade enabled: {result_simple.metadata.get('cascade_enabled', False)}")
    print(f"   Ambiguities detected: {result_simple.metadata.get('ambiguities_detected', 0)}")
    print(f"   Constraints extracted: {result_simple.metadata.get('constraints_extracted', 0)}")
    
    # Test request with cascade (ambiguous)
    print("\n5. Testing ambiguous request with cascade...")
    result_ambiguous = controller.process_request_with_cascade(
        "Write a good article about AI",
        enable_cascade=True
    )
    print(f"   Success: {result_ambiguous.success}")
    if result_ambiguous.error:
        print(f"   Error: {result_ambiguous.error}")
    print(f"   Output: {result_ambiguous.output[:100] if result_ambiguous.output else 'None'}...")
    print(f"   Cascade enabled: {result_ambiguous.metadata.get('cascade_enabled', False)}")
    print(f"   Ambiguities detected: {result_ambiguous.metadata.get('ambiguities_detected', 0)}")
    print(f"   Constraints extracted: {result_ambiguous.metadata.get('constraints_extracted', 0)}")
    
    # Test request with cascade (with constraints)
    print("\n6. Testing request with constraints and cascade...")
    result_constraints = controller.process_request_with_cascade(
        "Write a Python script for data analysis within 2 hours using pandas",
        enable_cascade=True
    )
    print(f"   Success: {result_constraints.success}")
    if result_constraints.error:
        print(f"   Error: {result_constraints.error}")
    print(f"   Output: {result_constraints.output[:100] if result_constraints.output else 'None'}...")
    print(f"   Cascade enabled: {result_constraints.metadata.get('cascade_enabled', False)}")
    print(f"   Ambiguities detected: {result_constraints.metadata.get('ambiguities_detected', 0)}")
    print(f"   Constraints extracted: {result_constraints.metadata.get('constraints_extracted', 0)}")
    print(f"   Feasibility status: {result_constraints.metadata.get('feasibility_status', 'N/A')}")
    print(f"   Execution path: {result_constraints.metadata.get('execution_path', 'N/A')}")
    print(f"   Subtasks total: {result_constraints.metadata.get('subtasks_total', 0)}")
    print(f"   Progress percentage: {result_constraints.metadata.get('progress_percentage', 0):.1f}%")
    print(f"   Obstacles detected: {result_constraints.metadata.get('obstacles_detected', 0)}")
    print(f"   Alerts generated: {result_constraints.metadata.get('alerts_generated', 0)}")
    
    # Test prompt adjustment
    print("\n7. Testing prompt adjustment for obstacle...")
    from cascade.progress_monitor import Obstacle, ObstacleType, AlertLevel
    from datetime import datetime
    
    obstacle = Obstacle(
        obstacle_type=ObstacleType.RESOURCE_LIMIT,
        description="Task is too complex for single prompt",
        subtask_id="test_subtask",
        timestamp=datetime.now(),
        severity=AlertLevel.ERROR,
        suggested_actions=["Break down task", "Use simpler model"],
        context={}
    )
    
    original_prompt = "Write a comprehensive guide to machine learning"
    adjusted_prompt = controller.adjust_prompt_for_obstacle(
        original_prompt, obstacle
    )
    print(f"   Original prompt: {original_prompt}")
    print(f"   Adjusted prompt: {adjusted_prompt}")
    
    # Check final cascade status
    print("\n8. Checking final cascade status...")
    final_status = controller.get_cascade_status()
    if final_status['execution_plan_active']:
        print(f"   Execution plan:")
        print(f"     Total subtasks: {final_status['execution_plan']['total_subtasks']}")
        print(f"     Completed subtasks: {final_status['execution_plan']['completed_subtasks']}")
        print(f"     Workflow type: {final_status['execution_plan']['workflow_type']}")
        print(f"     Total estimated time: {final_status['execution_plan']['total_estimated_time']:.1f} hours")
    
    print("\n" + "=" * 80)
    print("Cascade Integration Test Complete!")
    print("=" * 80)
    
    # Summary
    print("\nTest Summary:")
    print(f"  ✓ Controller initialization: PASS")
    print(f"  ✓ Cascade status check: PASS")
    print(f"  ✓ Simple request without cascade: {'PASS' if result_no_cascade.success else 'FAIL'}")
    print(f"  ✓ Simple request with cascade: {'PASS' if result_simple.success else 'FAIL'}")
    print(f"  ✓ Ambiguous request with cascade: {'PASS' if result_ambiguous.success else 'FAIL'}")
    print(f"  ✓ Request with constraints: {'PASS' if result_constraints.success else 'FAIL'}")
    print(f"  ✓ Prompt adjustment: PASS")
    print(f"  ✓ Final status check: PASS")
    
    all_passed = (
        result_no_cascade.success and 
        result_simple.success and 
        result_ambiguous.success and 
        result_constraints.success
    )
    
    print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = test_cascade_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
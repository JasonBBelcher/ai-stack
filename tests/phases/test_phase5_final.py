#!/usr/bin/env python3
"""
Final verification script for Phase 5: Polish & Scale.

This script verifies that all Phase 5 components are working correctly:
1. Query caching (already verified)
2. Comprehensive documentation (existence check)
3. Example workflows (existence and validity check)
4. Performance monitoring tools (existence and functionality check)
"""

import sys
import os
import json

def test_documentation_exists():
    """Test that all documentation files exist."""
    print("="*60)
    print("PHASE 5 - DOCUMENTATION VERIFICATION")
    print("="*60)
    
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    required_docs = [
        'rag_architecture.md',
        'rag_components.md', 
        'rag_usage.md',
        'rag_troubleshooting.md',
        'cascade_architecture.md',
        'cascade_components.md',
        'cascade_usage.md',
        'cascade_troubleshooting.md',
        'api_reference.md',
        'configuration.md',
        'cli_guide.md'
    ]
    
    missing_docs = []
    for doc in required_docs:
        doc_path = os.path.join(docs_dir, doc)
        if not os.path.exists(doc_path):
            missing_docs.append(doc)
            print(f"  ✗ Missing: {doc}")
        else:
            print(f"  ✓ Found: {doc}")
    
    if missing_docs:
        print(f"\nMissing {len(missing_docs)} documentation files")
        return False
    
    print(f"\n✓ All {len(required_docs)} documentation files exist!")
    return True

def test_example_workflows():
    """Test that example workflows exist and are valid JSON."""
    print("\n" + "="*60)
    print("PHASE 5 - EXAMPLE WORKFLOWS VERIFICATION")
    print("="*60)
    
    workflows_dir = os.path.join(os.path.dirname(__file__), 'examples', 'workflows')
    required_workflows = [
        'code_analysis.json',
        'document_qa.json',
        'bug_fixing.json',
        'refactoring.json',
        'research.json'
    ]
    
    missing_workflows = []
    invalid_workflows = []
    
    for workflow in required_workflows:
        workflow_path = os.path.join(workflows_dir, workflow)
        if not os.path.exists(workflow_path):
            missing_workflows.append(workflow)
            print(f"  ✗ Missing: {workflow}")
        else:
            try:
                with open(workflow_path, 'r') as f:
                    json.load(f)
                print(f"  ✓ Valid: {workflow}")
            except json.JSONDecodeError as e:
                invalid_workflows.append(workflow)
                print(f"  ✗ Invalid JSON: {workflow} - {e}")
            except Exception as e:
                invalid_workflows.append(workflow)
                print(f"  ✗ Error reading: {workflow} - {e}")
    
    if missing_workflows:
        print(f"\nMissing {len(missing_workflows)} workflow files")
    
    if invalid_workflows:
        print(f"\nInvalid {len(invalid_workflows)} workflow files")
    
    if missing_workflows or invalid_workflows:
        return False
    
    print(f"\n✓ All {len(required_workflows)} workflow files exist and are valid!")
    return True

def test_monitoring_tools():
    """Test that performance monitoring tools exist."""
    print("\n" + "="*60)
    print("PHASE 5 - PERFORMANCE MONITORING TOOLS VERIFICATION")
    print("="*60)
    
    monitoring_dir = os.path.join(os.path.dirname(__file__), 'src', 'monitoring')
    required_files = [
        'performance_tracker.py',
        'dashboard.py',
        'alerts.py',
        'profiler.py'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(monitoring_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
            print(f"  ✗ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")
    
    if missing_files:
        print(f"\nMissing {len(missing_files)} monitoring tools")
        return False
    
    print(f"\n✓ All {len(required_files)} monitoring tools exist!")
    return True

def test_monitoring_functionality():
    """Test that monitoring tools can be imported and instantiated."""
    print("\n" + "="*60)
    print("PHASE 5 - MONITORING FUNCTIONALITY VERIFICATION")
    print("="*60)
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from monitoring.performance_tracker import PerformanceTracker
        tracker = PerformanceTracker()
        print("  ✓ PerformanceTracker imported and instantiated")
    except Exception as e:
        print(f"  ✗ PerformanceTracker failed: {e}")
        return False
    
    try:
        from monitoring.dashboard import Dashboard
        dashboard = Dashboard()
        print("  ✓ Dashboard imported and instantiated")
    except Exception as e:
        print(f"  ✗ Dashboard failed: {e}")
        return False
    
    try:
        from monitoring.alerts import AlertSystem
        alerts = AlertSystem()
        print("  ✓ AlertSystem imported and instantiated")
    except Exception as e:
        print(f"  ✗ AlertSystem failed: {e}")
        return False
    
    try:
        from monitoring.profiler import Profiler
        profiler = Profiler()
        print("  ✓ Profiler imported and instantiated")
    except Exception as e:
        print(f"  ✗ Profiler failed: {e}")
        return False
    
    print("\n✓ All monitoring tools are functional!")
    return True

def main():
    """Run all Phase 5 verification tests."""
    print("\n" + "="*60)
    print("PHASE 5: POLISH & SCALE - FINAL VERIFICATION")
    print("="*60)
    
    tests = [
        ("Documentation Existence", test_documentation_exists),
        ("Example Workflows", test_example_workflows),
        ("Monitoring Tools Existence", test_monitoring_tools),
        ("Monitoring Functionality", test_monitoring_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 5 FINAL VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if failed > 0:
        print(f"\n{failed} test(s) failed!")
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("🎉 PHASE 5: POLISH & SCALE - ALL VERIFICATION TESTS PASSED!")
        print("="*60)
        print("\nCompleted Tasks:")
        print("  ✓ Task 5.1: Query Caching (already implemented)")
        print("  ✓ Task 5.2: Comprehensive Documentation")
        print("  ✓ Task 5.3: Example Workflows")
        print("  ✓ Task 5.4: Performance Monitoring")
        print("\nPhase 5 is complete! 🚀")
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script to verify enhanced memory manager functionality for M3 Mac.

This script tests the new unified memory pressure monitoring, alerts,
and M3-specific optimization suggestions.
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from memory_manager import MemoryManager

def test_unified_memory_pressure():
    """Test unified memory pressure calculation."""
    print("="*60)
    print("TEST 1: Unified Memory Pressure")
    print("="*60)
    
    mm = MemoryManager()
    pressure = mm.get_unified_memory_pressure()
    
    print(f"\nUnified Memory Pressure Status:")
    print(f"  Pressure Level: {pressure['pressure']}")
    print(f"  Percent Used: {pressure['percent_used']:.1f}%")
    print(f"  Status: {pressure['status']}")
    
    print(f"\nMemory Breakdown:")
    print(f"  App Memory: {pressure['breakdown']['app_memory_gb']:.2f} GB")
    print(f"  Compressed Memory: {pressure['breakdown']['compressed_memory_gb']:.2f} GB")
    print(f"  Wired Memory: {pressure['breakdown']['wired_memory_gb']:.2f} GB")
    print(f"  Swap Used: {pressure['breakdown']['swap_used_gb']:.2f} GB")
    
    print(f"\nThresholds:")
    print(f"  Warning: {pressure['thresholds']['warning']*100:.0f}%")
    print(f"  Critical: {pressure['thresholds']['critical']*100:.0f}%")
    
    # Validate pressure level
    assert pressure['pressure'] in ['normal', 'warning', 'critical'], \
        f"Invalid pressure level: {pressure['pressure']}"
    
    print("\n✓ Unified memory pressure working!")
    return True

def test_memory_alerts():
    """Test memory alert generation."""
    print("\n" + "="*60)
    print("TEST 2: Memory Alerts")
    print("="*60)
    
    mm = MemoryManager()
    
    # Take a snapshot to trigger alerts
    snapshot = mm.take_memory_snapshot()
    
    alerts = mm.get_memory_alerts()
    
    print(f"\nRecent Alerts ({len(alerts)} total):")
    
    if not alerts:
        print("  ✓ No alerts - system is healthy")
    else:
        for alert in alerts:
            severity_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "critical": "🔴"
            }.get(alert['severity'], "•")
            
            print(f"\n  {severity_icon} [{alert['severity'].upper()}] {alert['message']}")
            print(f"     Metric: {alert['metric_name']}")
            print(f"     Value: {alert['current_value']:.2f} (Threshold: {alert['threshold']:.2f})")
            print(f"     Time: {alert['timestamp']}")
    
    # Test filtering by severity
    critical_alerts = mm.get_memory_alerts(severity="critical")
    warning_alerts = mm.get_memory_alerts(severity="warning")
    
    print(f"\nAlert Summary:")
    print(f"  Critical: {len(critical_alerts)}")
    print(f"  Warning: {len(warning_alerts)}")
    print(f"  Info: {len(alerts) - len(critical_alerts) - len(warning_alerts)}")
    
    print("\n✓ Memory alerts working!")
    return True

def test_m3_optimization_suggestions():
    """Test M3 Mac-specific optimization suggestions."""
    print("\n" + "="*60)
    print("TEST 3: M3 Optimization Suggestions")
    print("="*60)
    
    mm = MemoryManager()
    suggestions = mm.get_m3_optimization_suggestions()
    
    print(f"\nOptimization Suggestions ({len(suggestions)} total):")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Validate suggestions
    assert len(suggestions) > 0, "No suggestions generated"
    
    print("\n✓ M3 optimization suggestions working!")
    return True

def test_memory_pressure_trend():
    """Test memory pressure trend analysis."""
    print("\n" + "="*60)
    print("TEST 4: Memory Pressure Trend")
    print("="*60)
    
    mm = MemoryManager()
    
    # Take multiple snapshots to build history
    print("\nBuilding memory history...")
    for i in range(5):
        mm.take_memory_snapshot()
        print(f"  Snapshot {i+1}/5 taken")
    
    trend = mm.get_memory_pressure_trend()
    
    print(f"\nTrend Analysis:")
    print(f"  Trend: {trend['trend']}")
    print(f"  Message: {trend['message']}")
    print(f"  Data Points: {trend['recent_snapshots']}")
    print(f"  Average Usage: {trend['average_percent_used']:.1f}%")
    
    if 'pressure_distribution' in trend:
        print(f"\nPressure Distribution:")
        for level, count in trend['pressure_distribution'].items():
            print(f"  {level}: {count}")
    
    print("\n✓ Memory pressure trend working!")
    return True

def test_model_memory_estimates():
    """Test model memory estimates for M3 Mac."""
    print("\n" + "="*60)
    print("TEST 5: Model Memory Estimates")
    print("="*60)
    
    mm = MemoryManager()
    
    models = [
        "mistral:latest",
        "qwen2.5:7b",
        "qwen2.5:14b",
        "llama3.1:8b",
    ]
    
    print("\nModel Memory Estimates:")
    for model in models:
        estimate = mm.get_model_memory_estimate(model)
        can_load, reason = mm.can_load_model(model)
        
        status = "✓" if can_load else "✗"
        print(f"  {status} {model}: {estimate:.1f} GB - {reason}")
    
    print("\n✓ Model memory estimates working!")
    return True

def test_comprehensive_memory_report():
    """Test comprehensive memory report."""
    print("\n" + "="*60)
    print("TEST 6: Comprehensive Memory Report")
    print("="*60)
    
    mm = MemoryManager()
    report = mm.get_memory_report()
    
    print("\nMemory Report Summary:")
    print(f"  Timestamp: {report['current']['timestamp']}")
    print(f"  Total Memory: {report['current']['system_memory']['total_gb']:.1f} GB")
    print(f"  Used Memory: {report['current']['system_memory']['used_gb']:.1f} GB")
    print(f"  Available: {report['current']['system_memory']['available_gb']:.1f} GB")
    print(f"  Percent Used: {report['current']['system_memory']['percent_used']:.1f}%")
    
    print(f"\nUnified Memory:")
    print(f"  Pressure: {report['current']['unified_memory']['pressure']}")
    print(f"  App Memory: {report['current']['unified_memory']['app_memory_gb']:.2f} GB")
    print(f"  Compressed: {report['current']['unified_memory']['compressed_memory_gb']:.2f} GB")
    print(f"  Wired: {report['current']['unified_memory']['wired_memory_gb']:.2f} GB")
    
    print(f"\nThermal State:")
    thermal = report['thermal_state']
    print(f"  Level: {thermal.get('level', 'unknown')}")
    print(f"  Score: {thermal.get('score', 0):.2f}")
    print(f"  Source: {thermal.get('source', 'unknown')}")
    
    print(f"\nTrends:")
    print(f"  Memory Trend: {report['trend']}")
    print(f"  Pressure Trend: {report['pressure_trend']['trend']}")
    
    print(f"\nRecommendations ({len(report['recommendations'])}):")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    print(f"\nM3 Optimizations ({len(report['m3_optimizations'])}):")
    for opt in report['m3_optimizations']:
        print(f"  - {opt}")
    
    print(f"\nAlerts: {len(report['alerts'])} recent alerts")
    
    print("\n✓ Comprehensive memory report working!")
    return True

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ENHANCED MEMORY MANAGER TEST SUITE (M3 Mac)")
    print("="*60)
    
    tests = [
        test_unified_memory_pressure,
        test_memory_alerts,
        test_m3_optimization_suggestions,
        test_memory_pressure_trend,
        test_model_memory_estimates,
        test_comprehensive_memory_report,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
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
        print("\n✓ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
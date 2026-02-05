"""
Dashboard - Provides a real-time performance monitoring dashboard.
"""
import time
from typing import Dict, List, Any
from datetime import datetime
import json


class Dashboard:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self, performance_tracker=None):
        self.performance_tracker = performance_tracker
        self.widgets = {}
        self.refresh_interval = 1.0  # seconds
        self.is_running = False
    
    def add_widget(self, name: str, widget):
        """Add a widget to the dashboard"""
        self.widgets[name] = widget
    
    def remove_widget(self, name: str):
        """Remove a widget from the dashboard"""
        if name in self.widgets:
            del self.widgets[name]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data from all widgets"""
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "widgets": {}
        }
        
        for name, widget in self.widgets.items():
            try:
                dashboard_data["widgets"][name] = widget.get_data()
            except Exception as e:
                dashboard_data["widgets"][name] = {
                    "error": f"Failed to get data: {str(e)}"
                }
        
        return dashboard_data
    
    def start_dashboard(self):
        """Start the dashboard (placeholder for real implementation)"""
        self.is_running = True
        print("Dashboard started. Press Ctrl+C to stop.")
        
        try:
            while self.is_running:
                data = self.get_dashboard_data()
                self._display_dashboard(data)
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
            self.is_running = False
    
    def stop_dashboard(self):
        """Stop the dashboard"""
        self.is_running = False
    
    def _display_dashboard(self, data: Dict[str, Any]):
        """Display dashboard data (simplified console output)"""
        print("\033[2J\033[H")  # Clear screen and move cursor to top-left
        print("=" * 60)
        print("AI STACK PERFORMANCE DASHBOARD")
        print("=" * 60)
        print(f"Last Update: {data['timestamp']}")
        print()
        
        for widget_name, widget_data in data["widgets"].items():
            print(f"{widget_name.upper()}:")
            if "error" in widget_data:
                print(f"  Error: {widget_data['error']}")
            else:
                self._print_widget_data(widget_data, indent=2)
            print()
    
    def _print_widget_data(self, data: Any, indent: int = 0):
        """Print widget data with proper indentation"""
        prefix = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}:")
                    self._print_widget_data(value, indent + 1)
                else:
                    print(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._print_widget_data(item, indent + 1)
                else:
                    print(f"{prefix}- {item}")
        else:
            print(f"{prefix}{data}")


class SystemMetricsWidget:
    """Widget for displaying system metrics"""
    
    def __init__(self, performance_tracker):
        self.performance_tracker = performance_tracker
    
    def get_data(self) -> Dict[str, Any]:
        """Get system metrics data"""
        if not self.performance_tracker:
            return {"error": "No performance tracker configured"}
        
        metrics = self.performance_tracker.get_current_metrics()
        if not metrics:
            return {"error": "No metrics available"}
        
        return {
            "cpu_usage_percent": round(metrics.get("cpu_percent", 0), 2),
            "memory_usage_percent": round(metrics.get("memory_percent", 0), 2),
            "memory_available_gb": round(metrics.get("memory_available_gb", 0), 2),
            "disk_read_mb": round(metrics.get("disk_io_read_mb", 0), 2),
            "disk_write_mb": round(metrics.get("disk_io_write_mb", 0), 2),
            "network_sent_mb": round(metrics.get("network_bytes_sent_mb", 0), 2),
            "network_received_mb": round(metrics.get("network_bytes_recv_mb", 0), 2)
        }


class ApplicationMetricsWidget:
    """Widget for displaying application metrics"""
    
    def __init__(self, performance_tracker):
        self.performance_tracker = performance_tracker
    
    def get_data(self) -> Dict[str, Any]:
        """Get application metrics data"""
        if not self.performance_tracker:
            return {"error": "No performance tracker configured"}
        
        summary = self.performance_tracker.get_performance_summary()
        if not summary:
            return {"error": "No metrics available"}
        
        return {
            "average_response_time_ms": round(summary.get("average_response_time_ms", 0), 2),
            "cache_hit_rate_percent": round(summary.get("cache_hit_rate", 0) * 100, 2),
            "model_calls_per_second": round(summary.get("model_calls_per_second", 0), 2),
            "uptime_minutes": round(summary.get("uptime_seconds", 0) / 60, 2)
        }


class RAGMetricsWidget:
    """Widget for displaying RAG-specific metrics"""
    
    def __init__(self, rag_engine=None):
        self.rag_engine = rag_engine
        self.queries_processed = 0
        self.average_retrieval_time = 0.0
        self.average_generation_time = 0.0
    
    def record_query(self, retrieval_time: float, generation_time: float):
        """Record a RAG query processing time"""
        self.queries_processed += 1
        self.average_retrieval_time = (
            (self.average_retrieval_time * (self.queries_processed - 1) + retrieval_time) 
            / self.queries_processed
        )
        self.average_generation_time = (
            (self.average_generation_time * (self.queries_processed - 1) + generation_time) 
            / self.queries_processed
        )
    
    def get_data(self) -> Dict[str, Any]:
        """Get RAG metrics data"""
        if not self.rag_engine and self.queries_processed == 0:
            return {"error": "No RAG engine configured and no queries processed"}
        
        return {
            "queries_processed": self.queries_processed,
            "average_retrieval_time_ms": round(self.average_retrieval_time * 1000, 2),
            "average_generation_time_ms": round(self.average_generation_time * 1000, 2),
            "total_processing_time_ms": round(
                (self.average_retrieval_time + self.average_generation_time) * 1000, 2
            )
        }


class CascadeMetricsWidget:
    """Widget for displaying Cascade-specific metrics"""
    
    def __init__(self, cascade_engine=None):
        self.cascade_engine = cascade_engine
        self.operations_processed = 0
        self.average_operation_time = 0.0
        self.stage_completion_rates = {}
    
    def record_operation(self, operation_time: float, stages_completed: Dict[str, bool]):
        """Record a Cascade operation processing time"""
        self.operations_processed += 1
        self.average_operation_time = (
            (self.average_operation_time * (self.operations_processed - 1) + operation_time) 
            / self.operations_processed
        )
        
        # Update stage completion rates
        for stage, completed in stages_completed.items():
            if stage not in self.stage_completion_rates:
                self.stage_completion_rates[stage] = {"completed": 0, "total": 0}
            
            self.stage_completion_rates[stage]["total"] += 1
            if completed:
                self.stage_completion_rates[stage]["completed"] += 1
    
    def get_data(self) -> Dict[str, Any]:
        """Get Cascade metrics data"""
        if not self.cascade_engine and self.operations_processed == 0:
            return {"error": "No Cascade engine configured and no operations processed"}
        
        completion_rates = {}
        for stage, stats in self.stage_completion_rates.items():
            if stats["total"] > 0:
                rate = stats["completed"] / stats["total"]
                completion_rates[f"{stage}_completion_rate"] = round(rate * 100, 2)
        
        return {
            "operations_processed": self.operations_processed,
            "average_operation_time_ms": round(self.average_operation_time * 1000, 2),
            "stage_completion_rates": completion_rates
        }
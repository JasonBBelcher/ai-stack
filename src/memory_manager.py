"""
Memory Manager - Monitors and manages system memory usage for the AI stack
"""
try:
    import psutil
except ImportError:
    psutil = None
import subprocess
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemorySnapshot:
    """Snapshot of current memory state"""
    timestamp: datetime
    total_gb: float
    used_gb: float
    available_gb: float
    percent_used: float
    swap_total_gb: float
    swap_used_gb: float
    gpu_memory_gb: float


class MemoryManager:
    """Manages memory monitoring and optimization for the AI stack"""
    
    def __init__(self, safety_buffer_gb: float = 2.0, thermal_threshold: float = 0.85):
        self.safety_buffer_gb = safety_buffer_gb
        self.thermal_threshold = thermal_threshold
        self.memory_history: List[MemorySnapshot] = []
        self.max_history_size = 100
        
        # Model memory estimates (in GB)
        self.model_memory_estimates = {
            "mistral": 5.0,
            "qwen2.5": 10.0,
            "qwen2.5-7b": 5.5,
            "qwen2.5-14b": 10.0,
        }
    
    def get_system_memory(self) -> Dict[str, float]:
        """Get current system memory information"""
        if psutil is None:
            # Fallback if psutil not available
            return {
                "total_gb": 16.0,
                "used_gb": 8.0,
                "available_gb": 8.0,
                "percent_used": 50.0,
                "swap_total_gb": 0.0,
                "swap_used_gb": 0.0,
            }
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "total_gb": memory.total / (1024**3),
            "used_gb": memory.used / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent_used": memory.percent,
            "swap_total_gb": swap.total / (1024**3),
            "swap_used_gb": swap.used / (1024**3),
        }
    
    def get_gpu_memory(self) -> float:
        """Estimate GPU memory usage on Apple Silicon"""
        try:
            # Use system_profiler to get GPU info on Mac
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType", "-json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # For Apple Silicon, estimate from total system memory
                return self.estimate_unified_memory_usage()
            
        except Exception:
            pass
        
        return self.estimate_unified_memory_usage()
    
    def estimate_unified_memory_usage(self) -> float:
        """Estimate memory being used by GPU/integrated graphics"""
        memory = self.get_system_memory()
        # On Apple Silicon, estimate GPU usage from system patterns
        # This is a rough approximation
        return max(0.0, memory["used_gb"] - memory["swap_used_gb"])
    
    def take_memory_snapshot(self) -> MemorySnapshot:
        """Capture current memory state"""
        mem_info = self.get_system_memory()
        gpu_memory = self.get_gpu_memory()
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            total_gb=mem_info["total_gb"],
            used_gb=mem_info["used_gb"],
            available_gb=mem_info["available_gb"],
            percent_used=mem_info["percent_used"],
            swap_total_gb=mem_info["swap_total_gb"],
            swap_used_gb=mem_info["swap_used_gb"],
            gpu_memory_gb=gpu_memory
        )
        
        self.memory_history.append(snapshot)
        if len(self.memory_history) > self.max_history_size:
            self.memory_history.pop(0)
        
        return snapshot
    
    def get_model_memory_estimate(self, model_name: str) -> float:
        """Get memory estimate for a specific model"""
        model_lower = model_name.lower()
        for key, estimate in self.model_memory_estimates.items():
            if key in model_lower:
                return estimate
        return 5.0  # Default estimate
    
    def can_load_model(self, model_name: str) -> tuple[bool, str]:
        """Check if model can be loaded safely"""
        current = self.get_system_memory()
        model_memory = self.get_model_memory_estimate(model_name)
        required_total = current["used_gb"] + model_memory + self.safety_buffer_gb
        
        if required_total > current["total_gb"]:
            shortage = required_total - current["total_gb"]
            return False, f"Insufficient memory: need {shortage:.1f}GB more"
        
        # Check swap usage
        if current["swap_used_gb"] > 1.0:
            return False, "High swap usage detected, may impact performance"
        
        # Check thermal state
        if current["percent_used"] > self.thermal_threshold * 100:
            return False, "System memory pressure too high"
        
        return True, "Memory available"
    
    def get_thermal_state(self) -> Dict[str, Any]:
        """Get thermal information"""
        try:
            # Try to get thermal info without sudo first
            result = subprocess.run(
                ["powermetrics", "--samplers", "thermal", "-i", "1000", "-n", "1"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                thermal_info = {"status": "available", "source": "powermetrics"}
            else:
                raise Exception("powermetrics failed without sudo")
            
            if "Thermal Level: 0" in result.stdout:
                thermal_info["level"] = "normal"
                thermal_info["score"] = 0.2
            elif "Thermal Level: 1" in result.stdout:
                thermal_info["level"] = "moderate"
                thermal_info["score"] = 0.4
            elif "Thermal Level: 2" in result.stdout:
                thermal_info["level"] = "high"
                thermal_info["score"] = 0.7
            else:
                thermal_info["level"] = "critical"
                thermal_info["score"] = 0.9
            
            return thermal_info
            
        except Exception:
            # Fallback to CPU-based estimation (no sudo required)
            if psutil is None:
                return {
                    "status": "estimated",
                    "level": "normal", 
                    "score": 0.2,
                    "cpu_percent": 0,
                    "source": "fallback"
                }
            
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent < 50:
                level, score = "normal", 0.2
            elif cpu_percent < 75:
                level, score = "moderate", 0.4
            elif cpu_percent < 90:
                level, score = "high", 0.7
            else:
                level, score = "critical", 0.9
            
            return {
                "status": "estimated",
                "level": level,
                "score": score,
                "cpu_percent": cpu_percent
            }
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        current = self.get_system_memory()
        thermal = self.get_thermal_state()
        
        # Memory pressure
        if current["percent_used"] > 75:
            recommendations.append("High memory pressure - consider closing applications")
        
        if current["swap_used_gb"] > 0.5:
            recommendations.append("Swap usage detected - may impact performance")
        
        # Thermal issues
        if thermal.get("score", 0) > 0.7:
            recommendations.append("High thermal state - reduce workload or allow cooling")
        
        # General optimization
        if len(self.memory_history) > 5:
            recent_trend = self.analyze_memory_trend()
            if recent_trend == "increasing":
                recommendations.append("Memory usage trending upward - monitor for leaks")
        
        return recommendations
    
    def analyze_memory_trend(self) -> str:
        """Analyze memory usage trend from history"""
        if len(self.memory_history) < 5:
            return "insufficient_data"
        
        recent = self.memory_history[-5:]
        if recent[-1].percent_used > recent[0].percent_used + 5:
            return "increasing"
        elif recent[-1].percent_used < recent[0].percent_used - 5:
            return "decreasing"
        else:
            return "stable"
    
    def get_optimization_suggestions(self, model_name: str) -> Dict[str, Any]:
        """Get specific optimization suggestions for loading a model"""
        can_load, reason = self.can_load_model(model_name)
        
        suggestions = {
            "can_load": can_load,
            "reason": reason,
            "current_memory": self.get_system_memory(),
            "model_memory_estimate": self.get_model_memory_estimate(model_name),
            "thermal_state": self.get_thermal_state(),
            "recommendations": []
        }
        
        if not can_load:
            if "swap usage" in reason:
                suggestions["recommendations"].append("Close unused applications to free memory")
                suggestions["recommendations"].append("Consider restarting if swap remains high")
            elif "need" in reason:
                suggestions["recommendations"].append("Unload other models first")
                suggestions["recommendations"].append("Reduce safety buffer if confident")
        
        # Add thermal suggestions
        thermal = suggestions["thermal_state"]
        if thermal.get("score", 0) > 0.6:
            suggestions["recommendations"].append("Allow system to cool before loading large models")
        
        return suggestions
    
    def cleanup_memory(self) -> bool:
        """Attempt to free up memory"""
        try:
            # Trigger Python garbage collection
            import gc
            gc.collect()
            
            # On macOS, try memory pressure relief
            subprocess.run(["purge"], capture_output=True, timeout=30)
            
            time.sleep(2)  # Allow time for cleanup
            
            return True
        except Exception:
            return False
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory report"""
        current_snapshot = self.take_memory_snapshot()
        
        return {
            "current": {
                "timestamp": current_snapshot.timestamp.isoformat(),
                "system_memory": {
                    "total_gb": current_snapshot.total_gb,
                    "used_gb": current_snapshot.used_gb,
                    "available_gb": current_snapshot.available_gb,
                    "percent_used": current_snapshot.percent_used,
                },
                "gpu_memory_gb": current_snapshot.gpu_memory_gb,
                "swap_memory": {
                    "total_gb": current_snapshot.swap_total_gb,
                    "used_gb": current_snapshot.swap_used_gb,
                }
            },
            "thermal_state": self.get_thermal_state(),
            "trend": self.analyze_memory_trend(),
            "recommendations": self.get_performance_recommendations(),
            "history_size": len(self.memory_history)
        }
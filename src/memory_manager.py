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
    unified_memory_pressure: str  # "normal", "warning", "critical"
    app_memory_gb: float
    compressed_memory_gb: float
    wired_memory_gb: float


@dataclass
class MemoryAlert:
    """Memory alert with severity and message"""
    timestamp: datetime
    severity: str  # "info", "warning", "critical"
    message: str
    metric_name: str
    current_value: float
    threshold: float


class MemoryManager:
    """Manages memory monitoring and optimization for the AI stack"""
    
    def __init__(self, safety_buffer_gb: float = 2.0, thermal_threshold: float = 0.85):
        self.safety_buffer_gb = safety_buffer_gb
        self.thermal_threshold = thermal_threshold
        self.memory_history: List[MemorySnapshot] = []
        self.max_history_size = 100
        self.alerts: List[MemoryAlert] = []
        self.max_alerts = 50
        
        # M3 Mac-specific thresholds
        self.unified_memory_thresholds = {
            "warning": 0.75,  # 75% usage triggers warning
            "critical": 0.90  # 90% usage triggers critical alert
        }
        
        # Model memory estimates (in GB) - updated for M3 Mac
        self.model_memory_estimates = {
            "mistral": 5.0,
            "qwen2.5": 10.0,
            "qwen2.5-7b": 5.5,
            "qwen2.5-14b": 10.0,
            "llama3.1": 6.0,
            "llama3.1-8b": 6.0,
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
                "app_memory_gb": 6.0,
                "compressed_memory_gb": 1.0,
                "wired_memory_gb": 1.0,
            }
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Get detailed memory breakdown for M3 Mac
        app_memory = getattr(memory, 'active', memory.used * 0.6)
        compressed_memory = getattr(memory, 'compressed', memory.used * 0.1)
        wired_memory = getattr(memory, 'wired', memory.used * 0.15)
        
        return {
            "total_gb": memory.total / (1024**3),
            "used_gb": memory.used / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent_used": memory.percent,
            "swap_total_gb": swap.total / (1024**3),
            "swap_used_gb": swap.used / (1024**3),
            "app_memory_gb": app_memory / (1024**3),
            "compressed_memory_gb": compressed_memory / (1024**3),
            "wired_memory_gb": wired_memory / (1024**3),
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
        
        # Determine unified memory pressure
        unified_pressure = self._calculate_unified_memory_pressure(mem_info)
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            total_gb=mem_info["total_gb"],
            used_gb=mem_info["used_gb"],
            available_gb=mem_info["available_gb"],
            percent_used=mem_info["percent_used"],
            swap_total_gb=mem_info["swap_total_gb"],
            swap_used_gb=mem_info["swap_used_gb"],
            gpu_memory_gb=gpu_memory,
            unified_memory_pressure=unified_pressure,
            app_memory_gb=mem_info["app_memory_gb"],
            compressed_memory_gb=mem_info["compressed_memory_gb"],
            wired_memory_gb=mem_info["wired_memory_gb"]
        )
        
        self.memory_history.append(snapshot)
        if len(self.memory_history) > self.max_history_size:
            self.memory_history.pop(0)
        
        # Check for memory alerts
        self._check_memory_alerts(snapshot)
        
        return snapshot
    
    def _calculate_unified_memory_pressure(self, mem_info: Dict[str, float]) -> str:
        """Calculate unified memory pressure for M3 Mac"""
        percent_used = mem_info["percent_used"]
        swap_used = mem_info["swap_used_gb"]
        compressed = mem_info["compressed_memory_gb"]
        
        # Base pressure from memory percentage
        if percent_used >= self.unified_memory_thresholds["critical"]:
            return "critical"
        elif percent_used >= self.unified_memory_thresholds["warning"]:
            return "warning"
        
        # Elevate pressure based on swap usage (indicates memory pressure)
        if swap_used > 2.0:
            return "critical"
        elif swap_used > 0.5:
            return "warning"
        
        # Elevate pressure based on compressed memory (indicates pressure)
        if compressed > 3.0:
            return "warning"
        
        return "normal"
    
    def _check_memory_alerts(self, snapshot: MemorySnapshot):
        """Check for memory alerts and add to alert history"""
        # Check unified memory pressure
        if snapshot.unified_memory_pressure == "critical":
            self._add_alert(
                severity="critical",
                message=f"Critical unified memory pressure: {snapshot.percent_used:.1f}%",
                metric_name="unified_memory_pressure",
                current_value=snapshot.percent_used,
                threshold=self.unified_memory_thresholds["critical"] * 100
            )
        elif snapshot.unified_memory_pressure == "warning":
            self._add_alert(
                severity="warning",
                message=f"High unified memory pressure: {snapshot.percent_used:.1f}%",
                metric_name="unified_memory_pressure",
                current_value=snapshot.percent_used,
                threshold=self.unified_memory_thresholds["warning"] * 100
            )
        
        # Check swap usage
        if snapshot.swap_used_gb > 2.0:
            self._add_alert(
                severity="critical",
                message=f"High swap usage: {snapshot.swap_used_gb:.1f}GB",
                metric_name="swap_usage",
                current_value=snapshot.swap_used_gb,
                threshold=2.0
            )
        elif snapshot.swap_used_gb > 0.5:
            self._add_alert(
                severity="warning",
                message=f"Swap usage detected: {snapshot.swap_used_gb:.1f}GB",
                metric_name="swap_usage",
                current_value=snapshot.swap_used_gb,
                threshold=0.5
            )
        
        # Check compressed memory (indicates memory pressure)
        if snapshot.compressed_memory_gb > 3.0:
            self._add_alert(
                severity="warning",
                message=f"High compressed memory: {snapshot.compressed_memory_gb:.1f}GB",
                metric_name="compressed_memory",
                current_value=snapshot.compressed_memory_gb,
                threshold=3.0
            )
    
    def _add_alert(self, severity: str, message: str, metric_name: str, 
                   current_value: float, threshold: float):
        """Add a memory alert to the alert history"""
        alert = MemoryAlert(
            timestamp=datetime.now(),
            severity=severity,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
    
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
                },
                "unified_memory": {
                    "pressure": current_snapshot.unified_memory_pressure,
                    "app_memory_gb": current_snapshot.app_memory_gb,
                    "compressed_memory_gb": current_snapshot.compressed_memory_gb,
                    "wired_memory_gb": current_snapshot.wired_memory_gb,
                }
            },
            "thermal_state": self.get_thermal_state(),
            "trend": self.analyze_memory_trend(),
            "pressure_trend": self.get_memory_pressure_trend(),
            "recommendations": self.get_performance_recommendations(),
            "m3_optimizations": self.get_m3_optimization_suggestions(),
            "alerts": self.get_memory_alerts(),
            "history_size": len(self.memory_history)
        }
    
    def get_unified_memory_pressure(self) -> Dict[str, Any]:
        """Get unified memory pressure status for M3 Mac"""
        snapshot = self.take_memory_snapshot()
        
        return {
            "pressure": snapshot.unified_memory_pressure,
            "percent_used": snapshot.percent_used,
            "thresholds": self.unified_memory_thresholds,
            "breakdown": {
                "app_memory_gb": snapshot.app_memory_gb,
                "compressed_memory_gb": snapshot.compressed_memory_gb,
                "wired_memory_gb": snapshot.wired_memory_gb,
                "swap_used_gb": snapshot.swap_used_gb,
            },
            "status": self._get_pressure_status(snapshot.unified_memory_pressure)
        }
    
    def _get_pressure_status(self, pressure: str) -> str:
        """Get human-readable status for pressure level"""
        status_map = {
            "normal": "✓ Memory pressure is normal. System is operating optimally.",
            "warning": "⚠ Memory pressure is elevated. Consider closing unused applications.",
            "critical": "✗ Critical memory pressure! Close applications immediately to prevent slowdowns."
        }
        return status_map.get(pressure, "Unknown pressure level")
    
    def get_memory_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent memory alerts, optionally filtered by severity"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return [
            {
                "timestamp": alert.timestamp.isoformat(),
                "severity": alert.severity,
                "message": alert.message,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "threshold": alert.threshold
            }
            for alert in alerts
        ]
    
    def get_m3_optimization_suggestions(self) -> List[str]:
        """Get M3 Mac-specific optimization suggestions"""
        suggestions = []
        snapshot = self.take_memory_snapshot()
        thermal = self.get_thermal_state()
        
        # Unified memory pressure suggestions
        if snapshot.unified_memory_pressure == "critical":
            suggestions.append("🔴 CRITICAL: Close unused applications immediately")
            suggestions.append("🔴 Consider restarting to clear memory pressure")
            suggestions.append("🔴 Unload any loaded AI models")
        elif snapshot.unified_memory_pressure == "warning":
            suggestions.append("🟡 Close unused applications to free memory")
            suggestions.append("🟡 Avoid loading multiple large models simultaneously")
        
        # Compressed memory suggestions
        if snapshot.compressed_memory_gb > 2.0:
            suggestions.append(f"🟡 High compressed memory ({snapshot.compressed_memory_gb:.1f}GB) - indicates memory pressure")
        
        # Swap usage suggestions
        if snapshot.swap_used_gb > 1.0:
            suggestions.append(f"🟡 Swap usage ({snapshot.swap_used_gb:.1f}GB) will impact model performance")
        
        # Thermal suggestions
        if thermal.get("score", 0) > 0.7:
            suggestions.append("🔴 High thermal state - allow system to cool before loading models")
        elif thermal.get("score", 0) > 0.5:
            suggestions.append("🟡 Elevated thermal state - monitor temperature during model use")
        
        # M3-specific optimizations
        if snapshot.percent_used < 60:
            suggestions.append("✓ Memory usage is optimal for M3 Mac performance")
            suggestions.append("✓ You can load larger models (14B+) without issues")
        elif snapshot.percent_used < 75:
            suggestions.append("✓ Memory usage is acceptable for most models")
            suggestions.append("ℹ️ Consider 7B-8B models for best performance")
        
        # Model-specific suggestions
        available_memory = snapshot.available_gb
        if available_memory < 6:
            suggestions.append("⚠️ Limited memory available - use 7B models or smaller")
        elif available_memory < 10:
            suggestions.append("ℹ️ Moderate memory available - 8B models recommended")
        else:
            suggestions.append("✓ Sufficient memory for 14B models")
        
        return suggestions
    
    def get_memory_pressure_trend(self) -> Dict[str, Any]:
        """Analyze memory pressure trend over time"""
        if len(self.memory_history) < 5:
            return {
                "trend": "insufficient_data",
                "message": "Need at least 5 snapshots to analyze trend",
                "data_points": len(self.memory_history)
            }
        
        recent = self.memory_history[-10:]  # Last 10 snapshots
        
        # Count pressure levels
        pressure_counts = {"normal": 0, "warning": 0, "critical": 0}
        for snapshot in recent:
            pressure_counts[snapshot.unified_memory_pressure] += 1
        
        # Determine trend
        if pressure_counts["critical"] > 0:
            trend = "critical"
            message = "Recent critical memory pressure detected"
        elif pressure_counts["warning"] > len(recent) / 2:
            trend = "elevated"
            message = "Consistently elevated memory pressure"
        elif pressure_counts["normal"] > len(recent) / 2:
            trend = "stable"
            message = "Memory pressure is stable and normal"
        else:
            trend = "fluctuating"
            message = "Memory pressure is fluctuating"
        
        return {
            "trend": trend,
            "message": message,
            "pressure_distribution": pressure_counts,
            "recent_snapshots": len(recent),
            "average_percent_used": sum(s.percent_used for s in recent) / len(recent)
        }
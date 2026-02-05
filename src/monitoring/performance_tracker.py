"""
Performance Tracker - Monitors and tracks system performance metrics.
"""
import time
import psutil
import threading
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent_mb: float
    network_bytes_recv_mb: float
    response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    model_calls_per_second: float = 0.0


class PerformanceTracker:
    """Tracks system performance metrics"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self.is_monitoring = False
        self.monitoring_thread = None
        self.start_time = None
        self.last_metrics = None
        
        # Performance counters
        self.response_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.model_calls = 0
        self.model_call_start_time = None
    
    def start_monitoring(self, interval_seconds: float = 5.0):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.start_time = time.time()
        self.monitoring_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
    
    def _monitor_loop(self, interval_seconds: float):
        """Monitoring loop that runs in a separate thread"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self._store_metrics(metrics)
                time.sleep(interval_seconds)
            except Exception:
                # Don't let monitoring errors crash the system
                time.sleep(interval_seconds)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / (1024**2) if disk_io else 0
        disk_io_write_mb = disk_io.write_bytes / (1024**2) if disk_io else 0
        
        # Network metrics
        net_io = psutil.net_io_counters()
        network_bytes_sent_mb = net_io.bytes_sent / (1024**2) if net_io else 0
        network_bytes_recv_mb = net_io.bytes_recv / (1024**2) if net_io else 0
        
        # Application-specific metrics
        response_time_ms = self._get_average_response_time()
        cache_hit_rate = self._get_cache_hit_rate()
        model_calls_per_second = self._get_model_calls_per_second()
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_bytes_sent_mb=network_bytes_sent_mb,
            network_bytes_recv_mb=network_bytes_recv_mb,
            response_time_ms=response_time_ms,
            cache_hit_rate=cache_hit_rate,
            model_calls_per_second=model_calls_per_second
        )
    
    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in history"""
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        self.last_metrics = metrics
    
    def _get_average_response_time(self) -> float:
        """Get average response time from collected samples"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return self.cache_hits / total_requests
    
    def _get_model_calls_per_second(self) -> float:
        """Get model calls per second"""
        if not self.start_time:
            return 0.0
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:
            return 0.0
        return self.model_calls / elapsed_time
    
    def record_response_time(self, response_time_ms: float):
        """Record a response time measurement"""
        self.response_times.append(response_time_ms)
        # Keep only recent response times
        if len(self.response_times) > 100:
            self.response_times.pop(0)
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1
    
    def record_model_call_start(self):
        """Record the start of a model call"""
        self.model_call_start_time = time.time()
        self.model_calls += 1
    
    def record_model_call_end(self):
        """Record the end of a model call"""
        if self.model_call_start_time:
            response_time_ms = (time.time() - self.model_call_start_time) * 1000
            self.record_response_time(response_time_ms)
            self.model_call_start_time = None
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.last_metrics:
            return {}
        
        return asdict(self.last_metrics)
    
    def get_metrics_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get historical performance metrics"""
        metrics_list = [asdict(metric) for metric in self.metrics_history[-limit:]]
        return metrics_list
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
        avg_cache_hit_rate = sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics)
        
        return {
            "average_cpu_percent": avg_cpu,
            "average_memory_percent": avg_memory,
            "average_response_time_ms": avg_response_time,
            "cache_hit_rate": avg_cache_hit_rate,
            "model_calls_per_second": self._get_model_calls_per_second(),
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0
        }
    
    def reset_counters(self):
        """Reset all performance counters"""
        self.response_times.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.model_calls = 0
        self.start_time = time.time()
        self.metrics_history.clear()
        self.last_metrics = None
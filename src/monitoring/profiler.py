"""
Profiler - Profiles code execution for performance analysis.
"""
import time
import cProfile
import pstats
import io
from typing import Dict, List, Any, Callable
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
import logging


@dataclass
class ProfileData:
    """Profile data structure"""
    name: str
    start_time: float
    end_time: float
    duration: float
    cpu_time: float = 0.0
    call_count: int = 0
    memory_delta_mb: float = 0.0


class Profiler:
    """Profiles code execution for performance analysis"""
    
    def __init__(self):
        self.profiles: List[ProfileData] = []
        self.max_profiles = 1000
        self.logger = logging.getLogger(__name__)
        self.active_profiles: Dict[str, ProfileData] = {}
    
    @contextmanager
    def profile(self, name: str, track_cpu: bool = False, track_memory: bool = False):
        """Context manager for profiling code blocks"""
        profile_data = ProfileData(
            name=name,
            start_time=time.perf_counter(),
            end_time=0.0,
            duration=0.0
        )
        
        # Store active profile
        self.active_profiles[name] = profile_data
        
        # Setup CPU profiling if requested
        if track_cpu:
            pr = cProfile.Profile()
            pr.enable()
        else:
            pr = None
        
        # Store memory before if requested
        if track_memory:
            try:
                import psutil
                process = psutil.Process()
                memory_before = process.memory_info().rss / (1024 * 1024)  # MB
            except ImportError:
                memory_before = 0.0
                track_memory = False
        else:
            memory_before = 0.0
        
        try:
            yield profile_data
        finally:
            # Calculate duration
            profile_data.end_time = time.perf_counter()
            profile_data.duration = profile_data.end_time - profile_data.start_time
            
            # Add CPU time if tracked
            if pr:
                pr.disable()
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s)
                profile_data.cpu_time = ps.total_tt
            
            # Add memory delta if tracked
            if track_memory:
                try:
                    import psutil
                    process = psutil.Process()
                    memory_after = process.memory_info().rss / (1024 * 1024)  # MB
                    profile_data.memory_delta_mb = memory_after - memory_before
                except ImportError:
                    pass
            
            # Remove from active profiles
            if name in self.active_profiles:
                del self.active_profiles[name]
            
            # Store profile data
            self._store_profile(profile_data)
    
    def _store_profile(self, profile_data: ProfileData):
        """Store profile data"""
        self.profiles.append(profile_data)
        if len(self.profiles) > self.max_profiles:
            self.profiles.pop(0)
        
        self.logger.debug(f"PROFILE [{profile_data.name}]: {profile_data.duration:.4f}s")
    
    def profile_function(self, func: Callable, track_cpu: bool = False, track_memory: bool = False):
        """Decorator for profiling functions"""
        def wrapper(*args, **kwargs):
            with self.profile(func.__name__, track_cpu, track_memory):
                return func(*args, **kwargs)
        return wrapper
    
    def get_profile_data(self, name: str = None) -> List[Dict[str, Any]]:
        """Get profile data"""
        if name:
            profiles = [p for p in self.profiles if p.name == name]
        else:
            profiles = self.profiles
        
        return [asdict(profile) for profile in profiles]
    
    def get_recent_profiles(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent profile data"""
        profiles = self.profiles[-limit:]
        return [asdict(profile) for profile in profiles]
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of profile data"""
        if not self.profiles:
            return {}
        
        # Group profiles by name
        profile_groups = {}
        for profile in self.profiles:
            if profile.name not in profile_groups:
                profile_groups[profile.name] = []
            profile_groups[profile.name].append(profile)
        
        # Calculate statistics for each group
        summary = {}
        for name, profiles in profile_groups.items():
            durations = [p.duration for p in profiles]
            cpu_times = [p.cpu_time for p in profiles if p.cpu_time > 0]
            memory_deltas = [p.memory_delta_mb for p in profiles if p.memory_delta_mb != 0]
            
            summary[name] = {
                "call_count": len(profiles),
                "total_time": sum(durations),
                "average_time": sum(durations) / len(durations),
                "min_time": min(durations),
                "max_time": max(durations),
                "average_cpu_time": sum(cpu_times) / len(cpu_times) if cpu_times else 0,
                "average_memory_delta_mb": sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0
            }
        
        return summary
    
    def get_slowest_profiles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest profiles"""
        sorted_profiles = sorted(self.profiles, key=lambda p: p.duration, reverse=True)
        return [asdict(profile) for profile in sorted_profiles[:limit]]
    
    def clear_profiles(self):
        """Clear all profile data"""
        self.profiles.clear()
        self.active_profiles.clear()
    
    def get_active_profile_names(self) -> List[str]:
        """Get names of currently active profiles"""
        return list(self.active_profiles.keys())
    
    def export_profiles(self, filepath: str):
        """Export profiles to a file"""
        import json
        profile_data = self.get_profile_data()
        with open(filepath, 'w') as f:
            json.dump(profile_data, f, indent=2)
        self.logger.info(f"Profiles exported to {filepath}")
    
    def get_performance_report(self) -> str:
        """Generate a performance report"""
        if not self.profiles:
            return "No profile data available."
        
        summary = self.get_profile_summary()
        slowest = self.get_slowest_profiles(5)
        
        report = []
        report.append("=" * 60)
        report.append("PERFORMANCE PROFILING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Profiles: {len(self.profiles)}")
        report.append("")
        
        report.append("FUNCTION SUMMARY:")
        report.append("-" * 30)
        for name, stats in summary.items():
            report.append(f"{name}:")
            report.append(f"  Calls: {stats['call_count']}")
            report.append(f"  Avg Time: {stats['average_time']:.4f}s")
            report.append(f"  Total Time: {stats['total_time']:.4f}s")
            report.append(f"  Min/Max: {stats['min_time']:.4f}s / {stats['max_time']:.4f}s")
            if stats['average_cpu_time'] > 0:
                report.append(f"  Avg CPU Time: {stats['average_cpu_time']:.4f}s")
            if stats['average_memory_delta_mb'] != 0:
                report.append(f"  Avg Memory Delta: {stats['average_memory_delta_mb']:.2f}MB")
            report.append("")
        
        report.append("SLOWEST OPERATIONS:")
        report.append("-" * 30)
        for profile in slowest:
            report.append(f"{profile['name']}: {profile['duration']:.4f}s")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create profiler
    profiler = Profiler()
    
    # Profile a function
    @profiler.profile_function
    def slow_function():
        time.sleep(0.1)
        return "Done"
    
    # Profile a code block
    with profiler.profile("example_block"):
        time.sleep(0.05)
        result = sum(range(1000000))
    
    # Profile with CPU tracking
    with profiler.profile("cpu_intensive", track_cpu=True):
        result = sum(i**2 for i in range(100000))
    
    # Print report
    print(profiler.get_performance_report())
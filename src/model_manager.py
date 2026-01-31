"""
Model Manager - Handles loading, unloading, and monitoring Ollama models
"""
import subprocess
import time
try:
    import psutil
except ImportError:
    psutil = None
from typing import Optional, List, Dict, Any
from enum import Enum


class ModelState(Enum):
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"


class ModelManager:
    """Manages Ollama model lifecycle with VRAM optimization"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.loaded_models: set = set()
        self.model_memory_usage: Dict[str, float] = {
            "mistral": 5.0,  # GB estimated
            "qwen2.5": 10.0,  # GB estimated
        }
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        try:
            result = subprocess.run(
                ["ollama", "ps"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            return []
        except subprocess.TimeoutExpired:
            return []
    
    def load_model(self, model_name: str, timeout: int = 60) -> ModelState:
        """Load a model with VRAM management"""
        if model_name in self.loaded_models:
            return ModelState.LOADED
        
        try:
            # Ensure Ollama is running
            if not self.check_ollama_status():
                raise RuntimeError("Ollama is not running")
            
            # Load the model
            start_time = time.time()
            process = subprocess.Popen(
                ["ollama", "run", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for model to be ready (first prompt appears)
            ready = False
            while not ready and (time.time() - start_time) < timeout:
                if process.poll() is not None:
                    raise RuntimeError(f"Model loading failed: {process.stderr.read()}")
                time.sleep(1)
                if model_name in self.get_loaded_models():
                    ready = True
            
            if ready:
                self.loaded_models.add(model_name)
                # Give the model time to fully initialize
                time.sleep(2)
                return ModelState.LOADED
            else:
                process.terminate()
                return ModelState.ERROR
                
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return ModelState.ERROR
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free VRAM"""
        try:
            result = subprocess.run(
                ["ollama", "stop", model_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if model_name in self.loaded_models:
                self.loaded_models.discard(model_name)
            
            # Give time for memory to be freed
            time.sleep(1)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error unloading model {model_name}: {e}")
            return False
    
    def unload_all_models(self) -> None:
        """Unload all models to free maximum VRAM"""
        current_models = self.get_loaded_models()
        for model in current_models:
            self.unload_model(model)
        self.loaded_models.clear()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current system memory usage"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "used_gb": memory.used / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent_used": memory.percent
        }
    
    def get_model_memory_estimate(self, model_name: str) -> float:
        """Get estimated memory usage for a model"""
        for key, usage in self.model_memory_usage.items():
            if key in model_name.lower():
                return usage
        return 5.0  # Default estimate
    
    def can_load_model(self, model_name: str, safety_buffer_gb: float = 2.0) -> tuple[bool, str]:
        """Check if model can be loaded within memory constraints"""
        if psutil is None:
            return True, "Memory check skipped (psutil not available)"
            
        current_memory = self.get_memory_usage()
        model_memory = self.get_model_memory_estimate(model_name)
        
        required_total = current_memory["used_gb"] + model_memory + safety_buffer_gb
        
        if required_total > current_memory["total_gb"]:
            shortage = required_total - current_memory["total_gb"]
            return False, f"Insufficient memory: need {shortage:.1f}GB more"
        
        # Check swap usage
        if current_memory.get("swap_used_gb", 0) > 1.0:
            return False, "High swap usage detected, may impact performance"
        
        # Check thermal state
        if current_memory.get("percent_used", 0) > 85:
            return False, "System memory pressure too high"
        
        return True, "Memory available"
    
    def safe_load_model(self, model_name: str, max_retries: int = 3) -> ModelState:
        """Load model with memory safety checks and retries"""
        for attempt in range(max_retries):
            try:
                # Check if we have enough memory
                if not self.can_load_model(model_name):
                    # Try to free up memory first
                    self.unload_all_models()
                    time.sleep(2)
                    
                    if not self.can_load_model(model_name):
                        raise RuntimeError("Insufficient memory to load model")
                
                # Load the model
                state = self.load_model(model_name)
                if state == ModelState.LOADED:
                    return state
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for model {model_name}: {e}")
                if attempt < max_retries - 1:
                    # Cleanup and retry
                    self.unload_all_models()
                    time.sleep(3)
        
        return ModelState.ERROR
    
    def get_thermal_state(self) -> str:
        """Get approximate thermal state (simplified for Mac)"""
        try:
            # Use powermetrics to get thermal data (requires sudo)
            result = subprocess.run(
                ["sudo", "powermetrics", "--samplers", "thermal", "-i", "1000", "-n", "1"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if "Thermal Level: 0" in result.stdout:
                return "normal"
            elif "Thermal Level: 1" in result.stdout:
                return "moderate"
            elif "Thermal Level: 2" in result.stdout:
                return "high"
            else:
                return "critical"
                
        except Exception:
            # Fallback to CPU usage as proxy
            if psutil is None:
                return "normal"  # Default if psutil not available
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 50:
                return "normal"
            elif cpu_percent < 75:
                return "moderate"
            elif cpu_percent < 90:
                return "high"
            else:
                return "critical"
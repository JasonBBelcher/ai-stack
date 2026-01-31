"""
Updated Controller - Integration with new generic model system
"""
import json
import time
import subprocess
from typing import Dict, Any, Optional

from src.enhanced_config import AIStackConfig, ModelType
from src.capabilities import ModelCapabilities, RoleRequirements
from src.prompt_templates import PromptTemplates, PromptConfig
from src.memory_manager import MemoryManager


class WorkflowResult:
    """Result of a workflow execution"""
    def __init__(self):
        self.success = False
        self.plan = None
        self.critique = None
        self.output = None
        self.error = None
        self.execution_time = 0.0
        self.memory_used = 0.0


class EnhancedAIStackController:
    """Enhanced controller using new generic model system"""
    
    def __init__(self, config_path: Optional[str] = None, profile_name: Optional[str] = None):
        # Initialize enhanced configuration system
        self.config = AIStackConfig(config_path, profile_name)
        self.memory_manager = MemoryManager()
        self.prompt_templates = PromptTemplates()
        
        # Take initial memory snapshot
        self.initial_memory = self.memory_manager.take_memory_snapshot()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health = {
            "timestamp": time.time(),
            "ollama_running": False,
            "models_available": [],
            "system_memory": {},
            "thermal_state": {},
            "overall_status": "healthy"
        }
        
        # Check Ollama
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            health["ollama_running"] = result.returncode == 0
            
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                health["models_available"] = models
        except Exception:
            health["ollama_running"] = False
        
        # System memory
        health["system_memory"] = self.memory_manager.get_memory_report()
        
        # Thermal state
        health["thermal_state"] = self.memory_manager.get_thermal_state()
        
        # Overall status
        if not health["ollama_running"]:
            health["overall_status"] = "ollama_down"
        elif len(health["models_available"]) == 0:
            health["overall_status"] = "no_models"
        elif health["thermal_state"].get("score", 0) > 0.8:
            health["overall_status"] = "thermal_throttle"
        elif health["system_memory"]["current"]["system_memory"]["percent_used"] > 85:
            health["overall_status"] = "memory_pressure"
        
        return health
    
    def call_model(self, model_config, prompt: str, role: str) -> str:
        """Call a model using the new system"""
        try:
            if model_config.ollama_name:  # Ollama model
                return self._call_ollama_model(model_config.ollama_name, prompt)
            else:  # Cloud model
                return self._call_cloud_model(model_config.name, prompt, role)
                
        except Exception as e:
            raise RuntimeError(f"Error calling model {model_config.name}: {e}")
    
    def _call_ollama_model(self, ollama_name: str, prompt: str) -> str:
        """Call Ollama model"""
        # Build the command
        cmd = ["ollama", "run", ollama_name, prompt]
        
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Ollama call failed: {result.stderr}")
        
        return result.stdout.strip()
    
    def _call_cloud_model(self, model_name: str, prompt: str, role: str) -> str:
        """Call cloud model (placeholder for now)"""
        # TODO: Implement cloud model integration
        print(f"Cloud model call not yet implemented for {model_name}")
        return f"Cloud model {model_name} would process: {prompt}"
    
    def planning_phase(self, user_input: str, context: str = "") -> tuple:
        """Execute the planning phase with new system"""
        try:
            # Get model configuration for planner role
            model_config = self.config.get_model_for_role("planner")
            if not model_config:
                return None, "Failed to get planner model configuration"
            
            # Create planner prompt
            prompt_config = self.prompt_templates.get_planner_config()
            user_prompt = self.prompt_templates.format_prompt(
                prompt_config.user_template,
                user_input=user_input,
                context=context
            )
            
            full_prompt = f"{prompt_config.system_prompt}\n\n{user_prompt}"
            
            # Call the model
            response = self.call_model(model_config, full_prompt, "planner")
            
            # Parse JSON response
            try:
                plan = json.loads(response)
                # Validate plan structure
                is_valid, risk_score = self.prompt_templates.validate_plan_quality(plan)
                if not is_valid:
                    return None, f"Invalid plan structure: {risk_score}"
                
                return plan, ""
                
            except json.JSONDecodeError as e:
                return None, f"Failed to parse plan JSON: {e}"
            
        except Exception as e:
            return None, f"Planning phase error: {e}"
    
    def critique_phase(self, plan: Dict[str, Any], max_iterations: int = 3) -> tuple:
        """Execute the critique phase with new system"""
        try:
            # Get model configuration for critic role
            model_config = self.config.get_model_for_role("critic")
            if not model_config:
                return False, plan, "Failed to get critic model configuration"
            
            current_plan = plan
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Create critique prompt
                prompt_config = self.prompt_templates.get_critic_config()
                user_prompt = self.prompt_templates.format_prompt(
                    prompt_config.user_template,
                    plan=json.dumps(current_plan, indent=2)
                )
                
                full_prompt = f"{prompt_config.system_prompt}\n\n{user_prompt}"
                
                # Get critique
                critique_response = self.call_model(model_config, full_prompt, "critic")
                critique = json.loads(critique_response)
                
                # Check if plan is valid
                if critique.get("is_valid", False) and critique.get("risk_score", 1.0) < 0.3:
                    return True, current_plan, ""
                
                # If this is the last iteration, return with current plan
                if iteration >= max_iterations:
                    return False, current_plan, f"Max iterations reached. Final risk score: {critique.get('risk_score', 1.0)}"
                
                # For now, skip refinement (would need additional model call)
                break
            
            return False, current_plan, "Critique loop completed without full validation"
            
        except Exception as e:
            return False, plan, f"Critique phase error: {e}"
    
    def execution_phase(self, plan: Dict[str, Any], additional_context: str = "") -> tuple:
        """Execute the final plan with new system"""
        try:
            # Get model configuration for executor role
            model_config = self.config.get_model_for_role("executor")
            if not model_config:
                return None, "Failed to get executor model configuration"
            
            # Create executor prompt
            prompt_config = self.prompt_templates.get_executor_config()
            user_prompt = self.prompt_templates.format_prompt(
                prompt_config.user_template,
                plan=json.dumps(plan, indent=2),
                additional_context=additional_context
            )
            
            full_prompt = f"{prompt_config.system_prompt}\n\n{user_prompt}"
            
            # Call the model
            response = self.call_model(model_config, full_prompt, "executor")
            
            return response, ""
            
        except Exception as e:
            return None, f"Execution phase error: {e}"
    
    def process_request(self, user_input: str, context: str = "", additional_context: str = "") -> WorkflowResult:
        """Process a user request through the new workflow"""
        start_time = time.time()
        result = WorkflowResult()
        
        try:
            # Health check first
            health = self.health_check()
            if health["overall_status"] != "healthy":
                result.error = f"System health issue: {health['overall_status']}"
                return result
            
            # Phase 1: Planning
            print("Starting planning phase...")
            plan, error = self.planning_phase(user_input, context)
            if error:
                result.error = f"Planning failed: {error}"
                return result
            
            result.plan = plan
            print(f"Plan created with {len(plan.get('steps', []))} steps")
            
            # Phase 2: Critique
            print("Starting critique phase...")
            is_valid, final_plan, critique_error = self.critique_phase(plan)
            if not is_valid and critique_error:
                print(f"Critique warnings: {critique_error}")
            
            result.plan = final_plan
            print("Critique phase completed")
            
            # Phase 3: Execution
            print("Starting execution phase...")
            output, error = self.execution_phase(final_plan, additional_context)
            if error:
                result.error = f"Execution failed: {error}"
                return result
            
            result.output = output
            result.success = True
            
            # Calculate execution metrics
            final_memory = self.memory_manager.take_memory_snapshot()
            result.execution_time = time.time() - start_time
            result.memory_used = final_memory.used_gb - self.initial_memory.used_gb
            
            print(f"Workflow completed in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.error = f"Workflow error: {e}"
        
        return result
    
    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all available models"""
        return self.config.get_all_models()
    
    def refresh_models(self) -> None:
        """Refresh model discovery"""
        self.config.refresh_models()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status with new system"""
        return {
            "health": self.health_check(),
            "config": self.config.get_system_status(),
            "models": self.config.get_all_models(),
            "profiles": self.config.get_available_profiles()
        }
    
    def get_model_for_role_info(self, role: str) -> Dict[str, Any]:
        """Get information about model for a role"""
        model_config = self.config.get_model_for_role(role)
        if not model_config:
            return {"error": f"No model available for role: {role}"}
        
        capabilities = model_config.capabilities
        return {
            "model_name": model_config.name,
            "source": model_config.source,
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "memory_gb": model_config.memory_gb,
            "capabilities": {
                "context_length": capabilities.context_length if capabilities else None,
                "reasoning_strength": capabilities.reasoning_strength if capabilities else None,
                "coding_strength": capabilities.coding_strength if capabilities else None,
                "model_size": capabilities.model_size if capabilities else None
            }
        }
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile"""
        return self.config.switch_profile(profile_name)
    
    def create_profile(self, name: str, description: str) -> bool:
        """Create a new profile from current configuration"""
        return self.config.create_profile_from_current(name, description)
    
    def get_all_models(self) -> Dict[str, Any]:
        """Get all available models"""
        return self.config.get_all_models()
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all available models with information"""
        return self.config.get_all_models()
    
    def validate_model_for_role(self, model_name: str, role: str) -> Dict[str, Any]:
        """Validate if a model is suitable for a role"""
        return self.config.validate_model_for_role(model_name, role)
    
    def process_request(self, user_input: str, context: str = "", additional_context: str = "", 
                         model_overrides: Optional[Dict[str, Any]] = None,
                         temp_overrides: Optional[Dict[str, Any]] = None,
                         config_overrides: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Process a user request through the new workflow"""
        start_time = time.time()
        result = WorkflowResult()
        
        try:
            # Health check first
            health = self.health_check()
            if health["overall_status"] != "healthy":
                result.error = f"System health issue: {health['overall_status']}"
                return result
            
            # Phase 1: Planning
            print("Starting planning phase...")
            plan, error = self.planning_phase(user_input, context)
            if error:
                result.error = f"Planning failed: {error}"
                return result
            
            result.plan = plan
            print(f"Plan created with {len(plan.get('steps', []))} steps")
            
            # Phase 2: Critique
            print("Starting critique phase...")
            is_valid, final_plan, critique_error = self.critique_phase(plan)
            if not is_valid and critique_error:
                print(f"Critique warnings: {critique_error}")
            
            result.plan = final_plan
            print("Critique phase completed")
            
            # Phase 3: Execution
            print("Starting execution phase...")
            output, error = self.execution_phase(final_plan, additional_context)
            if error:
                result.error = f"Execution failed: {error}"
                return result
            
            result.output = output
            result.success = True
            
            # Calculate execution metrics
            final_memory = self.memory_manager.take_memory_snapshot()
            result.execution_time = time.time() - start_time
            result.memory_used = final_memory.used_gb - self.initial_memory.used_gb
            
            print(f"Workflow completed in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.error = f"Workflow error: {e}"
        
        return result
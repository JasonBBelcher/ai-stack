"""
Main Controller - Orchestrates the AI stack workflow
"""
import json
import time
import asyncio
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from src.model_manager import ModelManager, ModelState
from src.prompt_templates import PromptTemplates, PromptConfig
from src.memory_manager import MemoryManager
from src.config import AIStackConfig, ModelType


@dataclass
class WorkflowResult:
    """Result of a workflow execution"""
    success: bool
    plan: Optional[Dict[str, Any]] = None
    critique: Optional[Dict[str, Any]] = None
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: float = 0.0


class AIStackController:
    """Main controller for the AI stack workflow"""
    
    def __init__(self, config: Optional[AIStackConfig] = None):
        self.config = config or AIStackConfig()
        self.model_manager = ModelManager()
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
        health["ollama_running"] = self.model_manager.check_ollama_status()
        
        # Check available models
        try:
            result = subprocess.run(
                ["ollama", "list"],
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
                health["models_available"] = models
        except Exception:
            pass
        
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
    
    def call_ollama(self, model_name: str, prompt: str, config: PromptConfig) -> str:
        """Call Ollama API with a model and prompt"""
        try:
            # Build the command
            cmd = ["ollama", "run", model_name, prompt]
            
            # Execute the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.ollama.timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Ollama call failed: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Model call timed out after {self.config.ollama.timeout}s")
        except Exception as e:
            raise RuntimeError(f"Error calling model {model_name}: {e}")
    
    def planning_phase(self, user_input: str, context: str = "") -> Tuple[Optional[Dict[str, Any]], str]:
        """Execute the planning phase"""
        try:
            # Load planner model
            model_config = self.config.get_planner_config()
            state = self.model_manager.safe_load_model(model_config.ollama_name)
            
            if state != ModelState.LOADED:
                return None, f"Failed to load planner model: {model_config.ollama_name}"
            
            # Create planner prompt
            prompt_config = self.prompt_templates.get_planner_config()
            user_prompt = self.prompt_templates.format_prompt(
                prompt_config.user_template,
                user_input=user_input,
                context=context
            )
            
            full_prompt = f"{prompt_config.system_prompt}\n\n{user_prompt}"
            
            # Call the model
            response = self.call_ollama(model_config.ollama_name, full_prompt, prompt_config)
            
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
        
        finally:
            # Unload planner model
            self.model_manager.unload_model(model_config.ollama_name)
    
    def critique_phase(self, plan: Dict[str, Any], max_iterations: int = 3) -> Tuple[bool, Dict[str, Any], str]:
        """Execute the critique phase with iterative refinement"""
        try:
            critic_config = self.config.get_critic_config()
            refinement_config = self.prompt_templates.get_refinement_config()
            
            current_plan = plan
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Load critic model
                critic_model = critic_config.ollama_name
                state = self.model_manager.safe_load_model(critic_model)
                
                if state != ModelState.LOADED:
                    return False, current_plan, f"Failed to load critic model: {critic_model}"
                
                try:
                    # Create critique prompt
                    prompt_config = self.prompt_templates.get_critic_config()
                    user_prompt = self.prompt_templates.format_prompt(
                        prompt_config.user_template,
                        plan=json.dumps(current_plan, indent=2)
                    )
                    
                    full_prompt = f"{prompt_config.system_prompt}\n\n{user_prompt}"
                    
                    # Get critique
                    critique_response = self.call_ollama(critic_model, full_prompt, prompt_config)
                    critique = json.loads(critique_response)
                    
                    # Check if plan is valid
                    if critique.get("is_valid", False) and critique.get("risk_score", 1.0) < 0.3:
                        return True, current_plan, ""
                    
                    # If this is the last iteration, return with current plan
                    if iteration >= max_iterations:
                        return False, current_plan, f"Max iterations reached. Final risk score: {critique.get('risk_score', 1.0)}"
                    
                    # Refine the plan
                    refinement_prompt = self.prompt_templates.format_prompt(
                        refinement_config.user_template,
                        original_plan=json.dumps(current_plan, indent=2),
                        critique=json.dumps(critique, indent=2)
                    )
                    
                    full_refinement_prompt = f"{refinement_config.system_prompt}\n\n{refinement_prompt}"
                    
                    # Get refined plan
                    refinement_response = self.call_ollama(critic_model, full_refinement_prompt, refinement_config)
                    refined_plan = json.loads(refinement_response)
                    
                    # Validate refined plan
                    is_valid, risk_score = self.prompt_templates.validate_plan_quality(refined_plan)
                    if is_valid:
                        current_plan = refined_plan
                    else:
                        # Keep original plan if refinement is invalid
                        pass
                
                finally:
                    # Unload critic model
                    self.model_manager.unload_model(critic_model)
                
                # Small delay between iterations
                time.sleep(1)
            
            return False, current_plan, "Critique loop completed without full validation"
            
        except Exception as e:
            return False, plan, f"Critique phase error: {e}"
    
    def execution_phase(self, plan: Dict[str, Any], additional_context: str = "") -> Tuple[Optional[str], str]:
        """Execute the final plan"""
        try:
            # Load executor model
            model_config = self.config.get_executor_config()
            state = self.model_manager.safe_load_model(model_config.ollama_name)
            
            if state != ModelState.LOADED:
                return None, f"Failed to load executor model: {model_config.ollama_name}"
            
            # Create executor prompt
            prompt_config = self.prompt_templates.get_executor_config()
            user_prompt = self.prompt_templates.format_prompt(
                prompt_config.user_template,
                plan=json.dumps(plan, indent=2),
                additional_context=additional_context
            )
            
            full_prompt = f"{prompt_config.system_prompt}\n\n{user_prompt}"
            
            # Call the model
            response = self.call_ollama(model_config.ollama_name, full_prompt, prompt_config)
            
            return response, ""
            
        except Exception as e:
            return None, f"Execution phase error: {e}"
        
        finally:
            # Unload executor model
            self.model_manager.unload_model(model_config.ollama_name)
    
    def process_request(self, user_input: str, context: str = "", additional_context: str = "") -> WorkflowResult:
        """Process a user request through the full workflow"""
        start_time = time.time()
        result = WorkflowResult(success=False)
        
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
        
        finally:
            # Ensure all models are unloaded
            self.model_manager.unload_all_models()
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "health": self.health_check(),
            "memory": self.memory_manager.get_memory_report(),
            "loaded_models": self.model_manager.get_loaded_models(),
            "config": self.config.get_optimization_settings()
        }
"""
Simplified Controller - Basic model calling without complex workflows
"""
import json
import time
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

from src.enhanced_config import AIStackConfig, ModelType
from src.capabilities import ModelCapabilities, RoleRequirements
from src.prompt_templates import PromptTemplates, PromptConfig
from src.memory_manager import MemoryManager
from src.rag import ContextRetriever
from src.prompt_engineer import IntentRouter, IntentType

# Cascade components
from src.cascade.ambiguity_detector import AmbiguityDetector
from src.cascade.clarification_engine import ClarificationEngine
from src.cascade.constraint_extractor import ConstraintExtractor
from src.cascade.feasibility_validator import FeasibilityValidator
from src.cascade.path_generator import PathGenerator
from src.cascade.execution_planner import ExecutionPlanner
from src.cascade.progress_monitor import ProgressMonitor
from src.cascade.prompt_adjuster import PromptAdjuster


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
        self.metadata = {}


class SimplifiedAIStackController:
    """Simplified controller for basic model calling"""
    
    def __init__(self, config_path: Optional[str] = None, profile_name: Optional[str] = None, project_path: Optional[str] = None):
        # Initialize enhanced configuration system
        self.config = AIStackConfig(config_path, profile_name)
        self.memory_manager = MemoryManager()
        self.prompt_templates = PromptTemplates()
        
        # Initialize RAG components
        self.project_path = project_path
        self.rag_retriever = None
        self.intent_router = IntentRouter()
        
        # Initialize RAG if project path is provided
        if self.project_path:
            self._initialize_rag()
        
        # Initialize cascade components
        self.ambiguity_detector = AmbiguityDetector()
        self.clarification_engine = ClarificationEngine(verbosity="normal")
        self.constraint_extractor = ConstraintExtractor()
        self.feasibility_validator = FeasibilityValidator()
        self.path_generator = PathGenerator()
        self.execution_planner = ExecutionPlanner()
        self.progress_monitor = ProgressMonitor()
        self.prompt_adjuster = PromptAdjuster()
        
        # Cascade state
        self.cascade_enabled = True
        self.current_execution_plan = None
        self.current_monitoring_session = None
        
        # Take initial memory snapshot
        self.initial_memory = self.memory_manager.take_memory_snapshot()
    
    def _initialize_rag(self):
        """Initialize RAG retriever for the project."""
        try:
            from src.rag import CodeEmbedder, FAISSVectorStore
            
            project_dir = Path(self.project_path)
            if not project_dir.exists():
                print(f"Warning: Project path {self.project_path} does not exist")
                return
            
            # Look for index file (try both .ai-stack and .ai-stack-index locations)
            index_path = str(project_dir / ".ai-stack-index")
            
            # Fallback to .ai-stack directory
            if not Path(f"{index_path}.index").exists():
                index_path = str(project_dir / ".ai-stack" / "code_index")
            
            if not Path(f"{index_path}.index").exists():
                print(f"Warning: No RAG index found at {index_path}.index")
                print("Run 'python main.py --index <path>' to create an index")
                return
            
            # Initialize embedder
            embedder = CodeEmbedder(model_name="BAAI/bge-small-en-v1.5")
            
            # Initialize vector store and load index
            vector_store = FAISSVectorStore(index_type="Flat", dimension=embedder.get_embedding_dimension())
            vector_store.load(index_path)
            
            # Initialize retriever
            self.rag_retriever = ContextRetriever(embedder, vector_store)
            print(f"RAG initialized for project: {self.project_path}")
            
        except Exception as e:
            print(f"Warning: Failed to initialize RAG: {e}")
            self.rag_retriever = None
    
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
        """Call a model using basic system"""
        try:
            if hasattr(model_config, 'ollama_name'):  # Ollama model
                return self._call_ollama_model(model_config.ollama_name, prompt)
            else:  # Cloud model
                return self._call_cloud_model(model_config.name, prompt, role)
                
        except Exception as e:
            raise RuntimeError(f"Error calling model {model_config.name}: {e}")
    
    def _call_ollama_model(self, ollama_name: str, prompt: str) -> str:
        """Call Ollama model"""
        # Use ollama run with flags to suppress interactive output
        cmd = ["ollama", "run", ollama_name, "--nowordwrap"]
        
        # Execute the command
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Ollama call failed: {result.stderr}")
        
        # Clean up terminal escape sequences from output
        import re
        clean_output = re.sub(r'\x1B\[[0-9;]*[mK]', '', result.stdout.strip())
        return clean_output
    
    def _call_cloud_model(self, model_name: str, prompt: str, role: str) -> str:
        """Call cloud model (placeholder for now)"""
        # TODO: Implement cloud model integration
        print(f"Cloud model call not yet implemented for {model_name}")
        return f"Cloud model {model_name} would process: {prompt}"
    
    def process_request(self, user_input: str, context: str = "", 
                     additional_context: str = "") -> WorkflowResult:
        """Process a simple request with RAG context and intent-based routing"""
        result = WorkflowResult()
        start_time = time.time()
        
        try:
            # Classify user intent
            intent_info = self.intent_router.get_intent_info(user_input)
            intent = IntentType(intent_info["intent"])
            
            # Retrieve RAG context if available
            rag_context = ""
            if self.rag_retriever:
                try:
                    rag_context = self.rag_retriever.retrieve_and_format(user_input)
                    if rag_context:
                        print(f"Retrieved {len(rag_context)} characters of code context")
                except Exception as e:
                    print(f"Warning: Failed to retrieve RAG context: {e}")
            
            # Get appropriate prompt template based on intent
            prompt_config = self._get_prompt_config_for_intent(intent)
            
            # Build prompt with context
            if rag_context:
                # Use RAG-aware template
                prompt = prompt_config.user_template.format(
                    user_input=user_input,
                    rag_context=rag_context,
                    plan="",
                    additional_context=""
                )
            else:
                # Use standard template
                prompt = prompt_config.user_template.format(
                    user_input=user_input,
                    rag_context="",
                    plan="",
                    additional_context=""
                )
            
            # Get model configuration for executor role
            model_config = self.config.get_model_for_role("executor")
            if not model_config:
                result.error = "Failed to get executor model configuration"
                return result
            
            # Call the model with the constructed prompt
            response = self.call_model(model_config, prompt, "executor")
            
            result.output = response
            result.success = True
            
            # Add metadata about intent and RAG usage
            result.metadata = {
                "intent": intent.value,
                "intent_confidence": intent_info["confidence"],
                "rag_used": bool(rag_context),
                "rag_context_length": len(rag_context) if rag_context else 0,
                "template_used": prompt_config.name
            }
            
        except Exception as e:
            result.error = f"Request processing failed: {e}"
        
        result.execution_time = time.time() - start_time
        
        # Calculate memory used
        final_memory = self.memory_manager.take_memory_snapshot()
        result.memory_used = final_memory.used_gb - self.initial_memory.used_gb
        
        return result
    
    def process_request_with_cascade(self, user_input: str, context: str = "",
                                    additional_context: str = "",
                                    enable_cascade: bool = True) -> WorkflowResult:
        """
        Process a request with cascade ambiguity resolution and adaptive execution.
        
        Args:
            user_input: User's request
            context: Additional context
            additional_context: More context
            enable_cascade: Whether to use cascade processing
            
        Returns:
            WorkflowResult with cascade metadata
        """
        result = WorkflowResult()
        start_time = time.time()
        
        try:
            # Step 1: Detect ambiguities
            if enable_cascade:
                print("\n[Cascade] Step 1: Detecting ambiguities...")
                ambiguities = self.ambiguity_detector.detect(user_input)
                
                if ambiguities:
                    print(f"[Cascade] Detected {len(ambiguities)} ambiguities")
                    
                    # Step 2: Clarify ambiguities (auto-skip for now, could be interactive)
                    print("[Cascade] Step 2: Clarifying ambiguities...")
                    session = self.clarification_engine.start_session(ambiguities)
                    
                    # Auto-skip all ambiguities for non-interactive mode
                    for ambiguity in session.ambiguities:
                        self.clarification_engine.process_choice(session, "skip")
                    
                    clarified_input = self.clarification_engine.apply_clarifications(user_input, session)
                    print(f"[Cascade] Clarified request: {clarified_input}")
                else:
                    clarified_input = user_input
                    print("[Cascade] No ambiguities detected")
            else:
                clarified_input = user_input
            
            # Step 3: Extract constraints
            if enable_cascade:
                print("\n[Cascade] Step 3: Extracting constraints...")
                constraints = self.constraint_extractor.extract(user_input)
                print(f"[Cascade] Extracted {len(constraints)} constraints")
                for constraint in constraints:
                    print(f"  - {constraint.type.value}: {constraint.value}")
            else:
                constraints = []
            
            # Step 4: Validate feasibility
            if enable_cascade and constraints:
                print("\n[Cascade] Step 4: Validating feasibility...")
                feasibility = self.feasibility_validator.validate(clarified_input, constraints)
                print(f"[Cascade] Feasibility: {feasibility.status.value} (confidence: {feasibility.confidence:.2f})")
                
                if feasibility.blockers:
                    print("[Cascade] Blockers:")
                    for blocker in feasibility.blockers:
                        print(f"  - {blocker}")
            else:
                feasibility = None
            
            # Step 5: Generate execution paths (if constraints provided)
            if enable_cascade and constraints:
                print("\n[Cascade] Step 5: Generating execution paths...")
                paths = self.path_generator.generate_paths(clarified_input, constraints, feasibility)
                print(f"[Cascade] Generated {len(paths)} execution paths")
                
                # Select best path
                best_path = self.path_generator.select_best_path(paths, constraints)
                if best_path:
                    print(f"[Cascade] Selected path: {best_path.path_type.value}")
                    print(f"  Description: {best_path.description}")
                    print(f"  Estimated time: {best_path.estimated_time:.1f} hours")
            else:
                best_path = None
            
            # Step 6: Create execution plan
            if enable_cascade:
                print("\n[Cascade] Step 6: Creating execution plan...")
                self.current_execution_plan = self.execution_planner.create_plan(
                    clarified_input, constraints, best_path
                )
                print(f"[Cascade] Created plan with {len(self.current_execution_plan.subtasks)} subtasks")
                print(f"  Total estimated time: {self.current_execution_plan.total_estimated_time:.1f} hours")
                print(f"  Workflow type: {self.current_execution_plan.workflow_type}")
            else:
                self.current_execution_plan = None
            
            # Step 7: Start progress monitoring
            if enable_cascade and self.current_execution_plan:
                print("\n[Cascade] Step 7: Starting progress monitoring...")
                self.progress_monitor.start_monitoring(self.current_execution_plan)
                self.current_monitoring_session = True
                print("[Cascade] Monitoring started")
            else:
                self.current_monitoring_session = False
            
            # Step 8: Execute the request using standard processing
            print("\n[Cascade] Step 8: Executing request...")
            standard_result = self.process_request(clarified_input, context, additional_context)
            
            # Update progress
            if self.current_monitoring_session and self.current_execution_plan:
                # Mark first subtask as completed
                if self.current_execution_plan.subtasks:
                    from cascade.execution_planner import TaskStatus
                    
                    first_subtask = self.current_execution_plan.subtasks[0]
                    self.execution_planner.update_subtask_status(
                        self.current_execution_plan, first_subtask.id,
                        TaskStatus.COMPLETED if standard_result.success else TaskStatus.FAILED
                    )
                    
                    if standard_result.success:
                        self.progress_monitor.update_progress(
                            self.current_execution_plan, first_subtask.id,
                            TaskStatus.COMPLETED,
                            output=standard_result.output
                        )
                    else:
                        self.progress_monitor.update_progress(
                            self.current_execution_plan, first_subtask.id,
                            TaskStatus.FAILED,
                            error=standard_result.error
                        )
            
            # Step 9: Get final progress report
            if self.current_monitoring_session and self.current_execution_plan:
                print("\n[Cascade] Step 9: Getting progress report...")
                progress_report = self.progress_monitor.generate_report(self.current_execution_plan)
                print(f"[Cascade] Progress: {progress_report.progress_percentage:.1f}%")
                print(f"  Completed: {progress_report.completed_subtasks}/{progress_report.total_subtasks}")
                print(f"  Obstacles: {len(progress_report.obstacles)}")
                print(f"  Alerts: {len(progress_report.alerts)}")
                
                # Add cascade metadata to result
                result.metadata = {
                    **standard_result.metadata,
                    "cascade_enabled": True,
                    "ambiguities_detected": len(ambiguities) if enable_cascade else 0,
                    "constraints_extracted": len(constraints) if enable_cascade else 0,
                    "feasibility_status": feasibility.status.value if feasibility else None,
                    "execution_path": best_path.path_type.value if best_path else None,
                    "subtasks_total": len(self.current_execution_plan.subtasks) if self.current_execution_plan else 0,
                    "progress_percentage": progress_report.progress_percentage,
                    "obstacles_detected": len(progress_report.obstacles),
                    "alerts_generated": len(progress_report.alerts)
                }
            else:
                result.metadata = {
                    **standard_result.metadata,
                    "cascade_enabled": False
                }
            
            # Copy standard result
            result.success = standard_result.success
            result.output = standard_result.output
            result.error = standard_result.error
            result.plan = standard_result.plan
            result.critique = standard_result.critique
            
            print("\n[Cascade] Processing complete")
            
        except Exception as e:
            result.error = f"Cascade processing failed: {e}"
            import traceback
            traceback.print_exc()
        
        result.execution_time = time.time() - start_time
        
        # Calculate memory used
        final_memory = self.memory_manager.take_memory_snapshot()
        result.memory_used = final_memory.used_gb - self.initial_memory.used_gb
        
        return result
    
    def adjust_prompt_for_obstacle(self, original_prompt: str, 
                                   obstacle: Obstacle,
                                   context: str = "") -> str:
        """
        Adjust a prompt when an obstacle is encountered.
        
        Args:
            original_prompt: The original prompt that failed
            obstacle: The obstacle that was encountered
            context: Additional context
            
        Returns:
            Adjusted prompt string
        """
        print(f"\n[Cascade] Adjusting prompt for obstacle: {obstacle.obstacle_type.value}")
        
        # Create a dummy subtask for the prompt_adjuster
        from cascade.execution_planner import Subtask, TaskStatus, TaskPriority
        
        dummy_subtask = Subtask(
            id="temp_subtask",
            description="Temporary subtask for prompt adjustment",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            estimated_time=1.0,
            required_model="llama3.1:8b",
            prompt=original_prompt,
            output_format="text",
            context={"original_context": context}
        )
        
        # Analyze obstacle and generate adjustments
        adjustments = self.prompt_adjuster.analyze_obstacle(
            obstacle, dummy_subtask, {"context": context}
        )
        
        print(f"[Cascade] Generated {len(adjustments)} adjustments")
        
        # Select best adjustment
        best_adjustment = self.prompt_adjuster.select_best_adjustment(
            adjustments, obstacle
        )
        
        if best_adjustment:
            print(f"[Cascade] Selected adjustment: {best_adjustment.type.value}")
            print(f"  Reason: {best_adjustment.reason}")
            
            # Apply adjustment
            adjusted_prompt = self.prompt_adjuster._apply_adjustment(
                original_prompt, best_adjustment
            )
            
            print(f"[Cascade] Adjusted prompt: {adjusted_prompt[:100]}...")
            return adjusted_prompt
        else:
            print("[Cascade] No suitable adjustment found, using original prompt")
            return original_prompt
    
    def get_cascade_status(self) -> dict:
        """
        Get current cascade system status.
        
        Returns:
            Dictionary with cascade status information
        """
        status = {
            "cascade_enabled": self.cascade_enabled,
            "execution_plan_active": self.current_execution_plan is not None,
            "monitoring_active": self.current_monitoring_session,
            "components": {
                "ambiguity_detector": self.ambiguity_detector is not None,
                "clarification_engine": self.clarification_engine is not None,
                "constraint_extractor": self.constraint_extractor is not None,
                "feasibility_validator": self.feasibility_validator is not None,
                "path_generator": self.path_generator is not None,
                "execution_planner": self.execution_planner is not None,
                "progress_monitor": self.progress_monitor is not None,
                "prompt_adjuster": self.prompt_adjuster is not None
            }
        }
        
        if self.current_execution_plan:
            from cascade.execution_planner import TaskStatus
            
            status["execution_plan"] = {
                "total_subtasks": len(self.current_execution_plan.subtasks),
                "completed_subtasks": sum(
                    1 for s in self.current_execution_plan.subtasks 
                    if s.status == TaskStatus.COMPLETED
                ),
                "workflow_type": self.current_execution_plan.workflow_type,
                "total_estimated_time": self.current_execution_plan.total_estimated_time
            }
        
        return status
    
    def _get_prompt_config_for_intent(self, intent: IntentType) -> PromptConfig:
        """Get the appropriate prompt configuration based on intent."""
        if intent == IntentType.DEBUG:
            return self.prompt_templates.get_debug_config()
        elif intent == IntentType.GENERATE:
            return self.prompt_templates.get_generate_config()
        elif intent == IntentType.EXPLAIN:
            return self.prompt_templates.get_explain_config()
        else:
            # Default to executor template for general requests
            return self.prompt_templates.get_executor_config()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "health": self.health_check(),
            "config": self.config.get_system_config().__dict__,
            "models": self.config.get_all_models(),
            "profiles": self.config.get_available_profiles()
        }
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get available models with information"""
        return self.config.get_all_models()
    
    def get_model_for_role_info(self, role: str) -> Dict[str, Any]:
        """Get information about model for a role"""
        model_config = self.config.get_model_for_role(role)
        if not model_config:
            return {"error": f"No model available for role: {role}"}
        
        capabilities = model_config.capabilities
        source_value = model_config.source
        if hasattr(source_value, 'value'):
            source_value = source_value.value
        
        return {
            "model_name": model_config.name,
            "source": source_value,
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "memory_gb": model_config.memory_gb,
            "validated": getattr(model_config, 'validated', False),
            "capabilities": {
                "context_length": capabilities.context_length if capabilities else None,
                "reasoning_strength": capabilities.reasoning_strength if capabilities else None,
                "coding_strength": capabilities.coding_strength if capabilities else None,
                "model_size": capabilities.model_size if capabilities else None
            }
        }
    
    def get_available_profiles(self) -> Dict[str, Any]:
        """Get available user profiles"""
        return self.config.profile_manager.list_profiles()
    
    def refresh_models(self) -> Dict[str, Any]:
        """Refresh model discovery"""
        self.config.model_registry.discover_models(force_rediscovery=True)
        return {"status": "refreshed", "models": list(self.config.model_registry.models.keys())}
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
                    rag_context=rag_context
                )
            else:
                # Use standard template
                prompt = prompt_config.user_template.format(user_input=user_input)
            
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
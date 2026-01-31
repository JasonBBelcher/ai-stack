"""
Integration tests for the AI stack
"""
import pytest
import json
import subprocess
import time

from src.controller import AIStackController, WorkflowResult
from src.config import AIStackConfig


class TestIntegration:
    """Integration tests for the complete AI stack"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.config = AIStackConfig()
        self.controller = AIStackController(self.config)
    
    def test_system_health(self):
        """Test that the system can perform a health check"""
        health = self.controller.health_check()
        
        # Check structure
        required_keys = ["timestamp", "ollama_running", "models_available", 
                        "system_memory", "thermal_state", "overall_status"]
        for key in required_keys:
            assert key in health
        
        # Check that we have some models available (assuming Ollama is set up)
        if health["ollama_running"]:
            assert len(health["models_available"]) > 0
    
    def test_memory_manager(self):
        """Test memory manager functionality"""
        memory_report = self.controller.memory_manager.get_memory_report()
        
        # Check structure
        assert "current" in memory_report
        assert "thermal_state" in memory_report
        assert "trend" in memory_report
        assert "recommendations" in memory_report
        
        # Check current memory info
        current = memory_report["current"]
        assert "system_memory" in current
        assert "gpu_memory_gb" in current
        
        system_memory = current["system_memory"]
        assert "total_gb" in system_memory
        assert "used_gb" in system_memory
        assert "available_gb" in system_memory
        assert "percent_used" in system_memory
    
    def test_prompt_templates(self):
        """Test prompt template functionality"""
        templates = self.controller.prompt_templates
        
        # Test getting all configs
        all_configs = templates.get_all_configs()
        assert "planner" in all_configs
        assert "critic" in all_configs
        assert "executor" in all_configs
        assert "refinement" in all_configs
        
        # Test planner config
        planner_config = templates.get_planner_config()
        assert planner_config.temperature == 0.2
        assert planner_config.max_tokens == 2000
        
        # Test template formatting
        formatted = templates.format_prompt(
            "Hello {name}!",
            name="World"
        )
        assert formatted == "Hello World!"
        
        # Test plan validation
        valid_plan = {
            "plan_summary": "Test plan",
            "steps": [
                {
                    "step_number": 1,
                    "description": "Test step",
                    "dependencies": [],
                    "tools_needed": [],
                    "estimated_time": "1 minute"
                }
            ],
            "total_steps": 1,
            "complexity": "simple"
        }
        
        is_valid, risk_score = templates.validate_plan_quality(valid_plan)
        assert is_valid == True
        assert risk_score == 0.1
    
    def test_configuration(self):
        """Test configuration system"""
        config = self.controller.config
        
        # Test model configs
        planner_config = config.get_planner_config()
        assert planner_config.type.value == "planner"
        assert planner_config.ollama_name == "mistral:latest"
        
        executor_config = config.get_executor_config()
        assert executor_config.type.value == "executor"
        assert executor_config.ollama_name == "qwen2.5:14b"
        
        # Test configuration validation
        issues = config.validate_configuration()
        assert isinstance(issues, list)
        
        # Test optimization settings
        settings = config.get_optimization_settings()
        assert "apple_silicon_optimized" in settings
        assert "memory_management" in settings
        assert "thermal_management" in settings
    
    @pytest.mark.slow
    def test_end_to_end_workflow_mock(self):
        """Test end-to-end workflow with mocked model calls"""
        # This test would require actual Ollama models to be loaded
        # For now, we'll test the workflow structure without actual model calls
        
        # Test that the workflow components can be called
        assert hasattr(self.controller, 'planning_phase')
        assert hasattr(self.controller, 'critique_phase')
        assert hasattr(self.controller, 'execution_phase')
        assert hasattr(self.controller, 'process_request')
        
        # Test workflow result structure
        result = self.controller.process_request(
            user_input="test input",
            context="test context"
        )
        
        # Should return a WorkflowResult object (may fail due to no models)
        assert isinstance(result, WorkflowResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'plan')
        assert hasattr(result, 'output')
        assert hasattr(result, 'error')
        assert hasattr(result, 'execution_time')
        assert hasattr(result, 'memory_used')
    
    def test_model_safety_checks(self):
        """Test model loading safety checks"""
        manager = self.controller.model_manager
        
        # Test memory estimation
        mistral_memory = manager.get_model_memory_estimate("mistral:latest")
        assert isinstance(mistral_memory, float)
        assert mistral_memory > 0
        
        qwen_memory = manager.get_model_memory_estimate("qwen2.5:14b")
        assert isinstance(qwen_memory, float)
        assert qwen_memory > mistral_memory  # 14B should be larger than 7B
        
        # Test memory availability check
        can_load, reason = manager.can_load_model("mistral:latest")
        assert isinstance(can_load, bool)
        assert isinstance(reason, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
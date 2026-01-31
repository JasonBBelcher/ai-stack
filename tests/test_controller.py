"""
Tests for Controller
"""
import pytest
import subprocess
from unittest.mock import Mock, patch

from src.controller import AIStackController, WorkflowResult
from src.config import AIStackConfig


class TestController:
    """Test cases for AIStackController"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = AIStackConfig()
        self.controller = AIStackController(self.config)
    
    def test_initialization(self):
        """Test controller initialization"""
        assert self.controller.config == self.config
        assert self.controller.model_manager is not None
        assert self.controller.memory_manager is not None
        assert self.controller.prompt_templates is not None
    
    @patch('subprocess.run')
    def test_health_check(self, mock_run):
        """Test system health check"""
        # Mock Ollama list output
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NAME ID SIZE\nmistral abc123 4.4GB\nqwen2.5 def456 9.0GB"
        )
        
        health = self.controller.health_check()
        assert "timestamp" in health
        assert "ollama_running" in health
        assert "models_available" in health
        assert "system_memory" in health
        assert "thermal_state" in health
        assert "overall_status" in health
    
    def test_workflow_result_creation(self):
        """Test WorkflowResult creation"""
        result = WorkflowResult(
            success=True,
            execution_time=10.5,
            memory_used=2.3
        )
        assert result.success == True
        assert result.execution_time == 10.5
        assert result.memory_used == 2.3
        assert result.output is None
        assert result.error is None
    
    @patch('subprocess.run')
    def test_call_ollama(self, mock_run):
        """Test Ollama API calling"""
        # Mock successful call
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Test response"
        )
        
        config = Mock()
        response = self.controller.call_ollama("mistral:latest", "test prompt", config)
        assert response == "Test response"
        
        # Test timeout
        mock_run.side_effect = Mock(side_effect=Mock(side_effect=subprocess.TimeoutExpired("cmd", 120)))
        with pytest.raises(RuntimeError):
            self.controller.call_ollama("mistral:latest", "test prompt", config)
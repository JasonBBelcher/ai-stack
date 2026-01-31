"""
Tests for Model Manager
"""
import pytest
import time
from unittest.mock import Mock, patch

from src.model_manager import ModelManager, ModelState
from src.config import AIStackConfig


class TestModelManager:
    """Test cases for ModelManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = AIStackConfig()
        self.manager = ModelManager()
    
    def test_initialization(self):
        """Test manager initialization"""
        assert self.manager.base_url == "http://localhost:11434"
        assert len(self.manager.loaded_models) == 0
        assert "mistral" in self.manager.model_memory_usage
    
    def test_memory_estimates(self):
        """Test model memory estimation"""
        mistral_memory = self.manager.get_model_memory_estimate("mistral:latest")
        assert mistral_memory == 5.0
        
        qwen_memory = self.manager.get_model_memory_estimate("qwen2.5:14b")
        assert qwen_memory == 10.0
        
        # Test unknown model
        unknown_memory = self.manager.get_model_memory_estimate("unknown")
        assert unknown_memory == 5.0  # Default
    
    def test_memory_safety_check(self):
        """Test memory safety checks"""
        # This test may need mocking based on actual system memory
        can_load, reason = self.manager.can_load_model("mistral:latest", safety_buffer_gb=1.0)
        assert isinstance(can_load, bool)
        assert isinstance(reason, str)
    
    @patch('subprocess.run')
    def test_ollama_status_check(self, mock_run):
        """Test Ollama status checking"""
        # Test successful check
        mock_run.return_value = Mock(returncode=0, stdout="MODEL NAME")
        assert self.manager.check_ollama_status() == True
        
        # Test failed check
        mock_run.return_value = Mock(returncode=1, stderr="Error")
        assert self.manager.check_ollama_status() == False
    
    @patch('subprocess.run')
    def test_get_loaded_models(self, mock_run):
        """Test getting loaded models"""
        # Test with models loaded
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NAME ID SIZE\nmistral abc123 4.4GB\nqwen2.5 def456 9.0GB"
        )
        models = self.manager.get_loaded_models()
        assert "mistral" in models
        assert "qwen2.5" in models
        
        # Test with no models
        mock_run.return_value = Mock(returncode=0, stdout="NAME ID SIZE")
        models = self.manager.get_loaded_models()
        assert len(models) == 0
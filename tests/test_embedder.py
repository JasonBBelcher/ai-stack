"""
Unit tests for RAG Embedder component.

Tests the CodeEmbedder class for text embedding generation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.rag.embedder import CodeEmbedder


class TestCodeEmbedder:
    """Test suite for CodeEmbedder class."""
    
    @pytest.fixture
    def mock_sentence_transformer(self):
        """Create a mock SentenceTransformer model."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        
        def mock_encode(texts, **kwargs):
            if len(texts) == 0:
                return np.array([]).reshape(0, 384).astype(np.float32)
            # Generate random embeddings and normalize them
            embeddings = np.random.rand(len(texts), 384).astype(np.float32)
            # Normalize each embedding to unit length
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            return embeddings
        
        mock_model.encode = Mock(side_effect=mock_encode)
        return mock_model
    
    @pytest.fixture
    def embedder(self, mock_sentence_transformer):
        """Create a CodeEmbedder instance with mocked model."""
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
            embedder = CodeEmbedder(model_name="test-model")
            return embedder
    
    def test_embedder_initialization(self, embedder):
        """Test that CodeEmbedder initializes with correct parameters."""
        assert embedder.model_name == "test-model"
        assert embedder.model is not None
    
    def test_embedder_default_model(self):
        """Test that CodeEmbedder uses default model name."""
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            
            embedder = CodeEmbedder()
            assert embedder.model_name == "BAAI/bge-small-en-v1.5"
    
    def test_embed_texts_single_text(self, embedder):
        """Test embedding a single text."""
        texts = ["Hello, world!"]
        embeddings = embedder.embed_texts(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 1
        assert embeddings.shape[1] == 384
        assert embeddings.dtype == np.float32
    
    def test_embed_texts_multiple_texts(self, embedder):
        """Test embedding multiple texts."""
        texts = ["Hello, world!", "This is a test.", "Another example."]
        embeddings = embedder.embed_texts(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == 384
        assert embeddings.dtype == np.float32
    
    def test_embed_texts_empty_list(self, embedder):
        """Test embedding an empty list."""
        texts = []
        embeddings = embedder.embed_texts(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 0
    
    def test_embed_text_single(self, embedder):
        """Test embedding a single text using embed_text method."""
        text = "Hello, world!"
        embedding = embedder.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        assert embedding.dtype == np.float32
    
    def test_embed_text_vs_embed_texts(self, embedder):
        """Test that embed_text and embed_texts produce consistent results."""
        text = "Hello, world!"
        
        # Using embed_text
        embedding1 = embedder.embed_text(text)
        
        # Using embed_texts
        embeddings = embedder.embed_texts([text])
        embedding2 = embeddings[0]
        
        # Both should have the same shape
        assert embedding1.shape == embedding2.shape
        assert embedding1.shape == (384,)
    
    def test_get_embedding_dimension(self, embedder):
        """Test getting the embedding dimension."""
        dimension = embedder.get_embedding_dimension()
        
        assert isinstance(dimension, int)
        assert dimension == 384
    
    def test_model_encode_called_with_correct_params(self, embedder, mock_sentence_transformer):
        """Test that model.encode is called with correct parameters."""
        texts = ["Hello", "World"]
        embedder.embed_texts(texts)
        
        mock_sentence_transformer.encode.assert_called_once()
        call_args = mock_sentence_transformer.encode.call_args
        
        assert call_args[0][0] == texts
        assert call_args[1]['show_progress_bar'] == False
        assert call_args[1]['convert_to_numpy'] == True
        assert call_args[1]['normalize_embeddings'] == True
    
    def test_embed_texts_normalization(self, embedder, mock_sentence_transformer):
        """Test that embeddings are normalized."""
        texts = ["Hello, world!"]
        embeddings = embedder.embed_texts(texts)
        
        # Check that embeddings are normalized (L2 norm should be ~1)
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_allclose(norms, 1.0, rtol=1e-5)
    
    def test_embed_texts_different_inputs(self, embedder):
        """Test that different inputs produce different embeddings."""
        texts = ["Hello, world!", "Goodbye, world!"]
        embeddings = embedder.embed_texts(texts)
        
        # Embeddings should be different
        assert not np.allclose(embeddings[0], embeddings[1])
    
    def test_embed_texts_same_inputs(self, embedder):
        """Test that same inputs produce embeddings with same shape."""
        texts = ["Hello, world!", "Hello, world!"]
        embeddings = embedder.embed_texts(texts)
        
        # Both embeddings should have the same shape
        assert embeddings[0].shape == embeddings[1].shape
        assert embeddings.shape == (2, 384)
    
    def test_embed_texts_code_snippets(self, embedder):
        """Test embedding code snippets."""
        code_snippets = [
            "def hello():\n    print('Hello')",
            "function hello() {\n    console.log('Hello');\n}",
            "class MyClass:\n    def __init__(self):\n        pass"
        ]
        embeddings = embedder.embed_texts(code_snippets)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == 384
    
    def test_embed_texts_long_text(self, embedder):
        """Test embedding long text."""
        long_text = " ".join(["word"] * 1000)
        embeddings = embedder.embed_texts([long_text])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 1
        assert embeddings.shape[1] == 384
    
    def test_embed_texts_special_characters(self, embedder):
        """Test embedding text with special characters."""
        special_texts = [
            "Hello @#$%^&*()",
            "Test with émojis 🎉",
            "Unicode: 你好世界",
            "Math: E = mc²"
        ]
        embeddings = embedder.embed_texts(special_texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 4
        assert embeddings.shape[1] == 384
    
    def test_model_not_loaded_error(self):
        """Test error when model is not loaded."""
        embedder = CodeEmbedder.__new__(CodeEmbedder)
        embedder.model_name = "test-model"
        embedder.model = None
        
        with pytest.raises(RuntimeError, match="Embedding model not loaded"):
            embedder.embed_texts(["test"])
    
    def test_get_embedding_dimension_error(self):
        """Test error when getting dimension without model."""
        embedder = CodeEmbedder.__new__(CodeEmbedder)
        embedder.model_name = "test-model"
        embedder.model = None
        
        with pytest.raises(RuntimeError, match="Embedding model not loaded"):
            embedder.get_embedding_dimension()
    
    def test_model_load_error(self):
        """Test error handling when model fails to load."""
        with patch('sentence_transformers.SentenceTransformer', side_effect=ImportError("No module")):
            with pytest.raises(ImportError):
                CodeEmbedder(model_name="nonexistent-model")
    
    def test_embed_texts_error_handling(self, embedder, mock_sentence_transformer):
        """Test error handling in embed_texts."""
        mock_sentence_transformer.encode.side_effect = Exception("Encoding failed")
        
        with pytest.raises(Exception, match="Encoding failed"):
            embedder.embed_texts(["test"])
    
    def test_embedding_shape_consistency(self, embedder):
        """Test that embedding shape is consistent across multiple calls."""
        texts1 = ["Hello", "World"]
        embeddings1 = embedder.embed_texts(texts1)
        
        texts2 = ["Test", "Another", "Example"]
        embeddings2 = embedder.embed_texts(texts2)
        
        # Both should have same dimension
        assert embeddings1.shape[1] == embeddings2.shape[1]
    
    def test_embedding_value_range(self, embedder):
        """Test that embedding values are in expected range."""
        texts = ["Hello, world!"]
        embeddings = embedder.embed_texts(texts)
        
        # Normalized embeddings should have values between -1 and 1
        assert np.all(embeddings >= -1.0)
        assert np.all(embeddings <= 1.0)
    
    def test_batch_embedding_performance(self, embedder, mock_sentence_transformer):
        """Test that batch embedding is efficient."""
        # Create a large batch
        texts = [f"Text {i}" for i in range(100)]
        
        # Mock encode to return appropriate shape
        mock_sentence_transformer.encode.return_value = np.random.rand(100, 384).astype(np.float32)
        
        embeddings = embedder.embed_texts(texts)
        
        assert embeddings.shape == (100, 384)
        # Should be called once for the entire batch
        assert mock_sentence_transformer.encode.call_count == 1
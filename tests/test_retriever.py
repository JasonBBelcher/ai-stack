"""
Unit tests for RAG Retriever component.

Tests the ContextRetriever class for retrieving and formatting code context.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.rag.retriever import ContextRetriever


class TestContextRetriever:
    """Test suite for ContextRetriever class."""
    
    @pytest.fixture
    def mock_embedder(self):
        """Create a mock CodeEmbedder."""
        embedder = Mock()
        embedder.embed_text.return_value = np.random.rand(384).astype(np.float32)
        return embedder
    
    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock FAISSVectorStore."""
        vector_store = Mock()
        vector_store.search.return_value = (
            np.array([0.1, 0.2, 0.3]),
            [
                {
                    'text': 'def hello():\n    print("Hello")',
                    'file_path': 'test1.py',
                    'start_line': 1,
                    'end_line': 2
                },
                {
                    'text': 'class MyClass:\n    pass',
                    'file_path': 'test2.py',
                    'start_line': 5,
                    'end_line': 6
                },
                {
                    'text': 'import os\nimport sys',
                    'file_path': 'test3.py',
                    'start_line': 1,
                    'end_line': 2
                }
            ]
        )
        return vector_store
    
    @pytest.fixture
    def retriever(self, mock_embedder, mock_vector_store):
        """Create a ContextRetriever instance with mocked dependencies."""
        retriever = ContextRetriever(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            max_context_length=10000
        )
        return retriever
    
    @pytest.fixture
    def sample_results(self):
        """Create sample search results for testing."""
        return [
            {
                'text': 'def hello():\n    print("Hello")',
                'file_path': 'test1.py',
                'start_line': 1,
                'end_line': 2
            },
            {
                'text': 'class MyClass:\n    pass',
                'file_path': 'test2.py',
                'start_line': 5,
                'end_line': 6
            },
            {
                'text': 'import os\nimport sys',
                'file_path': 'test3.py',
                'start_line': 1,
                'end_line': 2
            }
        ]
    
    def test_retriever_initialization(self, retriever):
        """Test that ContextRetriever initializes with correct parameters."""
        assert retriever.embedder is not None
        assert retriever.vector_store is not None
        assert retriever.max_context_length == 10000
    
    def test_retriever_default_max_length(self, mock_embedder, mock_vector_store):
        """Test that ContextRetriever uses default max context length."""
        retriever = ContextRetriever(
            embedder=mock_embedder,
            vector_store=mock_vector_store
        )
        assert retriever.max_context_length == 10000
    
    def test_retrieve(self, retriever):
        """Test retrieving context for a query."""
        query = "How do I create a function?"
        results = retriever.retrieve(query, k=3)
        
        assert len(results) == 3
        assert all('text' in result for result in results)
        assert all('file_path' in result for result in results)
        assert all('start_line' in result for result in results)
        assert all('end_line' in result for result in results)
    
    def test_retrieve_with_k_parameter(self, retriever):
        """Test that k parameter controls number of results."""
        query = "test query"
        
        results1 = retriever.retrieve(query, k=1)
        assert len(results1) == 1
        
        results5 = retriever.retrieve(query, k=5)
        assert len(results5) == 5
    
    def test_retrieve_empty_results(self, mock_embedder, mock_vector_store):
        """Test retrieving when no results are found."""
        mock_vector_store.search.return_value = (np.array([]), [])
        
        retriever = ContextRetriever(
            embedder=mock_embedder,
            vector_store=mock_vector_store
        )
        
        results = retriever.retrieve("test query", k=3)
        assert len(results) == 0
    
    def test_retrieve_calls_embedder(self, retriever, mock_embedder):
        """Test that retrieve calls embedder.embed_text."""
        query = "test query"
        retriever.retrieve(query, k=3)
        
        mock_embedder.embed_text.assert_called_once_with(query)
    
    def test_retrieve_calls_vector_store(self, retriever, mock_vector_store, mock_embedder):
        """Test that retrieve calls vector_store.search."""
        query = "test query"
        query_embedding = np.random.rand(384).astype(np.float32)
        mock_embedder.embed_text.return_value = query_embedding
        
        retriever.retrieve(query, k=3)
        
        mock_vector_store.search.assert_called_once()
        call_args = mock_vector_store.search.call_args
        np.testing.assert_array_equal(call_args[0][0], query_embedding)
        assert call_args[0][1] == 3
    
    def test_format_context(self, retriever, sample_results):
        """Test formatting retrieved results into context string."""
        context = retriever.format_context(sample_results)
        
        assert isinstance(context, str)
        assert 'Relevant code context:' in context
        assert 'test1.py' in context
        assert 'test2.py' in context
        assert 'test3.py' in context
        assert 'def hello():' in context
        assert 'class MyClass:' in context
    
    def test_format_context_empty_results(self, retriever):
        """Test formatting empty results."""
        context = retriever.format_context([])
        
        assert context == ""
    
    def test_format_context_includes_line_numbers(self, retriever, sample_results):
        """Test that formatted context includes line numbers."""
        context = retriever.format_context(sample_results)
        
        assert 'lines 1-2' in context
        assert 'lines 5-6' in context
    
    def test_format_context_includes_file_paths(self, retriever, sample_results):
        """Test that formatted context includes file paths."""
        context = retriever.format_context(sample_results)
        
        assert 'File: test1.py' in context
        assert 'File: test2.py' in context
        assert 'File: test3.py' in context
    
    def test_format_context_code_blocks(self, retriever, sample_results):
        """Test that formatted context includes code blocks."""
        context = retriever.format_context(sample_results)
        
        assert '```python' in context
        assert '```' in context
    
    def test_format_context_truncation(self, mock_embedder, mock_vector_store):
        """Test that large chunks are truncated."""
        # Create a large chunk
        large_text = "x" * 4000
        large_results = [
            {
                'text': large_text,
                'file_path': 'large.py',
                'start_line': 1,
                'end_line': 100
            }
        ]
        
        retriever = ContextRetriever(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            max_context_length=5000
        )
        
        context = retriever.format_context(large_results)
        
        # Should be truncated
        assert '(truncated)' in context
        assert len(context) < 5000
    
    def test_format_context_max_length(self, mock_embedder, mock_vector_store):
        """Test that context respects max_context_length."""
        # Create multiple large chunks
        large_results = [
            {
                'text': "x" * 2000,
                'file_path': f'test{i}.py',
                'start_line': 1,
                'end_line': 100
            }
            for i in range(10)
        ]
        
        retriever = ContextRetriever(
            embedder=mock_embedder,
            vector_store=mock_vector_store,
            max_context_length=5000
        )
        
        context = retriever.format_context(large_results)
        
        # Should be truncated to fit max length
        assert len(context) <= 5000 + 100  # Allow some margin
    
    def test_format_context_order_preserved(self, retriever, sample_results):
        """Test that results are formatted in order."""
        context = retriever.format_context(sample_results)
        
        # Check that results appear in order
        pos1 = context.find('test1.py')
        pos2 = context.find('test2.py')
        pos3 = context.find('test3.py')
        
        assert pos1 < pos2 < pos3
    
    def test_retrieve_and_format(self, retriever):
        """Test retrieve_and_format convenience method."""
        query = "test query"
        context = retriever.retrieve_and_format(query, k=3)
        
        assert isinstance(context, str)
        assert 'Relevant code context:' in context
    
    def test_retrieve_and_format_integration(self, retriever):
        """Test that retrieve_and_format calls both methods."""
        query = "test query"
        context = retriever.retrieve_and_format(query, k=3)
        
        # Should have called embedder and vector_store
        retriever.embedder.embed_text.assert_called_once_with(query)
        retriever.vector_store.search.assert_called_once()
    
    def test_retrieve_error_handling(self, mock_embedder, mock_vector_store):
        """Test error handling in retrieve method."""
        mock_embedder.embed_text.side_effect = Exception("Embedding failed")
        
        retriever = ContextRetriever(
            embedder=mock_embedder,
            vector_store=mock_vector_store
        )
        
        results = retriever.retrieve("test query", k=3)
        
        # Should return empty list on error
        assert results == []
    
    def test_format_context_missing_metadata(self, retriever):
        """Test formatting results with missing metadata."""
        incomplete_results = [
            {
                'text': 'def hello():\n    print("Hello")',
                # Missing file_path, start_line, end_line
            }
        ]
        
        context = retriever.format_context(incomplete_results)
        
        # Should still format, with defaults
        assert 'def hello():' in context
        assert 'unknown' in context
    
    def test_format_context_special_characters(self, retriever):
        """Test formatting code with special characters."""
        special_results = [
            {
                'text': 'def test():\n    # Comment with @#$%\n    return "value"',
                'file_path': 'special.py',
                'start_line': 1,
                'end_line': 3
            }
        ]
        
        context = retriever.format_context(special_results)
        
        assert '# Comment with @#$%' in context
        assert 'return "value"' in context
    
    def test_format_context_multiline_code(self, retriever):
        """Test formatting multiline code snippets."""
        multiline_results = [
            {
                'text': 'class MyClass:\n    def __init__(self):\n        self.value = 42\n\n    def get_value(self):\n        return self.value',
                'file_path': 'multiline.py',
                'start_line': 1,
                'end_line': 6
            }
        ]
        
        context = retriever.format_context(multiline_results)
        
        assert 'class MyClass:' in context
        assert 'def __init__(self):' in context
        assert 'def get_value(self):' in context
    
    def test_retrieve_with_long_query(self, retriever):
        """Test retrieving with a long query."""
        long_query = " ".join(["word"] * 100)
        results = retriever.retrieve(long_query, k=3)
        
        assert len(results) == 3
    
    def test_retrieve_with_special_query(self, retriever):
        """Test retrieving with special characters in query."""
        special_query = "How to use @#$%^&*() in Python?"
        results = retriever.retrieve(special_query, k=3)
        
        assert len(results) == 3
    
    def test_format_context_empty_text(self, retriever):
        """Test formatting results with empty text."""
        empty_results = [
            {
                'text': '',
                'file_path': 'empty.py',
                'start_line': 1,
                'end_line': 1
            }
        ]
        
        context = retriever.format_context(empty_results)
        
        # Should still format
        assert 'File: empty.py' in context
    
    def test_format_context_whitespace(self, retriever):
        """Test formatting results with whitespace."""
        whitespace_results = [
            {
                'text': '   \n\n   \n',
                'file_path': 'whitespace.py',
                'start_line': 1,
                'end_line': 3
            }
        ]
        
        context = retriever.format_context(whitespace_results)
        
        # Should still format
        assert 'File: whitespace.py' in context
    
    def test_retrieve_k_zero(self, retriever):
        """Test retrieving with k=0."""
        results = retriever.retrieve("test query", k=0)
        
        # Should return empty results
        assert len(results) == 0
    
    def test_retrieve_k_large(self, retriever):
        """Test retrieving with large k value."""
        results = retriever.retrieve("test query", k=100)
        
        # Should return up to available results
        assert len(results) <= 100
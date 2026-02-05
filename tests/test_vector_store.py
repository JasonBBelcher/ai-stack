"""
Unit tests for RAG Vector Store component.

Tests the FAISSVectorStore class for managing FAISS vector database.
"""

import pytest
import numpy as np
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock


class TestFAISSVectorStore:
    """Test suite for FAISSVectorStore class."""
    
    @pytest.fixture
    def mock_faiss(self):
        """Create a mock FAISS module."""
        mock_faiss = Mock()
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.d = 384
        mock_index.add = Mock()
        mock_index.search = Mock(return_value=(np.array([[0.1, 0.2, 0.3]]), np.array([[0, 1, 2]])))
        mock_faiss.IndexFlatL2 = Mock(return_value=mock_index)
        mock_faiss.write_index = Mock()
        mock_faiss.read_index = Mock(return_value=mock_index)
        return mock_faiss
    
    @pytest.fixture
    def vector_store(self, mock_faiss):
        """Create a FAISSVectorStore instance with mocked FAISS."""
        # Patch sys.modules to make faiss available for import
        with patch.dict('sys.modules', {'faiss': mock_faiss}):
            from src.rag.vector_store import FAISSVectorStore
            vector_store = FAISSVectorStore(index_type="Flat", dimension=384)
            return vector_store
    
    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        return np.random.rand(5, 384).astype(np.float32)
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata for testing."""
        return [
            {'file_path': 'test1.py', 'start_line': 1, 'end_line': 10},
            {'file_path': 'test2.py', 'start_line': 11, 'end_line': 20},
            {'file_path': 'test3.py', 'start_line': 21, 'end_line': 30},
            {'file_path': 'test4.py', 'start_line': 31, 'end_line': 40},
            {'file_path': 'test5.py', 'start_line': 41, 'end_line': 50},
        ]
    
    def test_vector_store_initialization(self, vector_store):
        """Test that FAISSVectorStore initializes with correct parameters."""
        assert vector_store.index_type == "Flat"
        assert vector_store.dimension == 384
        assert vector_store.index is not None
        assert vector_store.metadata == []
    
    def test_vector_store_default_initialization(self):
        """Test that FAISSVectorStore uses default parameters."""
        mock_faiss = Mock()
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.d = 384
        mock_index.add = Mock()
        mock_index.search = Mock(return_value=(np.array([[0.1]]), np.array([[0]])))
        mock_faiss.IndexFlatL2 = Mock(return_value=mock_index)
        
        with patch.dict('sys.modules', {'faiss': mock_faiss}):
            from src.rag.vector_store import FAISSVectorStore
            vector_store = FAISSVectorStore()
            assert vector_store.index_type == "Flat"
            assert vector_store.dimension == 384
    
    def test_vector_store_custom_dimension(self):
        """Test FAISSVectorStore with custom dimension."""
        mock_faiss = Mock()
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.d = 512
        mock_index.add = Mock()
        mock_index.search = Mock(return_value=(np.array([[0.1]]), np.array([[0]])))
        mock_faiss.IndexFlatL2 = Mock(return_value=mock_index)
        
        with patch.dict('sys.modules', {'faiss': mock_faiss}):
            from src.rag.vector_store import FAISSVectorStore
            vector_store = FAISSVectorStore(dimension=512)
            assert vector_store.dimension == 512
    
    def test_add_embeddings(self, vector_store, sample_embeddings, sample_metadata):
        """Test adding embeddings to the index."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        assert len(vector_store.metadata) == 5
        assert vector_store.index.ntotal == 5
        assert vector_store.index.add.called
    
    def test_add_embeddings_mismatch(self, vector_store, sample_embeddings):
        """Test error when embeddings and metadata count don't match."""
        metadata = [{'file_path': 'test.py'}]  # Only 1 metadata entry
        
        with pytest.raises(ValueError, match="Number of embeddings must match"):
            vector_store.add_embeddings(sample_embeddings, metadata)
    
    def test_add_embeddings_empty(self, vector_store):
        """Test adding empty embeddings."""
        embeddings = np.array([]).reshape(0, 384).astype(np.float32)
        metadata = []
        
        vector_store.add_embeddings(embeddings, metadata)
        
        assert len(vector_store.metadata) == 0
    
    def test_add_embeddings_multiple_batches(self, vector_store, sample_embeddings, sample_metadata):
        """Test adding embeddings in multiple batches."""
        # First batch
        vector_store.add_embeddings(sample_embeddings[:3], sample_metadata[:3])
        assert len(vector_store.metadata) == 3
        
        # Second batch
        vector_store.add_embeddings(sample_embeddings[3:], sample_metadata[3:])
        assert len(vector_store.metadata) == 5
    
    def test_search(self, vector_store, sample_embeddings, sample_metadata):
        """Test searching for similar embeddings."""
        # Add embeddings first
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        # Search
        query_embedding = np.random.rand(384).astype(np.float32)
        distances, results = vector_store.search(query_embedding, k=3)
        
        assert isinstance(distances, np.ndarray)
        assert len(distances) == 3
        assert len(results) == 3
        assert all('distance' in result for result in results)
    
    def test_search_empty_index(self, vector_store):
        """Test searching when index is empty."""
        query_embedding = np.random.rand(384).astype(np.float32)
        distances, results = vector_store.search(query_embedding, k=3)
        
        assert len(distances) == 0
        assert len(results) == 0
    
    def test_search_with_1d_query(self, vector_store, sample_embeddings, sample_metadata):
        """Test searching with 1D query embedding."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        query_embedding = np.random.rand(384).astype(np.float32)
        distances, results = vector_store.search(query_embedding, k=3)
        
        assert len(results) == 3
    
    def test_search_with_2d_query(self, vector_store, sample_embeddings, sample_metadata):
        """Test searching with 2D query embedding."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        query_embedding = np.random.rand(1, 384).astype(np.float32)
        distances, results = vector_store.search(query_embedding, k=3)
        
        assert len(results) == 3
    
    def test_search_k_parameter(self, vector_store, sample_embeddings, sample_metadata):
        """Test that k parameter controls number of results."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        query_embedding = np.random.rand(384).astype(np.float32)
        
        # Test with k=1
        distances1, results1 = vector_store.search(query_embedding, k=1)
        assert len(results1) == 1
        
        # Test with k=5
        distances5, results5 = vector_store.search(query_embedding, k=5)
        assert len(results5) == 5
    
    def test_search_metadata_includes_distance(self, vector_store, sample_embeddings, sample_metadata):
        """Test that search results include distance in metadata."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        query_embedding = np.random.rand(384).astype(np.float32)
        distances, results = vector_store.search(query_embedding, k=3)
        
        for i, result in enumerate(results):
            assert 'distance' in result
            assert result['distance'] == distances[i]
    
    def test_search_metadata_preserved(self, vector_store, sample_embeddings, sample_metadata):
        """Test that original metadata is preserved in search results."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        query_embedding = np.random.rand(384).astype(np.float32)
        distances, results = vector_store.search(query_embedding, k=3)
        
        for result in results:
            assert 'file_path' in result
            assert 'start_line' in result
            assert 'end_line' in result
    
    def test_save(self, vector_store, sample_embeddings, sample_metadata):
        """Test saving the index to disk."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_index")
            vector_store.save(file_path)
            
            # Check that files were created
            assert os.path.exists(f"{file_path}.index")
            assert os.path.exists(f"{file_path}.metadata")
    
    def test_load(self, vector_store, sample_embeddings, sample_metadata, mock_faiss):
        """Test loading the index from disk."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_index")
            vector_store.save(file_path)
            
            # Create new vector store and load
            new_vector_store = FAISSVectorStore(dimension=384)
            new_vector_store.load(file_path)
            
            assert len(new_vector_store.metadata) == 5
            assert new_vector_store.index.ntotal == 5
    
    def test_load_nonexistent_file(self, vector_store):
        """Test loading a non-existent file."""
        with pytest.raises(FileNotFoundError):
            vector_store.load("/nonexistent/path/test_index")
    
    def test_get_size(self, vector_store):
        """Test getting the size of the index."""
        assert vector_store.get_size() == 0
    
    def test_get_size_with_embeddings(self, vector_store, sample_embeddings, sample_metadata):
        """Test getting the size after adding embeddings."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        assert vector_store.get_size() == 5
    
    def test_get_size_after_multiple_adds(self, vector_store, sample_embeddings, sample_metadata):
        """Test getting the size after multiple additions."""
        vector_store.add_embeddings(sample_embeddings[:3], sample_metadata[:3])
        assert vector_store.get_size() == 3
        
        vector_store.add_embeddings(sample_embeddings[3:], sample_metadata[3:])
        assert vector_store.get_size() == 5
    
    def test_index_not_initialized_error(self):
        """Test error when index is not initialized."""
        vector_store = FAISSVectorStore.__new__(FAISSVectorStore)
        vector_store.index = None
        vector_store.metadata = []
        
        with pytest.raises(RuntimeError, match="Index not initialized"):
            vector_store.add_embeddings(np.array([[1.0]]), [{'test': 'data'}])
    
    def test_faiss_import_error(self):
        """Test error handling when FAISS is not installed."""
        # Remove faiss from sys.modules to simulate it not being installed
        import sys
        faiss_backup = sys.modules.get('faiss')
        if 'faiss' in sys.modules:
            del sys.modules['faiss']
        
        try:
            with pytest.raises(ImportError):
                from src.rag.vector_store import FAISSVectorStore
                FAISSVectorStore()
        finally:
            # Restore faiss if it was there
            if faiss_backup is not None:
                sys.modules['faiss'] = faiss_backup
    
    def test_unsupported_index_type(self):
        """Test that unsupported index types fall back to Flat."""
        mock_faiss = Mock()
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.d = 384
        mock_index.add = Mock()
        mock_index.search = Mock(return_value=(np.array([[0.1]]), np.array([[0]])))
        mock_faiss.IndexFlatL2 = Mock(return_value=mock_index)
        
        with patch.dict('sys.modules', {'faiss': mock_faiss}):
            from src.rag.vector_store import FAISSVectorStore
            vector_store = FAISSVectorStore(index_type="UnsupportedType")
            # Should fall back to Flat
            assert mock_faiss.IndexFlatL2.called
    
    def test_add_embeddings_dtype_conversion(self, vector_store, mock_faiss):
        """Test that embeddings are converted to float32."""
        embeddings = np.random.rand(5, 384)  # Default float64
        metadata = [{'test': i} for i in range(5)]
        
        vector_store.add_embeddings(embeddings, metadata)
        
        # Check that add was called with float32
        call_args = vector_store.index.add.call_args
        assert call_args[0][0].dtype == np.float32
    
    def test_search_dtype_conversion(self, vector_store, sample_embeddings, sample_metadata):
        """Test that query embedding is converted to float32."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        query_embedding = np.random.rand(384)  # Default float64
        distances, results = vector_store.search(query_embedding, k=3)
        
        # Should work without error
        assert len(results) == 3
    
    def test_metadata_order_preserved(self, vector_store, sample_embeddings, sample_metadata):
        """Test that metadata order is preserved."""
        vector_store.add_embeddings(sample_embeddings, sample_metadata)
        
        # Check that metadata is in the same order as added
        for i, meta in enumerate(vector_store.metadata):
            assert meta['file_path'] == sample_metadata[i]['file_path']
    
    def test_large_batch_add(self, vector_store):
        """Test adding a large batch of embeddings."""
        large_embeddings = np.random.rand(1000, 384).astype(np.float32)
        large_metadata = [{'id': i} for i in range(1000)]
        
        vector_store.add_embeddings(large_embeddings, large_metadata)
        
        assert vector_store.get_size() == 1000
        assert len(vector_store.metadata) == 1000
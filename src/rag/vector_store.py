"""
Vector Store for RAG functionality.

Manages FAISS database connections for storing and searching embeddings.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """Manage FAISS vector database for code embeddings."""
    
    def __init__(self, index_type: str = "Flat", dimension: int = 384):
        """
        Initialize the FAISS vector store.
        
        Args:
            index_type: Type of FAISS index (Flat, IVF, etc.)
            dimension: Dimension of the embedding vectors
        """
        self.index_type = index_type
        self.dimension = dimension
        self.index = None
        self.metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize the FAISS index."""
        try:
            import faiss
            logger.info(f"Initializing FAISS index: {self.index_type}")
            
            if self.index_type == "Flat":
                self.index = faiss.IndexFlatL2(self.dimension)
            else:
                logger.warning(f"Index type {self.index_type} not fully implemented, using Flat")
                self.index = faiss.IndexFlatL2(self.dimension)
            
            logger.info(f"FAISS index initialized with dimension {self.dimension}")
        except ImportError:
            logger.error("faiss not installed. Install with: pip install faiss-cpu")
            raise
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {e}")
            raise
    
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Add embeddings to the index.
        
        Args:
            embeddings: numpy array of embeddings with shape (n, dimension)
            metadata: List of metadata dictionaries for each embedding
        """
        if self.index is None:
            raise RuntimeError("Index not initialized")
        
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        try:
            self.index.add(embeddings.astype('float32'))
            self.metadata.extend(metadata)
            logger.info(f"Added {len(embeddings)} embeddings to index. Total: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error adding embeddings: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            Tuple of (distances, metadata_list)
        """
        if self.index is None:
            raise RuntimeError("Index not initialized")
        
        if self.index.ntotal == 0:
            logger.warning("Index is empty, no results to return")
            return np.array([]), []
        
        try:
            # Reshape query if needed
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Search
            distances, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Get metadata for results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata):
                    results.append({
                        **self.metadata[idx],
                        'distance': float(distances[0][i])
                    })
            
            return distances[0], results
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            raise
    
    def save(self, file_path: str):
        """
        Save the index to disk.
        
        Args:
            file_path: Path to save the index (without extension)
        """
        if self.index is None:
            raise RuntimeError("Index not initialized")
        
        try:
            import faiss
            import pickle
            
            # Save index
            index_path = f"{file_path}.index"
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            metadata_path = f"{file_path}.metadata"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Index saved to {index_path}")
            logger.info(f"Metadata saved to {metadata_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load(self, file_path: str):
        """
        Load the index from disk.
        
        Args:
            file_path: Path to load the index from (without extension)
        """
        try:
            import faiss
            import pickle
            
            # Load index
            index_path = f"{file_path}.index"
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index file not found: {index_path}")
            
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            metadata_path = f"{file_path}.metadata"
            if not os.path.exists(metadata_path):
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
            
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            # Update dimension
            self.dimension = self.index.d
            
            logger.info(f"Index loaded from {index_path}")
            logger.info(f"Metadata loaded from {metadata_path}")
            logger.info(f"Total embeddings: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise
    
    def get_size(self) -> int:
        """
        Get the number of embeddings in the index.
        
        Returns:
            Number of embeddings
        """
        if self.index is None:
            return 0
        return self.index.ntotal
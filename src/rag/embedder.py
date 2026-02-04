"""
Code Embedder for RAG functionality.

Creates vector representations of code chunks using sentence transformers.
"""

import logging
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)


class CodeEmbedder:
    """Generate embeddings for code chunks."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize the code embedder.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding with shape (embedding_dim,)
        """
        return self.embed_texts([text])[0]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            Dimension of the embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        return self.model.get_sentence_embedding_dimension()
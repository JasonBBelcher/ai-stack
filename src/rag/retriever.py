"""
Context Retriever for RAG functionality.

Retrieves relevant code context from the vector store and formats it for prompts.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ContextRetriever:
    """Retrieve relevant code context for queries."""
    
    def __init__(self, embedder, vector_store, max_context_length: int = 10000):
        """
        Initialize the context retriever.
        
        Args:
            embedder: CodeEmbedder instance
            vector_store: FAISSVectorStore instance
            max_context_length: Maximum length of context to return (in characters)
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.max_context_length = max_context_length
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant code chunks for a query.
        
        Args:
            query: Query string
            k: Number of results to retrieve
            
        Returns:
            List of relevant code chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)
            
            # Search vector store
            distances, results = self.vector_store.search(query_embedding, k)
            
            logger.info(f"Retrieved {len(results)} results for query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved results into a context string for prompts.
        
        Args:
            results: List of retrieved code chunks
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        current_length = 0
        
        for result in results:
            chunk_text = result.get('text', '')
            file_path = result.get('file_path', 'unknown')
            start_line = result.get('start_line', 0)
            end_line = result.get('end_line', 0)
            
            # Truncate chunk if it's too large
            max_chunk_size = 3000
            if len(chunk_text) > max_chunk_size:
                chunk_text = chunk_text[:max_chunk_size] + "\n... (truncated)"
            
            # Format chunk with metadata
            formatted_chunk = f"""
File: {file_path} (lines {start_line}-{end_line})
```python
{chunk_text}
```
"""
            
            # Check if adding this chunk would exceed max length
            if current_length + len(formatted_chunk) > self.max_context_length:
                logger.warning(f"Context truncated at {current_length} characters")
                break
            
            context_parts.append(formatted_chunk)
            current_length += len(formatted_chunk)
        
        context = "\n".join(context_parts)
        
        if context:
            context = f"Relevant code context:\n{context}\n"
        
        return context
    
    def retrieve_and_format(self, query: str, k: int = 5) -> str:
        """
        Retrieve and format context in one step.
        
        Args:
            query: Query string
            k: Number of results to retrieve
            
        Returns:
            Formatted context string
        """
        results = self.retrieve(query, k)
        return self.format_context(results)
"""
RAG (Retrieval-Augmented Generation) module for AI-Stack.

This module provides codebase context awareness through:
- Indexing: Processing and chunking code files
- Embedding: Creating vector representations
- Vector Store: Managing FAISS database connections
- Retrieval: Searching and formatting context for prompts
"""

from .indexer import CodeIndexer
from .embedder import CodeEmbedder
from .vector_store import FAISSVectorStore
from .retriever import ContextRetriever

__all__ = [
    "CodeIndexer",
    "CodeEmbedder",
    "FAISSVectorStore",
    "ContextRetriever",
]
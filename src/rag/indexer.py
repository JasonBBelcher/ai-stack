"""
Code Indexer for RAG functionality.

Processes and chunks code files for embedding and retrieval.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CodeIndexer:
    """Index code files by processing and chunking them."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize the code indexer.
        
        Args:
            chunk_size: Maximum size of each chunk in tokens
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs'}
        self.exclude_dirs = {
            'venv', 'env', '.venv', '.env', 'node_modules', '.git',
            '__pycache__', '.pytest_cache', 'dist', 'build', '.tox',
            '.mypy_cache', 'htmlcov', '.coverage', 'site-packages'
        }
    
    def index_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Index all code files in a directory.
        
        Args:
            directory: Path to the directory to index
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return chunks
        
        for file_path in directory_path.rglob('*'):
            # Skip excluded directories
            if any(excluded_dir in file_path.parts for excluded_dir in self.exclude_dirs):
                continue
            
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                try:
                    file_chunks = self.index_file(str(file_path))
                    chunks.extend(file_chunks)
                    logger.info(f"Indexed {file_path}: {len(file_chunks)} chunks")
                except Exception as e:
                    logger.error(f"Error indexing {file_path}: {e}")
        
        logger.info(f"Total chunks indexed: {len(chunks)}")
        return chunks
    
    def index_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Index a single code file.
        
        Args:
            file_path: Path to the file to index
            
        Returns:
            List of chunks with metadata
        """
        try:
            # Try UTF-8 first, then fallback to latin-1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            chunks = self._chunk_content(content, file_path)
            return chunks
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
    
    def _chunk_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Split content into chunks.
        
        Args:
            content: File content to chunk
            file_path: Path to the source file
            
        Returns:
            List of chunks with metadata
        """
        # Simple line-based chunking for now
        # TODO: Implement AST-based parsing for better chunks
        lines = content.split('\n')
        chunks = []
        
        current_chunk = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_tokens = len(line.split())
            
            if current_size + line_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'file_path': file_path,
                    'start_line': i - len(current_chunk) + 1,
                    'end_line': i,
                    'chunk_id': f"{file_path}:{i - len(current_chunk) + 1}-{i}"
                })
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else []
                current_chunk = overlap_lines
                current_size = sum(len(l.split()) for l in overlap_lines)
            
            current_chunk.append(line)
            current_size += line_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'file_path': file_path,
                'start_line': len(lines) - len(current_chunk) + 1,
                'end_line': len(lines),
                'chunk_id': f"{file_path}:{len(lines) - len(current_chunk) + 1}-{len(lines)}"
            })
        
        return chunks
# RAG Components Documentation

## Indexer

The Indexer component processes code files and splits them into manageable chunks for embedding.

### Features
- AST-based parsing for code files
- Configurable chunking strategies
- Support for multiple programming languages
- Error handling for malformed files

### Configuration
```json
{
  "chunking": {
    "strategy": "ast", // or "fixed", "semantic"
    "size": 512,
    "overlap": 50
  }
}
```

## Embedder

The Embedder creates vector representations of text chunks using sentence transformers.

### Features
- Multiple model support (BGE, Sentence-BERT, etc.)
- Batch processing for efficiency
- Metal acceleration on M3 Macs
- Error handling for model loading

### Configuration
```json
{
  "embedding": {
    "model": "BAAI/bge-small-en-v1.5",
    "dimension": 384,
    "batch_size": 32
  }
}
```

## Vector Store

The Vector Store manages FAISS database connections for efficient similarity search.

### Features
- FAISS integration for fast similarity search
- Persistent storage and loading
- Index management and optimization
- Memory-efficient operations

### Configuration
```json
{
  "vector_store": {
    "index_type": "Flat",
    "persistence": true,
    "path": "/tmp/vector_store"
  }
}
```

## Retriever

The Retriever searches the vector store and formats context for prompts.

### Features
- Similarity-based search with configurable thresholds
- Result reranking for improved relevance
- Metadata filtering
- Context formatting for prompts

### Configuration
```json
{
  "retrieval": {
    "top_k": 5,
    "min_similarity": 0.7,
    "rerank": true
  }
}
```

## Query Cache

The Query Cache stores frequent queries to improve performance.

### Features
- In-memory caching with LRU eviction
- Disk-based persistence
- Configurable cache size and expiration
- Automatic cache warming

### Configuration
```json
{
  "cache": {
    "max_size": 1000,
    "ttl": 3600,
    "persistence": true
  }
}
```

## Post Processor

The Post Processor formats and validates retrieved results.

### Features
- Result formatting and deduplication
- Content validation and filtering
- Metadata enrichment
- Customizable processing rules

### Configuration
```json
{
  "post_processing": {
    "deduplicate": true,
    "validate": true,
    "format": "markdown"
  }
}
```
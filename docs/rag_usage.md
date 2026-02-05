# RAG Usage Guide

## Getting Started

To use the RAG functionality in the AI Stack, you need to:

1. Index your codebase or documents
2. Configure RAG profiles for your use case
3. Use the CLI or API to perform RAG-enhanced queries

## Indexing Your Codebase

### Using the CLI

```bash
# Index a directory of code files
python3 main.py --rag-index /path/to/codebase

# Index with specific profile
python3 main.py --rag-index /path/to/codebase --profile coding
```

### Using the API

```python
from src.rag.indexer import Indexer
from src.rag.embedder import CodeEmbedder

# Create indexer and embedder
indexer = Indexer(chunk_size=512, overlap=50)
embedder = CodeEmbedder(model_name="BAAI/bge-small-en-v1.5")

# Process and index files
chunks = indexer.process_directory("/path/to/codebase")
embedder.embed_chunks(chunks)
```

## Configuring RAG Profiles

RAG profiles are stored in `config/rag_profiles/` and define settings for different use cases:

### Coding Profile
Optimized for code analysis and understanding:
- Chunk size: 512 tokens
- AST-based chunking
- Code-aware embedding model
- Temperature: 0.3 for precise responses

### Research Profile
Optimized for document analysis:
- Chunk size: 1024 tokens
- Semantic chunking
- General-purpose embedding model
- Temperature: 0.5 for balanced analysis

### Writing Profile
Optimized for creative content:
- Chunk size: 768 tokens
- Paragraph-based chunking
- Style-aware embedding model
- Temperature: 0.7 for creative responses

## Performing RAG-Enhanced Queries

### Using the CLI

```bash
# Perform a RAG query
python3 main.py --rag-query "How does the memory manager work?"

# Query with specific profile
python3 main.py --rag-query "Explain the RAG architecture" --profile research

# Query with context
python3 main.py --rag-query "Fix this bug" --context-file bug_report.txt
```

### Using the API

```python
from src.rag.retriever import Retriever
from src.rag.query_cache import QueryCache

# Create retriever and cache
retriever = Retriever()
cache = QueryCache()

# Perform RAG query
results = retriever.search("How does the memory manager work?")
context = "\n".join([r.content for r in results])

# Generate response with context
response = model.generate(f"Context: {context}\n\nQuestion: How does the memory manager work?")
```

## Performance Optimization

### Cache Configuration
Configure the query cache for your usage patterns:

```json
{
  "cache": {
    "max_size": 1000,
    "ttl": 3600,
    "persistence": true,
    "warm_queries": ["common query 1", "common query 2"]
  }
}
```

### Metal Acceleration
Enable Metal acceleration on M3 Macs for improved performance:

```bash
export METAL_DEVICE_FORCE_LOW_POWER_GPU=1
```

### Batch Processing
Process multiple queries in batches for improved efficiency:

```python
queries = ["query 1", "query 2", "query 3"]
results = retriever.batch_search(queries)
```

## Troubleshooting

### Common Issues

1. **Slow Query Performance**
   - Check if Metal acceleration is enabled
   - Increase cache size for frequent queries
   - Reduce chunk size for faster processing

2. **Low Relevance Results**
   - Adjust similarity thresholds
   - Try different embedding models
   - Increase top_k parameter

3. **Memory Issues**
   - Reduce batch size
   - Enable memory-efficient indexing
   - Use smaller embedding models

### Debugging

Enable verbose logging to debug issues:

```bash
python3 main.py --rag-query "test query" --verbose
```

Or in code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Chunking Strategy**
   - Use AST-based chunking for code
   - Use semantic chunking for documents
   - Adjust chunk size based on context window

2. **Embedding Models**
   - Use BGE models for code-related tasks
   - Use Sentence-BERT for general documents
   - Fine-tune models for domain-specific tasks

3. **Query Formulation**
   - Be specific with queries
   - Include relevant context
   - Use natural language questions

4. **Result Processing**
   - Filter results by similarity score
   - Deduplicate overlapping chunks
   - Validate results before use
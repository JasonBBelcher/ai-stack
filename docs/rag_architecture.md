# RAG Architecture Overview

## Introduction

The Retrieval-Augmented Generation (RAG) system in the AI Stack provides enhanced context awareness by retrieving relevant information from codebases and documents before generating responses. This document outlines the architecture and components of the RAG system.

## System Architecture

The RAG system consists of several interconnected components:

1. **Indexer** - Processes and chunks code files using AST-based parsing
2. **Embedder** - Creates vector representations using sentence transformers
3. **Vector Store** - Manages FAISS database connections
4. **Retriever** - Searches database and formats context for prompts
5. **Query Cache** - Caches frequent queries for improved performance
6. **Post Processor** - Formats and validates retrieved results

## Data Flow

1. **Indexing Phase**:
   - Indexer processes code files and splits them into chunks
   - Embedder generates vector representations for each chunk
   - Vector Store stores the embeddings for efficient retrieval

2. **Retrieval Phase**:
   - User query is processed by the Embedder
   - Retriever searches the Vector Store for relevant chunks
   - Results are cached by Query Cache for future use
   - Post Processor formats and validates the results

3. **Generation Phase**:
   - Retrieved context is incorporated into the prompt
   - Selected model generates a response based on the context

## Component Interactions

### Indexer ↔ Embedder
The Indexer provides processed chunks to the Embedder, which converts them into vector representations.

### Embedder ↔ Vector Store
The Embedder stores generated vectors in the Vector Store for efficient retrieval.

### Vector Store ↔ Retriever
The Retriever queries the Vector Store to find relevant chunks based on user queries.

### Retriever ↔ Query Cache
The Retriever caches frequent queries to improve performance.

### Retriever ↔ Post Processor
The Post Processor formats and validates results from the Retriever.

## Configuration

The RAG system can be configured through:
- `config/rag_profiles/` - Predefined profiles for different use cases
- `config/models.json` - Model capabilities and preferences
- Environment variables for performance tuning

## Performance Considerations

- Use appropriate chunk sizes for your use case
- Configure cache settings based on query patterns
- Monitor memory usage when indexing large codebases
- Use Metal acceleration on M3 Macs for improved performance

## Security

- All data processing occurs locally
- No data is sent to external services
- Access controls are managed through the main AI Stack configuration
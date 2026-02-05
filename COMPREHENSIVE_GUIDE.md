# AI Stack - Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [RAG System](#rag-system)
5. [Cascade Processing](#cascade-processing)
6. [Profiles and Configuration](#profiles-and-configuration)
7. [Example Workflows](#example-workflows)
8. [Performance Monitoring](#performance-monitoring)
9. [CLI Commands](#cli-commands)
10. [Troubleshooting](#troubleshooting)

## Overview

The AI Stack is a professional-grade, multi-model AI system that runs locally on Apple Silicon M-series chips. It features generic model swappability, intelligent model selection, and a comprehensive CLI interface with advanced RAG (Retrieval-Augmented Generation) and Cascade processing capabilities.

Key capabilities:
- Generic model system with local (Ollama) and cloud (OpenAI, Anthropic) support
- Intelligent model selection based on task requirements
- Profile management for coding, writing, and research use cases
- Resource awareness with memory and thermal management
- Professional CLI with JSON output for scripting
- Advanced RAG system for codebase and document understanding
- Cascade processing for complex multi-stage tasks

## Quick Start

### Prerequisites
1. **Ollama** (Required)
   ```bash
   brew install ollama
   ollama serve  # Keep running in background
   ```

2. **Pull Recommended Models**
   ```bash
   ollama pull llama3.1:8b      # Primary model (~5GB)
   ollama pull qwen2.5:7b       # Coding model (~4.5GB)
   ollama pull qwen2.5:14b      # Large coding model (~9GB)
   ollama pull mistral:latest   # General purpose (~4GB)
   ```

3. **Install Python Dependencies**
   ```bash
   cd ai-stack
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python3 main.py --health-check
   ```

### Basic Usage
```bash
# Simple request
python3 main.py "What is 2+2?"

# List available models
python3 main.py --models list

# Check system status
python3 main.py --status

# Use a specific profile
python3 main.py --profile coding "Write a Python function"
```

## Core Features

### Generic Model System
The AI Stack supports both local Ollama models and cloud models (OpenAI, Anthropic). Models are selected intelligently based on:
- Capability tags (coding, reasoning, generation, etc.)
- Memory requirements
- Performance characteristics
- User preferences in profiles

### Intelligent Model Selection
Models are automatically selected based on:
- Task requirements (coding, reasoning, generation)
- Available system resources
- User profile preferences
- Performance history

### Profile Management
Three built-in profiles optimized for different use cases:
- **coding**: Optimized for programming tasks
- **writing**: Optimized for creative content
- **research**: Optimized for analysis and research

### Resource Management
- Memory monitoring with M3 Mac optimizations
- Thermal state awareness
- Automatic model unloading to free resources
- Safety buffers to prevent system overload

## RAG System

### Overview
The Retrieval-Augmented Generation (RAG) system enhances AI responses by retrieving relevant information from codebases and documents before generating responses.

### Components
1. **Indexer**: Processes and chunks code files using AST-based parsing
2. **Embedder**: Creates vector representations using sentence transformers
3. **Vector Store**: Manages FAISS database connections
4. **Retriever**: Searches database and formats context for prompts
5. **Query Cache**: Caches frequent queries for improved performance
6. **Post Processor**: Formats and validates retrieved results

### RAG Profiles
Three specialized RAG profiles:
- **coding**: Code-aware retrieval with 512-token chunks
- **research**: Comprehensive retrieval with 1024-token chunks
- **writing**: Creative retrieval with 768-token chunks

### Usage Examples
```bash
# Index a codebase
python3 main.py --rag-index /path/to/codebase

# Query with RAG context
python3 main.py --rag-query "How does the memory manager work?"

# Check RAG status
python3 main.py --rag-status
```

## Cascade Processing

### Overview
Cascade processing implements a multi-stage approach to resolve ambiguity, validate feasibility, and execute complex tasks through adaptive execution paths.

### Components
1. **Ambiguity Detector**: Identifies undefined terms and generates interpretations
2. **Clarification Engine**: Presents concrete choices to users
3. **Constraint Extractor**: Discovers user constraints and limitations
4. **Feasibility Validator**: Checks if tasks can be completed within constraints
5. **Multi-Path Generator**: Creates alternative approaches when needed
6. **Execution Planner**: Breaks tasks into model-sized chunks
7. **Progress Monitor**: Tracks execution and identifies obstacles
8. **Prompt Adjuster**: Modifies prompts based on execution progress

### Usage Examples
```bash
# Submit a request for cascade processing
python3 main.py --request "Create a REST API for a todo application"

# View current cascade operations
python3 main.py --cascade-status

# Start interactive cascade session
python3 main.py --interactive --cascade
```

## Profiles and Configuration

### User Profiles
Profiles customize the AI Stack for different use cases:

**Coding Profile**
- Uses coding-optimized models (qwen2.5 series)
- Lower temperature settings for precise code
- Cascade settings optimized for code tasks

**Research Profile**
- Uses reasoning-optimized models
- Higher context windows for document analysis
- Cloud model fallbacks for complex tasks

**Writing Profile**
- Uses generation-optimized models
- Higher temperature settings for creativity
- Style-aware RAG configurations

### Model Configuration
Models are configured in `config/models.json` with:
- Capability tags for intelligent selection
- Memory requirements
- Performance characteristics
- Cloud provider settings

### RAG Profiles
Located in `config/rag_profiles/` with settings for:
- Chunking strategies and sizes
- Embedding model configurations
- Retrieval parameters
- Generation settings
- M3 Mac optimizations

## Example Workflows

Five pre-built workflows demonstrate advanced capabilities:

### 1. Code Analysis
Analyzes codebases to understand structure, identify issues, and suggest improvements.

### 2. Document QA
Answers questions about documents using RAG to retrieve relevant information.

### 3. Bug Fixing
Identifies, diagnoses, and fixes bugs in code using AI assistance.

### 4. Refactoring
Refactors code to improve structure, readability, and maintainability.

### 5. Research
Assists with research tasks by gathering information, analyzing findings, and synthesizing results.

Usage:
```bash
# Run a workflow
python3 main.py --workflow code_analysis --input-path ./my-project
```

## Performance Monitoring

### Monitoring Tools
The AI Stack includes comprehensive performance monitoring:
- **Performance Tracker**: Real-time system metrics
- **Dashboard**: Visual monitoring interface
- **Alert System**: Notifications for performance issues
- **Profiler**: Detailed performance analysis

### Metrics Tracked
- CPU and memory usage
- Response times
- Cache hit rates
- Model call frequency
- Disk I/O and network usage

### Usage
```bash
# View performance dashboard
python3 main.py --dashboard

# Check for alerts
python3 main.py --alerts

# Profile a specific operation
python3 main.py --profile-performance "operation-name"
```

## CLI Commands

### Core Commands
```bash
# System information
python3 main.py --status
python3 main.py --health-check
python3 main.py --config

# Model management
python3 main.py --models list
python3 main.py --model-info model:name
python3 main.py --models discover

# Profile management
python3 main.py --profile list
python3 main.py --profile current
```

### RAG Commands
```bash
# Indexing
python3 main.py --rag-index /path/to/content
python3 main.py --rag-status
python3 main.py --rag-validate

# Querying
python3 main.py --rag-query "question"
python3 main.py --rag-query "question" --context-file file.txt

# Cache management
python3 main.py --rag-clear-cache
python3 main.py --rag-cache-stats
```

### Cascade Commands
```bash
# Processing requests
python3 main.py --request "complex task"
python3 main.py --interactive --cascade

# Monitoring
python3 main.py --cascade-status
python3 main.py --cascade-history
```

### Advanced Options
```bash
# JSON output for scripting
python3 main.py --status --json

# Verbose output for debugging
python3 main.py --status --verbose

# Batch processing
python3 main.py --batch-process requests.json

# Export/Import
python3 main.py --export-config backup.json
python3 main.py --import-config backup.json
```

## Troubleshooting

### Common Issues

1. **Slow Performance**
   - Check system resources (memory, CPU)
   - Enable Metal acceleration on M3 Macs
   - Use smaller models for faster responses
   - Clear cache if it's consuming too much memory

2. **Model Not Found**
   - Verify model is installed in Ollama
   - Check model name spelling
   - Use `--models list` to see available models

3. **High Memory Usage**
   - Reduce batch sizes
   - Unload unused models
   - Use memory-efficient settings
   - Close other applications

4. **RAG Retrieval Issues**
   - Re-index content with appropriate chunking
   - Adjust similarity thresholds
   - Try different embedding models
   - Increase top_k parameter

### Debugging

Enable debugging for detailed output:
```bash
# Enable general debugging
export DEBUG=1

# Enable RAG debugging
export RAG_DEBUG=1

# Enable Cascade debugging
export CASCADE_DEBUG=1

# Run with verbose output
python3 main.py --request "debug task" --verbose
```

### Logs and Diagnostics

View detailed logs:
```bash
# View system logs
python3 main.py --logs

# Validate configuration
python3 main.py --validate-config

# Check system requirements
python3 main.py --check-requirements
```

## Conclusion

The AI Stack provides a powerful, flexible platform for local AI development with enterprise-grade features. Its combination of generic model support, intelligent selection, RAG capabilities, and cascade processing makes it suitable for a wide range of AI tasks while maintaining privacy and control over your data.

For detailed information about specific components, refer to the individual documentation files in the `docs/` directory.
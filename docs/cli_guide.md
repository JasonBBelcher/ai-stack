# CLI Guide

## Overview

The AI Stack provides a comprehensive command-line interface for interacting with all system components. This guide covers all available CLI commands and their usage.

## Basic Usage

```bash
python3 main.py [OPTIONS] COMMAND [ARGS]
```

## Core Commands

### System Information

```bash
# Check system status
python3 main.py --status

# Get health check report
python3 main.py --health-check

# View current configuration
python3 main.py --config
```

### Model Management

```bash
# List available models
python3 main.py --models list

# Get detailed model information
python3 main.py --model-info llama3.1:8b

# Discover new models
python3 main.py --models discover
```

### Profile Management

```bash
# List available profiles
python3 main.py --profile list

# Switch to a specific profile
python3 main.py --profile coding

# View current profile
python3 main.py --profile current
```

## RAG Commands

### Indexing

```bash
# Index a codebase or document collection
python3 main.py --rag-index /path/to/documents

# Index with specific profile
python3 main.py --rag-index /path/to/documents --profile coding

# View indexing status
python3 main.py --rag-status

# Validate index integrity
python3 main.py --rag-validate

# Clear the index
python3 main.py --rag-clear
```

### Querying

```bash
# Perform a RAG-enhanced query
python3 main.py --rag-query "How does the memory manager work?"

# Query with context file
python3 main.py --rag-query "Explain this code" --context-file code.py

# Query with specific profile
python3 main.py --rag-query "Research question" --profile research

# Enable verbose output
python3 main.py --rag-query "Question" --verbose
```

### Cache Management

```bash
# Clear query cache
python3 main.py --rag-clear-cache

# View cache statistics
python3 main.py --rag-cache-stats

# Warm cache with common queries
python3 main.py --rag-warm-cache
```

## Cascade Commands

### Processing Requests

```bash
# Submit a request for cascade processing
python3 main.py --request "Create a REST API for a todo application"

# Submit with specific profile
python3 main.py --request "Research task" --profile research

# Enable interactive mode
python3 main.py --interactive --cascade
```

### Monitoring

```bash
# View current cascade operations
python3 main.py --cascade-status

# View cascade history
python3 main.py --cascade-history

# Reset cascade state
python3 main.py --cascade-reset
```

## Advanced Commands

### Interactive Mode

```bash
# Start interactive mode
python3 main.py --interactive

# Start interactive mode with JSON output
python3 main.py --interactive --json
```

### Batch Processing

```bash
# Process multiple requests from a file
python3 main.py --batch-process requests.json

# Process with specific concurrency
python3 main.py --batch-process requests.json --concurrency 3
```

### Export/Import

```bash
# Export configuration
python3 main.py --export-config config_backup.json

# Import configuration
python3 main.py --import-config config_backup.json

# Export index
python3 main.py --export-index index_backup.faiss

# Import index
python3 main.py --import-index index_backup.faiss
```

## Output Options

### JSON Output

Many commands support JSON output for scripting:

```bash
# Get models list as JSON
python3 main.py --models list --json

# Get health check as JSON
python3 main.py --health-check --json

# Get status as JSON
python3 main.py --status --json
```

### Verbose Output

Enable verbose output for debugging:

```bash
# Verbose mode
python3 main.py --status --verbose

# Very verbose mode
python3 main.py --status --verbose --verbose
```

## Environment Commands

### Validation

```bash
# Validate configuration files
python3 main.py --validate-config

# Check system requirements
python3 main.py --check-requirements

# Validate model installations
python3 main.py --validate-models
```

### Maintenance

```bash
# Clean temporary files
python3 main.py --clean

# Update model registry
python3 main.py --update-registry

# Reload configuration
python3 main.py --reload-config
```

## Scripting Examples

### Automation Script

```bash
#!/bin/bash

# Check system health
echo "Checking system health..."
python3 main.py --health-check --json > health.json

# Index new documents if needed
if [ -d "/new/documents" ]; then
    echo "Indexing new documents..."
    python3 main.py --rag-index /new/documents
fi

# Process user requests
while read request; do
    echo "Processing: $request"
    python3 main.py --request "$request" --json >> results.json
done < requests.txt
```

### Monitoring Script

```bash
#!/bin/bash

# Monitor cascade operations
while true; do
    status=$(python3 main.py --cascade-status --json)
    if [ "$status" != "{}" ]; then
        echo "Active operations: $status"
    fi
    sleep 30
done
```

## Error Handling

### Exit Codes

The CLI returns standard exit codes:
- 0: Success
- 1: General error
- 2: Misuse of shell builtins
- 64: Command line usage error
- 65: Data format error
- 66: Cannot open input
- 67: Addressee unknown
- 68: Host name unknown
- 69: Service unavailable
- 70: Internal software error
- 71: System error
- 72: Critical OS file missing
- 73: Cannot create user output file
- 74: Input/output error
- 75: Temp failure
- 76: Remote error
- 77: Permission denied
- 78: Configuration error

### Error Messages

Error messages provide detailed information about issues:

```bash
$ python3 main.py --model-info nonexistent:model
Error: Model 'nonexistent:model' not found
Suggestions:
  - Check model name spelling
  - Verify model is installed in Ollama
  - Use --models list to see available models
```

## Performance Tips

### Efficient Querying

1. **Use cache**: Enable caching for repeated queries
2. **Batch requests**: Process multiple queries together
3. **Limit results**: Use appropriate top_k values
4. **Filter early**: Apply constraints before processing

### Resource Management

1. **Monitor memory**: Keep track of memory usage
2. **Close unused models**: Unload models when not needed
3. **Use appropriate models**: Select models based on task complexity
4. **Enable Metal acceleration**: On M3 Macs, use Metal for better performance

### Troubleshooting CLI Issues

1. **Command not found**: Ensure you're in the correct directory
2. **Permission denied**: Check file permissions
3. **Model not found**: Verify model installation in Ollama
4. **Connection refused**: Check that Ollama is running
5. **Timeout errors**: Increase timeout settings for slow operations

### Debugging

Enable debugging for detailed output:

```bash
# Enable general debugging
export DEBUG=1

# Enable RAG debugging
export RAG_DEBUG=1

# Enable Cascade debugging
export CASCADE_DEBUG=1

# Run with debug output
python3 main.py --request "Debug this" --verbose
```
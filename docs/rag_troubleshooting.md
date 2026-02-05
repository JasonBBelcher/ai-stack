# RAG Troubleshooting Guide

## Common Issues and Solutions

### 1. Slow Query Performance

**Symptoms**: Queries take longer than expected to return results.

**Possible Causes and Solutions**:
- **Metal acceleration not enabled**: On M3 Macs, ensure Metal acceleration is enabled with `export METAL_DEVICE_FORCE_LOW_POWER_GPU=1`
- **Cache not warmed**: Configure warm queries in the cache settings to preload common queries
- **Large chunk sizes**: Reduce chunk size for faster processing
- **Small batch sizes**: Increase batch size for embedding operations
- **Insufficient memory**: Close other applications to free up memory

### 2. Low Relevance Results

**Symptoms**: Retrieved results don't match the query intent.

**Possible Causes and Solutions**:
- **Incorrect similarity threshold**: Adjust the min_similarity parameter in retrieval settings
- **Poor embedding model**: Try different embedding models suited for your content type
- **Inappropriate chunking**: Use AST-based chunking for code, semantic chunking for documents
- **Too few results**: Increase the top_k parameter to retrieve more candidates
- **Metadata filtering**: Add metadata filters to narrow down results

### 3. Memory Issues

**Symptoms**: High memory usage or out-of-memory errors.

**Possible Causes and Solutions**:
- **Large batch sizes**: Reduce batch size for embedding operations
- **Memory-efficient indexing not enabled**: Enable memory-efficient indexing for large codebases
- **Large embedding models**: Use smaller embedding models with lower memory footprint
- **Multiple concurrent operations**: Process one operation at a time

### 4. Indexing Failures

**Symptoms**: Indexing process fails or stops unexpectedly.

**Possible Causes and Solutions**:
- **Malformed files**: Skip or preprocess malformed files before indexing
- **Unsupported file types**: Ensure only supported file types are being indexed
- **Permission issues**: Check file permissions for read access
- **Disk space**: Ensure sufficient disk space for index storage

### 5. Cache Misses

**Symptoms**: Frequently repeated queries don't benefit from caching.

**Possible Causes and Solutions**:
- **Cache size too small**: Increase max_size in cache configuration
- **Short TTL**: Increase time-to-live for cached entries
- **Query variations**: Normalize queries to improve cache hit rate
- **Cache not persisted**: Enable persistence to maintain cache across sessions

## Debugging Techniques

### Enable Verbose Logging

Add logging to see detailed information about the RAG process:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or use the CLI flag:

```bash
python3 main.py --rag-query "test query" --verbose
```

### Monitor Performance Metrics

Use the built-in monitoring tools to track performance:

```python
from src.monitoring.performance_tracker import PerformanceTracker
tracker = PerformanceTracker()
tracker.start_monitoring()

# Perform RAG operations
# ...

metrics = tracker.get_metrics()
print(metrics)
```

### Profile Code Execution

Use the profiler to identify bottlenecks:

```python
from src.monitoring.profiler import Profiler
profiler = Profiler()

with profiler.profile("embedding_operation"):
    # Perform embedding operation
    pass

profile_data = profiler.get_profile_data()
print(profile_data)
```

## Diagnostic Commands

### Check Index Status

```bash
python3 main.py --rag-status
```

This command shows:
- Number of indexed documents
- Index size
- Cache statistics
- Performance metrics

### Validate Index Integrity

```bash
python3 main.py --rag-validate
```

This command checks:
- Index file integrity
- Vector consistency
- Metadata completeness

### Clear Cache

```bash
python3 main.py --rag-clear-cache
```

This command:
- Clears in-memory cache
- Removes persisted cache files
- Resets cache statistics

## Performance Tuning

### Optimize Chunking

Experiment with different chunking strategies:

```json
{
  "chunking": {
    "strategy": "ast",
    "size": 512,
    "overlap": 50
  }
}
```

Try different values for size and overlap to find the optimal balance between granularity and context.

### Tune Retrieval Parameters

Adjust retrieval settings for better results:

```json
{
  "retrieval": {
    "top_k": 5,
    "min_similarity": 0.7,
    "rerank": true
  }
}
```

Increase top_k to get more candidates, adjust min_similarity for precision vs. recall tradeoff.

### Configure Cache Settings

Optimize cache for your usage patterns:

```json
{
  "cache": {
    "max_size": 1000,
    "ttl": 3600,
    "persistence": true
  }
}
```

Increase max_size for more cached queries, adjust ttl based on how often content changes.

## Environment-Specific Issues

### M3 Mac Specific Issues

**Issue**: Metal acceleration not working
**Solution**: Ensure you're using a compatible version of PyTorch with Metal support

**Issue**: Thermal throttling affecting performance
**Solution**: Monitor system temperature and allow cooling periods between intensive operations

### Virtual Environment Issues

**Issue**: Missing dependencies
**Solution**: Install all required packages with `pip install -r requirements.txt`

**Issue**: Path issues
**Solution**: Ensure PYTHONPATH includes the src directory

## Advanced Debugging

### Enable Debug Mode

Set environment variable for maximum verbosity:

```bash
export RAG_DEBUG=1
python3 main.py --rag-query "debug query"
```

### Dump Internal State

Use internal debugging functions to dump state:

```python
from src.rag.debug import dump_internal_state
dump_internal_state()
```

This will output:
- Current index state
- Cache contents
- Configuration settings
- Performance counters

## Contact Support

If you're unable to resolve an issue:

1. Check the GitHub issues page for similar problems
2. Include the following information in your support request:
   - Error messages and stack traces
   - System specifications (OS, Python version, hardware)
   - Steps to reproduce the issue
   - Relevant configuration files
3. Attach debug logs if available
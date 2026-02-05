# Cascade Troubleshooting Guide

## Common Issues and Solutions

### 1. Cascade Not Triggering

**Symptoms**: Requests are processed directly without cascade intervention.

**Possible Causes and Solutions**:
- **Cascade disabled in profile**: Ensure `"enabled": true` in cascade_settings
- **Request not complex enough**: Cascade triggers on ambiguous or complex requests
- **Model unavailable**: Check that specified models in cascade stages are available
- **Configuration error**: Verify cascade configuration in user profiles

### 2. Infinite Clarification Loops

**Symptoms**: The system keeps asking for clarifications without making progress.

**Possible Causes and Solutions**:
- **Low confidence threshold**: Increase min_confidence_threshold in flow_control
- **Ambiguous request**: Provide more specific initial requests
- **Conflicting constraints**: Resolve contradictory requirements in the request
- **Model inconsistency**: Use more consistent models across cascade stages

### 3. Performance Issues

**Symptoms**: Cascade operations take too long or consume excessive resources.

**Possible Causes and Solutions**:
- **Parallel processing disabled**: Enable enable_parallel_stages for faster execution
- **Large models in early stages**: Use smaller, faster models for initial analysis
- **Too many iterations**: Reduce max_iterations in stage configurations
- **Memory constraints**: Enable unload_between_stages to free memory between stages

### 4. Poor Quality Results

**Symptoms**: Generated outputs don't meet expectations.

**Possible Causes and Solutions**:
- **Inappropriate models**: Use models better suited for each stage
- **Insufficient critique iterations**: Increase max_iterations for critique stage
- **Low confidence thresholds**: Increase thresholds to ensure higher quality
- **Poor prompt engineering**: Review and improve prompts for each stage

### 5. Memory Issues

**Symptoms**: High memory usage or out-of-memory errors during cascade operations.

**Possible Causes and Solutions**:
- **Caching intermediate results**: Disable cache_intermediate_results if memory is limited
- **Large context windows**: Reduce context window sizes in stage configurations
- **Multiple concurrent cascades**: Process one cascade at a time
- **Model sizes**: Use smaller models that require less memory

## Debugging Techniques

### Enable Verbose Logging

Add logging to see detailed information about the cascade process:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or use the CLI flag:

```bash
python3 main.py --request "test request" --cascade --verbose
```

### Monitor Stage Progress

Use callbacks to monitor progress at each stage:

```python
def progress_callback(stage, status, progress):
    print(f"Stage: {stage}, Status: {status}, Progress: {progress}%")

cascade = CascadeRAG(progress_callback=progress_callback)
```

### Dump Internal State

Use internal debugging functions to dump state:

```python
from src.cascade.debug import dump_cascade_state
dump_cascade_state()
```

This will output:
- Current stage information
- Configuration settings
- Progress metrics
- Error history

## Diagnostic Commands

### Check Cascade Status

```bash
python3 main.py --cascade-status
```

This command shows:
- Active cascade operations
- Current stage for each operation
- Progress percentages
- Resource usage

### View Cascade History

```bash
python3 main.py --cascade-history
```

This command shows:
- Completed cascade operations
- Duration of each operation
- Success/failure status
- User feedback scores

### Reset Cascade State

```bash
python3 main.py --cascade-reset
```

This command:
- Clears active cascade operations
- Resets progress tracking
- Clears error history

## Performance Tuning

### Optimize Stage Configuration

Experiment with different stage configurations:

```json
{
  "cascade_settings": {
    "stages": {
      "planning": {
        "model": "mistral:latest",
        "max_iterations": 1,
        "timeout_seconds": 15
      }
    }
  }
}
```

Try different models and timeout values to find the optimal balance between speed and quality.

### Adjust Flow Control

Fine-tune flow control settings:

```json
{
  "cascade_settings": {
    "flow_control": {
      "enable_parallel_stages": true,
      "enable_early_termination": true,
      "min_confidence_threshold": 0.75
    }
  }
}
```

Enable parallel processing for speed, adjust confidence thresholds for quality.

### Configure Memory Management

Optimize memory usage:

```json
{
  "cascade_settings": {
    "memory_management": {
      "unload_between_stages": true,
      "cache_intermediate_results": false
    }
  }
}
```

Unload models between stages to save memory, disable caching if memory is limited.

## Environment-Specific Issues

### M3 Mac Specific Issues

**Issue**: Thermal throttling affecting cascade performance
**Solution**: Monitor system temperature and allow cooling periods between intensive operations

**Issue**: Memory pressure from multiple large models
**Solution**: Use memory_management settings to unload models between stages

### Resource-Constrained Environments

**Issue**: Limited memory for cascade operations
**Solution**: Use smaller models and disable intermediate result caching

**Issue**: Slow processing due to CPU limitations
**Solution**: Reduce max_iterations and use faster models

## Advanced Debugging

### Enable Debug Mode

Set environment variable for maximum verbosity:

```bash
export CASCADE_DEBUG=1
python3 main.py --request "debug request" --cascade
```

### Profile Stage Performance

Use the profiler to identify slow stages:

```python
from src.monitoring.profiler import Profiler
profiler = Profiler()

# Profile each cascade stage
with profiler.profile("planning_stage"):
    # Planning stage execution
    pass

profile_data = profiler.get_profile_data()
print(profile_data)
```

### Analyze Decision Making

Enable decision logging to understand cascade choices:

```python
from src.cascade.debug import enable_decision_logging
enable_decision_logging(True)
```

This will log:
- Why certain stages were selected
- How confidence scores were calculated
- Reasoning behind model choices
- Path selection rationale

## Contact Support

If you're unable to resolve an issue:

1. Check the GitHub issues page for similar problems
2. Include the following information in your support request:
   - Error messages and stack traces
   - System specifications (OS, Python version, hardware)
   - Steps to reproduce the issue
   - Relevant configuration files
   - Cascade history and status information
3. Attach debug logs if available
4. Provide sample requests that trigger the issue
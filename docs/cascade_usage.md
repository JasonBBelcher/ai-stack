# Cascade Usage Guide

## Getting Started

To use the Cascade functionality in the AI Stack, you need to:

1. Configure cascade settings in user profiles
2. Submit requests that benefit from multi-stage processing
3. Respond to clarifications when prompted
4. Monitor progress through the CLI or API

## Configuring Cascade Settings

Cascade settings are configured in user profiles located in `config/user_profiles/`:

```json
{
  "cascade_settings": {
    "enabled": true,
    "stages": {
      "planning": {
        "model": "llama3.1:8b",
        "max_iterations": 2,
        "timeout_seconds": 30,
        "temperature": 0.3
      },
      "critique": {
        "model": "qwen2.5:14b",
        "max_iterations": 2,
        "timeout_seconds": 30,
        "temperature": 0.2
      },
      "execution": {
        "model": "qwen2.5:14b",
        "max_iterations": 1,
        "timeout_seconds": 60,
        "temperature": 0.3
      }
    },
    "flow_control": {
      "enable_parallel_stages": false,
      "enable_early_termination": true,
      "min_confidence_threshold": 0.8
    }
  }
}
```

## Using Cascade with the CLI

### Basic Cascade Request

```bash
# Submit a request that will trigger cascade processing
python3 main.py --request "Create a REST API for a todo application"

# Use a specific profile with cascade settings
python3 main.py --request "Analyze this codebase" --profile coding
```

### Interactive Cascade Session

```bash
# Start an interactive cascade session
python3 main.py --interactive --cascade

# The system will prompt for clarifications and show progress
```

### Monitoring Cascade Progress

```bash
# View current cascade operations
python3 main.py --cascade-status

# View detailed cascade history
python3 main.py --cascade-history
```

## Using Cascade with the API

### Basic Cascade Request

```python
from src.cascade.cascade_rag import CascadeRAG

# Create cascade instance
cascade = CascadeRAG()

# Submit request
result = cascade.process_request("Create a REST API for a todo application")

# Get progress updates
progress = cascade.get_progress()
print(progress)
```

### Handling Clarifications

```python
from src.cascade.cascade_rag import CascadeRAG

def handle_clarification(question, options):
    # Present question to user and get response
    print(question)
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    
    choice = input("Select an option: ")
    return options[int(choice)-1]

# Create cascade instance with clarification handler
cascade = CascadeRAG(clarification_callback=handle_clarification)

# Submit request
result = cascade.process_request("Build a machine learning model")
```

### Monitoring Progress

```python
from src.cascade.cascade_rag import CascadeRAG

def progress_callback(stage, status, progress):
    print(f"Stage: {stage}, Status: {status}, Progress: {progress}%")

# Create cascade instance with progress callback
cascade = CascadeRAG(progress_callback=progress_callback)

# Submit request
result = cascade.process_request("Analyze customer data")
```

## Cascade Profiles

Different user profiles have different cascade configurations optimized for specific use cases:

### Coding Profile
- Detailed planning stage with code-focused models
- Thorough critique stage for code quality
- Execution stage optimized for code generation
- Conservative confidence thresholds

### Research Profile
- Comprehensive planning for thorough analysis
- Multiple critique iterations for accuracy
- Cloud models for complex reasoning tasks
- Lower confidence thresholds for exploratory research

### Writing Profile
- Creative planning stage
- Style-focused critique
- Multiple execution paths for different tones
- Higher temperature settings for creativity

## Performance Optimization

### Parallel Processing

Enable parallel stage execution for faster processing:

```json
{
  "cascade_settings": {
    "flow_control": {
      "enable_parallel_stages": true
    }
  }
}
```

### Early Termination

Enable early termination to skip unnecessary stages:

```json
{
  "cascade_settings": {
    "flow_control": {
      "enable_early_termination": true,
      "min_confidence_threshold": 0.8
    }
  }
}
```

### Memory Management

Configure memory management for large cascade operations:

```json
{
  "cascade_settings": {
    "memory_management": {
      "unload_between_stages": true,
      "cache_intermediate_results": true
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Cascade Not Triggering**
   - Check if cascade is enabled in profile
   - Ensure request complexity warrants cascade processing
   - Verify model availability

2. **Clarification Loops**
   - Adjust confidence thresholds
   - Provide more specific initial requests
   - Review ambiguity detector settings

3. **Performance Issues**
   - Enable parallel processing
   - Adjust timeout settings
   - Use smaller models for initial stages

### Debugging

Enable verbose logging to debug cascade operations:

```bash
python3 main.py --request "test request" --cascade --verbose
```

Or in code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### Request Formulation

1. **Be Specific**: Provide clear goals and constraints upfront
2. **Include Context**: Mention relevant background information
3. **Define Success**: Explain what constitutes a successful outcome
4. **List Constraints**: Specify time, budget, or technical limitations

### Response to Clarifications

1. **Respond Promptly**: Delays can affect cascade efficiency
2. **Be Decisive**: Indecision can lead to multiple clarification rounds
3. **Provide Detail**: Elaborate on your choices when possible
4. **Stay Consistent**: Maintain consistent preferences throughout the process

### Monitoring and Feedback

1. **Track Progress**: Regularly check cascade status for long operations
2. **Provide Feedback**: Rate results to improve future cascade operations
3. **Review History**: Learn from previous cascade operations
4. **Adjust Settings**: Modify cascade configuration based on usage patterns

### Resource Management

1. **Plan Ahead**: Consider resource requirements for complex cascades
2. **Monitor Usage**: Keep track of memory and processing consumption
3. **Set Limits**: Configure timeouts and iteration limits
4. **Clean Up**: Remove intermediate results when no longer needed
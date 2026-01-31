# Example Usage of AI Stack

This document provides examples of how to use the local AI stack.

## Quick Start

### 1. Health Check
```bash
python3 main.py --health-check
```

### 2. System Status
```bash
python3 main.py --status
```

### 3. Configuration View
```bash
python3 main.py --config
```

### 4. Simple Request
```bash
python3 main.py "Create a Python function that calculates factorial"
```

### 5. Interactive Mode
```bash
python3 main.py --interactive
```

## Example Workflows

### Code Generation Example
```bash
python3 main.py "Write a REST API endpoint in Python using Flask that handles user authentication" --json --output flask_auth.py
```

### Debugging Example
```bash
python3 main.py "My Python script is crashing with a segmentation fault. Help me debug it." --context "The script processes large CSV files and uses pandas"
```

### Planning Example
```bash
python3 main.py "I need to migrate a database from PostgreSQL to MySQL. Create a migration plan." --additional-context "The database has 50 tables and complex relationships"
```

## Advanced Usage

### Custom Configuration
You can modify the `src/config.py` file to adjust:
- Model settings (temperature, max tokens)
- Memory management thresholds
- Retry logic
- Performance optimization settings

### Monitoring
The system includes comprehensive monitoring:
- Memory usage tracking
- Thermal state monitoring
- Model loading/unloading metrics
- Performance timing

### Error Handling
The system includes robust error handling:
- Automatic model retries
- Memory cleanup on failures
- Thermal throttling adjustment
- Graceful degradation

## Expected Outputs

### Successful Workflow
```json
{
  "success": true,
  "execution_time": 45.2,
  "memory_used": 8.3,
  "plan": {
    "plan_summary": "Create Flask authentication endpoint",
    "steps": [...],
    "total_steps": 5,
    "complexity": "moderate"
  },
  "output": "# Complete Flask authentication code...",
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "execution_time": 0.0,
  "memory_used": 0.0,
  "plan": null,
  "output": null,
  "error": "Failed to load planner model: mistral:latest"
}
```

## Performance Expectations

### Model Loading Times
- mistral-7b: ~15-20 seconds
- qwen2.5-14b: ~25-35 seconds

### Memory Usage
- Planner phase: ~5GB
- Critic phase: ~5GB  
- Executor phase: ~10GB
- Peak usage: ~10GB with 2GB safety buffer

### Thermal Considerations
- Normal operation: Stable performance
- High thermal: Automatic performance adjustment
- Critical thermal: Suggests cooling period

## Troubleshooting

### Common Issues
1. **Ollama not running**: Start Ollama with `ollama serve`
2. **Insufficient memory**: Close other applications
3. **Model loading failures**: Check Ollama with `ollama list`
4. **High thermal state**: Allow system to cool

### Debug Commands
```bash
# Check Ollama status
ollama ps

# Monitor system memory
vm_stat

# Check thermal state (requires sudo)
sudo powermetrics --samplers thermal -i 1000 -n 1
```

## Next Steps

After initial setup:
1. Test with simple prompts
2. Experiment with different contexts
3. Monitor performance metrics
4. Adjust configuration as needed
5. Explore more complex workflows
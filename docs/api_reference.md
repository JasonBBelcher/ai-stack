# API Reference

## Core Classes

### AIStackController

Main controller class that orchestrates the AI stack workflow.

#### Methods

##### `__init__(config: Optional[AIStackConfig] = None)`
Initialize the controller with optional configuration.

**Parameters:**
- `config`: Optional AIStackConfig instance

##### `health_check() -> Dict[str, Any]`
Perform system health check.

**Returns:**
- Dict containing health status, Ollama status, available models, memory state, and thermal state

**Example:**
```python
controller = AIStackController()
health = controller.health_check()
print(f"Ollama running: {health['ollama_running']}")
```

##### `process_request(user_input: str, context: str = "", additional_context: str = "") -> WorkflowResult`
Process a user request through the full workflow.

**Parameters:**
- `user_input`: The main request or prompt
- `context`: Additional context for planning phase
- `additional_context`: Additional context for execution phase

**Returns:**
- WorkflowResult object with execution details

**Example:**
```python
result = controller.process_request(
    "Write a Python function to sort a list",
    context="For a data processing pipeline",
    additional_context="Use built-in sorted() function"
)
if result.success:
    print(result.output)
else:
    print(f"Error: {result.error}")
```

##### `get_system_status() -> Dict[str, Any]`
Get comprehensive system status.

**Returns:**
- Dict with health, memory, loaded models, and configuration info

---

### ModelManager

Handles model loading, unloading, and monitoring.

#### Methods

##### `load_model(model_name: str, timeout: int = 60) -> ModelState`
Load a specific model into memory.

**Parameters:**
- `model_name`: Name of the model to load
- `timeout`: Maximum time to wait for loading

**Returns:**
- ModelState enum (LOADED, UNLOADED, ERROR)

##### `unload_model(model_name: str) -> bool`
Unload a model from memory.

**Parameters:**
- `model_name`: Name of the model to unload

**Returns:**
- Boolean indicating success

##### `unload_all_models() -> None`
Unload all currently loaded models.

##### `get_loaded_models() -> List[str]`
Get list of currently loaded models.

**Returns:**
- List of model names

##### `can_load_model(model_name: str, safety_buffer_gb: float = 2.0) -> bool`
Check if a model can be loaded within memory constraints.

**Parameters:**
- `model_name`: Name of the model to check
- `safety_buffer_gb`: Memory buffer to maintain

**Returns:**
- Boolean indicating if model can be loaded

---

### MemoryManager

Monitors and manages system memory usage.

#### Methods

##### `get_system_memory() -> Dict[str, float]`
Get current system memory information.

**Returns:**
- Dict with total, used, available memory in GB and usage percentage

##### `take_memory_snapshot() -> MemorySnapshot`
Capture current memory state and add to history.

**Returns:**
- MemorySnapshot object with detailed memory info

##### `get_thermal_state() -> Dict[str, Any]`
Get thermal information.

**Returns:**
- Dict with thermal level and score (normal, moderate, high, critical)

##### `get_memory_report() -> Dict[str, Any]`
Generate comprehensive memory report.

**Returns:**
- Dict with current memory, thermal state, trend, and recommendations

---

### PromptTemplates

Manages role-specific prompt templates.

#### Methods

##### `get_planner_config() -> PromptConfig`
Get configuration for Planner model.

##### `get_critic_config() -> PromptConfig`
Get configuration for Critic model.

##### `get_executor_config() -> PromptConfig`
Get configuration for Executor model.

##### `format_template(template: str, **kwargs) -> str`
Format a template with provided variables.

**Parameters:**
- `template`: Template string with placeholders
- `**kwargs`: Values to substitute in template

**Returns:**
- Formatted string

---

### AIStackConfig

Centralized configuration management.

#### Methods

##### `get_planner_config() -> ModelConfig`
Get planner model configuration.

##### `get_executor_config() -> ModelConfig`
Get executor model configuration.

##### `get_critic_config(use_alternative: bool = False) -> ModelConfig`
Get critic model configuration.

##### `validate_configuration() -> List[str]`
Validate current configuration.

**Returns:**
- List of configuration issues (empty if valid)

##### `get_optimization_settings() -> Dict[str, Any]`
Get performance optimization settings.

**Returns:**
- Dict with optimization settings and thresholds

---

## Data Classes

### WorkflowResult
Result of a workflow execution.

**Fields:**
- `success`: bool - Whether the workflow completed successfully
- `plan`: Optional[Dict] - The generated plan
- `critique`: Optional[Dict] - The critique results
- `output`: Optional[str] - The final output
- `error`: Optional[str] - Error message if failed
- `execution_time`: float - Total execution time in seconds
- `memory_used`: float - Peak memory usage in GB

### ModelConfig
Configuration for a specific model.

**Fields:**
- `name`: str - Model name
- `ollama_name`: str - Ollama model identifier
- `type`: ModelType - Model role type
- `temperature`: float - Sampling temperature
- `max_tokens`: int - Maximum tokens to generate
- `memory_gb`: float - Estimated memory usage
- `alternative`: str - Alternative model

### PromptConfig
Configuration for model prompting.

**Fields:**
- `temperature`: float - Sampling temperature
- `max_tokens`: int - Maximum tokens
- `system_prompt`: str - System prompt template
- `user_template`: str - User prompt template

---

## Enums

### ModelType
Enumeration of model roles.

**Values:**
- `PLANNER`: Task planning and decomposition
- `CRITIC`: Plan validation and critique
- `EXECUTOR`: Output generation and execution

### ModelState
Enumeration of model loading states.

**Values:**
- `LOADED`: Model is loaded in memory
- `UNLOADED`: Model is not loaded
- `ERROR`: Error occurred during loading

---

## Command Line Interface

### Main Commands

```bash
# Basic usage
python3 main.py "your prompt here"

# With context
python3 main.py "prompt" --context "additional context"

# Interactive mode
python3 main.py --interactive

# System checks
python3 main.py --health-check
python3 main.py --status
python3 main.py --config

# Output options
python3 main.py "prompt" --json --output result.json
```

### Options

- `input`: Prompt or request to process
- `--context`: Additional context for planning
- `--additional-context`: Additional context for execution
- `--health-check`: Perform system health check
- `--status`: Show detailed system status
- `--config`: Show current configuration
- `--interactive`: Start interactive mode
- `--output`: Output file for results
- `--json`: Output results in JSON format

---

## Error Handling

### Common Errors

1. **Ollama not running**: Ensure Ollama is started with `ollama serve`
2. **Model not found**: Check available models with `ollama list`
3. **Insufficient memory**: Close other applications or reduce safety buffer
4. **Thermal throttling**: Allow system to cool before continuing

### Error Recovery

The system includes automatic error recovery:
- Model loading retries (default 3 attempts)
- Memory cleanup on failures
- Thermal adjustment when overheating
- Graceful degradation when resources are constrained
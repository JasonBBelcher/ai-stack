# Configuration Guide

## Overview

The AI Stack uses a hierarchical configuration system that allows fine-grained control over all components. This guide explains how to configure the system for optimal performance.

## Configuration Files

### Main Configuration
- `config/models.json` - Model definitions and capabilities
- `config/user_profiles/` - User profile configurations
- `config/rag_profiles/` - RAG profile configurations

### Profile Configuration

User profiles are stored in `config/user_profiles/` and contain settings for different use cases:

```json
{
  "name": "coding",
  "description": "Optimized for programming and development tasks",
  "role_mappings": {
    "planner": {
      "preferred": ["llama3.1:8b", "mistral:latest"],
      "reasoning_strength": 0.8
    }
  },
  "system_settings": {
    "enable_cloud_fallbacks": true,
    "max_memory_usage_gb": 12.0
  },
  "cascade_settings": {
    "enabled": true,
    "stages": {
      "planning": {
        "model": "llama3.1:8b",
        "max_iterations": 2,
        "timeout_seconds": 30
      }
    }
  }
}
```

### Model Configuration

Model configurations are stored in `config/models.json`:

```json
{
  "model_profiles": {
    "llama3.1:8b": {
      "capabilities": {
        "tags": ["coding", "reasoning", "generation"],
        "coding_strength": 0.7,
        "reasoning_strength": 0.8
      },
      "requirements": {
        "min_memory_gb": 6.0,
        "supports_function_calling": true
      }
    }
  },
  "cloud_providers": {
    "openai": {
      "models": {
        "gpt-4o": {
          "capabilities": {
            "tags": ["coding", "reasoning", "generation", "premium"],
            "coding_strength": 0.9,
            "reasoning_strength": 0.95
          }
        }
      }
    }
  }
}
```

## RAG Profile Configuration

RAG profiles are stored in `config/rag_profiles/`:

```json
{
  "profile_name": "coding",
  "chunking": {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "strategy": "code_aware"
  },
  "embedding": {
    "model": "nomic-embed-text",
    "dimension": 768
  },
  "retrieval": {
    "top_k": 5,
    "min_similarity": 0.7
  }
}
```

## Environment Variables

The system supports several environment variables for configuration:

```bash
# Ollama settings
export OLLAMA_HOST=127.0.0.1:11434

# Performance settings
export METAL_DEVICE_FORCE_LOW_POWER_GPU=1

# Debug settings
export RAG_DEBUG=1
export CASCADE_DEBUG=1

# Cache settings
export CACHE_DIR=/tmp/ai_stack_cache
```

## Configuration Best Practices

### Model Selection

1. **Match models to tasks**: Use coding-strong models for programming tasks
2. **Consider memory requirements**: Ensure sufficient memory for selected models
3. **Balance local vs cloud**: Use local models for privacy, cloud for complex tasks
4. **Set appropriate timeouts**: Configure timeouts based on model response times

### Profile Customization

1. **Create specialized profiles**: Different profiles for coding, research, writing
2. **Adjust cascade settings**: Modify stages based on typical workflows
3. **Set resource limits**: Configure memory and thermal thresholds
4. **Enable/disable features**: Turn off unused features to save resources

### RAG Optimization

1. **Choose appropriate chunk sizes**: Smaller for code, larger for documents
2. **Select embedding models**: BGE for code, Sentence-BERT for general text
3. **Tune retrieval parameters**: Adjust top_k and similarity thresholds
4. **Configure caching**: Set cache size and TTL based on usage patterns

### Performance Tuning

1. **Monitor resource usage**: Keep track of memory and CPU consumption
2. **Adjust batch sizes**: Larger batches for better throughput, smaller for responsiveness
3. **Enable Metal acceleration**: On M3 Macs, use Metal for improved performance
4. **Use efficient models**: Balance model size with performance requirements

## Security Configuration

### API Key Management

API keys are encrypted and stored securely:

```json
{
  "cloud_settings": {
    "enable_openai": true,
    "enable_anthropic": false
  }
}
```

### Access Controls

Profiles can restrict access to certain models or features:

```json
{
  "access_controls": {
    "allowed_models": ["llama3.1:8b", "mistral:latest"],
    "restricted_features": ["cloud_fallback"]
  }
}
```

## Troubleshooting Configuration Issues

### Common Configuration Errors

1. **Invalid JSON**: Ensure all configuration files are valid JSON
2. **Missing required fields**: Check that all required configuration fields are present
3. **Incorrect model names**: Verify that model names match those available in Ollama
4. **Resource conflicts**: Ensure memory requirements don't exceed system limits

### Validation Tools

Use the built-in configuration validator:

```bash
python3 main.py --validate-config
```

This command checks:
- JSON syntax validity
- Required fields presence
- Model name correctness
- Resource requirement feasibility

### Configuration Reload

Reload configuration without restarting:

```bash
python3 main.py --reload-config
```

This command:
- Reloads all configuration files
- Updates running system settings
- Preserves current state where possible
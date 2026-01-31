# Generic Model Swappability Implementation Plan

## Overview

This document describes the implementation plan for making the AI stack's model system generically swappable, moving from hardcoded model definitions to a dynamic, configuration-driven system.

## Current State Analysis

### Existing Architecture
- **Role-based system**: Planner (mistral), Critic (mistral/qwen2.5-7b), Executor (qwen2.5-14b)
- **Hardcoded models**: Model definitions in `src/config.py` lines 71-97
- **Fixed mappings**: Direct role-to-model assignments
- **Memory estimates**: Hardcoded across multiple files

### Problems to Solve
1. Model definitions are hardcoded in Python code
2. No dynamic model discovery from Ollama
3. Fixed role-to-model mappings
4. Manual memory estimates scattered across files
5. No user customization or profiles
6. No cloud model fallback support

## New Architecture Design

### Core Components

#### 1. Model Registry (`src/model_registry.py`)
- **Purpose**: Central model discovery and registration
- **Features**: Auto-discover Ollama models, validate existence, query capabilities
- **Interface**: Dynamic model loading, capability detection

#### 2. Capability System (`src/capabilities.py`)
- **Purpose**: Granular model capability definitions
- **Features**: Technical specs, performance characteristics, resource requirements
- **Interface**: Capability matching, validation, scoring

#### 3. Role Mapper (`src/role_mapper.py`)
- **Purpose**: Intelligent role-to-model mapping
- **Features**: Requirement validation, resource-aware selection, fallback chains
- **Interface**: Smart model selection based on capabilities and constraints

#### 4. Profile Manager (`src/profile_manager.py`)
- **Purpose**: User configuration profiles
- **Features**: Save/load profiles, custom preferences, task-specific optimizations
- **Interface**: Profile CRUD operations, active profile management

#### 5. Model Factory (`src/model_factory.py`)
- **Purpose**: Generic model instantiation and runtime switching
- **Features**: Dynamic model creation, hot-swapping, validation
- **Interface**: Model instantiation, runtime switching, error handling

### Configuration System

#### Directory Structure
```
config/
├── models.json          # Default model configuration
├── models.yaml          # YAML alternative (if exists)
├── user_models.json     # Global user overrides
├── api_keys.json        # Encrypted cloud API keys
└── user_profiles/       # User custom profiles
    ├── coding.json
    ├── writing.json
    └── research.json
```

#### Configuration Loading Priority
1. `config/user_profiles/{active_profile}.json` (active user profile)
2. `config/user_models.json` (global user overrides)
3. `config/models.json` (default configuration)
4. `config/models.yaml` (YAML alternative)
5. Auto-discovered Ollama models

#### JSON Configuration Structure
```json
{
  "role_mappings": {
    "planner": {
      "preferred": ["llama3.1:8b", "mistral:latest"],
      "cloud_fallback": "openai:gpt-4o-mini",
      "requirements": {
        "reasoning_strength": 0.7,
        "context_length_min": 8000,
        "memory_gb_max": 8,
        "supports_tools": false
      }
    }
  },
  "model_profiles": {
    "mistral:latest": {
      "capabilities": {
        "context_length": 32000,
        "quantization_level": "Q4_K_M",
        "model_size": 7240000000,
        "reasoning_strength": 0.7,
        "coding_strength": 0.6,
        "memory_gb_estimate": 5.0
      }
    }
  },
  "cloud_providers": {
    "openai": {
      "models": {...},
      "api_endpoint": "https://api.openai.com/v1"
    }
  }
}
```

### Capability System Design

#### ModelCapabilities Dataclass
```python
@dataclass
class ModelCapabilities:
    # Technical specifications
    context_length: int
    quantization_level: str
    model_size: int  # parameter count
    memory_gb_estimate: float
    
    # Performance characteristics (0-1 scales)
    reasoning_strength: float
    coding_strength: float
    creativity: float
    multilingual_score: float
    
    # Feature support
    supports_function_calling: bool
    supports_vision: bool
    supports_tools: bool
    
    # Resource requirements
    min_memory_gb: float
    recommended_memory_gb: float
    thermal_sensitivity: float
    
    # Availability
    model_source: str  # "ollama", "openai", "anthropic"
    requires_api_key: bool
```

### User Requirements

1. **Configuration Format**: JSON default, YAML support
2. **Model Discovery**: Auto-detect Ollama models + explicit config override
3. **Capabilities**: Granular capability system
4. **Fallbacks**: Use default models when preferred unavailable
5. **Interface**: No backward compatibility - change as needed
6. **Config Location**: `config/` directory
7. **Validation**: Yes - validate Ollama models exist
8. **Runtime Switching**: Flag-based hot-swap (default off, startup selection)
9. **Cloud Fallbacks**: Yes - with API key support
10. **User Profiles**: Yes - multiple model configurations

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
1. **Directory Structure Setup**
   - Create `config/` directory with default files
   - Set up `user_profiles/` subdirectory
   - Create initial `models.json` with existing model definitions

2. **Model Registry Implementation**
   - Auto-discover models from `ollama list`
   - Validate model existence before registration
   - Query model capabilities via Ollama API
   - Support for cloud model integration

3. **Capability System Implementation**
   - Define `ModelCapabilities` dataclass
   - Create capability validation methods
   - Implement capability scoring algorithms
   - Build requirement matching logic

4. **Basic Role Mapper**
   - Implement role-to-model mapping logic
   - Create validation framework
   - Add basic resource constraint checking
   - Build fallback chain support

### Phase 2: Configuration System (Week 2)
1. **Enhanced Configuration Loading**
   - JSON/YAML parsing with priority system
   - Configuration validation and merging
   - User profile loading and overriding
   - Cloud provider configuration

2. **Profile Manager Implementation**
   - Profile CRUD operations
   - Active profile management
   - Profile validation and migration
   - Import/export functionality

3. **Cloud Provider Integration**
   - OpenAI API integration
   - Anthropic API integration
   - API key management and encryption
   - Cloud model capability definitions

4. **Model Validation System**
   - Comprehensive validation framework
   - Ollama model existence checking
   - Cloud API connectivity testing
   - Capability requirement validation

### Phase 3: Dynamic Selection (Week 3)
1. **Advanced Role Mapping**
   - Intelligent model selection algorithms
   - Resource-aware optimization
   - Performance-based recommendations
   - Dynamic fallback strategies

2. **Model Factory Implementation**
   - Generic model instantiation
   - Runtime model switching
   - Error handling and recovery
   - Performance monitoring

3. **CLI Interface Updates**
   - New model management commands
   - Profile management CLI
   - Runtime switching flags
   - Cloud provider commands

4. **Resource Integration**
   - Enhanced system resource monitoring
   - Thermal-aware model selection
   - Memory constraint optimization
   - Performance profiling

### Phase 4: Testing & Polish (Week 4)
1. **Comprehensive Testing**
   - Unit tests for all new components
   - Integration tests for model switching
   - Performance benchmarking
   - Error scenario testing

2. **Documentation Updates**
   - API reference updates
   - User guide for new features
   - Migration guide from old system
   - Troubleshooting documentation

3. **Performance Optimization**
   - Model loading optimization
   - Memory usage optimization
   - Response time improvements
   - Resource usage tuning

4. **User Experience Polish**
   - Error message improvements
   - Progress indicators
   - Configuration validation feedback
   - Help system updates

## Migration Strategy

### Backward Compatibility
- **No backward compatibility required** - can change interface as needed
- Migration from hardcoded to configuration-based system
- Automatic profile creation for existing setups
- Configuration validation and upgrade path

### Data Migration
- Convert existing model configurations to `models.json`
- Migrate user settings to profile system
- Preserve existing preference patterns
- Validate migrated configurations

## Key Technical Decisions

### Model Selection Algorithm
1. Load user profile and system resources
2. Check preferred models in configuration order
3. Validate against role requirements
4. Check system resource constraints
5. Try cloud fallbacks if enabled and API keys available
6. Use system default as last resort
7. Provide detailed feedback on selection process

### Error Handling Strategy
- Graceful degradation when models unavailable
- Detailed error messages for debugging
- Automatic fallback to working configurations
- User notifications for missing requirements

### Performance Considerations
- Cache model capabilities to reduce API calls
- Lazy loading of model configurations
- Background model discovery and validation
- Optimized model switching with minimal downtime

## Success Criteria

### Functional Requirements
- [ ] Successfully load models from external configuration
- [ ] Auto-discover available Ollama models
- [ ] Dynamically map roles to models based on capabilities
- [ ] Support user profiles and customizations
- [ ] Enable cloud model fallbacks with API keys
- [ ] Provide runtime model switching capability
- [ ] Maintain all existing functionality

### Performance Requirements
- [ ] Model selection under 1 second
- [ ] Configuration loading under 2 seconds
- [ ] Runtime switching under 5 seconds
- [ ] Memory usage comparable to current system
- [ ] No degradation in response quality

### User Experience Requirements
- [ ] Intuitive CLI interface for model management
- [ ] Clear error messages and validation feedback
- [ ] Easy profile creation and switching
- [ ] Comprehensive documentation and examples

## Next Steps for Implementation

### Immediate Actions
1. Create `config/` directory structure
2. Implement `ModelCapabilities` dataclass
3. Build basic `ModelRegistry` with Ollama discovery
4. Create initial `models.json` with existing configurations
5. Start refactoring `config.py` to use external configuration

### Implementation Order
1. **Core Infrastructure** → Model registry, capabilities, basic mapping
2. **Configuration System** → External loading, profiles, cloud integration
3. **Dynamic Selection** → Advanced mapping, factory, CLI updates
4. **Testing & Polish** → Comprehensive testing, optimization, documentation

This implementation plan provides a clear roadmap for transforming the AI stack from a hardcoded model system to a flexible, user-configurable platform while maintaining the excellent role-based architecture already in place.

---

**Last Updated**: 2025-01-31  
**Phase**: Generic Model Swappability Implementation  
**Next Action**: Start with Phase 1 - Core Infrastructure
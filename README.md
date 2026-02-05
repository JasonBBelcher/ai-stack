# AI Stack - Local Multi-Model AI System

A professional-grade, multi-model AI system that runs locally on Apple Silicon M-series chips. Features generic model swappability, intelligent model selection, and a comprehensive CLI interface.

## 🚀 Quick Start

### Prerequisites

#### 1. **Ollama** (Required)
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull recommended models
ollama pull llama3.1:8b      # Primary model (8B parameters, ~5GB)
ollama pull qwen2.5:7b       # Coding model (7B parameters, ~4.5GB)
ollama pull qwen2.5:14b      # Large coding model (14B parameters, ~9GB)
ollama pull mistral:latest   # General purpose (7B parameters, ~4GB)
```

#### 2. **Python 3.10+** (Required)
```bash
# Check Python version
python3 --version

# If not installed, install via Homebrew
brew install python@3.14
```

#### 3. **Install Python Dependencies**
```bash
# Navigate to project directory
cd ai-stack

# Install all dependencies
pip install -r requirements.txt

# Core dependencies will be installed:
# - psutil>=5.9.0          (system monitoring)
# - pydantic>=2.0.0        (data validation)
# - PyYAML>=6.0.0          (configuration files)
# - cryptography>=46.0.0   (API key encryption)
# - requests>=2.32.0       (HTTP for cloud APIs)
# - orjson>=3.8.0          (fast JSON)
# - structlog>=23.0.0      (logging)

# Optional but recommended:
# - pytest>=7.0.0          (testing)
# - black>=23.0.0          (code formatting)
```

### 4. **Verify Installation**
```bash
# Test basic functionality
python3 main.py --status

# Should output system health and available models
```

## 📋 System Requirements

### Hardware
- **Mac with M1/M2/M3/M4 chip** (Apple Silicon required for Metal acceleration)
- **16GB+ unified memory** (8GB minimum, 32GB+ recommended for large models)
- **SSD storage** (recommended for fast model loading)

### Software
- **macOS 12.0+** (Monterey or later)
- **Ollama 0.1.15+** (for local model inference)
- **Python 3.10 or 3.11+** (3.14 tested and working)
- **Homebrew** (recommended for installation)

### Recommended Models
| Model | Size | Purpose | Memory | Status |
|-------|------|---------|--------|--------|
| llama3.1:8b | ~5GB | Primary/General | 6GB | ✅ Tested |
| qwen2.5:7b | ~4.5GB | Coding | 5.5GB | ✅ Tested |
| qwen2.5:14b | ~9GB | Large Coding | 10GB | ✅ Tested |
| mistral:latest | ~4GB | General | 5GB | ✅ Tested |

## 🛠️ Installation Guide

### Step 1: Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Ollama
```bash
brew install ollama
# or download from https://ollama.com
```

### Step 3: Start Ollama
```bash
# Start Ollama as a background service
ollama serve

# Keep this running in a terminal tab
```

### Step 4: Pull Models
```bash
# In a new terminal
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
```

### Step 5: Clone and Install Project
```bash
# Clone the repository
git clone https://github.com/JasonBBelcher/ai-stack.git
cd ai-stack

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Verify Installation
```bash
# Test basic functionality
python3 main.py --health-check

# Test model listing
python3 main.py --models list

# Test simple request
python3 main.py "Say hello"
```

## 📖 Usage Guide

### Basic Commands

#### List Available Models
```bash
python3 main.py --models list
```

#### Check System Status
```bash
python3 main.py --status           # Full status with models/profiles
python3 main.py --health-check     # Quick health check
python3 main.py --config           # Configuration details
```

#### Make a Request
```bash
# Simple request
python3 main.py "What is 2+2?"

# With context
python3 main.py "Write a Python function" --context "for calculating factorials"

# With custom temperature
python3 main.py "Write creative content" --temperature 0.8
```

#### Profile Management
```bash
# List available profiles
python3 main.py --profile list

# Available profiles:
# - coding    (optimized for programming)
# - writing   (optimized for creative writing)
# - research  (optimized for analysis)
```

### Advanced Features (RAG and Cascade)

#### RAG (Retrieval-Augmented Generation)
The AI Stack now includes advanced RAG capabilities for enhanced context awareness:

```bash
# Index a codebase or document collection
python3 main.py --index /path/to/codebase

# Query with RAG context (automatically uses indexed content)
python3 main.py --project-path /path/to/codebase "How does the memory manager work?"

# Check RAG status and statistics
python3 main.py --status  # RAG information included in status output
```

Three specialized RAG profiles are available:
- **coding**: Optimized for code analysis with AST-based chunking
- **research**: Optimized for document analysis with semantic chunking
- **writing**: Optimized for creative content with paragraph-based chunking

#### Cascade Processing
Complex tasks can be processed through multi-stage cascade workflows:

```bash
# Submit complex requests that automatically trigger cascade processing
python3 main.py "Create a REST API for a todo application with authentication"

# Start interactive cascade session
python3 main.py --interactive

# View cascade operations
python3 main.py --status  # Shows active cascade operations
```

#### Example Workflows
Pre-built workflows demonstrate advanced capabilities:

```bash
# Run a workflow (requires workflow runner script)
python3 examples/run_workflow.py code_analysis /path/to/project

# Available workflows:
# - code_analysis: Analyze codebase structure and identify issues
# - document_qa: Answer questions about documents
# - bug_fixing: Identify and fix bugs in code
# - refactoring: Improve code structure and readability
# - research: Gather and synthesize research information
```

For detailed usage of RAG and Cascade features, see:
- `QUICK_START.md` - 5-minute getting started guide
- `COMPREHENSIVE_GUIDE.md` - Complete feature reference
- `docs/rag_usage.md` - RAG usage guide
- `docs/cascade_usage.md` - Cascade usage guide

### Advanced Usage

#### Model Override
```bash
# Use specific model for requests
python3 main.py "Write code" --models-override executor=llama3.1:8b
```

#### Memory Constraints
```bash
# Limit maximum memory usage
python3 main.py --max-memory 8.0 "Process this request"
```

#### Cloud Model Fallback
```bash
# Enable cloud models if local model fails
python3 main.py --enable-cloud "Request"
```

#### Interactive Mode
```bash
# Start interactive chat session
python3 main.py --interactive

# Commands in interactive mode:
# - help     Show available commands
# - exit     Exit the session
# - status   Show current system status
# - models   List available models
```

#### JSON Output
```bash
# Get machine-readable output
python3 main.py --status --json
python3 main.py --health-check --json
```

#### Verbose Mode
```bash
# Detailed model information
python3 main.py --models list --verbose
python3 main.py --model-info llama3.1:8b --verbose
```

## 📁 Project Structure

```
ai-stack/
├── main.py                    # Main CLI entry point
├── requirements.txt           # Python dependencies
├── config/
│   ├── models.json           # Model configurations
│   └── user_profiles/        # User profile storage
├── src/
│   ├── enhanced_controller.py    # Main controller
│   ├── enhanced_config.py        # Configuration system
│   ├── capabilities.py           # Model capabilities
│   ├── model_registry.py         # Model discovery/management
│   ├── role_mapper.py            # Role-model mapping
│   ├── profile_manager.py        # User profiles
│   ├── memory_manager.py         # Memory/thermal monitoring
│   ├── api_keys_manager.py       # Cloud API keys
│   ├── prompt_templates.py       # System prompts
│   ├── rag/                      # RAG system components
│   ├── cascade/                  # Cascade processing components
│   ├── monitoring/               # Performance monitoring tools
│   └── prompt_engineer/          # Prompt engineering utilities
├── tests/                     # Organized test suite
│   ├── rag/                     # RAG system tests
│   ├── cascade/                 # Cascade processing tests
│   ├── integration/             # Integration tests
│   ├── phases/                 # Phase-specific tests
│   ├── misc/                   # Miscellaneous tests
│   └── *.py                    # Core component tests
├── docs/                      # Current documentation
├── examples/                  # Example workflows and usage
├── archive/                   # Historical documentation
└── venv/                      # Virtual environment
```

## ⚙️ Configuration

### Model Settings
Edit `config/models.json` to:
- Add new models
- Configure model capabilities
- Set default temperatures
- Configure validation timeouts

### Profile Settings
Profiles are stored in `config/user_profiles/` as JSON files.

### Environment Variables
```bash
# Optional: Set custom config path
export AI_STACK_CONFIG=/path/to/config.json

# Optional: Set default profile
export AI_STACK_PROFILE=coding
```

## 🔧 Troubleshooting

### Common Issues

#### "Ollama not running"
```bash
# Start Ollama service
ollama serve

# Verify Ollama is running
ollama list
```

#### "Model not found"
```bash
# Pull the model
ollama pull llama3.1:8b

# List available models
ollama list
```

#### "ImportError: No module named..."
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

#### "Timeout" on requests
```bash
# Default timeout is 60s, which should handle most requests
# For very long responses, increase timeout in config/models.json
```

#### "Memory error" with large models
```bash
# Use smaller models
ollama pull qwen2.5:7b  # 4.5GB instead of 14GB model

# Check available memory
python3 main.py --status | grep available_gb
```

### Performance Tuning

#### For Faster Response Times
1. Use Q4_K_M quantized models (default in Ollama)
2. Keep memory usage below 80%
3. Use smaller models for simple tasks
4. Preheat models before use

#### For Large Context Windows
1. 16GB Mac: Up to 8K context
2. 32GB Mac: Up to 16K context
3. 64GB Mac: Up to 32K context

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_controller.py -v

# Run with coverage
pytest --cov=src tests/
```

## 📚 Documentation

- **Implementation Guide**: [docs/generic_models_implementation.md](docs/generic_models_implementation.md)
- **API Reference**: [docs/api_reference.md](docs/api_reference.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) for local LLM inference
- [Meta AI](https://ai.meta.com/) for Llama models
- [Qwen](https://qwenlm.github.io/) for Qwen models
- [Mistral AI](https://mistral.ai/) for Mistral models

---

**Note**: This system requires an Apple Silicon Mac for optimal performance. The Metal acceleration provides 2-3x speedup over CPU-only inference.

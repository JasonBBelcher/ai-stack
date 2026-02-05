# AI Stack - Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Prerequisites

```bash
# Install Ollama
brew install ollama

# Start Ollama service (keep running)
ollama serve

# In a new terminal, pull recommended models
ollama pull llama3.1:8b      # Primary model
ollama pull qwen2.5:7b       # Coding model
ollama pull qwen2.5:14b      # Large coding model
ollama pull mistral:latest   # General purpose
```

### 2. Setup AI Stack

```bash
# Clone the repository
git clone https://github.com/JasonBBelcher/ai-stack.git
cd ai-stack

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test basic functionality
python3 main.py --health-check

# Should show system is healthy and models are available
```

## Basic Usage

### Simple Requests
```bash
# Ask a question
python3 main.py "What is the capital of France?"

# Write code
python3 main.py --profile coding "Write a Python function to calculate factorial"

# Creative writing
python3 main.py --profile writing "Write a short story about a robot learning to paint"
```

### Check System Status
```bash
# View system health and available models
python3 main.py --status

# List available profiles
python3 main.py --profile list

# View detailed model information
python3 main.py --models list --verbose
```

## Advanced Features

### RAG (Retrieval-Augmented Generation)

Enhance AI responses with information from your codebase or documents:

```bash
# Index a codebase or document collection
python3 main.py --rag-index /path/to/your/code

# Query with RAG context
python3 main.py --rag-query "How does the memory manager work?"

# Check RAG status
python3 main.py --rag-status
```

### Cascade Processing

Handle complex tasks with multi-stage processing:

```bash
# Submit a complex request
python3 main.py --request "Create a REST API for a todo application with authentication"

# Start interactive cascade session
python3 main.py --interactive --cascade

# View cascade operations
python3 main.py --cascade-status
```

## Example Workflows

Run pre-built workflows for common tasks:

```bash
# Analyze a codebase
python3 main.py --workflow code_analysis --input-path ./my-project

# Answer questions about documents
python3 main.py --workflow document_qa --input-path ./documents

# Fix bugs in code
python3 main.py --workflow bug_fixing --input-path ./problematic-code
```

Available workflows:
- `code_analysis`: Understand codebase structure and identify issues
- `document_qa`: Answer questions about documents
- `bug_fixing`: Identify and fix bugs in code
- `refactoring`: Improve code structure and readability
- `research`: Gather and synthesize research information

## Profiles

Optimize the AI for different tasks with profiles:

```bash
# Coding (default for code tasks)
python3 main.py --profile coding "Write a Python class"

# Writing (for creative content)
python3 main.py --profile writing "Write a poem about technology"

# Research (for analysis tasks)
python3 main.py --profile research "Analyze the impact of AI on software development"
```

## Performance Monitoring

Monitor system performance and resource usage:

```bash
# View real-time performance dashboard
python3 main.py --dashboard

# Check for performance alerts
python3 main.py --alerts

# Profile specific operations
python3 main.py --profile-performance "operation-name"
```

## Troubleshooting

### Common Issues

1. **"Model not found" errors**
   ```bash
   # Check available models
   python3 main.py --models list
   
   # Pull missing models
   ollama pull model:name
   ```

2. **Slow responses**
   ```bash
   # Check system resources
   python3 main.py --health-check
   
   # Use smaller models for faster responses
   python3 main.py --models-override executor=mistral:latest "Simple task"
   ```

3. **High memory usage**
   ```bash
   # Clear caches
   python3 main.py --rag-clear-cache
   
   # Monitor memory usage
   python3 main.py --status
   ```

### Getting Help

```bash
# View all available commands
python3 main.py --help

# Get help for specific commands
python3 main.py --help --models

# Enable verbose output for debugging
python3 main.py --verbose "task"
```

## Next Steps

1. **Explore Documentation**: Check `docs/` directory for detailed guides
2. **Customize Profiles**: Modify `config/user_profiles/` for your needs
3. **Create Workflows**: Build custom workflows in `examples/workflows/`
4. **Monitor Performance**: Use built-in tools to optimize usage
5. **Extend Functionality**: Add new models and capabilities

## System Requirements

- **Hardware**: Mac with M1/M2/M3/M4 chip (16GB+ memory recommended)
- **Software**: macOS 12.0+, Ollama 0.1.15+, Python 3.10+
- **Storage**: SSD storage recommended for fast model loading

Ready to dive deeper? Check out the comprehensive guide at `COMPREHENSIVE_GUIDE.md` for detailed information about all features and capabilities.
#!/bin/bash
# AI Stack Startup Script

echo "=== AI Stack Local Multi-Model System ==="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Ollama is running
if ! ollama list > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Please start it with:"
    echo "   ollama serve"
    echo
fi

# Show system status
echo "Checking system status..."
python3 main.py --health-check

echo
echo "=== Usage Examples ==="
echo "Interactive mode:     python3 main.py --interactive"
echo "Quick request:        python3 main.py 'Your prompt here'"
echo "System status:        python3 main.py --status"
echo "View config:          python3 main.py --config"
echo
echo "=== Ready to use! ==="
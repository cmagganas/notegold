#!/bin/bash

# notegold CLI script
# Usage: ./run.sh /path/to/meeting_notes.txt [--meeting-id ID] [--graph /path/to/graph.json]

# Ensure we're in the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable not set."
    echo "Please set your OpenAI API key with: export OPENAI_API_KEY=your_api_key"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Check if we have a virtual environment
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
else
    # Activate existing virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# Run the notegold application
python -m src.main "$@" 
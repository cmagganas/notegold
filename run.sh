#!/bin/bash

# This script runs the notegold application with proper module paths

# Get directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Export pythonpath to ensure modules are found
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the application as a module
python -m src.main "$@"

# Deactivate environment if activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 
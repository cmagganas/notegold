#!/bin/bash

# Initialize Git repository and create an initial commit
# Exit on any error
set -e

# Ensure we're in the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if it's already a git repository
if [ -d ".git" ]; then
    echo "Git repository already initialized. Skipping initialization."
    exit 0
fi

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit for notegold project"

echo "Git repository successfully initialized!"
echo "You may want to set the remote origin with:"
echo "git remote add origin your-repository-url" 
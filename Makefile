.PHONY: setup install clean test run

# Default target executed when no arguments are given to make.
all: setup

# Setup development environment
setup:
	test -d .venv || python3 -m venv .venv
	.venv/bin/pip install -e .

# Run tests
test:
	.venv/bin/python -m unittest discover

# Install dependencies
install:
	.venv/bin/pip install -e .

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the application
run:
	./run.sh $(ARGS)

# Run application with specific meeting notes
process:
	@if [ -z "$(NOTES)" ]; then \
		echo "Error: NOTES parameter required. Usage: make process NOTES=/path/to/meeting_notes.txt"; \
	else \
		./run.sh $(NOTES) $(ARGS); \
	fi 
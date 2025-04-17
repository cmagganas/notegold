.PHONY: setup install clean test run

# Default target executed when no arguments are given to make.
all: setup

# Setup development environment using uv
setup:
	test -d .venv || uv venv .venv
	uv pip install -e .

# Run tests
test:
	.venv/bin/python -m unittest discover

# Install dependencies
install:
	uv pip install -e .

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
		echo "Error: NOTES parameter required. Usage: make process NOTES=/path/to/meeting_notes.txt [MEETING_ID=custom_id]"; \
	else \
		if [ -f ".env" ]; then \
			source .env; \
		fi; \
		if [ -z "$$OPENAI_API_KEY" ]; then \
			echo "Error: OPENAI_API_KEY environment variable not set. Please run:"; \
			echo "export OPENAI_API_KEY=your-api-key"; \
			exit 1; \
		fi; \
		MEETING_ID_ARG=""; \
		if [ ! -z "$(MEETING_ID)" ]; then \
			MEETING_ID_ARG="--meeting-id $(MEETING_ID)"; \
		fi; \
		echo "Processing meeting notes: $(NOTES)"; \
		echo "Output directory: ./"; \
		echo "Meeting ID argument: $$MEETING_ID_ARG"; \
		.venv/bin/python -m src.main $(NOTES) $$MEETING_ID_ARG --output-dir ./; \
	fi

# Install development package for use in current directory
develop: clean
	uv pip install -e . 
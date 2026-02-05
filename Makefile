.PHONY: setup test lint format check-specs clean docker-build docker-run

# Default target
all: setup test

setup:
	@echo "Installing dependencies..."
	uv pip install --system ".[dev]"

test:
	@echo "Running tests..."
	python -m pytest tests/ -v

lint:
	@echo "Running linters..."
	ruff check .
	mypy .

format:
	@echo "Formatting code..."
	black .
	ruff check --fix .

check-specs:
	@echo "Checking spec alignment..."
	@if [ -f "scripts/check_spec_alignment.py" ]; then \
		python scripts/check_spec_alignment.py; \
	else \
		echo "Spec alignment check not implemented"; \
	fi

clean:
	@echo "Cleaning build artifacts..."
	rm -rf .pytest_cache __pycache__ .mypy_cache build dist *.egg-info

docker-build:
	@echo "Building Docker image..."
	docker build -t project-chimera .

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm project-chimera

docker-test:
	@echo "Running tests in Docker..."
	docker build -t project-chimera-test . && \
	docker run --rm project-chimera-test make test

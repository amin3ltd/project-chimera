FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
ENV UV_SYSTEM_PYTHON=1
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project metadata and packages first for better caching
COPY pyproject.toml .
COPY project_chimera ./project_chimera
COPY services ./services
COPY skills ./skills

# Install dependencies
RUN uv pip install --system .

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "-m", "project_chimera"]

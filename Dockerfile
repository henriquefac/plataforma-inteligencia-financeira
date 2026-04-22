FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install system dependencies if needed (none identified yet but good to have basics)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the application code
COPY app ./app

# Expose the port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=.

# Command to run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

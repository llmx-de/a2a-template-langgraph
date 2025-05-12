FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies
# Note: We're using pip instead of UV for Docker builds due to compatibility issues
RUN pip install -e .

# Copy application code
COPY a2a_service/ ./a2a_service/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY main.py .
COPY docker-entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=10000
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 10000

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["start"] 
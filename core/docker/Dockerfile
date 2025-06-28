# RooCode Local Agent System - Docker Container
# Minimal but complete container for productive agent operation

FROM python:3.11-slim

# Set working directory - Task 39 Implementation
WORKDIR /project

# Install system dependencies for LLM engines and tools
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /project/logs \
    /project/models \
    /project/engines \
    /project/data

# Copy requirements first for better Docker layer caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy project structure
COPY core/ ./core/
COPY modules/ ./modules/
COPY pim/ ./pim/
COPY buddy.yaml ./
COPY bootstrap.sh ./
COPY README.md LICENSE ./

# Copy Docker-specific files
COPY core/docker/entrypoint.sh ./
COPY core/docker/docker-entrypoint.sh ./
COPY start.sh ./
COPY core/docker/.env.docker ./

# Make scripts executable
RUN chmod +x entrypoint.sh docker-entrypoint.sh start.sh bootstrap.sh

# Create non-root user for security
RUN useradd -m -u 1000 roocode && \
    chown -R roocode:roocode /project

# Switch to non-root user
USER roocode

# Expose ports for API server and LLM engine
EXPOSE 8080 11434

# Set environment variables - Task 39
ENV PYTHONPATH=/project
ENV PYTHONUNBUFFERED=1
ENV PROFILE=buddy
ENV API_PORT=8080
ENV LLM_PORT=11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set entrypoint - Task 39 Implementation
ENTRYPOINT ["./entrypoint.sh"]

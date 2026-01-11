# NewsDigest Dockerfile
# Multi-stage build for optimized image size

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 newsdigest && \
    useradd --uid 1000 --gid newsdigest --shell /bin/bash --create-home newsdigest

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=newsdigest:newsdigest . .

# Create data directories
RUN mkdir -p /data /config && \
    chown -R newsdigest:newsdigest /data /config

# Switch to non-root user
USER newsdigest

# Default command
ENTRYPOINT ["python", "-m", "newsdigest"]
CMD ["--help"]

# =============================================================================
# Stage 3: API Server (optional)
# =============================================================================
FROM runtime as api

# Install API dependencies
USER root
RUN pip install fastapi uvicorn
USER newsdigest

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/v1/health')" || exit 1

# Run API server
ENTRYPOINT ["python", "-m", "newsdigest"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8080"]

# Multi-stage build for optimized Docker image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p user_data onestream_vectordb

# Initialize users.json if it doesn't exist
RUN if [ ! -f users.json ]; then \
    echo '[{"username":"admin","password_hash":"8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918","full_name":"Administrator","role":"admin","created_at":"2024-01-01T00:00:00"}]' > users.json; \
    fi

# Initialize empty onestream_kb.json if it doesn't exist
RUN if [ ! -f onestream_kb.json ]; then \
    echo '[]' > onestream_kb.json; \
    fi

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Health check with longer timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:${PORT:-8080}/_stcore/health || exit 1

# Run the application (Cloud Run sets PORT environment variable)
CMD streamlit run app_multiuser.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true

FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make test script executable
RUN chmod +x test_auth_log.py

# Create a health check script
RUN echo '#!/bin/bash\npython test_auth_log.py' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Default command - can be overridden
CMD ["python", "ssh_log_simulator.py"] 
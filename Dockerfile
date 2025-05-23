# Build stage
FROM python:3.13-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    swi-prolog \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.13-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    swi-prolog \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

# Copy only necessary project files
COPY requirements.txt .
COPY scripts/ scripts/
COPY examples/ examples/

# Create QE directory if it doesn't exist
RUN mkdir -p scripts/QE

# Note: DT-Golog.pl needs to be manually added to scripts/QE/
# as it's not included in the repository

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["python", "scripts/main.py"] 
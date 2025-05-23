# Use Python 3.13 as base image
FROM python:3.13-slim

# Install system dependencies including SWI-Prolog
RUN apt-get update && apt-get install -y \
    swi-prolog \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create QE directory if it doesn't exist
RUN mkdir -p scripts/QE

# Note: DT-Golog.pl needs to be manually added to scripts/QE/
# as it's not included in the repository

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["python", "scripts/main.py"] 
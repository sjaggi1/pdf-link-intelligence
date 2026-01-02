# Single-stage optimized build
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY web/ ./app/
COPY data/ ./data/

# Create output directory
RUN mkdir -p outputs/reports

# Set Python path
ENV PYTHONPATH=/app

# Expose port for Flask
EXPOSE 5000

# Entrypoint
ENTRYPOINT ["python", "app/app.py"]

# Default command (optional)
CMD ["--help"]

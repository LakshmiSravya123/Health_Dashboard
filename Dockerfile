# Dockerfile for Mental Health Dashboard (Render/Cloud deployment)

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements for demo mode (lightweight)
COPY requirements.vercel.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Expose dashboard port
EXPOSE 8050

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DEPLOY_MODE=vercel

# Run dashboard
CMD ["python", "src/dashboard/app.py"]

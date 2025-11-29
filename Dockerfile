FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create Python3.10 symlink if needed
RUN ln -sf /usr/bin/python3.10 /usr/bin/python

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5150

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5150/health')"

# Run API server
CMD ["uvicorn", "indextts_app.api.main:app", "--host", "0.0.0.0", "--port", "5150"]

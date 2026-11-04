FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV, MediaPipe, and FFmpeg video transcoding
RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg \
  libgl1 \
  libglib2.0-0 \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

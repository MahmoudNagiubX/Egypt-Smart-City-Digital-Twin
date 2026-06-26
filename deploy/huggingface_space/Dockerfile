# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Create the Python runtime
FROM python:3.11-slim AS backend-runtime

# Install system dependencies for geospatial packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libspatialindex-dev \
    libgdal-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Copy documentation
COPY docs/ ./docs/

# Copy frontend build outputs
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set permissions for writeable cache/output directories in Hugging Face Space (runs as non-root user 1000)
RUN chmod -R 777 /app/backend/app/data/nasr_city

# Set PYTHONPATH environment variable to ensure project imports resolve
ENV PYTHONPATH=/app

# Expose port 7860 for Hugging Face Spaces
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]

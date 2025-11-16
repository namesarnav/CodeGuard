#!/bin/bash
# Setup script for Qdrant

set -e

echo "Setting up Qdrant..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Pull Qdrant image
echo "Pulling Qdrant image..."
docker pull qdrant/qdrant:latest

# Start Qdrant container
echo "Starting Qdrant container..."
docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -v qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to be ready..."
sleep 5

# Check health
if curl -f http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant is running and healthy!"
    echo "   API: http://localhost:6333"
    echo "   Dashboard: http://localhost:6333/dashboard"
else
    echo "❌ Qdrant health check failed"
    exit 1
fi


#!/bin/bash
# Setup script for CodeGuard AI with Docker

set -e

echo "🐳 CodeGuard AI - Docker Setup"
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check for docker-compose or docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ Found docker-compose command"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ Found docker compose plugin"
else
    echo "❌ Neither 'docker-compose' nor 'docker compose' found!"
    echo ""
    echo "Please install docker-compose:"
    echo "  macOS: brew install docker-compose"
    echo "  Or update Docker Desktop to get the compose plugin"
    exit 1
fi

echo ""
echo "📦 Building and starting services..."
echo ""

# Build and start services
$COMPOSE_CMD up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
$COMPOSE_CMD ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs: $COMPOSE_CMD logs -f"
echo "   Stop services: $COMPOSE_CMD down"
echo "   Restart: $COMPOSE_CMD restart"
echo ""


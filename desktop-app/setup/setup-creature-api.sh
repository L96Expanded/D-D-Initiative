#!/bin/bash

# D&D Initiative Creature API Docker Setup

echo "🐉 Setting up D&D Initiative Creature API with Docker..."

# Create local directories if they don't exist
echo "📁 Creating directories..."
mkdir -p local_creature_images
mkdir -p docker_data/database
mkdir -p docker_data/uploads

# Add some sample creature images if directory is empty
if [ ! "$(ls -A local_creature_images)" ]; then
    echo "📸 Local images directory is empty. You can add your own creature images here!"
    echo "   Supported formats: JPG, PNG, GIF, WEBP"
    echo "   Naming convention: creature_name.ext (e.g., ancient_red_dragon.jpg)"
fi

# Build and start the Docker container
echo "🐳 Building and starting Docker container..."
docker-compose -f docker-compose.creature-api.yml up --build -d

# Wait a moment for the container to start
sleep 3

# Check if container is running
if docker ps | grep -q "dnd-creature-api"; then
    echo "✅ Container is running successfully!"
    echo ""
    echo "🎯 API Endpoints available at:"
    echo "   http://localhost:8000/api/curated-images/get_creature_image"
    echo "   http://localhost:8000/api/curated-images/list_all_creatures"
    echo "   http://localhost:8000/api/curated-images/search_creatures"
    echo "   http://localhost:8000/docs (API documentation)"
    echo ""
    echo "📁 To add your own creature images:"
    echo "   1. Place images in ./local_creature_images/ directory"
    echo "   2. Restart the container: docker-compose -f docker-compose.creature-api.yml restart"
    echo ""
    echo "🛑 To stop: docker-compose -f docker-compose.creature-api.yml down"
else
    echo "❌ Container failed to start. Check logs with:"
    echo "   docker-compose -f docker-compose.creature-api.yml logs"
fi
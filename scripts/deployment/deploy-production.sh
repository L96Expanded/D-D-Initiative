#!/bin/bash

# Production Deployment Script for D&D Initiative Tracker

echo "🚀 Starting production deployment..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please copy .env.production.example to .env.production and configure it."
    exit 1
fi

# Check if domain is configured
if grep -q "your-domain.com" .env.production; then
    echo "⚠️  Warning: Please update DOMAIN_NAME in .env.production"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.production down

# Build and start production containers
echo "🔨 Building and starting production containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d

# Check if containers are running
echo "📋 Checking container status..."
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

echo "✅ Deployment complete!"
echo "🌐 Your D&D Initiative Tracker should be available at:"
echo "   Frontend: http://$(grep DOMAIN_NAME .env.production | cut -d'=' -f2)"
echo "   API: http://$(grep DOMAIN_NAME .env.production | cut -d'=' -f2):8000"
echo ""
echo "📝 Next steps for internet access:"
echo "1. Configure your router to forward ports 80 and 8000 to this machine"
echo "2. Set up a domain name or use dynamic DNS"
echo "3. Configure SSL certificates for HTTPS (recommended)"
echo "4. Update firewall rules if necessary"
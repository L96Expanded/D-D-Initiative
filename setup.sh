#!/bin/bash
# D&D Initiative Tracker - Automated Setup Script for Linux/Mac
# This script automates the entire setup process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🎲 D&D Initiative Tracker - Setup${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate secure random string
generate_secret() {
    openssl rand -base64 $1 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe($1))"
}

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check Docker
if command_exists docker; then
    echo -e "${GREEN}✅ Docker is installed${NC}"
    
    # Check if Docker is running
    if docker ps >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker is running${NC}"
    else
        echo -e "${RED}❌ Docker is installed but not running${NC}"
        echo -e "${RED}   Please start Docker and run this script again${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo ""
    echo -e "${RED}Please install Docker from: https://docs.docker.com/get-docker/${NC}"
    echo -e "${RED}After installation, run this script again.${NC}"
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose is available${NC}"
    # Set the compose command
    if command_exists docker-compose; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
else
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo -e "${RED}Please install Docker Compose and run this script again.${NC}"
    exit 1
fi

echo ""

# Step 2: Setup environment file
echo -e "${YELLOW}Step 2: Setting up environment configuration...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo -e "${GREEN}Keeping existing .env file${NC}"
        SETUP_ENV=false
    else
        SETUP_ENV=true
    fi
else
    SETUP_ENV=true
fi

if [ "$SETUP_ENV" = true ]; then
    echo "Creating .env file from template..."
    
    # Copy template
    cp .env.example .env
    
    # Generate secure secrets
    echo "Generating secure passwords and secrets..."
    DB_PASSWORD=$(generate_secret 32)
    JWT_SECRET=$(generate_secret 64)
    
    # Replace values in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/changeme_to_secure_password/$DB_PASSWORD/g" .env
        sed -i '' "s/changeme_to_long_random_secret_key/$JWT_SECRET/g" .env
    else
        # Linux
        sed -i "s/changeme_to_secure_password/$DB_PASSWORD/g" .env
        sed -i "s/changeme_to_long_random_secret_key/$JWT_SECRET/g" .env
    fi
    
    echo -e "${GREEN}✅ Created .env file with secure credentials${NC}"
    echo -e "   Database password: ${DB_PASSWORD:0:10}..."
    echo -e "   JWT secret: ${JWT_SECRET:0:10}..."
fi

echo ""

# Step 3: Ask about production deployment
echo -e "${YELLOW}Step 3: Deployment configuration...${NC}"
read -p "Are you setting up for (L)ocal development or (P)roduction? [L/P]: " deploy_type

if [ "$deploy_type" = "P" ] || [ "$deploy_type" = "p" ]; then
    echo ""
    echo -e "${CYAN}Production Setup${NC}"
    echo -e "${CYAN}================${NC}"
    read -p "Enter your domain name (e.g., mydomain.com): " domain
    
    if [ -n "$domain" ]; then
        # Update .env file with production settings
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/ENVIRONMENT=development/ENVIRONMENT=production/" .env
            sed -i '' "s/SECURE_COOKIES=false/SECURE_COOKIES=true/" .env
            sed -i '' "s/DOMAIN_NAME=/DOMAIN_NAME=$domain/" .env
            sed -i '' "s|CORS_ORIGINS=\[\"http://localhost:3000\",\"http://127.0.0.1:3000\"\]|CORS_ORIGINS=[\"http://localhost:3000\",\"https://$domain\",\"http://$domain\"]|" .env
            sed -i '' "s|ALLOWED_HOSTS=\[\"localhost\",\"127.0.0.1\"\]|ALLOWED_HOSTS=[\"localhost\",\"127.0.0.1\",\"$domain\"]|" .env
            sed -i '' "s|VITE_API_URL=http://localhost:8000|VITE_API_URL=https://$domain/api|" .env
        else
            # Linux
            sed -i "s/ENVIRONMENT=development/ENVIRONMENT=production/" .env
            sed -i "s/SECURE_COOKIES=false/SECURE_COOKIES=true/" .env
            sed -i "s/DOMAIN_NAME=/DOMAIN_NAME=$domain/" .env
            sed -i "s|CORS_ORIGINS=\[\"http://localhost:3000\",\"http://127.0.0.1:3000\"\]|CORS_ORIGINS=[\"http://localhost:3000\",\"https://$domain\",\"http://$domain\"]|" .env
            sed -i "s|ALLOWED_HOSTS=\[\"localhost\",\"127.0.0.1\"\]|ALLOWED_HOSTS=[\"localhost\",\"127.0.0.1\",\"$domain\"]|" .env
            sed -i "s|VITE_API_URL=http://localhost:8000|VITE_API_URL=https://$domain/api|" .env
        fi
        
        echo -e "${GREEN}✅ Configured for production deployment at $domain${NC}"
    fi
fi

echo ""

# Step 4: Build and start containers
echo -e "${YELLOW}Step 4: Building and starting Docker containers...${NC}"
echo -e "   This may take 5-10 minutes on first run..."
echo ""

$COMPOSE_CMD up --build -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker containers started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start Docker containers${NC}"
    echo -e "${RED}   Check the error messages above${NC}"
    exit 1
fi

echo ""

# Step 5: Wait for services to be healthy
echo -e "${YELLOW}Step 5: Waiting for services to be ready...${NC}"

max_attempts=30
attempt=0
all_healthy=false

while [ $all_healthy = false ] && [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "   Checking... (attempt $attempt/$max_attempts)"
    
    if curl -s -f http://localhost:8000/api/health >/dev/null 2>&1; then
        all_healthy=true
    else
        sleep 2
    fi
done

if [ $all_healthy = true ]; then
    echo -e "${GREEN}✅ All services are healthy and ready${NC}"
else
    echo -e "${YELLOW}⚠️  Services are starting but may need more time${NC}"
    echo -e "${YELLOW}   You can check status with: $COMPOSE_CMD ps${NC}"
fi

echo ""

# Step 6: Summary
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}Your D&D Initiative Tracker is now running!${NC}"
echo ""
echo -e "${CYAN}Access the application at:${NC}"
echo "  Frontend:    http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo ""
echo -e "${CYAN}Useful commands:${NC}"
echo "  View logs:        $COMPOSE_CMD logs -f"
echo "  Stop services:    $COMPOSE_CMD down"
echo "  Restart services: $COMPOSE_CMD restart"
echo "  Check status:     $COMPOSE_CMD ps"
echo ""

# Ask to open browser
read -p "Open the application in your browser now? (Y/n): " open_browser
if [ "$open_browser" != "n" ] && [ "$open_browser" != "N" ]; then
    if command_exists xdg-open; then
        xdg-open http://localhost:3000
    elif command_exists open; then
        open http://localhost:3000
    else
        echo "Please open http://localhost:3000 in your browser"
    fi
fi

echo ""
echo -e "${GREEN}Happy adventuring! 🗡️✨${NC}"
echo ""

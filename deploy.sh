#!/bin/bash

# Canon ViaPrint Manager Deployment Script
# This script will deploy the app on port 6000 to avoid conflicts with Next.js

set -e

echo "🚀 Deploying Canon ViaPrint Manager..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please don't run this script as root${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if port 6000 is available
if lsof -Pi :6000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}Port 6000 is already in use. Stopping existing service...${NC}"
    docker-compose down 2>/dev/null || true
fi

# Create data directory if it doesn't exist
mkdir -p data

# Set proper permissions
chmod 755 data
chmod 644 data/papers.json 2>/dev/null || true

echo -e "${BLUE}Building and starting the application...${NC}"

# Build and start the application
docker-compose up --build -d

# Wait for the service to be healthy
echo -e "${BLUE}Waiting for service to be ready...${NC}"
sleep 10

# Check if the service is running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Canon ViaPrint Manager deployed successfully!${NC}"
    echo -e "${GREEN}🌐 Access your app at: http://your-vps-ip:6000${NC}"
    echo -e "${GREEN}🔧 Health check: http://your-vps-ip:6000/api/health${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo -e "  View logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  Stop app: ${YELLOW}docker-compose down${NC}"
    echo -e "  Restart app: ${YELLOW}docker-compose restart${NC}"
    echo -e "  Update app: ${YELLOW}./deploy.sh${NC}"
else
    echo -e "${RED}❌ Deployment failed. Check logs with: docker-compose logs${NC}"
    exit 1
fi
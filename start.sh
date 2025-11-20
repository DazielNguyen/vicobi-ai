#!/bin/bash

# ===================================================================
# Vicobi AI - Startup Script for macOS/Linux
# ===================================================================

set -e

echo "🚀 Starting Vicobi AI..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "${YELLOW}💡 Please copy .env-example to .env and configure it:${NC}"
    echo "   cp .env-example .env"
    echo "   nano .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads output temp logs

# Check MongoDB
echo "🔍 Checking MongoDB connection..."
if ! docker ps | grep -q mongo; then
    echo -e "${YELLOW}⚠️  MongoDB not running. Starting with Docker...${NC}"
    if command -v docker &> /dev/null; then
        docker compose up -d
        echo -e "${GREEN}✅ MongoDB started${NC}"
        sleep 2
    else
        echo -e "${YELLOW}⚠️  Docker not found. Please start MongoDB manually${NC}"
    fi
fi

# Start the application
echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "🌟 Starting Vicobi AI API Server..."
echo "📚 API Documentation: http://localhost:8000/docs"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo "================================"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

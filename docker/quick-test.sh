#!/bin/bash

# Quick test script for MVEU Telegram Bot Docker setup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=========================================="
echo "  MVEU Telegram Bot - Quick Test"
echo "=========================================="
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found. Please run from project root.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-flight checks...${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed${NC}"
    echo "   Install: curl -fsSL https://get.docker.com | sh"
    exit 1
else
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not installed${NC}"
    echo "   Install: sudo apt-get install docker-compose-plugin"
    exit 1
else
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from example...${NC}"
    cp .env.example .env
    echo -e "${BLUE}📝 Please edit .env file with your settings:${NC}"
    echo "   - TELEGRAM_BOT_TOKEN (required)"
    echo "   - OPENAI_API_KEY (optional)"
    echo "   - Other passwords and settings"
    echo ""
    read -p "Press Enter to continue..."
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Check if scripts are executable
if [ ! -x "docker/run.sh" ]; then
    echo -e "${YELLOW}⚠️  Making scripts executable...${NC}"
    chmod +x docker/*.sh
    echo -e "${GREEN}✅ Scripts made executable${NC}"
else
    echo -e "${GREEN}✅ Scripts are executable${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"

# Try to start services
if docker-compose up -d; then
    echo -e "${GREEN}✅ Services started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    echo "   Check logs: docker-compose logs"
    exit 1
fi

echo ""
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Check service status
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}🧪 Running tests...${NC}"

# Test 1: Django API
echo -n "Testing Django API... "
if curl -sf "http://localhost:8001/api/users/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "   Django may still be starting up"
fi

# Test 2: Redis
echo -n "Testing Redis... "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test 3: Main page
echo -n "Testing main page... "
if curl -sf "http://localhost:8001/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test 4: Admin page (should redirect to login)
echo -n "Testing admin page... "
if curl -s "http://localhost:8001/admin/" | grep -q "login" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

echo ""
echo -e "${BLUE}📱 Checking Telegram Bot...${NC}"

# Extract bot token from .env
BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")

if [ -n "$BOT_TOKEN" ] && [ "$BOT_TOKEN" != "your-telegram-bot-token" ]; then
    echo -n "Testing Telegram Bot API... "
    if curl -sf "https://api.telegram.org/bot$BOT_TOKEN/getMe" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        BOT_INFO=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe" | jq -r '.result.username // "unknown"')
        echo "   Bot username: @$BOT_INFO"
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "   Check your TELEGRAM_BOT_TOKEN in .env"
    fi
else
    echo -e "${YELLOW}⚠️  Telegram bot token not configured${NC}"
    echo "   Add TELEGRAM_BOT_TOKEN to .env file"
fi

echo ""
echo -e "${BLUE}🌐 Application URLs:${NC}"
echo "   Main Chat:     http://localhost:8001/"
echo "   Admin Panel:   http://localhost:8001/admin/"
echo "   Admin Chat:    http://localhost:8001/admin-chat/"
echo "   API Users:     http://localhost:8001/api/users/"
echo "   API Stats:     http://localhost:8001/api/admin/stats/"

echo ""
echo -e "${BLUE}👤 Default Admin Credentials:${NC}"
echo "   Username: admin"
echo "   Password: admin123"

echo ""
echo -e "${BLUE}📊 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo -e "${GREEN}🎉 Quick test completed!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "   1. Visit http://localhost:8001/ to test the chat interface"
echo "   2. Login to admin at http://localhost:8001/admin/ (admin/admin123)"
echo "   3. Test your Telegram bot by messaging it"
echo "   4. Check admin chat at http://localhost:8001/admin-chat/"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo "   Stop services:    docker-compose down"
echo "   View logs:        docker-compose logs -f"
echo "   Restart:          docker-compose restart"
echo "   Full cleanup:     docker-compose down -v"
echo ""
echo -e "${GREEN}✨ MVEU Telegram Bot is ready to use!${NC}"
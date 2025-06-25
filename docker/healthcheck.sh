#!/bin/bash

# Health check script for MVEU Telegram Bot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DJANGO_URL="http://localhost:8001"
REDIS_HOST="redis"
POSTGRES_HOST="postgres"
POSTGRES_DB="mveu_bot"
POSTGRES_USER="mveu_user"

echo "🏥 MVEU Telegram Bot Health Check"
echo "=================================="

# Check Django application
echo -n "Django API... "
if curl -sf "$DJANGO_URL/api/users/" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
    DJANGO_STATUS="OK"
else
    echo -e "${RED}✗ FAIL${NC}"
    DJANGO_STATUS="FAIL"
fi

# Check Redis
echo -n "Redis... "
if redis-cli -h "$REDIS_HOST" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
    REDIS_STATUS="OK"
else
    echo -e "${RED}✗ FAIL${NC}"
    REDIS_STATUS="FAIL"
fi

# Check PostgreSQL
echo -n "PostgreSQL... "
if pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
    POSTGRES_STATUS="OK"
else
    echo -e "${RED}✗ FAIL${NC}"
    POSTGRES_STATUS="FAIL"
fi

# Check Telegram Bot
echo -n "Telegram Bot... "
BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
if [ -n "$BOT_TOKEN" ]; then
    if curl -sf "https://api.telegram.org/bot$BOT_TOKEN/getMe" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        BOT_STATUS="OK"
    else
        echo -e "${RED}✗ FAIL${NC}"
        BOT_STATUS="FAIL"
    fi
else
    echo -e "${YELLOW}✗ NOT CONFIGURED${NC}"
    BOT_STATUS="NOT_CONFIGURED"
fi

# Overall status
echo ""
echo "Summary:"
echo "--------"
echo "Django:     $DJANGO_STATUS"
echo "Redis:      $REDIS_STATUS"
echo "PostgreSQL: $POSTGRES_STATUS"
echo "Bot:        $BOT_STATUS"

# Exit with appropriate code
if [ "$DJANGO_STATUS" = "OK" ] && [ "$REDIS_STATUS" = "OK" ] && [ "$POSTGRES_STATUS" = "OK" ]; then
    echo -e "\n${GREEN}🎉 All core services are healthy!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some services are not healthy${NC}"
    exit 1
fi
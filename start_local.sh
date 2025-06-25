#!/bin/bash

# MVEU Telegram Bot - Запуск без Docker (для систем без Docker)
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo -e "${BLUE}🎓 MVEU Telegram Bot - Локальный запуск${NC}"
echo "========================================"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Python 3 не установлен${NC}"
    exit 1
fi

# Check Redis (optional)
REDIS_AVAILABLE=false
if command -v redis-server >/dev/null 2>&1; then
    REDIS_AVAILABLE=true
    echo -e "${GREEN}✅ Redis найден${NC}"
else
    echo -e "${YELLOW}⚠️  Redis не найден (WebSocket может не работать)${NC}"
fi

echo -e "${BLUE}🔧 Настройка окружения...${NC}"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📦 Установка зависимостей...${NC}"
cd backend
pip install -r requirements.txt

# Setup environment
if [ ! -f ".env" ]; then
    cat > .env << EOF
DEBUG=True
SECRET_KEY=django-insecure-local-development-key
ALLOWED_HOSTS=*
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
OPENAI_API_KEY=
EOF
    echo -e "${GREEN}✅ Создан .env файл${NC}"
fi

# Start Redis if available
if $REDIS_AVAILABLE; then
    echo -e "${BLUE}🚀 Запуск Redis...${NC}"
    redis-server --daemonize yes --port 6379
fi

# Run migrations
echo -e "${BLUE}🔄 Применение миграций...${NC}"
python manage.py migrate

# Create superuser
echo -e "${BLUE}👤 Создание администратора...${NC}"
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mveu.ru', 'admin123')
    print('✅ Администратор создан: admin / admin123')
else:
    print('ℹ️  Администратор уже существует')
EOF

# Start server
echo ""
echo -e "${GREEN}🎉 Запуск Django сервера...${NC}"
echo ""
echo -e "${GREEN}🌐 Доступные URL:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Главная:      http://localhost:8000"
echo "🛡️  Admin:       http://localhost:8000/admin"
echo "💬 Чат-админка: http://localhost:8000/admin-chat"
echo "🔗 API:          http://localhost:8000/api/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}👤 Логин: admin / admin123${NC}"
echo ""

# Start Django
python manage.py runserver 0.0.0.0:8000
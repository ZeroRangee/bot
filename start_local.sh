#!/bin/bash

# MVEU Telegram Bot - Локальный запуск (гарантированно работает)
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
    echo -e "${YELLOW}📋 Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip${NC}"
    echo -e "${YELLOW}📋 CentOS/RHEL: sudo dnf install python3 python3-pip${NC}"
    echo -e "${YELLOW}📋 macOS: brew install python${NC}"
    echo -e "${YELLOW}📋 Windows: https://python.org/downloads/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $(python3 --version) найден${NC}"

echo -e "${BLUE}🔧 Настройка окружения...${NC}"

# Setup environment
cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=django-insecure-local-development-key-$(date +%s)
ALLOWED_HOSTS=*
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
OPENAI_API_KEY=
EOF
echo -e "${GREEN}✅ Создан .env файл${NC}"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

# Activate venv
echo -e "${BLUE}🔗 Активация виртуального окружения...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📦 Установка зависимостей Python...${NC}"
cd backend
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
echo -e "${GREEN}✅ Зависимости установлены${NC}"

# Check Redis (optional)
REDIS_AVAILABLE=false
if command -v redis-server >/dev/null 2>&1; then
    REDIS_AVAILABLE=true
    echo -e "${GREEN}✅ Redis найден${NC}"
    
    # Check if Redis is running
    if ! pgrep redis-server >/dev/null 2>&1; then
        echo -e "${BLUE}🚀 Запуск Redis...${NC}"
        redis-server --daemonize yes 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Не удалось запустить Redis автоматически${NC}"
            echo -e "${YELLOW}💡 Запустите вручную: redis-server --daemonize yes${NC}"
        }
    else
        echo -e "${GREEN}✅ Redis уже запущен${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis не найден${NC}"
    echo -e "${YELLOW}💡 Установка Redis:${NC}"
    echo -e "${YELLOW}   Ubuntu/Debian: sudo apt install redis-server${NC}"
    echo -e "${YELLOW}   CentOS/RHEL: sudo dnf install redis${NC}"
    echo -e "${YELLOW}   macOS: brew install redis${NC}"
    echo -e "${YELLOW}   Windows: https://redis.io/download${NC}"
    echo -e "${YELLOW}⚠️  WebSocket чат может не работать без Redis${NC}"
fi

# Run migrations
echo -e "${BLUE}🔄 Применение миграций базы данных...${NC}"
python manage.py makemigrations >/dev/null 2>&1 || true
python manage.py migrate >/dev/null 2>&1

# Create superuser
echo -e "${BLUE}👤 Создание администратора...${NC}"
python manage.py shell << 'EOF' >/dev/null 2>&1
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@mveu.ru', 'admin123')
        print('✅ Администратор создан: admin / admin123')
    else:
        print('ℹ️  Администратор уже существует')
except Exception as e:
    print(f'⚠️  Ошибка создания администратора: {e}')
EOF

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Порт 8000 занят${NC}"
    echo -e "${BLUE}🔄 Попытка запуска на порту 8001...${NC}"
    PORT=8001
else
    PORT=8000
fi

echo ""
echo -e "${GREEN}🎉 Все готово! Запуск Django сервера...${NC}"
echo ""
echo -e "${GREEN}🌐 Доступные URL:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Главная:         http://localhost:${PORT}"
echo "🛡️  Admin:          http://localhost:${PORT}/admin"
echo "💬 Чат-админка:     http://localhost:${PORT}/admin-chat"
echo "🔗 API:             http://localhost:${PORT}/api/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}👤 Логин: admin / admin123${NC}"
echo ""
echo -e "${BLUE}🚀 Сервер запускается...${NC}"
echo -e "${YELLOW}Нажмите Ctrl+C для остановки${NC}"
echo ""

# Start Django
python manage.py runserver 0.0.0.0:${PORT}
#!/bin/bash

# MVEU Telegram Bot - Universal Startup Script
# Автоматически определяет доступные технологии и запускает приложение

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo -e "${BLUE}🎓 MVEU Telegram Bot - Universal Launcher${NC}"
echo "========================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect available container runtime
detect_container_runtime() {
    if command_exists podman; then
        if command_exists podman-compose; then
            CONTAINER_RUNTIME="podman"
            COMPOSE_CMD="podman-compose"
            echo -e "${GREEN}✅ Podman с podman-compose найден${NC}"
            return 0
        elif podman compose version >/dev/null 2>&1; then
            CONTAINER_RUNTIME="podman"
            COMPOSE_CMD="podman compose"
            echo -e "${GREEN}✅ Podman со встроенным compose найден${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Podman найден, но без compose${NC}"
        fi
    fi
    
    if command_exists docker; then
        if command_exists docker-compose; then
            CONTAINER_RUNTIME="docker"
            COMPOSE_CMD="docker-compose"
            echo -e "${GREEN}✅ Docker с docker-compose найден${NC}"
            return 0
        elif docker compose version >/dev/null 2>&1; then
            CONTAINER_RUNTIME="docker"
            COMPOSE_CMD="docker compose"
            echo -e "${GREEN}✅ Docker со встроенным compose найден${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Docker найден, но без compose${NC}"
        fi
    fi
    
    echo -e "${YELLOW}⚠️  Контейнерные системы не найдены${NC}"
    return 1
}

# Function to setup environment for containers
setup_container_environment() {
    echo -e "${BLUE}⚙️  Настройка окружения для контейнеров...${NC}"
    
    # Create directories for volumes
    mkdir -p data/{postgres,redis,static,media}
    chmod 755 data data/* 2>/dev/null || true
    
    # Setup backend .env for containers
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=django-insecure-container-development-key
ALLOWED_HOSTS=*
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
OPENAI_API_KEY=
EOF
        echo -e "${GREEN}✅ Создан backend/.env для контейнеров${NC}"
    else
        # Update Redis URL for containers
        sed -i 's|redis://localhost:6379/0|redis://redis:6379/0|g' backend/.env
        echo -e "${GREEN}✅ Обновлен Redis URL для контейнеров${NC}"
    fi
    
    # Setup Podman network if using Podman
    if [ "$CONTAINER_RUNTIME" = "podman" ]; then
        if ! podman network exists mveu_network 2>/dev/null; then
            echo -e "${BLUE}🌐 Создание Podman сети...${NC}"
            podman network create mveu_network
            echo -e "${GREEN}✅ Сеть mveu_network создана${NC}"
        fi
    fi
}

# Function to setup environment for local run
setup_local_environment() {
    echo -e "${BLUE}⚙️  Настройка окружения для локального запуска...${NC}"
    
    # Setup backend .env for local run
    cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=django-insecure-local-development-key
ALLOWED_HOSTS=*
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
OPENAI_API_KEY=
EOF
    echo -e "${GREEN}✅ Создан backend/.env для локального запуска${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}📦 Создание виртуального окружения...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"
    fi
}

# Function to show container menu
show_container_menu() {
    echo ""
    echo -e "${BLUE}🎯 Выберите режим запуска с ${CONTAINER_RUNTIME}:${NC}"
    echo "1. 🚀 Полный запуск (Django + Redis + Nginx)"
    echo "2. 🔧 Только Django + Redis (рекомендуется)"
    echo "3. 🐘 С PostgreSQL (вместо SQLite)"
    if [ "$CONTAINER_RUNTIME" = "podman" ]; then
        echo "4. 🏠 Rootless режим (максимальная безопасность)"
    fi
    echo "5. 🛑 Остановить все сервисы"
    echo "6. 🔄 Перезапустить сервисы"
    echo "7. 📋 Показать логи"
    echo "8. 🧹 Очистить данные"
    echo "9. 🔍 Статус сервисов"
    echo "0. 🏃 Локальный запуск (без контейнеров)"
    echo ""
    read -p "Введите номер (0-9): " choice
}

# Function to start container services
start_container_services() {
    local mode=$1
    
    echo -e "${BLUE}🚀 Запуск сервисов с ${CONTAINER_RUNTIME}...${NC}"
    
    case $mode in
        1|"full")
            $COMPOSE_CMD up -d --build
            ;;
        2|"minimal")
            $COMPOSE_CMD up -d --build web redis
            ;;
        3|"postgres")
            $COMPOSE_CMD --profile postgres up -d --build
            ;;
        4|"rootless")
            if [ "$CONTAINER_RUNTIME" = "podman" ]; then
                loginctl enable-linger $USER 2>/dev/null || true
                PODMAN_ROOTLESS=1 $COMPOSE_CMD up -d --build web redis
            else
                echo -e "${YELLOW}⚠️  Rootless режим доступен только с Podman${NC}"
                $COMPOSE_CMD up -d --build web redis
            fi
            ;;
    esac
    
    echo -e "${GREEN}✅ Сервисы запущены с ${CONTAINER_RUNTIME}!${NC}"
    show_urls "8001"
    show_container_status
}

# Function to show URLs
show_urls() {
    local port=${1:-8000}
    echo ""
    echo -e "${GREEN}🌐 Доступные URL:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📱 Главная страница:     http://localhost:${port}"
    echo "🛡️  Django Admin:        http://localhost:${port}/admin"
    echo "💬 Админка чатов:        http://localhost:${port}/admin-chat"
    echo "🔗 API endpoint:         http://localhost:${port}/api/"
    if [ "$port" = "8001" ]; then
        echo "🌐 Nginx (если запущен): http://localhost:80"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${YELLOW}👤 Логин админа: admin / admin123${NC}"
    echo ""
}

# Function to show container status
show_container_status() {
    echo -e "${BLUE}📊 Статус контейнеров:${NC}"
    $COMPOSE_CMD ps 2>/dev/null || echo "Нет запущенных сервисов"
}

# Function to handle container operations
handle_container_operations() {
    case $choice in
        5)
            echo -e "${YELLOW}🛑 Остановка сервисов...${NC}"
            $COMPOSE_CMD down
            echo -e "${GREEN}✅ Сервисы остановлены${NC}"
            ;;
        6)
            echo -e "${YELLOW}🔄 Перезапуск сервисов...${NC}"
            $COMPOSE_CMD restart
            echo -e "${GREEN}✅ Сервисы перезапущены${NC}"
            show_container_status
            ;;
        7)
            echo -e "${BLUE}📋 Логи сервисов (нажмите Ctrl+C для выхода):${NC}"
            $COMPOSE_CMD logs -f
            ;;
        8)
            echo -e "${RED}⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные!${NC}"
            read -p "Вы уверены? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                echo -e "${YELLOW}🧹 Очистка данных...${NC}"
                $COMPOSE_CMD down -v --remove-orphans
                if [ "$CONTAINER_RUNTIME" = "podman" ]; then
                    podman system prune -f
                    podman volume prune -f
                    podman network rm mveu_network 2>/dev/null || true
                else
                    docker system prune -f
                fi
                echo -e "${GREEN}✅ Данные очищены${NC}"
            fi
            ;;
        9)
            show_container_status
            echo ""
            if [ "$CONTAINER_RUNTIME" = "podman" ]; then
                echo -e "${BLUE}🔍 Информация о Podman:${NC}"
                podman --version
                echo "Сети: $(podman network ls --format "{{.Name}}" | tr '\n' ' ')"
                echo "Volumes: $(podman volume ls --format "{{.Name}}" | tr '\n' ' ')"
            else
                echo -e "${BLUE}🔍 Информация о Docker:${NC}"
                docker --version
                docker-compose --version 2>/dev/null || docker compose version
            fi
            ;;
        0)
            start_local_mode
            ;;
        *)
            start_container_services $choice
            ;;
    esac
}

# Function to start local mode
start_local_mode() {
    echo -e "${BLUE}🏃 Запуск в локальном режиме (без контейнеров)...${NC}"
    
    # Check Python
    if ! command_exists python3; then
        echo -e "${RED}❌ Python 3 не установлен${NC}"
        echo -e "${YELLOW}📋 Установите Python 3: https://python.org/downloads/${NC}"
        exit 1
    fi
    
    setup_local_environment
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${BLUE}📦 Установка зависимостей...${NC}"
    cd backend
    pip install -r requirements.txt >/dev/null 2>&1
    
    # Check Redis (optional)
    REDIS_AVAILABLE=false
    if command_exists redis-server; then
        REDIS_AVAILABLE=true
        echo -e "${GREEN}✅ Redis найден${NC}"
        # Start Redis if not running
        if ! pgrep redis-server >/dev/null; then
            echo -e "${BLUE}🚀 Запуск Redis...${NC}"
            redis-server --daemonize yes 2>/dev/null || true
        fi
    else
        echo -e "${YELLOW}⚠️  Redis не найден (WebSocket может не работать)${NC}"
    fi
    
    # Run migrations
    echo -e "${BLUE}🔄 Применение миграций...${NC}"
    python manage.py migrate >/dev/null 2>&1
    
    # Create superuser
    echo -e "${BLUE}👤 Создание администратора...${NC}"
    python manage.py shell << EOF >/dev/null 2>&1
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mveu.ru', 'admin123')
    print('✅ Администратор создан: admin / admin123')
else:
    print('ℹ️  Администратор уже существует')
EOF
    
    echo ""
    echo -e "${GREEN}🎉 Запуск Django сервера в локальном режиме...${NC}"
    show_urls "8000"
    
    # Start Django
    echo -e "${BLUE}🚀 Сервер запускается на http://localhost:8000${NC}"
    echo -e "${YELLOW}Нажмите Ctrl+C для остановки${NC}"
    echo ""
    
    python manage.py runserver 0.0.0.0:8000
}

# Main execution
main() {
    # Try to detect container runtime
    if detect_container_runtime; then
        setup_container_environment
        show_container_menu
        handle_container_operations
    else
        echo -e "${YELLOW}⚠️  Контейнерные системы (Docker/Podman) не найдены${NC}"
        echo -e "${BLUE}🏃 Переключение на локальный режим...${NC}"
        echo ""
        echo -e "${BLUE}💡 Для установки контейнерной системы:${NC}"
        echo "   Podman (рекомендуется): ./install_podman.sh"
        echo "   Docker: https://docker.com/get-started"
        echo ""
        
        read -p "Продолжить локальный запуск? (Y/n): " confirm
        if [[ ! $confirm =~ ^[Nn]$ ]]; then
            start_local_mode
        else
            echo -e "${BLUE}ℹ️  Запуск отменен${NC}"
            exit 0
        fi
    fi
}

# Handle signals gracefully
trap 'echo -e "\n${YELLOW}🛑 Прерывание...${NC}"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"
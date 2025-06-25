#!/bin/bash

# MVEU Telegram Bot - Universal Startup Script
# Работает на Linux, macOS, Windows (через WSL/Git Bash)

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

# Function to check Docker/Docker Compose
check_docker() {
    if ! command_exists docker; then
        echo -e "${RED}❌ Docker не установлен${NC}"
        echo -e "${YELLOW}📋 Установите Docker с https://docker.com/get-started${NC}"
        exit 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose не установлен${NC}"
        echo -e "${YELLOW}📋 Установите Docker Compose${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker и Docker Compose найдены${NC}"
}

# Function to setup environment
setup_environment() {
    echo -e "${BLUE}⚙️  Настройка окружения...${NC}"
    
    # Copy example env if not exists
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            echo -e "${GREEN}✅ Создан backend/.env из примера${NC}"
        else
            # Create minimal .env
            cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=django-insecure-local-development-key
ALLOWED_HOSTS=*
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
OPENAI_API_KEY=
EOF
            echo -e "${GREEN}✅ Создан минимальный backend/.env${NC}"
        fi
    fi
    
    # Create frontend .env if not exists
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
EOF
        echo -e "${GREEN}✅ Создан frontend/.env${NC}"
    fi
}

# Function to show menu
show_menu() {
    echo ""
    echo -e "${BLUE}🎯 Выберите режим запуска:${NC}"
    echo "1. 🚀 Полный запуск (Django + Redis + Nginx)"
    echo "2. 🔧 Только Django + Redis (без Nginx)"
    echo "3. 🐘 С PostgreSQL (вместо SQLite)"
    echo "4. 🛑 Остановить все сервисы"
    echo "5. 🔄 Перезапустить сервисы"
    echo "6. 📋 Показать логи"
    echo "7. 🧹 Очистить данные"
    echo ""
    read -p "Введите номер (1-7): " choice
}

# Function to start services
start_services() {
    local profile=$1
    local compose_cmd="docker-compose"
    
    # Check if docker compose (new syntax) is available
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    echo -e "${BLUE}🚀 Запуск сервисов...${NC}"
    
    case $profile in
        "full")
            $compose_cmd up -d --build
            ;;
        "minimal")
            $compose_cmd up -d --build web redis
            ;;
        "postgres")
            $compose_cmd --profile postgres up -d --build
            ;;
    esac
    
    echo -e "${GREEN}✅ Сервисы запущены!${NC}"
    show_urls
    show_status
}

# Function to show URLs
show_urls() {
    echo ""
    echo -e "${GREEN}🌐 Доступные URL:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📱 Главная страница:     http://localhost:8001"
    echo "🛡️  Django Admin:        http://localhost:8001/admin"
    echo "💬 Админка чатов:        http://localhost:8001/admin-chat"
    echo "🔗 API endpoint:         http://localhost:8001/api/"
    echo "🌐 Nginx (если запущен): http://localhost:80"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${YELLOW}👤 Логин админа: admin / admin123${NC}"
    echo ""
}

# Function to show status
show_status() {
    local compose_cmd="docker-compose"
    
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    echo -e "${BLUE}📊 Статус сервисов:${NC}"
    $compose_cmd ps
}

# Function to show logs
show_logs() {
    local compose_cmd="docker-compose"
    
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    echo -e "${BLUE}📋 Логи сервисов (нажмите Ctrl+C для выхода):${NC}"
    $compose_cmd logs -f
}

# Function to stop services
stop_services() {
    local compose_cmd="docker-compose"
    
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    echo -e "${YELLOW}🛑 Остановка сервисов...${NC}"
    $compose_cmd down
    echo -e "${GREEN}✅ Сервисы остановлены${NC}"
}

# Function to restart services
restart_services() {
    local compose_cmd="docker-compose"
    
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    echo -e "${YELLOW}🔄 Перезапуск сервисов...${NC}"
    $compose_cmd restart
    echo -e "${GREEN}✅ Сервисы перезапущены${NC}"
    show_status
}

# Function to clean data
clean_data() {
    local compose_cmd="docker-compose"
    
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi
    
    echo -e "${RED}⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные!${NC}"
    read -p "Вы уверены? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🧹 Очистка данных...${NC}"
        $compose_cmd down -v --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Данные очищены${NC}"
    else
        echo -e "${BLUE}ℹ️  Отменено${NC}"
    fi
}

# Main execution
main() {
    check_docker
    setup_environment
    
    show_menu
    
    case $choice in
        1)
            start_services "full"
            ;;
        2)
            start_services "minimal"
            ;;
        3)
            start_services "postgres"
            ;;
        4)
            stop_services
            ;;
        5)
            restart_services
            ;;
        6)
            show_logs
            ;;
        7)
            clean_data
            ;;
        *)
            echo -e "${RED}❌ Неверный выбор${NC}"
            exit 1
            ;;
    esac
}

# Handle signals gracefully
trap 'echo -e "\n${YELLOW}🛑 Прерывание...${NC}"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"
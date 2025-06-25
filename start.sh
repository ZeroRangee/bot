#!/bin/bash

# MVEU Telegram Bot - Universal Startup Script with Podman
# Работает на Linux, macOS, Windows (через WSL/Git Bash)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo -e "${BLUE}🎓 MVEU Telegram Bot - Podman Launcher${NC}"
echo "========================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Podman/Podman Compose
check_podman() {
    if ! command_exists podman; then
        echo -e "${RED}❌ Podman не установлен${NC}"
        echo -e "${YELLOW}📋 Установите Podman:${NC}"
        echo "  Ubuntu/Debian: sudo apt install podman"
        echo "  CentOS/RHEL:   sudo dnf install podman"
        echo "  macOS:         brew install podman"
        echo "  Windows:       https://podman.io/getting-started/installation"
        exit 1
    fi
    
    # Check for podman-compose or podman compose
    COMPOSE_CMD=""
    if command_exists podman-compose; then
        COMPOSE_CMD="podman-compose"
        echo -e "${GREEN}✅ Podman и podman-compose найдены${NC}"
    elif podman compose version >/dev/null 2>&1; then
        COMPOSE_CMD="podman compose"
        echo -e "${GREEN}✅ Podman со встроенным compose найден${NC}"
    else
        echo -e "${RED}❌ Podman Compose не установлен${NC}"
        echo -e "${YELLOW}📋 Установите podman-compose:${NC}"
        echo "  pip3 install podman-compose"
        echo "  или используйте встроенный: podman compose"
        exit 1
    fi
    
    export COMPOSE_CMD
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
    
    # Setup Podman network if not exists
    if ! podman network exists mveu_network 2>/dev/null; then
        echo -e "${BLUE}🌐 Создание Podman сети...${NC}"
        podman network create mveu_network
        echo -e "${GREEN}✅ Сеть mveu_network создана${NC}"
    fi
}

# Function to show menu
show_menu() {
    echo ""
    echo -e "${BLUE}🎯 Выберите режим запуска:${NC}"
    echo "1. 🚀 Полный запуск (Django + Redis + Nginx)"
    echo "2. 🔧 Только Django + Redis (без Nginx)"
    echo "3. 🐘 С PostgreSQL (вместо SQLite)"
    echo "4. 🏠 Rootless режим (без sudo)"
    echo "5. 🛑 Остановить все сервисы"
    echo "6. 🔄 Перезапустить сервисы"
    echo "7. 📋 Показать логи"
    echo "8. 🧹 Очистить данные"
    echo "9. 🔍 Статус сервисов"
    echo ""
    read -p "Введите номер (1-9): " choice
}

# Function to start services
start_services() {
    local profile=$1
    local rootless=$2
    
    echo -e "${BLUE}🚀 Запуск сервисов с Podman...${NC}"
    
    if [ "$rootless" = "true" ]; then
        echo -e "${YELLOW}🏠 Запуск в rootless режиме${NC}"
        # Enable lingering for rootless containers
        loginctl enable-linger $USER 2>/dev/null || true
    fi
    
    case $profile in
        "full")
            $COMPOSE_CMD up -d --build
            ;;
        "minimal")
            $COMPOSE_CMD up -d --build web redis
            ;;
        "postgres")
            $COMPOSE_CMD --profile postgres up -d --build
            ;;
        "rootless")
            # Force rootless mode
            PODMAN_ROOTLESS=1 $COMPOSE_CMD up -d --build web redis
            ;;
    esac
    
    echo -e "${GREEN}✅ Сервисы запущены с Podman!${NC}"
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
    echo -e "${BLUE}📊 Статус контейнеров Podman:${NC}"
    $COMPOSE_CMD ps
    
    echo ""
    echo -e "${BLUE}🔍 Podman контейнеры:${NC}"
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 Логи сервисов (нажмите Ctrl+C для выхода):${NC}"
    $COMPOSE_CMD logs -f
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}🛑 Остановка сервисов Podman...${NC}"
    $COMPOSE_CMD down
    echo -e "${GREEN}✅ Сервисы остановлены${NC}"
}

# Function to restart services
restart_services() {
    echo -e "${YELLOW}🔄 Перезапуск сервисов Podman...${NC}"
    $COMPOSE_CMD restart
    echo -e "${GREEN}✅ Сервисы перезапущены${NC}"
    show_status
}

# Function to clean data
clean_data() {
    echo -e "${RED}⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные!${NC}"
    read -p "Вы уверены? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🧹 Очистка данных Podman...${NC}"
        $COMPOSE_CMD down -v --remove-orphans
        
        # Clean Podman system
        podman system prune -f
        podman volume prune -f
        
        # Remove network if exists
        podman network rm mveu_network 2>/dev/null || true
        
        echo -e "${GREEN}✅ Данные очищены${NC}"
    else
        echo -e "${BLUE}ℹ️  Отменено${NC}"
    fi
}

# Function to show podman info
show_podman_info() {
    echo -e "${BLUE}🔍 Информация о Podman:${NC}"
    echo "Версия Podman: $(podman --version)"
    if command_exists podman-compose; then
        echo "Версия Compose: $(podman-compose --version)"
    fi
    echo ""
    echo -e "${BLUE}🌐 Сети Podman:${NC}"
    podman network ls
    echo ""
    echo -e "${BLUE}💾 Volumes Podman:${NC}"
    podman volume ls
}

# Main execution
main() {
    check_podman
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
            start_services "rootless" "true"
            ;;
        5)
            stop_services
            ;;
        6)
            restart_services
            ;;
        7)
            show_logs
            ;;
        8)
            clean_data
            ;;
        9)
            show_status
            show_podman_info
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
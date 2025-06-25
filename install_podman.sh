#!/bin/bash

# MVEU Telegram Bot - Podman Installation Script
# Автоматическая установка Podman на разных системах

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo -e "${BLUE}🐳 Установка Podman для MVEU Bot${NC}"
echo "========================================"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    echo "Обнаружена система: $OS"
}

# Install Podman on Ubuntu/Debian
install_debian() {
    echo -e "${BLUE}📦 Установка Podman на Ubuntu/Debian...${NC}"
    
    # Update package list
    sudo apt update
    
    # Install dependencies
    sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add repository for newer Podman versions
    echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_$(lsb_release -rs)/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
    curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_$(lsb_release -rs)/Release.key" | sudo apt-key add -
    
    # Update and install
    sudo apt update
    sudo apt install -y podman
    
    # Install podman-compose
    sudo apt install -y python3-pip
    pip3 install podman-compose
    
    echo -e "${GREEN}✅ Podman установлен на Ubuntu/Debian${NC}"
}

# Install Podman on CentOS/RHEL/Fedora
install_redhat() {
    echo -e "${BLUE}📦 Установка Podman на CentOS/RHEL/Fedora...${NC}"
    
    # Determine package manager
    if command -v dnf >/dev/null 2>&1; then
        PKG_MGR="dnf"
    else
        PKG_MGR="yum"
    fi
    
    # Install Podman
    sudo $PKG_MGR install -y podman
    
    # Install Python and pip if not available
    sudo $PKG_MGR install -y python3 python3-pip
    
    # Install podman-compose
    pip3 install --user podman-compose
    
    echo -e "${GREEN}✅ Podman установлен на RedHat/CentOS/Fedora${NC}"
}

# Install Podman on Arch Linux
install_arch() {
    echo -e "${BLUE}📦 Установка Podman на Arch Linux...${NC}"
    
    # Update package database
    sudo pacman -Sy
    
    # Install Podman
    sudo pacman -S --noconfirm podman
    
    # Install podman-compose from AUR (if yay is available)
    if command -v yay >/dev/null 2>&1; then
        yay -S --noconfirm podman-compose
    else
        # Install with pip
        sudo pacman -S --noconfirm python-pip
        pip install --user podman-compose
    fi
    
    echo -e "${GREEN}✅ Podman установлен на Arch Linux${NC}"
}

# Install Podman on macOS
install_macos() {
    echo -e "${BLUE}📦 Установка Podman на macOS...${NC}"
    
    # Check if Homebrew is installed
    if ! command -v brew >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Homebrew не найден. Устанавливаем...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Podman
    brew install podman
    
    # Install podman-compose
    pip3 install podman-compose
    
    # Initialize Podman machine
    echo -e "${BLUE}🚀 Инициализация Podman машины...${NC}"
    podman machine init
    podman machine start
    
    echo -e "${GREEN}✅ Podman установлен на macOS${NC}"
}

# Setup Podman for rootless mode
setup_rootless() {
    echo -e "${BLUE}🏠 Настройка rootless режима...${NC}"
    
    # Add user to subuid/subgid if not present
    if ! grep -q "^$USER:" /etc/subuid; then
        echo "$USER:100000:65536" | sudo tee -a /etc/subuid
    fi
    
    if ! grep -q "^$USER:" /etc/subgid; then
        echo "$USER:100000:65536" | sudo tee -a /etc/subgid
    fi
    
    # Enable lingering for systemd
    if command -v loginctl >/dev/null 2>&1; then
        loginctl enable-linger $USER
    fi
    
    # Configure storage if needed
    mkdir -p ~/.config/containers
    if [ ! -f ~/.config/containers/storage.conf ]; then
        cat > ~/.config/containers/storage.conf << EOF
[storage]
driver = "overlay"
runroot = "/run/user/\$UID/containers"
graphroot = "\$HOME/.local/share/containers/storage"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF
    fi
    
    echo -e "${GREEN}✅ Rootless режим настроен${NC}"
}

# Test Podman installation
test_podman() {
    echo -e "${BLUE}🧪 Тестирование установки Podman...${NC}"
    
    # Test Podman
    if podman --version; then
        echo -e "${GREEN}✅ Podman работает${NC}"
    else
        echo -e "${RED}❌ Podman не работает${NC}"
        return 1
    fi
    
    # Test podman-compose
    if command -v podman-compose >/dev/null 2>&1; then
        echo -e "${GREEN}✅ podman-compose доступен${NC}"
    elif podman compose version >/dev/null 2>&1; then
        echo -e "${GREEN}✅ встроенный podman compose доступен${NC}"
    else
        echo -e "${YELLOW}⚠️  podman-compose не найден, установка...${NC}"
        pip3 install --user podman-compose
    fi
    
    # Test with hello-world
    echo -e "${BLUE}🌍 Тест с hello-world контейнером...${NC}"
    if podman run --rm hello-world; then
        echo -e "${GREEN}✅ Podman полностью работает!${NC}"
    else
        echo -e "${YELLOW}⚠️  Тест не прошел, но Podman установлен${NC}"
    fi
}

# Create data directories for volumes
create_data_dirs() {
    echo -e "${BLUE}📁 Создание директорий для данных...${NC}"
    
    mkdir -p data/{postgres,redis,static,media}
    chmod 755 data
    chmod 755 data/*
    
    echo -e "${GREEN}✅ Директории созданы${NC}"
}

# Main installation function
main() {
    detect_os
    
    case $OS in
        "debian")
            install_debian
            ;;
        "redhat")
            install_redhat
            ;;
        "arch")
            install_arch
            ;;
        "macos")
            install_macos
            ;;
        *)
            echo -e "${RED}❌ Неподдерживаемая операционная система${NC}"
            echo -e "${YELLOW}📋 Пожалуйста, установите Podman вручную:${NC}"
            echo "https://podman.io/getting-started/installation"
            exit 1
            ;;
    esac
    
    # Setup rootless mode
    setup_rootless
    
    # Create data directories
    create_data_dirs
    
    # Test installation
    test_podman
    
    echo ""
    echo -e "${GREEN}🎉 Podman успешно установлен!${NC}"
    echo "========================================"
    echo -e "${BLUE}📋 Следующие шаги:${NC}"
    echo "1. Запустите: ./start.sh"
    echo "2. Выберите режим запуска"
    echo "3. Откройте: http://localhost:8001"
    echo ""
    echo -e "${YELLOW}💡 Полезные команды:${NC}"
    echo "• podman ps              - список контейнеров"
    echo "• podman images          - список образов"
    echo "• podman system info     - информация о системе"
    echo "• podman machine start   - запуск машины (macOS)"
    echo "========================================"
}

# Handle signals gracefully
trap 'echo -e "\n${YELLOW}🛑 Установка прервана...${NC}"; exit 1' SIGTERM SIGINT

# Run main function
main "$@"
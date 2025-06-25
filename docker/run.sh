#!/bin/bash

# MVEU Telegram Bot - Docker Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "    MVEU Telegram Bot Docker Setup"
    echo "========================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_info "Please edit .env file with your configuration before running the application"
        print_info "Required settings:"
        echo "  - TELEGRAM_BOT_TOKEN: Your Telegram bot token"
        echo "  - OPENAI_API_KEY: Your OpenAI API key (optional)"
        echo "  - SECRET_KEY: Django secret key"
        echo "  - Database passwords"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    else
        print_success ".env file found"
    fi
}

# Build and start services
start_services() {
    print_info "Building Docker images..."
    docker-compose build
    
    print_info "Starting services..."
    docker-compose up -d
    
    print_info "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    if docker-compose ps | grep -q "Up (healthy)"; then
        print_success "Services are running and healthy"
    else
        print_warning "Some services may not be fully ready yet"
    fi
}

# Show service status
show_status() {
    echo ""
    print_info "Service Status:"
    docker-compose ps
    
    echo ""
    print_info "Application URLs:"
    echo "  🌐 Main Chat Interface: http://localhost:8001"
    echo "  🛡️  Admin Interface: http://localhost:8001/admin"
    echo "  👥 Admin Chat: http://localhost:8001/admin-chat"
    echo "  📊 API Stats: http://localhost:8001/api/admin/stats"
    echo ""
    print_info "Default Admin Credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
}

# Show logs
show_logs() {
    print_info "Recent logs (press Ctrl+C to exit):"
    docker-compose logs -f --tail=50
}

# Stop services
stop_services() {
    print_info "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Clean up
cleanup() {
    print_warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Main script
print_header

case "${1:-start}" in
    "start")
        check_docker
        setup_env
        start_services
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "cleanup")
        cleanup
        ;;
    "build")
        check_docker
        print_info "Building Docker images..."
        docker-compose build --no-cache
        print_success "Build completed"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|cleanup|build}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status and URLs"
        echo "  logs     - Show real-time logs"
        echo "  cleanup  - Remove all containers and data"
        echo "  build    - Rebuild Docker images"
        exit 1
        ;;
esac
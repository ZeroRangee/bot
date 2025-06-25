#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎓 Starting MVEU Telegram Bot Application...${NC}"

# Function to wait for database
wait_for_db() {
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    
    # If using PostgreSQL
    if [ "$DATABASE_URL" ]; then
        echo "Waiting for PostgreSQL..."
        python << EOF
import os
import psycopg2
import time
import sys

database_url = os.environ.get('DATABASE_URL')
if database_url:
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ PostgreSQL is ready!")
            sys.exit(0)
        except psycopg2.OperationalError:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts} - PostgreSQL not ready yet...")
            time.sleep(2)
    print("❌ Failed to connect to PostgreSQL")
    sys.exit(1)
EOF
    else
        echo "Using SQLite database"
        sleep 3
    fi
}

# Function to wait for Redis
wait_for_redis() {
    echo -e "${YELLOW}⏳ Waiting for Redis to be ready...${NC}"
    python << EOF
import redis
import time
import os
import sys

redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis is ready!")
        sys.exit(0)
    except (redis.ConnectionError, redis.TimeoutError):
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts} - Redis not ready yet...")
        time.sleep(2)

print("❌ Failed to connect to Redis")
sys.exit(1)
EOF
}

# Function to run migrations
run_migrations() {
    echo -e "${BLUE}🔄 Running database migrations...${NC}"
    
    # Create migrations if they don't exist
    python manage.py makemigrations --noinput
    
    # Apply migrations
    python manage.py migrate --noinput
    
    echo -e "${GREEN}✅ Database migrations completed${NC}"
}

# Function to create superuser
create_superuser() {
    echo -e "${BLUE}👤 Setting up superuser...${NC}"
    
    python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@mveu.ru')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created successfully!")
else:
    print(f"ℹ️  Superuser '{username}' already exists.")
EOF
}

# Function to collect static files
collect_static() {
    echo -e "${BLUE}📁 Collecting static files...${NC}"
    python manage.py collectstatic --noinput --clear
    echo -e "${GREEN}✅ Static files collected${NC}"
}

# Function to load initial data
load_initial_data() {
    echo -e "${BLUE}📊 Loading initial data...${NC}"
    
    python manage.py shell << EOF
from chat.services.schedule_service import ScheduleService
import asyncio

try:
    service = ScheduleService()
    # Load initial schedule data
    asyncio.run(service.update_schedule_data())
    print("✅ Initial schedule data loaded")
except Exception as e:
    print(f"⚠️  Warning: Could not load initial schedule data: {e}")
EOF
}

# Function to start telegram bot
start_telegram_bot() {
    echo -e "${BLUE}🤖 Starting Telegram bot in background...${NC}"
    
    python manage.py shell << EOF
import asyncio
import threading
import logging
from chat.telegram_bot import application

logger = logging.getLogger(__name__)

def run_bot():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def start():
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            logger.info("Telegram bot started successfully")
        
        loop.run_until_complete(start())
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")

# Start bot in background thread
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
print("✅ Telegram bot started in background")
EOF
}

# Function to run health checks
health_check() {
    echo -e "${BLUE}🏥 Running health checks...${NC}"
    
    # Check Django
    if python manage.py check --deploy > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Django health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Django health check warnings (continuing...)${NC}"
    fi
    
    # Check database connectivity
    python manage.py shell << EOF
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connectivity check passed")
except Exception as e:
    print(f"❌ Database connectivity check failed: {e}")
    exit(1)
EOF

    # Check Telegram bot token
    if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
        python << EOF
import requests
import os

token = os.environ.get('TELEGRAM_BOT_TOKEN')
try:
    response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print(f"✅ Telegram bot token valid: @{data['result'].get('username', 'unknown')}")
        else:
            print("⚠️  Telegram bot token invalid")
    else:
        print("⚠️  Telegram bot token check failed")
except Exception as e:
    print(f"⚠️  Telegram bot token check error: {e}")
EOF
    else
        echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN not set${NC}"
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "🎓 MVEU Telegram Bot - Starting Up"
    echo "========================================"
    
    # Wait for dependencies
    wait_for_redis
    wait_for_db
    
    # Setup database
    run_migrations
    
    # Create admin user
    create_superuser
    
    # Collect static files
    collect_static
    
    # Load initial data
    load_initial_data
    
    # Health checks
    health_check
    
    # Start Telegram bot
    if [ "${START_BOT:-true}" = "true" ]; then
        start_telegram_bot
        sleep 2  # Give bot time to start
    fi
    
    echo ""
    echo -e "${GREEN}🎉 MVEU Telegram Bot is ready!${NC}"
    echo "========================================"
    echo "📱 Bot: @$(python -c "
import os, requests
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
if token:
    try:
        r = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=5)
        print(r.json().get('result', {}).get('username', 'unknown'))
    except:
        print('unknown')
else:
    print('not_configured')
")"
    echo "🌐 Web: http://localhost:8001"
    echo "🛡️  Admin: http://localhost:8001/admin (admin:admin123)"
    echo "💬 Chat Admin: http://localhost:8001/admin-chat"
    echo "========================================"
    echo ""
    
    # Start Django development server
    echo -e "${BLUE}🚀 Starting Django server...${NC}"
    exec python manage.py runserver 0.0.0.0:8001
}

# Handle signals gracefully
trap 'echo -e "\n${YELLOW}🛑 Shutting down gracefully...${NC}"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"
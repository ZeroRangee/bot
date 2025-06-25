@echo off
chcp 65001 >nul
title MVEU Telegram Bot - Universal Windows Launcher

echo ========================================
echo 🎓 MVEU Telegram Bot - Universal Launcher
echo ========================================

REM Initialize variables
set CONTAINER_RUNTIME=
set COMPOSE_CMD=

REM Function to check for Podman
:check_podman
podman --version >nul 2>&1
if %errorlevel% equ 0 (
    set CONTAINER_RUNTIME=podman
    
    REM Check for podman-compose
    podman-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=podman-compose
        echo ✅ Podman с podman-compose найден
        goto setup_container_env
    )
    
    REM Check for built-in compose
    podman compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=podman compose
        echo ✅ Podman со встроенным compose найден
        goto setup_container_env
    )
    
    echo ⚠️  Podman найден, но без compose
)

REM Function to check for Docker
:check_docker
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    set CONTAINER_RUNTIME=docker
    
    REM Check for docker-compose
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker-compose
        echo ✅ Docker с docker-compose найден
        goto setup_container_env
    )
    
    REM Check for built-in compose
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker compose
        echo ✅ Docker со встроенным compose найден
        goto setup_container_env
    )
    
    echo ⚠️  Docker найден, но без compose
)

REM No container runtime found
echo ⚠️  Контейнерные системы (Docker/Podman) не найдены
echo 🏃 Переключение на локальный режим...
echo.
echo 💡 Для установки контейнерной системы:
echo    Podman Desktop: https://podman.io/getting-started/installation
echo    Docker Desktop: https://docker.com/get-started
echo.

set /p confirm="Продолжить локальный запуск? (Y/n): "
if /i "%confirm%"=="n" (
    echo ℹ️  Запуск отменен
    pause
    exit /b 0
)
goto start_local_mode

REM Setup container environment
:setup_container_env
echo ⚙️  Настройка окружения для контейнеров...

REM Create directories
if not exist "data" mkdir data
if not exist "data\postgres" mkdir data\postgres
if not exist "data\redis" mkdir data\redis
if not exist "data\static" mkdir data\static
if not exist "data\media" mkdir data\media

REM Setup backend .env for containers
(
echo DEBUG=True
echo SECRET_KEY=django-insecure-container-development-key
echo ALLOWED_HOSTS=*
echo REDIS_URL=redis://redis:6379/0
echo TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
echo OPENAI_API_KEY=
) > backend\.env
echo ✅ Создан backend\.env для контейнеров

REM Setup Podman network if needed
if "%CONTAINER_RUNTIME%"=="podman" (
    podman network exists mveu_network >nul 2>&1
    if %errorlevel% neq 0 (
        echo 🌐 Создание Podman сети...
        podman network create mveu_network
        echo ✅ Сеть mveu_network создана
    )
)

goto show_container_menu

REM Show container menu
:show_container_menu
echo.
echo 🎯 Выберите режим запуска с %CONTAINER_RUNTIME%:
echo 1. 🚀 Полный запуск (Django + Redis + Nginx)
echo 2. 🔧 Только Django + Redis (рекомендуется)
echo 3. 🐘 С PostgreSQL (вместо SQLite)
if "%CONTAINER_RUNTIME%"=="podman" (
    echo 4. 🏠 Rootless режим (максимальная безопасность)
)
echo 5. 🛑 Остановить все сервисы
echo 6. 🔄 Перезапустить сервисы
echo 7. 📋 Показать логи
echo 8. 🧹 Очистить данные
echo 9. 🔍 Статус сервисов
echo 0. 🏃 Локальный запуск (без контейнеров)
echo.

set /p choice="Введите номер (0-9): "

if "%choice%"=="1" goto start_full
if "%choice%"=="2" goto start_minimal
if "%choice%"=="3" goto start_postgres
if "%choice%"=="4" goto start_rootless
if "%choice%"=="5" goto stop_services
if "%choice%"=="6" goto restart_services
if "%choice%"=="7" goto show_logs
if "%choice%"=="8" goto clean_data
if "%choice%"=="9" goto show_status
if "%choice%"=="0" goto start_local_mode
goto invalid_choice

:start_full
echo 🚀 Запуск всех сервисов с %CONTAINER_RUNTIME%...
%COMPOSE_CMD% up -d --build
goto show_success

:start_minimal
echo 🔧 Запуск Django + Redis с %CONTAINER_RUNTIME%...
%COMPOSE_CMD% up -d --build web redis
goto show_success

:start_postgres
echo 🐘 Запуск с PostgreSQL...
%COMPOSE_CMD% --profile postgres up -d --build
goto show_success

:start_rootless
if "%CONTAINER_RUNTIME%"=="podman" (
    echo 🏠 Запуск в rootless режиме...
    set PODMAN_ROOTLESS=1
    %COMPOSE_CMD% up -d --build web redis
) else (
    echo ⚠️  Rootless режим доступен только с Podman
    %COMPOSE_CMD% up -d --build web redis
)
goto show_success

:stop_services
echo 🛑 Остановка сервисов...
%COMPOSE_CMD% down
echo ✅ Сервисы остановлены
goto end

:restart_services
echo 🔄 Перезапуск сервисов...
%COMPOSE_CMD% restart
echo ✅ Сервисы перезапущены
%COMPOSE_CMD% ps
goto end

:show_logs
echo 📋 Логи сервисов (нажмите Ctrl+C для выхода):
%COMPOSE_CMD% logs -f
goto end

:clean_data
echo ⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные!
set /p confirm="Вы уверены? (y/N): "
if /i "%confirm%"=="y" (
    echo 🧹 Очистка данных...
    %COMPOSE_CMD% down -v --remove-orphans
    if "%CONTAINER_RUNTIME%"=="podman" (
        podman system prune -f
        podman volume prune -f
        podman network rm mveu_network 2>nul
    ) else (
        docker system prune -f
    )
    echo ✅ Данные очищены
) else (
    echo ℹ️  Отменено
)
goto end

:show_status
echo 📊 Статус контейнеров:
%COMPOSE_CMD% ps
echo.
if "%CONTAINER_RUNTIME%"=="podman" (
    echo 🔍 Информация о Podman:
    podman --version
) else (
    echo 🔍 Информация о Docker:
    docker --version
)
goto end

:show_success
echo.
echo ✅ Сервисы запущены с %CONTAINER_RUNTIME%!
echo.
echo 🌐 Доступные URL:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📱 Главная страница:     http://localhost:8001
echo 🛡️  Django Admin:        http://localhost:8001/admin
echo 💬 Админка чатов:        http://localhost:8001/admin-chat
echo 🔗 API endpoint:         http://localhost:8001/api/
echo 🌐 Nginx (если запущен): http://localhost:80
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 👤 Логин админа: admin / admin123
echo.
echo 📊 Статус сервисов:
%COMPOSE_CMD% ps
goto end

:start_local_mode
echo 🏃 Запуск в локальном режиме (без контейнеров)...

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не установлен
    echo 📋 Установите Python: https://python.org/downloads/
    pause
    exit /b 1
)

REM Setup local environment
echo ⚙️  Настройка локального окружения...
(
echo DEBUG=True
echo SECRET_KEY=django-insecure-local-development-key
echo ALLOWED_HOSTS=*
echo REDIS_URL=redis://localhost:6379/0
echo TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
echo OPENAI_API_KEY=
) > backend\.env
echo ✅ Создан backend\.env для локального запуска

REM Create virtual environment if not exists
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    echo ✅ Виртуальное окружение создано
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Установка зависимостей...
cd backend
pip install -r requirements.txt >nul 2>&1

REM Check Redis (optional)
redis-server --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis найден
) else (
    echo ⚠️  Redis не найден (WebSocket может не работать)
    echo 💡 Установите Redis: https://redis.io/download
)

REM Run migrations
echo 🔄 Применение миграций...
python manage.py migrate >nul 2>&1

REM Create superuser
echo 👤 Создание администратора...
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mveu.ru', 'admin123')
    print('✅ Администратор создан: admin / admin123')
else:
    print('ℹ️  Администратор уже существует')
" >nul 2>&1

echo.
echo 🎉 Запуск Django сервера в локальном режиме...
echo.
echo 🌐 Доступные URL:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📱 Главная страница:     http://localhost:8000
echo 🛡️  Django Admin:        http://localhost:8000/admin
echo 💬 Админка чатов:        http://localhost:8000/admin-chat
echo 🔗 API endpoint:         http://localhost:8000/api/
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 👤 Логин админа: admin / admin123
echo.
echo 🚀 Сервер запускается на http://localhost:8000
echo ⚠️  Нажмите Ctrl+C для остановки
echo.

python manage.py runserver 0.0.0.0:8000
goto end

:invalid_choice
echo ❌ Неверный выбор
goto end

:end
pause
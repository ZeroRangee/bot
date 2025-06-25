@echo off
chcp 65001 >nul
title MVEU Telegram Bot - Podman Windows Launcher

echo ========================================
echo 🎓 MVEU Telegram Bot - Podman Launcher  
echo ========================================

REM Check if Podman is installed
podman --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Podman не установлен
    echo 📋 Установите Podman Desktop с https://podman.io/getting-started/installation
    echo    или используйте WSL2 с Linux установкой
    pause
    exit /b 1
)

echo ✅ Podman найден

REM Check for podman-compose
set COMPOSE_CMD=
podman-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set COMPOSE_CMD=podman-compose
    echo ✅ podman-compose найден
) else (
    podman compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=podman compose
        echo ✅ встроенный podman compose найден
    ) else (
        echo ❌ Podman Compose не найден
        echo 📋 Установите: pip install podman-compose
        pause
        exit /b 1
    )
)

REM Setup environment files
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul
        echo ✅ Создан backend\.env из примера
    ) else (
        (
        echo DEBUG=True
        echo SECRET_KEY=django-insecure-local-development-key
        echo ALLOWED_HOSTS=*
        echo REDIS_URL=redis://redis:6379/0
        echo TELEGRAM_BOT_TOKEN=7510155003:AAHxU-SkAlo5yN1SoHVzom3b9LIZv-JhPK8
        echo OPENAI_API_KEY=
        ) > backend\.env
        echo ✅ Создан минимальный backend\.env
    )
)

if not exist "frontend\.env" (
    (
    echo REACT_APP_BACKEND_URL=http://localhost:8001
    echo WDS_SOCKET_PORT=3000
    ) > frontend\.env
    echo ✅ Создан frontend\.env
)

REM Setup Podman network
podman network exists mveu_network >nul 2>&1
if %errorlevel% neq 0 (
    echo 🌐 Создание Podman сети...
    podman network create mveu_network
    echo ✅ Сеть mveu_network создана
)

echo.
echo 🎯 Выберите режим запуска:
echo 1. 🚀 Полный запуск (Django + Redis + Nginx)
echo 2. 🔧 Только Django + Redis (без Nginx)
echo 3. 🐘 С PostgreSQL (вместо SQLite)
echo 4. 🏠 Rootless режим (рекомендуется для Windows)
echo 5. 🛑 Остановить все сервисы
echo 6. 🔄 Перезапустить сервисы
echo 7. 📋 Показать логи
echo 8. 🧹 Очистить данные
echo 9. 🔍 Статус сервисов
echo.

set /p choice="Введите номер (1-9): "

if "%choice%"=="1" goto full_start
if "%choice%"=="2" goto minimal_start  
if "%choice%"=="3" goto postgres_start
if "%choice%"=="4" goto rootless_start
if "%choice%"=="5" goto stop_services
if "%choice%"=="6" goto restart_services
if "%choice%"=="7" goto show_logs
if "%choice%"=="8" goto clean_data
if "%choice%"=="9" goto show_status
goto invalid_choice

:full_start
echo 🚀 Запуск всех сервисов с Podman...
%COMPOSE_CMD% up -d --build
goto show_info

:minimal_start
echo 🔧 Запуск Django + Redis с Podman...
%COMPOSE_CMD% up -d --build web redis
goto show_info

:postgres_start
echo 🐘 Запуск с PostgreSQL...
%COMPOSE_CMD% --profile postgres up -d --build
goto show_info

:rootless_start
echo 🏠 Запуск в rootless режиме...
set PODMAN_ROOTLESS=1
%COMPOSE_CMD% up -d --build web redis
goto show_info

:stop_services
echo 🛑 Остановка сервисов Podman...
%COMPOSE_CMD% down
echo ✅ Сервисы остановлены
goto end

:restart_services
echo 🔄 Перезапуск сервисов Podman...
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
    echo 🧹 Очистка данных Podman...
    %COMPOSE_CMD% down -v --remove-orphans
    podman system prune -f
    podman volume prune -f
    podman network rm mveu_network 2>nul
    echo ✅ Данные очищены
) else (
    echo ℹ️  Отменено
)
goto end

:show_status
echo 📊 Статус контейнеров Podman:
%COMPOSE_CMD% ps
echo.
echo 🔍 Podman контейнеры:
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo 🔍 Информация о Podman:
podman --version
if exist podman-compose (
    podman-compose --version
)
echo.
echo 🌐 Сети Podman:
podman network ls
echo.
echo 💾 Volumes Podman:
podman volume ls
goto end

:show_info
echo.
echo ✅ Сервисы запущены с Podman!
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

:invalid_choice
echo ❌ Неверный выбор
goto end

:end
pause
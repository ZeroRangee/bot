@echo off
chcp 65001 >nul
title MVEU Telegram Bot - Windows Launcher

echo ========================================
echo 🎓 MVEU Telegram Bot - Windows Launcher  
echo ========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен
    echo 📋 Установите Docker Desktop с https://docker.com/get-started
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker Compose не установлен
        pause
        exit /b 1
    )
)

echo ✅ Docker найден

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

echo.
echo 🎯 Выберите режим запуска:
echo 1. 🚀 Полный запуск (Django + Redis + Nginx)
echo 2. 🔧 Только Django + Redis (без Nginx)
echo 3. 🐘 С PostgreSQL (вместо SQLite)
echo 4. 🛑 Остановить все сервисы
echo 5. 🔄 Перезапустить сервисы
echo 6. 📋 Показать логи
echo 7. 🧹 Очистить данные
echo.

set /p choice="Введите номер (1-7): "

if "%choice%"=="1" goto full_start
if "%choice%"=="2" goto minimal_start  
if "%choice%"=="3" goto postgres_start
if "%choice%"=="4" goto stop_services
if "%choice%"=="5" goto restart_services
if "%choice%"=="6" goto show_logs
if "%choice%"=="7" goto clean_data
goto invalid_choice

:full_start
echo 🚀 Запуск всех сервисов...
docker-compose up -d --build
if %errorlevel% neq 0 docker compose up -d --build
goto show_info

:minimal_start
echo 🔧 Запуск Django + Redis...
docker-compose up -d --build web redis
if %errorlevel% neq 0 docker compose up -d --build web redis
goto show_info

:postgres_start
echo 🐘 Запуск с PostgreSQL...
docker-compose --profile postgres up -d --build
if %errorlevel% neq 0 docker compose --profile postgres up -d --build
goto show_info

:stop_services
echo 🛑 Остановка сервисов...
docker-compose down
if %errorlevel% neq 0 docker compose down
echo ✅ Сервисы остановлены
goto end

:restart_services
echo 🔄 Перезапуск сервисов...
docker-compose restart
if %errorlevel% neq 0 docker compose restart
echo ✅ Сервисы перезапущены
docker-compose ps
if %errorlevel% neq 0 docker compose ps
goto end

:show_logs
echo 📋 Логи сервисов (нажмите Ctrl+C для выхода):
docker-compose logs -f
if %errorlevel% neq 0 docker compose logs -f
goto end

:clean_data
echo ⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные!
set /p confirm="Вы уверены? (y/N): "
if /i "%confirm%"=="y" (
    echo 🧹 Очистка данных...
    docker-compose down -v --remove-orphans
    if %errorlevel% neq 0 docker compose down -v --remove-orphans
    docker system prune -f
    echo ✅ Данные очищены
) else (
    echo ℹ️  Отменено
)
goto end

:show_info
echo.
echo ✅ Сервисы запущены!
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
docker-compose ps
if %errorlevel% neq 0 docker compose ps
goto end

:invalid_choice
echo ❌ Неверный выбор
goto end

:end
pause
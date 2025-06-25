# 🎓 MVEU Telegram Bot - Универсальная установка

## 🚀 Автоматический выбор запуска

Скрипт автоматически определит лучший способ запуска:

### 1. С Docker (рекомендуется)
```bash
# Linux/macOS
./start.sh

# Windows  
start.bat
```

### 2. Без Docker (если Docker недоступен)
```bash
# Linux/macOS
./start_local.sh

# Windows - требует WSL или Git Bash
```

## 📋 Системные требования

### Минимальные требования:
- **Python 3.8+** 
- **4GB RAM**
- **2GB** свободного места

### Рекомендуемые требования (с Docker):
- **Docker Desktop**
- **8GB RAM**
- **5GB** свободного места

## 🔧 Установка на разных системах

### Ubuntu/Debian
```bash
# Установка зависимостей
sudo apt update
sudo apt install python3 python3-venv python3-pip redis-server

# Клонирование и запуск
git clone <repository>
cd mveu-telegram-bot
./start_local.sh
```

### CentOS/RHEL
```bash
# Установка зависимостей
sudo yum install python3 python3-pip redis
sudo systemctl start redis

# Запуск
./start_local.sh
```

### macOS
```bash
# С Homebrew
brew install python redis
brew services start redis

# Запуск
./start_local.sh
```

### Windows 10/11

#### Вариант 1: Docker Desktop (рекомендуется)
1. Установить [Docker Desktop](https://docker.com/get-started)
2. Двойной клик на `start.bat`

#### Вариант 2: WSL2
1. Установить WSL2 с Ubuntu
2. Следовать инструкциям для Ubuntu
3. Запустить `./start_local.sh`

#### Вариант 3: Git Bash
1. Установить [Git for Windows](https://git-scm.com/downloads)
2. Установить [Python](https://python.org/downloads/)
3. Запустить через Git Bash: `./start_local.sh`

## 🎯 Проверка работоспособности

После любого типа запуска:

1. **Откройте браузер:** http://localhost:8001 (Docker) или http://localhost:8000 (локально)
2. **Проверьте API:** /api/users/
3. **Войдите в админку:** /admin (admin/admin123)
4. **Протестируйте бота:** [@test_mvek_bot](https://t.me/test_mvek_bot)

## 🐛 Решение проблем

### Docker не запускается
```bash
# Проверить статус Docker
docker --version
docker-compose --version

# Альтернативный запуск
./start_local.sh
```

### Python ошибки
```bash
# Обновить pip
pip install --upgrade pip

# Переустановить зависимости  
pip install -r backend/requirements.txt --force-reinstall
```

### Порт занят
```bash
# Найти процесс
sudo lsof -i :8001    # или :8000

# Убить процесс
sudo kill -9 <PID>
```

### Redis недоступен
```bash
# Запустить Redis
redis-server --daemonize yes

# Или без Redis (ограниченный функционал)
# WebSocket чат не будет работать
```

## 🔄 Обновление

```bash
# Остановить сервисы
docker-compose down
# или Ctrl+C для локального запуска

# Обновить код
git pull

# Перезапустить
./start.sh
```

## 📞 Поддержка

- **Telegram Bot:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- **GitHub Issues:** Создать issue в репозитории
- **Email:** support@mveu.ru

---

**Выберите подходящий способ запуска для вашей системы!** 🎯
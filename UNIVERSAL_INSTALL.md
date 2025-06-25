# 🎓 MVEU Telegram Bot - Универсальная установка (Podman Edition)

## 🚀 Автоматический выбор запуска

Скрипт автоматически определит лучший способ запуска:

### 1. С Podman (рекомендуется - безопаснее Docker)
```bash
# Автоматическая установка Podman
chmod +x install_podman.sh
./install_podman.sh

# Запуск
./start.sh      # Linux/macOS
start.bat       # Windows
```

### 2. Без контейнеров (если Podman недоступен)
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

### Рекомендуемые требования (с Podman):
- **Podman 4.0+** 
- **8GB RAM**
- **5GB** свободного места

## 🐳 Почему Podman лучше Docker?

| Аспект | Docker | Podman |
|--------|--------|--------|
| **Безопасность** | Требует демон с root | Rootless, без демона |
| **Простота** | Часто нужен sudo | Запуск как обычный пользователь |
| **Надежность** | Единая точка отказа | Изолированные процессы |
| **Производительность** | Overhead от демона | Прямое взаимодействие |
| **Совместимость** | Docker API | Docker API + OCI стандарт |

## 🔧 Установка на разных системах

### Ubuntu/Debian
```bash
# Автоматическая установка Podman
./install_podman.sh

# Или вручную:
sudo apt update
sudo apt install podman
pip3 install podman-compose

# Запуск приложения
./start.sh
```

### CentOS/RHEL/Fedora
```bash
# Автоматическая установка Podman
./install_podman.sh

# Или вручную:
sudo dnf install podman  # или yum
pip3 install podman-compose

# Запуск
./start.sh
```

### macOS
```bash
# Автоматическая установка
./install_podman.sh

# Или вручную с Homebrew:
brew install podman
pip3 install podman-compose
podman machine init && podman machine start

# Запуск
./start.sh
```

### Windows 10/11

#### Вариант 1: Podman Desktop (рекомендуется)
1. Скачать [Podman Desktop](https://podman.io/getting-started/installation)
2. Установить Podman Desktop
3. Двойной клик на `start.bat`

#### Вариант 2: WSL2 + Ubuntu
1. Установить WSL2 с Ubuntu
2. В Ubuntu: `./install_podman.sh`
3. Запустить: `./start.sh`

#### Вариант 3: Без контейнеров
1. Установить [Python](https://python.org/downloads/)
2. Установить [Git for Windows](https://git-scm.com/downloads)
3. В Git Bash: `./start_local.sh`

## 🎯 Проверка работоспособности

После любого типа запуска:

1. **Откройте браузер:** http://localhost:8001 (Podman) или http://localhost:8000 (локально)
2. **Проверьте API:** /api/users/
3. **Войдите в админку:** /admin (admin/admin123)
4. **Протестируйте бота:** [@test_mvek_bot](https://t.me/test_mvek_bot)

## 🐛 Решение проблем

### Podman не запускается
```bash
# Проверить статус Podman
podman --version
podman system info

# macOS: Перезапуск машины
podman machine restart

# Linux: Настройка rootless режима
loginctl enable-linger $USER

# Альтернативный запуск без контейнеров
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
sudo lsof -i :8001    # Podman
sudo lsof -i :8000    # локальный запуск

# Убить процесс
sudo kill -9 <PID>

# Или использовать другой порт
export PORT=8002
./start_local.sh
```

### Redis недоступен
```bash
# С Podman (автоматически включен)
podman-compose logs redis

# Без Podman (установить отдельно)
sudo apt install redis-server  # Ubuntu
brew install redis            # macOS
redis-server --daemonize yes
```

## 🔄 Миграция с Docker

Если у вас был Docker:

1. **Остановить Docker:**
```bash
docker-compose down
```

2. **Установить Podman:**
```bash
./install_podman.sh
```

3. **Запустить с Podman:**
```bash
./start.sh
```

> **Примечание:** docker-compose.yml полностью совместим с Podman!

## 🎛️ Режимы запуска Podman

1. **🚀 Полный** - Django + Redis + Nginx (production-ready)
2. **🔧 Минимальный** - Django + Redis (для разработки)
3. **🐘 PostgreSQL** - С PostgreSQL вместо SQLite
4. **🏠 Rootless** - Без sudo (рекомендуется для безопасности)
5. **🛑 Остановка** - Остановить все сервисы
6. **🔄 Перезапуск** - Перезапустить сервисы
7. **📋 Логи** - Логи в реальном времени
8. **🧹 Очистка** - Полная очистка данных
9. **🔍 Статус** - Подробная информация о контейнерах

## 🔐 Безопасность Podman

### Преимущества rootless режима:
- ✅ Контейнеры не могут получить root права
- ✅ Изоляция на уровне пользователя
- ✅ Нет демона с привилегиями
- ✅ Автоматическая настройка безопасности

### Security features:
- **User namespaces:** Изоляция пользователей
- **Seccomp profiles:** Ограничение системных вызовов
- **no-new-privileges:** Запрет повышения привилегий
- **SELinux/AppArmor:** Дополнительная защита

## 🔄 Обновление

```bash
# Остановить сервисы
podman-compose down
# или Ctrl+C для локального запуска

# Обновить код
git pull

# Обновить Podman образы
podman-compose pull

# Перезапустить
./start.sh
```

## 📞 Поддержка

- **Telegram Bot:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- **GitHub Issues:** Создать issue в репозитории
- **Podman Docs:** https://docs.podman.io/
- **Email:** support@mveu.ru

## 🎯 Рекомендуемый путь установки

1. **Первый выбор:** Podman (безопасный, современный)
2. **Если Podman недоступен:** Локальный запуск с Python
3. **Для разработки:** Rootless режим Podman
4. **Для продакшена:** Полный режим с Nginx

---

**Выберите Podman для максимальной безопасности и производительности!** 🐳🔒
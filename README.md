# 🎓 MVEU Telegram Bot - Система Приемной Комиссии (Podman Edition)

Полнофункциональная система для работы с абитуриентами и студентами через Telegram бота с веб-админкой. **Теперь на Podman!**

## 🐳 Зачем Podman?

- **🔒 Безопасность:** Работает без демона, rootless режим
- **🏠 Простота:** Не требует sudo для запуска контейнеров
- **⚡ Совместимость:** Полная совместимость с Docker Compose
- **🎯 Надежность:** Меньше точек отказа, лучшая изоляция

## 🚀 Быстрый запуск

### 1. Автоматическая установка Podman
```bash
# Автоматическая установка (рекомендуется)
chmod +x install_podman.sh
./install_podman.sh
```

### 2. Запуск приложения

#### Windows
```bash
# Двойной клик или запуск в PowerShell/CMD
start.bat
```

#### Linux/macOS
```bash
# Сделать исполняемым и запустить
chmod +x start.sh
./start.sh
```

### 3. Ручная установка Podman (при необходимости)

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install podman
pip3 install podman-compose
```

#### CentOS/RHEL/Fedora
```bash
sudo dnf install podman  # или yum
pip3 install podman-compose
```

#### macOS
```bash
brew install podman
pip3 install podman-compose
podman machine init && podman machine start
```

#### Windows
- [Podman Desktop](https://podman.io/getting-started/installation) (рекомендуется)
- WSL2 с Linux установкой

## 📋 Системные требования

- **Podman 4.0+** - https://podman.io/getting-started/installation
- **Python 3.8+** (для podman-compose)
- **8GB RAM** (рекомендуется)
- **5GB** свободного места

## 🎛️ Режимы запуска

| Режим | Описание | Команда |
|-------|----------|---------|
| 🚀 **Полный** | Django + Redis + Nginx | Выбрать 1 в меню |
| 🔧 **Минимальный** | Django + Redis (разработка) | Выбрать 2 в меню |
| 🐘 **PostgreSQL** | С PostgreSQL вместо SQLite | Выбрать 3 в меню |
| 🏠 **Rootless** | Без sudo (рекомендуется) | Выбрать 4 в меню |
| 🛑 **Остановка** | Остановить все сервисы | Выбрать 5 в меню |
| 🔄 **Перезапуск** | Перезапустить сервисы | Выбрать 6 в меню |
| 📋 **Логи** | Логи в реальном времени | Выбрать 7 в меню |
| 🧹 **Очистка** | Полная очистка данных | Выбрать 8 в меню |
| 🔍 **Статус** | Информация о контейнерах | Выбрать 9 в меню |

## 🌐 Доступные URL после запуска

| Сервис | URL | Описание |
|--------|-----|----------|
| 📱 Главная | http://localhost:8001 | Основной интерфейс |
| 🛡️ Django Admin | http://localhost:8001/admin | Администрирование |
| 💬 Админка чатов | http://localhost:8001/admin-chat | Управление чатами |
| 🔗 API | http://localhost:8001/api/ | REST API |
| 🌐 Nginx | http://localhost:80 | Веб-сервер (если запущен) |

**Логин админа:** `admin` / `admin123`

## 🤖 Telegram Bot

**Бот:** [@test_mvek_bot](https://t.me/test_mvek_bot)

### Функции бота:
- 🎯 Меню Абитуриент/Студент
- 🤖 ИИ-помощник для вопросов
- 📄 Загрузка и управление документами
- 💬 Связь с приемной комиссией
- 📊 Статистика и аналитика

## ⚙️ Конфигурация

### Переменные окружения (backend/.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=*
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=your-bot-token
OPENAI_API_KEY=your-openai-key
```

### Базы данных
- **По умолчанию:** SQLite (не требует настройки)
- **PostgreSQL:** Запустить с режимом 3 (PostgreSQL)

## 📊 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/` | Список пользователей |
| GET | `/api/messages/` | Список сообщений |
| POST | `/api/send/` | Отправка сообщения |
| GET | `/api/admin/stats/` | Статистика |
| POST | `/api/ai-chat/` | ИИ-чат |

## 🔧 Разработка с Podman

### Структура проекта
```
/app/
├── backend/              # Django приложение
├── frontend/             # React фронтенд (если нужен)
├── docker/               # Конфигурации контейнеров
├── data/                 # Локальные данные (создается автоматически)
│   ├── postgres/         # Данные PostgreSQL
│   ├── redis/            # Данные Redis
│   ├── static/           # Статические файлы
│   └── media/            # Медиа файлы
├── start.sh             # Linux/macOS запуск
├── start.bat            # Windows запуск
├── install_podman.sh    # Установка Podman
└── docker-compose.yml   # Оркестрация (совместим с Podman)
```

### Полезные команды Podman
```bash
# Статус контейнеров
podman ps

# Логи контейнера
podman logs mveu-web

# Вход в контейнер
podman exec -it mveu-web bash

# Информация о системе
podman system info

# Очистка системы
podman system prune -f

# Список образов
podman images

# Статус машины (macOS)
podman machine list
```

## 🐛 Устранение проблем

### Проблемы с Podman
```bash
# Проверить статус Podman
podman --version
podman system info

# Перезапуск машины (macOS)
podman machine stop && podman machine start

# Права доступа (Linux)
sudo usermod -aG wheel $USER  # или sudo
```

### Проблемы с контейнерами
```bash
# Логи всех сервисов
podman-compose logs  # или podman compose logs

# Перестроить контейнеры
podman-compose build --no-cache

# Полная очистка
podman-compose down -v
podman system prune -af
```

### Проблемы с сетью
```bash
# Список сетей
podman network ls

# Пересоздать сеть
podman network rm mveu_network
podman network create mveu_network
```

## 🔐 Безопасность Podman

### Rootless режим (рекомендуется)
- ✅ Контейнеры запускаются от имени пользователя
- ✅ Не требует sudo для управления
- ✅ Изоляция на уровне пользователя
- ✅ Автоматическая настройка при установке

### Security features
- **no-new-privileges:** Запрет повышения привилегий
- **User namespace:** Изоляция пользователей
- **Seccomp profiles:** Ограничение системных вызовов
- **SELinux/AppArmor:** Дополнительная изоляция

## 🔄 Миграция с Docker

Если у вас был Docker:
1. **Остановите Docker:** `docker-compose down`
2. **Установите Podman:** `./install_podman.sh`
3. **Запустите с Podman:** `./start.sh`

> **Примечание:** docker-compose.yml полностью совместим с Podman!

## 📞 Поддержка

- **Telegram:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- **Issues:** Создайте issue в репозитории
- **Podman Docs:** https://docs.podman.io/
- **Email:** support@mveu.ru

## 🎯 Статус проекта

✅ **Готово к использованию с Podman**
- Все основные функции портированы на Podman
- Rootless режим настроен и работает
- Полная совместимость с Docker Compose
- Автоматическая установка на всех платформах
- Улучшенная безопасность и производительность

## 📝 Лицензия

MIT License - свободное использование и модификация.

---

**🎓 МВЭУ - Московский Высший Экономический Университет**  
**🐳 Powered by Podman - Secure Container Runtime**
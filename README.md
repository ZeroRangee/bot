# 🎓 MVEU Telegram Bot - Система Приемной Комиссии

Полнофункциональная система для работы с абитуриентами и студентами через Telegram бота с веб-админкой.

## 🚀 Быстрый запуск

### Windows
```bash
# Двойной клик или запуск в командной строке
start.bat
```

### Linux/macOS
```bash
# Сделать исполняемым и запустить
chmod +x start.sh
./start.sh
```

### Ручной запуск через Docker
```bash
# Полный запуск (рекомендуется)
docker-compose up -d --build

# Только Django + Redis (без Nginx)
docker-compose up -d --build web redis

# С PostgreSQL
docker-compose --profile postgres up -d --build
```

## 📋 Системные требования

- **Docker** - https://docker.com/get-started
- **Docker Compose** (обычно включен в Docker Desktop)
- **8GB RAM** (рекомендуется)
- **5GB** свободного места

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
- **PostgreSQL:** Запустить с `--profile postgres`

## 🛠️ Режимы запуска

1. **🚀 Полный** - Django + Redis + Nginx (production-like)
2. **🔧 Минимальный** - Django + Redis (для разработки)
3. **🐘 PostgreSQL** - С PostgreSQL вместо SQLite
4. **🛑 Остановка** - Остановить все сервисы
5. **🔄 Перезапуск** - Перезапустить сервисы
6. **📋 Логи** - Просмотр логов в реальном времени
7. **🧹 Очистка** - Полная очистка данных

## 📊 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/` | Список пользователей |
| GET | `/api/messages/` | Список сообщений |
| POST | `/api/send/` | Отправка сообщения |
| GET | `/api/admin/stats/` | Статистика |
| POST | `/api/ai-chat/` | ИИ-чат |

## 🔧 Разработка

### Структура проекта
```
/app/
├── backend/           # Django приложение
│   ├── telegram_app/  # Django проект
│   ├── chat/          # Основное приложение
│   └── requirements.txt
├── frontend/          # React фронтенд (если нужен)
├── docker/            # Docker конфигурации
├── start.sh          # Linux/macOS запуск
├── start.bat         # Windows запуск
└── docker-compose.yml # Оркестрация
```

### Локальная разработка
```bash
# Войти в контейнер Django
docker-compose exec web bash

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Собрать статику
python manage.py collectstatic
```

## 🐛 Устранение проблем

### Проблемы с запуском
1. **Порт занят:** Остановите сервисы на портах 8001, 80, 6379
2. **Docker не запускается:** Убедитесь что Docker Desktop запущен
3. **Permissions:** На Linux может потребоваться `sudo`

### Логи и диагностика
```bash
# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs web

# Статус сервисов
docker-compose ps

# Вход в контейнер для диагностики
docker-compose exec web bash
```

### Очистка при проблемах
```bash
# Полная очистка
docker-compose down -v --remove-orphans
docker system prune -f

# Пересборка без кеша
docker-compose build --no-cache
```

## 🔐 Безопасность

### Для продакшена:
1. Смените `SECRET_KEY` в backend/.env
2. Установите `DEBUG=False`
3. Настройте `ALLOWED_HOSTS`
4. Используйте HTTPS
5. Настройте ограничения Nginx

## 📞 Поддержка

- **Telegram:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- **Issues:** Создайте issue в репозитории
- **Email:** support@mveu.ru

## 🎯 Статус проекта

✅ **Готово к использованию**
- Все основные функции реализованы
- Telegram бот активен и работает
- Веб-интерфейс функционален
- API endpoints протестированы
- Docker конфигурация готова

## 📝 Лицензия

MIT License - свободное использование и модификация.

---

**🎓 МВЭУ - Московский Высший Экономический Университет**
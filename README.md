# 🎓 МВЭУ Telegram Bot

Полнофункциональный Telegram бот для Московского Внешкольного Экономического Университета с веб-админкой, ИИ-помощником и системой документооборота.

## 🚀 Быстрый старт с Docker

### Предварительные требования
- Docker и Docker Compose установлены
- Telegram Bot Token (получить у @BotFather)
- OpenAI API Key (опционально)

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий (или скопируйте файлы)
git clone <your-repo> mveu-telegram-bot
cd mveu-telegram-bot

# Сделайте скрипт запуска исполняемым
chmod +x docker/run.sh
```

### 2. Настройка переменных окружения

```bash
# Скопируйте файл с примером настроек
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

**Обязательные настройки в .env:**
```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
SECRET_KEY=your-django-secret-key
POSTGRES_PASSWORD=your-secure-password
```

### 3. Запуск приложения

```bash
# Простой запуск (рекомендуется)
./docker/run.sh start

# Или напрямую через docker-compose
docker-compose up -d
```

### 4. Доступ к приложению

После запуска приложение будет доступно по адресам:

- 🌐 **Основной чат**: http://localhost:8001
- 🛡️ **Django Admin**: http://localhost:8001/admin (admin:admin123)
- 👥 **Админка чатов**: http://localhost:8001/admin-chat
- 📊 **API документация**: http://localhost:8001/api/admin/stats

## 🤖 Возможности Telegram бота

### Главное меню
- **Абитуриент** / **Студент** - выбор типа пользователя

### Меню абитуриента
- **Задать вопрос** - ИИ-помощник с информацией о университете
- **Отправить документы** - загрузка и типизация документов
- **Связаться с приемной комиссией** - прямой чат с админами
- **Назад к меню** - возврат в главное меню

### Типы документов
- Паспорт
- Аттестат об образовании  
- Фотографии
- Медицинская справка
- Военный билет
- Другие документы

## 🌐 Веб-админка

### Функционал для приемной комиссии
- **Управление чатами** - переключение между пользователями
- **Real-time сообщения** - мгновенные уведомления через WebSocket
- **Массовая рассылка** - отправка сообщений всем или по группам
- **Статистика** - аналитика по документам, школам, активности

### Доступ к админке
1. Войдите в Django Admin: http://localhost:8001/admin
2. Используйте креды: `admin` / `admin123`
3. Перейдите в админку чатов: http://localhost:8001/admin-chat

## 📊 API Endpoints

```bash
# Пользователи Telegram
GET /api/users/

# Сообщения
GET /api/messages/

# Статистика (требует авторизации)
GET /api/admin/stats/

# Чат-сессии (требует авторизации)
GET /api/admin/sessions/

# Отправка сообщения от админа (требует авторизации)
POST /api/admin/send/

# Массовая рассылка (требует авторизации)
POST /api/admin/broadcast/

# ИИ-чат
POST /api/ai-chat/
```

## 🐳 Docker команды

### Основные команды

```bash
# Запуск всех сервисов
./docker/run.sh start

# Остановка сервисов
./docker/run.sh stop

# Перезапуск
./docker/run.sh restart

# Просмотр статуса
./docker/run.sh status

# Просмотр логов
./docker/run.sh logs

# Пересборка образов
./docker/run.sh build

# Полная очистка (осторожно!)
./docker/run.sh cleanup
```

### Прямые Docker команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Вход в контейнер Django
docker-compose exec web bash

# Выполнение Django команд
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic
```

## 🔧 Производственная конфигурация

### Настройка для продакшн

1. **Скопируйте продакшн конфиг:**
```bash
cp docker/docker-compose.prod.yml docker-compose.yml
```

2. **Настройте SSL сертификаты:**
```bash
mkdir ssl
# Поместите ваши SSL сертификаты в папку ssl/
```

3. **Настройте домен в .env:**
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Бэкапы базы данных

Автоматические бэкапы создаются каждые 24 часа:
```bash
# Просмотр бэкапов
ls -la backups/

# Восстановление из бэкапа
docker-compose exec postgres psql -U mveu_user -d mveu_bot < backups/backup_20231225_120000.sql
```

## 🛠️ Разработка

### Локальная разработка

```bash
# Клонирование для разработки
git clone <repo> && cd mveu-telegram-bot

# Установка зависимостей
cd backend
pip install -r requirements.txt

# Настройка локальной БД
python manage.py migrate
python manage.py createsuperuser

# Запуск локального сервера
python manage.py runserver
```

### Структура проекта

```
mveu-telegram-bot/
├── backend/                 # Django приложение
│   ├── chat/               # Основное приложение
│   ├── telegram_app/       # Настройки Django
│   ├── templates/          # HTML шаблоны
│   └── requirements.txt    # Python зависимости
├── docker/                 # Docker конфигурация
│   ├── nginx.conf         # Nginx конфиг
│   ├── entrypoint.sh      # Скрипт запуска
│   └── run.sh             # Утилита управления
├── docker-compose.yml     # Docker Compose конфиг
├── Dockerfile             # Docker образ
└── .env.example          # Пример настроек
```

## 🧪 Тестирование

```bash
# Тестирование API
curl http://localhost:8001/api/users/
curl http://localhost:8001/api/admin/stats/

# Тестирование ИИ
curl -X POST http://localhost:8001/api/ai-chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Какие направления есть в МВЭУ?"}'

# Проверка здоровья сервисов
docker-compose ps
```

## 🔐 Безопасность

### Продакшн настройки безопасности

1. **Измените все пароли по умолчанию**
2. **Используйте сильный SECRET_KEY**
3. **Настройте HTTPS с SSL сертификатами**
4. **Ограничьте доступ к админке по IP**
5. **Включите логирование и мониторинг**

### Рекомендуемые .env настройки для продакшн

```env
DEBUG=False
SECRET_KEY=super-secret-key-with-50-characters-minimum
ALLOWED_HOSTS=yourdomain.com
POSTGRES_PASSWORD=very-secure-password-123
REDIS_PASSWORD=another-secure-password-456
```

## 🆘 Устранение неполадок

### Частые проблемы

**Проблема:** Контейнеры не стартуют
```bash
# Проверка логов
docker-compose logs

# Пересборка образов
docker-compose build --no-cache
```

**Проблема:** База данных недоступна
```bash
# Проверка статуса PostgreSQL
docker-compose exec postgres pg_isready

# Перезапуск БД
docker-compose restart postgres
```

**Проблема:** Telegram бот не отвечает
```bash
# Проверка токена
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# Проверка логов Django
docker-compose logs web
```

### Полезные команды диагностики

```bash
# Проверка состояния всех сервисов
docker-compose ps

# Проверка использования ресурсов
docker stats

# Проверка сетевого подключения
docker-compose exec web ping redis
docker-compose exec web ping postgres
```

## 📞 Поддержка

- 📧 Email: admin@mveu.ru
- 💬 Telegram: @mveu_support
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

## 📝 Лицензия

MIT License - см. файл LICENSE

---

🎓 **МВЭУ - Московский Внешкольный Экономический Университет**  
Telegram Bot Platform v1.0
# 🧪 Быстрое тестирование MVEU Telegram Bot

## ⚡ Быстрый тест (2 минуты)

### 1. Запуск приложения
```bash
# Linux/macOS
./start.sh

# Windows
start.bat

# Выберите пункт "2" (Только Django + Redis)
```

### 2. Проверка основных функций
После запуска откройте в браузере:

✅ **Главная страница:** http://localhost:8001
- Должна загрузиться страница чата

✅ **API статус:** http://localhost:8001/api/users/
- Должен вернуть JSON с пользователями

✅ **Django Admin:** http://localhost:8001/admin
- Логин: `admin` / `admin123`

✅ **Админка чатов:** http://localhost:8001/admin-chat
- Интерфейс управления чатами

### 3. Тест Telegram бота
📱 **Бот:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- Отправьте `/start`
- Проверьте работу меню

## 🔧 Диагностика проблем

### Если что-то не работает:

1. **Проверить статус сервисов:**
```bash
docker-compose ps
```

2. **Посмотреть логи:**
```bash
docker-compose logs web
```

3. **Перезапустить:**
```bash
docker-compose restart
```

4. **Полная перезагрузка:**
```bash
docker-compose down
docker-compose up -d --build
```

## 📊 Ожидаемые результаты

- ✅ Django сервер запущен на порту 8001
- ✅ Redis работает для WebSocket
- ✅ База данных SQLite создана
- ✅ API endpoints отвечают
- ✅ Telegram bot активен
- ✅ Веб-интерфейс загружается

## 🎯 Готово!

Если все тесты прошли успешно - приложение готово к использованию на любом компьютере с Docker.

## 🐛 Частые проблемы

| Проблема | Решение |
|----------|---------|
| Порт 8001 занят | `sudo lsof -ti:8001 \| xargs kill -9` |
| Docker не найден | Установить Docker Desktop |
| Нет прав на Linux | Добавить пользователя в группу `docker` |
| Redis не подключается | Проверить `docker-compose logs redis` |
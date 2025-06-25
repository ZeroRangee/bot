# 🧪 Быстрое тестирование MVEU Telegram Bot (Podman Edition)

## ⚡ Быстрый тест (2 минуты)

### 1. Установка Podman (если нужно)
```bash
# Автоматическая установка
chmod +x install_podman.sh
./install_podman.sh

# Или вручную по инструкции в PODMAN_GUIDE.md
```

### 2. Запуск приложения
```bash
# Linux/macOS
./start.sh

# Windows
start.bat

# Выберите пункт "2" (Только Django + Redis) или "4" (Rootless режим)
```

### 3. Проверка основных функций
После запуска откройте в браузере:

✅ **Главная страница:** http://localhost:8001
- Должна загрузиться страница чата

✅ **API статус:** http://localhost:8001/api/users/
- Должен вернуть JSON с пользователями

✅ **Django Admin:** http://localhost:8001/admin
- Логин: `admin` / `admin123`

✅ **Админка чатов:** http://localhost:8001/admin-chat
- Интерфейс управления чатами

### 4. Тест Telegram бота
📱 **Бот:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- Отправьте `/start`
- Проверьте работу меню

## 🔧 Диагностика проблем с Podman

### Если что-то не работает:

1. **Проверить статус сервисов:**
```bash
podman-compose ps
# или
podman ps
```

2. **Посмотреть логи:**
```bash
podman-compose logs web
# или
podman logs mveu-web
```

3. **Проверить Podman:**
```bash
podman --version
podman system info
```

4. **Перезапустить:**
```bash
podman-compose restart
```

5. **Полная перезагрузка:**
```bash
podman-compose down
podman-compose up -d --build
```

6. **Очистка при проблемах:**
```bash
# Остановить все
podman-compose down -v

# Очистить систему
podman system prune -af
podman volume prune -f

# Пересоздать сеть
podman network rm mveu_network
podman network create mveu_network

# Запустить заново
./start.sh
```

## 🐳 Специфичные для Podman команды

### Полезные команды диагностики:
```bash
# Информация о Podman
podman system info

# Статус машины (macOS)
podman machine list
podman machine start

# Rootless режим
podman unshare cat /proc/self/uid_map

# Сети
podman network ls
podman network inspect mveu_network

# Volumes
podman volume ls
podman volume inspect mveu_postgres_data
```

### Решение типичных проблем:

#### macOS: Машина не запускается
```bash
podman machine stop
podman machine start
# или
podman machine init --cpus 2 --memory 4096
```

#### Linux: Права доступа
```bash
# Проверить настройки rootless
podman system migrate
loginctl enable-linger $USER
```

#### Windows: WSL2 проблемы
```bash
# В PowerShell
wsl --shutdown
wsl --start
```

## 📊 Ожидаемые результаты

- ✅ Podman установлен и работает
- ✅ Django сервер запущен на порту 8001 (без sudo!)
- ✅ Redis работает для WebSocket
- ✅ База данных SQLite создана
- ✅ API endpoints отвечают
- ✅ Telegram bot активен
- ✅ Веб-интерфейс загружается
- ✅ Rootless режим активен (безопасность++)

## 🎯 Готово!

Если все тесты прошли успешно - приложение готово к использованию на любом компьютере с Podman.

## 🐛 Частые проблемы с Podman

| Проблема | Решение |
|----------|---------|
| Порт 8001 занят | `podman ps` → `podman stop <container>` |
| Podman не найден | Запустить `./install_podman.sh` |
| Нет прав на Linux | `loginctl enable-linger $USER` |
| Redis не подключается | `podman network inspect mveu_network` |
| macOS машина не работает | `podman machine restart` |
| WSL2 не работает | `wsl --shutdown && wsl --start` |

## 🚀 Преимущества Podman

- 🔒 **Безопасность:** Rootless контейнеры по умолчанию
- 🏠 **Простота:** Не требует sudo для запуска
- ⚡ **Скорость:** Нет демона, прямое взаимодействие
- 🎯 **Надежность:** Лучшая изоляция процессов
- 🔧 **Совместимость:** Полная совместимость с Docker Compose

**Podman делает контейнеризацию безопаснее и проще!** 🐳
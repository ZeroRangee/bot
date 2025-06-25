# 🐳 MVEU Telegram Bot - Полное руководство по Podman

## 🎯 Что такое Podman и зачем он лучше Docker?

### Podman vs Docker

| Аспект | Docker | Podman |
|--------|--------|--------|
| **Демон** | Требует Docker daemon | Без демона (daemonless) |
| **Root права** | Часто требует sudo | Rootless по умолчанию |
| **Безопасность** | Единая точка отказа (daemon) | Изолированные процессы |
| **Производительность** | Overhead от daemon | Прямое взаимодействие |
| **Совместимость** | Docker API | Docker API + OCI совместимость |
| **Systemd интеграция** | Ограниченная | Нативная поддержка |

### Преимущества Podman для MVEU Bot:
- 🔒 **Безопасность:** Контейнеры не могут получить root права
- 🏠 **Простота:** Запуск без sudo
- ⚡ **Скорость:** Меньше накладных расходов
- 🎯 **Надежность:** Если один контейнер падает, остальные продолжают работать

## 🚀 Установка Podman на всех платформах

### 📱 Windows

#### Вариант 1: Podman Desktop (Рекомендуется)
```powershell
# Скачать с официального сайта
# https://podman.io/getting-started/installation

# Или через winget
winget install RedHat.Podman-Desktop
```

#### Вариант 2: WSL2
```bash
# Установить WSL2 с Ubuntu
wsl --install -d Ubuntu

# В Ubuntu выполнить:
sudo apt update
sudo apt install podman
pip3 install podman-compose
```

#### Вариант 3: Chocolatey
```powershell
# Установить Chocolatey, затем
choco install podman-desktop
```

### 🍎 macOS

#### Homebrew (Рекомендуется)
```bash
# Установить Homebrew если нет
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установить Podman
brew install podman

# Установить podman-compose
pip3 install podman-compose

# Инициализировать машину
podman machine init
podman machine start
```

#### MacPorts
```bash
sudo port install podman
```

### 🐧 Linux

#### Ubuntu/Debian
```bash
# Обновить репозитории
sudo apt update

# Установить зависимости
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавить репозиторий Podman
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_$(lsb_release -rs)/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list

curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_$(lsb_release -rs)/Release.key" | sudo apt-key add -

# Установить Podman
sudo apt update
sudo apt install -y podman

# Установить podman-compose
sudo apt install -y python3-pip
pip3 install podman-compose
```

#### CentOS/RHEL/Fedora
```bash
# Fedora
sudo dnf install podman

# CentOS/RHEL 8+
sudo dnf install podman

# CentOS/RHEL 7
sudo yum install podman

# Установить podman-compose
pip3 install --user podman-compose
```

#### Arch Linux
```bash
# Установить Podman
sudo pacman -S podman

# Установить podman-compose
yay -S podman-compose  # или pip3 install podman-compose
```

## ⚙️ Настройка Podman для MVEU Bot

### 1. Настройка rootless режима
```bash
# Проверить настройки пользователя
id

# Настроить subuid/subgid (автоматически при установке)
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid

# Включить lingering для systemd
loginctl enable-linger $USER

# Настроить хранилище
mkdir -p ~/.config/containers
cat > ~/.config/containers/storage.conf << EOF
[storage]
driver = "overlay"
runroot = "/run/user/\$UID/containers"
graphroot = "\$HOME/.local/share/containers/storage"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF
```

### 2. Настройка сети
```bash
# Создать сеть для MVEU Bot
podman network create mveu_network

# Проверить сети
podman network ls
```

### 3. Настройка хранилища
```bash
# Создать директории для данных
mkdir -p data/{postgres,redis,static,media}
chmod 755 data data/*
```

## 🎛️ Управление MVEU Bot с Podman

### Основные команды

#### Запуск и остановка
```bash
# Запуск всех сервисов
./start.sh  # выбрать режим в меню

# Или напрямую
podman-compose up -d

# Остановка
podman-compose down

# Перезапуск
podman-compose restart
```

#### Мониторинг
```bash
# Статус контейнеров
podman ps
podman-compose ps

# Логи
podman logs mveu-web
podman-compose logs

# Ресурсы
podman stats
```

#### Управление образами
```bash
# Список образов
podman images

# Обновление образов
podman pull redis:7-alpine
podman pull postgres:15-alpine

# Очистка
podman image prune -f
```

### Работа с контейнерами

#### Вход в контейнер
```bash
# Django контейнер
podman exec -it mveu-web bash

# Redis контейнер
podman exec -it mveu-redis redis-cli

# PostgreSQL контейнер (если используется)
podman exec -it mveu-postgres psql -U mveu_user -d mveu_bot
```

#### Копирование файлов
```bash
# Из контейнера на хост
podman cp mveu-web:/app/db.sqlite3 ./backup.db

# С хоста в контейнер
podman cp ./new_settings.py mveu-web:/app/settings.py
```

## 🔧 Устранение проблем

### Проблемы с установкой

#### macOS: Машина не запускается
```bash
# Остановить и пересоздать
podman machine stop
podman machine rm
podman machine init --cpus 2 --memory 4096
podman machine start
```

#### Linux: Права доступа
```bash
# Добавить пользователя в группы
sudo usermod -aG wheel $USER
newgrp wheel

# Перелогиниться или перезагрузиться
```

#### Windows: WSL проблемы
```bash
# Обновить WSL
wsl --update

# Перезапустить WSL
wsl --shutdown
wsl
```

### Проблемы с контейнерами

#### Контейнеры не запускаются
```bash
# Проверить логи
podman-compose logs web

# Проверить сеть
podman network ls
podman network inspect mveu_network

# Пересоздать сеть
podman network rm mveu_network
podman network create mveu_network
```

#### Проблемы с volumes
```bash
# Проверить volumes
podman volume ls

# Очистить неиспользуемые
podman volume prune -f

# Проверить права доступа
ls -la data/
chmod -R 755 data/
```

#### Медленная работа
```bash
# Проверить ресурсы
podman stats

# Увеличить лимиты (если нужно)
# Редактировать docker-compose.yml:
# resources:
#   limits:
#     memory: 2G
#     cpus: '2.0'
```

### Проблемы с сетью

#### Порты недоступны
```bash
# Проверить занятые порты
ss -tulpn | grep :8001

# Убить процесс
sudo kill -9 <PID>

# Проверить маршрутизацию Podman
podman network inspect mveu_network
```

#### DNS не работает
```bash
# Проверить DNS в контейнере
podman exec mveu-web nslookup redis

# Перезапустить сеть
podman-compose down
podman network rm mveu_network
podman network create mveu_network
podman-compose up -d
```

## 🔍 Мониторинг и логи

### Системная информация
```bash
# Общая информация о Podman
podman system info

# Статистика использования
podman system df

# События в реальном времени
podman system events
```

### Детальные логи
```bash
# Логи с меткой времени
podman logs -t mveu-web

# Следить за логами
podman logs -f mveu-web

# Последние N строк
podman logs --tail 50 mveu-web

# Логи за определенный период
podman logs --since 2024-01-01T00:00:00 mveu-web
```

### Мониторинг ресурсов
```bash
# Использование ресурсов всеми контейнерами
podman stats

# Использование ресурсов конкретным контейнером
podman stats mveu-web

# Информация о процессах в контейнере
podman top mveu-web
```

## 🔄 Автоматизация и Systemd

### Создание systemd сервисов
```bash
# Создать systemd юнит для автозапуска
podman generate systemd --new --files --name mveu-web

# Установить сервис
mkdir -p ~/.config/systemd/user
mv container-mveu-web.service ~/.config/systemd/user/

# Включить автозапуск
systemctl --user daemon-reload
systemctl --user enable container-mveu-web.service
systemctl --user start container-mveu-web.service
```

### Автоматические обновления
```bash
# Включить автообновления образов
podman auto-update

# Настроить регулярное обновление
# Добавить в crontab:
# 0 3 * * * /usr/bin/podman auto-update
```

## 📊 Бэкапы и восстановление

### Создание бэкапов
```bash
# Бэкап volumes
podman volume export mveu_postgres_data > postgres_backup.tar
podman volume export mveu_redis_data > redis_backup.tar

# Бэкап базы данных
podman exec mveu-postgres pg_dump -U mveu_user mveu_bot > db_backup.sql

# Бэкап конфигурации
tar -czf config_backup.tar.gz backend/.env docker-compose.yml
```

### Восстановление
```bash
# Восстановление volumes
podman volume import mveu_postgres_data postgres_backup.tar
podman volume import mveu_redis_data redis_backup.tar

# Восстановление базы данных
podman exec -i mveu-postgres psql -U mveu_user mveu_bot < db_backup.sql
```

## 🚀 Продвинутые возможности

### Podman Pods
```bash
# Создать pod (альтернатива docker-compose)
podman pod create --name mveu-pod -p 8001:8001 -p 6379:6379

# Добавить контейнеры в pod
podman run -d --pod mveu-pod --name redis redis:7-alpine
podman run -d --pod mveu-pod --name web mveu-django-app
```

### Rootless containers с systemd
```bash
# Создать пользовательский systemd сервис
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/mveu-bot.service << EOF
[Unit]
Description=MVEU Telegram Bot
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/mveu-telegram-bot
ExecStart=/usr/bin/podman-compose up -d
ExecStop=/usr/bin/podman-compose down
TimeoutStartSec=0

[Install]
WantedBy=default.target
EOF

# Активировать сервис
systemctl --user daemon-reload
systemctl --user enable mveu-bot.service
systemctl --user start mveu-bot.service
```

## 📞 Получение помощи

### Официальные ресурсы
- **Документация:** https://docs.podman.io/
- **GitHub:** https://github.com/containers/podman
- **Форум:** https://github.com/containers/podman/discussions

### Сообщество
- **Reddit:** r/podman
- **IRC:** #podman на Libera.Chat
- **Matrix:** #podman:matrix.org

### Для MVEU Bot
- **Telegram:** [@test_mvek_bot](https://t.me/test_mvek_bot)
- **Issues:** Создайте issue в репозитории проекта
- **Email:** support@mveu.ru

---

**🎓 MVEU Bot теперь работает на безопасном и современном Podman!** 🐳
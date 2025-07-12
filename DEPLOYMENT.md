# 🚀 Деплой StreetPong на сервер

## Обзор

Это руководство описывает процесс деплоя StreetPong на сервер с автоматическим SSL сертификатом для домена streetpong.ru.

## 📋 Требования к серверу

- Ubuntu 20.04+ или Debian 11+
- Минимум 2GB RAM
- 20GB свободного места
- Домен streetpong.ru (настроенный на сервер)

## 🔧 Настройка сервера

### 1. Подключение к серверу
```bash
ssh user@your-server-ip
```

### 2. Запуск скрипта настройки
```bash
# Клонирование репозитория
git clone https://github.com/your-username/streetpong.git
cd streetpong

# Запуск скрипта настройки
chmod +x scripts/setup-server.sh
./scripts/setup-server.sh
```

### 3. Настройка переменных окружения
```bash
# Редактирование .env файла
nano /opt/streetpong/.env
```

Добавьте ваши значения:
```env
# База данных
POSTGRES_DB=streetpong
POSTGRES_USER=streetpong_user
POSTGRES_PASSWORD=your_secure_password

# Приложение
DATABASE_URL=postgresql://streetpong_user:your_secure_password@db:5432/streetpong
SECRET_KEY=your_secret_key_here
BOT_TOKEN=your_telegram_bot_token_here

# SSL
CERTBOT_EMAIL=admin@streetpong.ru

# Настройки
SKIP_TELEGRAM_SIGNATURE=false
```

### 4. Копирование файлов конфигурации
```bash
# Копирование docker-compose.prod.yml
cp docker-compose.prod.yml /opt/streetpong/

# Копирование nginx конфигурации
cp -r nginx/ /opt/streetpong/
```

## 🌐 Настройка домена

### 1. DNS настройки
Настройте DNS записи для домена streetpong.ru:
```
A     streetpong.ru     -> ваш-ip-сервера
A     www.streetpong.ru -> ваш-ip-сервера
```

### 2. Проверка DNS
```bash
nslookup streetpong.ru
nslookup www.streetpong.ru
```

## 🔒 Получение SSL сертификата

### 1. Первый запуск (без SSL)
```bash
cd /opt/streetpong
docker-compose -f docker-compose.prod.yml up -d db backend frontend
```

### 2. Получение SSL сертификата
```bash
# Получение сертификата
docker-compose -f docker-compose.prod.yml run --rm certbot

# Запуск всех сервисов с SSL
docker-compose -f docker-compose.prod.yml up -d
```

## 🚀 Запуск приложения

### 1. Автоматический запуск
```bash
# Включение автозапуска
sudo systemctl enable streetpong

# Запуск сервиса
sudo systemctl start streetpong

# Проверка статуса
sudo systemctl status streetpong
```

### 2. Ручной запуск
```bash
cd /opt/streetpong
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Мониторинг

### 1. Логи приложения
```bash
# Логи всех сервисов
docker-compose -f /opt/streetpong/docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker-compose -f /opt/streetpong/docker-compose.prod.yml logs -f backend
```

### 2. Статус сервисов
```bash
# Статус контейнеров
docker-compose -f /opt/streetpong/docker-compose.prod.yml ps

# Использование ресурсов
docker stats
```

## 🔄 Обновление приложения

### 1. Автоматическое обновление через GitHub Actions
При пуше в ветку `main` происходит автоматический деплой.

### 2. Ручное обновление
```bash
cd /opt/streetpong

# Остановка сервисов
docker-compose -f docker-compose.prod.yml down

# Обновление образов
docker pull ghcr.io/your-username/streetpong/backend:latest
docker pull ghcr.io/your-username/streetpong/frontend:latest

# Запуск обновленных сервисов
docker-compose -f docker-compose.prod.yml up -d
```

## 🛠️ Устранение неполадок

### 1. Проверка SSL сертификата
```bash
# Проверка срока действия
docker-compose -f /opt/streetpong/docker-compose.prod.yml run --rm certbot certificates

# Обновление сертификата
/opt/streetpong/renew-ssl.sh
```

### 2. Проверка базы данных
```bash
# Подключение к базе данных
docker-compose -f /opt/streetpong/docker-compose.prod.yml exec db psql -U streetpong_user -d streetpong

# Проверка миграций
docker-compose -f /opt/streetpong/docker-compose.prod.yml exec backend alembic current
```

### 3. Перезапуск сервисов
```bash
# Перезапуск всех сервисов
sudo systemctl restart streetpong

# Перезапуск конкретного сервиса
docker-compose -f /opt/streetpong/docker-compose.prod.yml restart backend
```

## 🔐 Безопасность

### 1. Файрвол
```bash
# Установка UFW
sudo apt install ufw

# Настройка правил
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Регулярные обновления
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker system prune -a
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose -f /opt/streetpong/docker-compose.prod.yml logs`
2. Проверьте статус сервисов: `sudo systemctl status streetpong`
3. Проверьте SSL сертификат: `/opt/streetpong/renew-ssl.sh`

## ✅ Проверка работоспособности

После деплоя проверьте:
- [ ] https://streetpong.ru - фронтенд загружается
- [ ] https://streetpong.ru/api/docs - API документация доступна
- [ ] Telegram бот отвечает на команды
- [ ] SSL сертификат действителен
- [ ] Автоматическое обновление SSL работает 
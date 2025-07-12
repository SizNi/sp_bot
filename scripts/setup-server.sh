#!/bin/bash

# Скрипт настройки сервера для StreetPong
# Использование: ./scripts/setup-server.sh

set -e

echo "🚀 Настройка сервера для StreetPong..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка Docker
echo "🐳 Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Установка Docker Compose
echo "📦 Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Создание директории проекта
echo "📁 Создание директории проекта..."
sudo mkdir -p /opt/streetpong
sudo chown $USER:$USER /opt/streetpong

# Создание .env файла
echo "🔧 Создание .env файла..."
cat > /opt/streetpong/.env << EOF
# База данных
POSTGRES_DB=streetpong
POSTGRES_USER=streetpong_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Приложение
DATABASE_URL=postgresql://streetpong_user:$(openssl rand -base64 32)@db:5432/streetpong
SECRET_KEY=$(openssl rand -base64 64)
BOT_TOKEN=your_telegram_bot_token_here

# SSL
CERTBOT_EMAIL=admin@streetpong.ru

# Настройки
SKIP_TELEGRAM_SIGNATURE=false
EOF

# Создание nginx директорий
echo "🌐 Настройка nginx..."
sudo mkdir -p /opt/streetpong/nginx/ssl
sudo mkdir -p /opt/streetpong/nginx/sites-enabled

# Копирование конфигурации nginx
cp nginx/nginx.conf /opt/streetpong/nginx/

# Создание скрипта обновления SSL
echo "🔒 Создание скрипта обновления SSL..."
cat > /opt/streetpong/renew-ssl.sh << 'EOF'
#!/bin/bash
cd /opt/streetpong
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
EOF

chmod +x /opt/streetpong/renew-ssl.sh

# Добавление cron задачу для обновления SSL
echo "⏰ Настройка автоматического обновления SSL..."
(crontab -l 2>/dev/null; echo "0 12 * * * /opt/streetpong/renew-ssl.sh") | crontab -

# Создание systemd сервиса для автозапуска
echo "🔧 Создание systemd сервиса..."
sudo tee /etc/systemd/system/streetpong.service > /dev/null << EOF
[Unit]
Description=StreetPong Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/streetpong
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Включение автозапуска
sudo systemctl enable streetpong.service

echo "✅ Настройка сервера завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте /opt/streetpong/.env файл"
echo "2. Добавьте ваш BOT_TOKEN в .env файл"
echo "3. Скопируйте docker-compose.prod.yml в /opt/streetpong/"
echo "4. Запустите: sudo systemctl start streetpong"
echo ""
echo "🔒 Для получения SSL сертификата:"
echo "docker-compose -f /opt/streetpong/docker-compose.prod.yml run --rm certbot" 
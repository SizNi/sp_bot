# 🔧 Настройка GitHub Actions для автоматического деплоя

## Обзор

Для автоматического деплоя через GitHub Actions необходимо настроить секреты в репозитории.

## 📋 Необходимые секреты

### 1. HOST
IP адрес или домен вашего сервера
```
HOST=your-server-ip.com
```

### 2. USERNAME
Имя пользователя для SSH подключения
```
USERNAME=ubuntu
```

### 3. SSH_KEY
Приватный SSH ключ для подключения к серверу

## 🔑 Настройка SSH ключей

### 1. Генерация SSH ключа
```bash
# Генерация ключа (если еще нет)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Копирование публичного ключа на сервер
ssh-copy-id username@your-server-ip
```

### 2. Получение приватного ключа
```bash
# Показать приватный ключ
cat ~/.ssh/id_rsa
```

## ⚙️ Настройка секретов в GitHub

### 1. Переход в настройки репозитория
1. Откройте ваш репозиторий на GitHub
2. Перейдите в Settings → Secrets and variables → Actions
3. Нажмите "New repository secret"

### 2. Добавление секретов

#### HOST
- **Name**: `HOST`
- **Value**: IP адрес или домен сервера

#### USERNAME
- **Name**: `USERNAME`
- **Value**: Имя пользователя для SSH

#### SSH_KEY
- **Name**: `SSH_KEY`
- **Value**: Весь содержимый приватного SSH ключа (включая `-----BEGIN OPENSSH PRIVATE KEY-----` и `-----END OPENSSH PRIVATE KEY-----`)

## 🔄 Проверка настройки

### 1. Тестовый коммит
Сделайте небольшое изменение в коде и запушьте в ветку `main`:

```bash
git add .
git commit -m "test: проверка автоматического деплоя"
git push origin main
```

### 2. Проверка Actions
1. Перейдите в вкладку Actions в репозитории
2. Найдите запущенный workflow "Deploy to Production"
3. Проверьте, что все шаги выполнились успешно

## 🛠️ Устранение неполадок

### 1. Ошибка SSH подключения
- Проверьте правильность HOST и USERNAME
- Убедитесь, что SSH_KEY добавлен полностью
- Проверьте, что публичный ключ добавлен на сервер

### 2. Ошибка Docker
- Убедитесь, что Docker установлен на сервере
- Проверьте права пользователя для работы с Docker

### 3. Ошибка доступа к реестру
- Убедитесь, что репозиторий публичный или настроен доступ к приватному реестру

## 📊 Мониторинг деплоя

### 1. Логи Actions
- Перейдите в Actions → Deploy to Production
- Нажмите на конкретный запуск
- Просмотрите логи каждого шага

### 2. Проверка на сервере
```bash
# Подключение к серверу
ssh username@your-server-ip

# Проверка статуса контейнеров
docker-compose -f /opt/streetpong/docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f /opt/streetpong/docker-compose.prod.yml logs -f
```

## 🔐 Безопасность

### 1. Ограничение доступа
- Используйте отдельного пользователя для деплоя
- Ограничьте права пользователя только необходимыми директориями

### 2. Ротация ключей
- Регулярно обновляйте SSH ключи
- Используйте временные токены доступа

### 3. Мониторинг
- Настройте уведомления о неудачных деплоях
- Регулярно проверяйте логи сервера

## ✅ Чек-лист настройки

- [ ] SSH ключи сгенерированы и настроены
- [ ] Публичный ключ добавлен на сервер
- [ ] Секрет HOST добавлен в GitHub
- [ ] Секрет USERNAME добавлен в GitHub
- [ ] Секрет SSH_KEY добавлен в GitHub
- [ ] Тестовый деплой выполнен успешно
- [ ] Приложение доступно по адресу https://streetpong.ru 
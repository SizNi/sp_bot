#!/usr/bin/env python3
"""
Script to set up the first admin user in the system.
Usage: python scripts/setup_admin.py <telegram_username>
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import get_db
from app.database.models import User

def setup_admin(username: str):
    """Устанавливает пользователя как администратора"""
    db = next(get_db())
    
    # Ищем пользователя по username
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        print(f"❌ Пользователь @{username} не найден в базе данных.")
        print("Убедитесь, что пользователь уже взаимодействовал с ботом.")
        return False
    
    if user.is_admin:
        print(f"✅ @{username} уже является администратором.")
        return True
    
    # Делаем пользователя администратором
    user.is_admin = True
    db.commit()
    
    print(f"✅ @{username} успешно назначен администратором!")
    return True

def main():
    if len(sys.argv) != 2:
        print("Использование: python scripts/setup_admin.py <telegram_username>")
        print("Пример: python scripts/setup_admin.py john_doe")
        sys.exit(1)
    
    username = sys.argv[1]
    if username.startswith('@'):
        username = username[1:]  # Убираем @ если есть
    
    success = setup_admin(username)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 
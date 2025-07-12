from app.database.database import SessionLocal
from app.database.models import User

def add_test_user():
    db = SessionLocal()
    
    # Создаем тестового пользователя
    test_user = User(
        telegram_id=123456789,  # Тестовый telegram_id
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"Тестовый пользователь создан с ID: {test_user.id}")
    
    db.close()

if __name__ == "__main__":
    add_test_user() 
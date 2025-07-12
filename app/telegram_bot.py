import asyncio
import logging
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, Challenge
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_or_create_user(db, tg_user: types.User):
    user = db.query(User).filter(User.telegram_id == tg_user.id).first()
    if not user:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            avatar_url=None,  # Можно получить через Telegram API, если нужно
            created_at=datetime.now()  # Добавляем текущее время
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def is_admin(db, user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    user = db.query(User).filter(User.telegram_id == user_id).first()
    return user and user.is_admin

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    db = next(get_db())
    user = get_or_create_user(db, message.from_user)
    
    help_text = (
        f"Привет, {user.first_name or user.username or 'игрок'}! Я бот для игры в настольный теннис.\n\n"
        "Команды:\n"
        "/вызов @username - вызвать игрока на матч\n"
        "/challenges - посмотреть ваши вызовы"
    )
    
    # Добавляем админские команды, если пользователь админ
    if user.is_admin:
        help_text += "\n\nАдминские команды:\n"
        help_text += "/addadmin @username - добавить администратора\n"
        help_text += "/removeadmin @username - убрать администратора\n"
        help_text += "/tournament - создать турнир (только для админов)"
    
    await message.answer(help_text)

# Команда /вызов
@dp.message(Command("вызов"))
async def cmd_challenge(message: types.Message):
    if not message.entities:
        await message.answer("Использование: /вызов @username")
        return
    
    # Извлекаем username из сообщения
    username = None
    for entity in message.entities:
        if entity.type == "mention":
            username = message.text[entity.offset + 1:entity.offset + entity.length]
            break
    
    if not username:
        await message.answer("Использование: /вызов @username")
        return
    
    db = next(get_db())
    challenger = get_or_create_user(db, message.from_user)
    challenged = db.query(User).filter(User.username == username).first()
    
    if not challenged:
        await message.answer(f"Пользователь @{username} не найден в системе.")
        return
    
    if challenger.id == challenged.id:
        await message.answer("Вы не можете вызвать сами себя.")
        return
    
    # Проверяем ограничение: 1 вызов в день
    today = datetime.now().date()
    existing_challenge = db.query(Challenge).filter(
        Challenge.challenger_id == challenger.id,
        Challenge.created_at >= today
    ).first()
    
    if existing_challenge:
        await message.answer("Вы уже создали вызов сегодня. Попробуйте завтра.")
        return
    
    # Создаем вызов
    new_challenge = Challenge(
        challenger_id=challenger.id,
        challenged_id=challenged.id,
        status="pending"
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    
    # Создаем inline кнопки для принятия/отклонения
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{new_challenge.id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{new_challenge.id}")
    )
    
    await message.answer(
        f"🎾 Вызов от @{challenger.username} для @{challenged.username}!\n\n"
        f"Примите или отклоните вызов:",
        reply_markup=keyboard.as_markup()
    )

# Обработка принятия вызова
@dp.callback_query(lambda c: c.data.startswith("accept_"))
async def accept_challenge(callback: types.CallbackQuery):
    challenge_id = int(callback.data.split("_")[1])
    db = next(get_db())
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        await callback.answer("Вызов не найден")
        return
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user or user.id != challenge.challenged_id:
        await callback.answer("Вы не можете принять этот вызов")
        return
    
    if challenge.status != "pending":
        await callback.answer("Вызов уже не в ожидании")
        return
    
    challenge.status = "accepted"
    challenge.accepted_at = datetime.now()
    db.commit()
    
    # Создаем кнопки для ввода результатов
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🏆 Я победил", callback_data=f"result_{challenge_id}_won"),
        InlineKeyboardButton(text="💀 Я проиграл", callback_data=f"result_{challenge_id}_lost")
    )
    
    await callback.message.edit_text(
        f"✅ Вызов принят!\n\n"
        f"После матча оба игрока должны нажать кнопку с результатом:",
        reply_markup=keyboard.as_markup()
    )

# Обработка отклонения вызова
@dp.callback_query(lambda c: c.data.startswith("decline_"))
async def decline_challenge(callback: types.CallbackQuery):
    challenge_id = int(callback.data.split("_")[1])
    db = next(get_db())
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        await callback.answer("Вызов не найден")
        return
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user or user.id != challenge.challenged_id:
        await callback.answer("Вы не можете отклонить этот вызов")
        return
    
    if challenge.status != "pending":
        await callback.answer("Вызов уже не в ожидании")
        return
    
    challenge.status = "declined"
    db.commit()
    
    await callback.message.edit_text("❌ Вызов отклонен")

# Обработка ввода результатов
@dp.callback_query(lambda c: c.data.startswith("result_"))
async def submit_result(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    challenge_id = int(parts[1])
    result = parts[2]
    
    db = next(get_db())
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        await callback.answer("Вызов не найден")
        return
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("Вы не зарегистрированы")
        return
    
    # Определяем, кто подает результат
    is_challenger = challenge.challenger_id == user.id
    is_challenged = challenge.challenged_id == user.id
    
    if not (is_challenger or is_challenged):
        await callback.answer("Вы не участвуете в этом вызове")
        return
    
    if challenge.status != "accepted":
        await callback.answer("Вызов не принят")
        return
    
    # Сохраняем результат
    if is_challenger:
        challenge.challenger_result = result
    else:
        challenge.challenged_result = result
    
    # Проверяем, оба ли игрока подали результаты
    if challenge.challenger_result and challenge.challenged_result:
        # Верифицируем результаты
        if challenge.challenger_result == challenge.challenged_result:
            await callback.answer("Ошибка: оба игрока не могут иметь одинаковый результат")
            return
        
        # Определяем победителя
        if challenge.challenger_result == "won":
            winner_id = challenge.challenger_id
            loser_id = challenge.challenged_id
        else:
            winner_id = challenge.challenged_id
            loser_id = challenge.challenger_id
        
        # Обновляем рейтинги (упрощенная версия)
        winner = db.query(User).filter(User.id == winner_id).first()
        loser = db.query(User).filter(User.id == loser_id).first()
        
        if winner and loser:
            winner.rating += 10
            loser.rating = max(0, loser.rating - 10)
        
        # Завершаем вызов
        challenge.status = "completed"
        challenge.completed_at = datetime.now()
        db.commit()
        
        await callback.message.edit_text(
            f"🏆 Матч завершен!\n\n"
            f"Победитель: @{winner.username if winner else 'Unknown'}\n"
            f"Проигравший: @{loser.username if loser else 'Unknown'}\n\n"
            f"Рейтинги обновлены!"
        )
    else:
        await callback.answer(f"Результат записан: {result}")
        db.commit()

# Команда для просмотра вызовов
@dp.message(Command("challenges"))
async def cmd_challenges(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Вы не зарегистрированы в системе.")
        return
    
    challenges = db.query(Challenge).filter(
        (Challenge.challenger_id == user.id) | (Challenge.challenged_id == user.id)
    ).order_by(Challenge.created_at.desc()).limit(5).all()
    
    if not challenges:
        await message.answer("У вас нет активных вызовов.")
        return
    
    text = "Ваши последние вызовы:\n\n"
    for challenge in challenges:
        challenger = db.query(User).filter(User.id == challenge.challenger_id).first()
        challenged = db.query(User).filter(User.id == challenge.challenged_id).first()
        
        status_emoji = {
            "pending": "⏳",
            "accepted": "✅",
            "declined": "❌",
            "completed": "🏆"
        }.get(challenge.status, "❓")
        
        text += f"{status_emoji} @{challenger.username} vs @{challenged.username} - {challenge.status}\n"
    
    await message.answer(text)

# Команда для добавления администратора
@dp.message(Command("addadmin"))
async def cmd_add_admin(message: types.Message):
    # Проверяем права администратора
    db = next(get_db())
    if not is_admin(db, message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    if not message.entities:
        await message.answer("Использование: /addadmin @username")
        return
    
    # Извлекаем username из сообщения
    username = None
    for entity in message.entities:
        if entity.type == "mention":
            username = message.text[entity.offset + 1:entity.offset + entity.length]
            break
    
    if not username:
        await message.answer("Использование: /addadmin @username")
        return
    
    # Находим пользователя
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        await message.answer(f"Пользователь @{username} не найден в системе.")
        return
    
    if target_user.is_admin:
        await message.answer(f"@{username} уже является администратором.")
        return
    
    # Делаем пользователя администратором
    target_user.is_admin = True
    db.commit()
    
    await message.answer(f"✅ @{username} назначен администратором!")

# Команда для удаления администратора
@dp.message(Command("removeadmin"))
async def cmd_remove_admin(message: types.Message):
    # Проверяем права администратора
    db = next(get_db())
    if not is_admin(db, message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    if not message.entities:
        await message.answer("Использование: /removeadmin @username")
        return
    
    # Извлекаем username из сообщения
    username = None
    for entity in message.entities:
        if entity.type == "mention":
            username = message.text[entity.offset + 1:entity.offset + entity.length]
            break
    
    if not username:
        await message.answer("Использование: /removeadmin @username")
        return
    
    # Находим пользователя
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        await message.answer(f"Пользователь @{username} не найден в системе.")
        return
    
    if not target_user.is_admin:
        await message.answer(f"@{username} не является администратором.")
        return
    
    # Убираем права администратора
    target_user.is_admin = False
    db.commit()
    
    await message.answer(f"✅ @{username} больше не является администратором.")

# Команда для создания турнира (только для админов)
@dp.message(Command("tournament"))
async def cmd_create_tournament(message: types.Message):
    # Проверяем права администратора
    db = next(get_db())
    if not is_admin(db, message.from_user.id):
        await message.answer("❌ Создавать турниры могут только администраторы.")
        return
    
    # Пока что просто сообщение о том, что команда работает
    # В будущем здесь можно добавить интерактивное создание турнира
    await message.answer(
        "🏆 Команда создания турнира работает!\n\n"
        "В будущих версиях здесь будет интерактивное создание турнира.\n"
        "Пока что используйте веб-интерфейс для создания турниров."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
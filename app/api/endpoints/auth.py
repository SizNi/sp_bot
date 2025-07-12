from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, Match, UserRatingHistory
from jose import jwt
from datetime import datetime, timedelta
import hashlib
import hmac
import os
from typing import List

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
JWT_SECRET = os.getenv("JWT_SECRET", "jwtsecret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 1 неделя

# Проверка подписи Telegram

def check_telegram_auth(data: dict, bot_token: str) -> bool:
    auth_data = data.copy()
    hash_ = auth_data.pop("hash", None)
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == hash_

@router.post("/auth/telegram")
async def telegram_auth(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    print(f"Received Telegram auth data: {data}")
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("Bot token not configured")
        raise HTTPException(status_code=500, detail="Bot token not configured")
    
    print(f"Checking Telegram auth with bot token: {bot_token[:10]}...")
    
    # Временно отключаем проверку подписи для разработки
    # TODO: Включить обратно для продакшена
    skip_signature_check = os.getenv("SKIP_TELEGRAM_SIGNATURE", "true").lower() == "true"
    
    if not skip_signature_check and not check_telegram_auth(data, bot_token):
        print("Invalid Telegram signature")
        raise HTTPException(status_code=400, detail="Invalid Telegram signature")
    
    telegram_id = int(data["id"])
    print(f"Processing user with telegram_id: {telegram_id}")
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        print(f"Creating new user: {data.get('username')}")
        user = User(
            telegram_id=telegram_id,
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            avatar_url=data.get("photo_url")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        print(f"Updating existing user: {user.username}")
        # Обновляем данные пользователя
        user.username = data.get("username")
        user.first_name = data.get("first_name")
        user.last_name = data.get("last_name")
        user.avatar_url = data.get("photo_url")
        db.commit()
    
    # Генерируем JWT
    payload = {
        "sub": str(user.id),
        "telegram_id": user.telegram_id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(f"Generated JWT for user {user.id}")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.rating.desc()).all()
    leaderboard = [
        {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
            "rating": user.rating,
            "place": idx + 1
        }
        for idx, user in enumerate(users)
    ]
    return leaderboard

@router.get("/user/{user_id}/history")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    history = db.query(UserRatingHistory).filter(UserRatingHistory.user_id == user_id).order_by(UserRatingHistory.created_at.desc()).all()
    result = []
    for h in history:
        match = db.query(Match).filter(Match.id == h.match_id).first()
        if not match:
            continue
        opponent_id = match.player2_id if match.player1_id == user_id else match.player1_id
        result.append({
            "date": match.created_at,
            "opponent_id": opponent_id,
            "score": match.score,
            "rating_before": h.rating_before,
            "rating_after": h.rating_after,
            "change": h.change,
            "is_win": match.winner_id == user_id
        })
    return result 
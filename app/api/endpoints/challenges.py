from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Challenge, User, Match, UserRatingHistory
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import and_

router = APIRouter()

class ChallengeCreate(BaseModel):
    challenged_username: str

class ChallengeResponse(BaseModel):
    challenger_username: str
    challenged_username: str
    status: str
    created_at: datetime

@router.post("/challenges")
def create_challenge(challenge: ChallengeCreate, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    challenger_id = 1  # Временно используем фиксированный ID
    
    # Находим пользователя, которого вызывают
    challenged_user = db.query(User).filter(User.username == challenge.challenged_username).first()
    if not challenged_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if challenged_user.id == challenger_id:
        raise HTTPException(status_code=400, detail="Cannot challenge yourself")
    
    # Проверяем ограничение: 1 вызов в день
    today = datetime.now().date()
    existing_challenge = db.query(Challenge).filter(
        and_(
            Challenge.challenger_id == challenger_id,
            Challenge.created_at >= today
        )
    ).first()
    
    if existing_challenge:
        raise HTTPException(status_code=400, detail="You can only create one challenge per day")
    
    # Проверяем, что нет активного вызова между этими пользователями
    active_challenge = db.query(Challenge).filter(
        and_(
            Challenge.challenger_id == challenger_id,
            Challenge.challenged_id == challenged_user.id,
            Challenge.status.in_(["pending", "accepted"])
        )
    ).first()
    
    if active_challenge:
        raise HTTPException(status_code=400, detail="You already have an active challenge with this user")
    
    new_challenge = Challenge(
        challenger_id=challenger_id,
        challenged_id=challenged_user.id,
        status="pending"
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    
    return {"id": new_challenge.id, "message": "Challenge created successfully"}

@router.post("/challenges/{challenge_id}/accept")
def accept_challenge(challenge_id: int, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge.challenged_id != user_id:
        raise HTTPException(status_code=403, detail="You can only accept challenges sent to you")
    
    if challenge.status != "pending":
        raise HTTPException(status_code=400, detail="Challenge is not pending")
    
    challenge.status = "accepted"
    challenge.accepted_at = datetime.now()
    db.commit()
    
    return {"message": "Challenge accepted successfully"}

@router.post("/challenges/{challenge_id}/decline")
def decline_challenge(challenge_id: int, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge.challenged_id != user_id:
        raise HTTPException(status_code=403, detail="You can only decline challenges sent to you")
    
    if challenge.status != "pending":
        raise HTTPException(status_code=400, detail="Challenge is not pending")
    
    challenge.status = "declined"
    db.commit()
    
    return {"message": "Challenge declined successfully"}

@router.post("/challenges/{challenge_id}/result")
def submit_result(challenge_id: int, result: str, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    if result not in ["won", "lost"]:
        raise HTTPException(status_code=400, detail="Result must be 'won' or 'lost'")
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge.status != "accepted":
        raise HTTPException(status_code=400, detail="Challenge is not accepted")
    
    # Определяем, кто подает результат
    is_challenger = challenge.challenger_id == user_id
    is_challenged = challenge.challenged_id == user_id
    
    if not (is_challenger or is_challenged):
        raise HTTPException(status_code=403, detail="You are not part of this challenge")
    
    # Сохраняем результат
    if is_challenger:
        challenge.challenger_result = result
    else:
        challenge.challenged_result = result
    
    # Проверяем, оба ли игрока подали результаты
    if challenge.challenger_result and challenge.challenged_result:
        # Верифицируем результаты
        if challenge.challenger_result == challenge.challenged_result:
            raise HTTPException(status_code=400, detail="Both players cannot have the same result")
        
        # Определяем победителя и проигравшего
        if challenge.challenger_result == "won":
            winner_id = challenge.challenger_id
            loser_id = challenge.challenged_id
        else:
            winner_id = challenge.challenged_id
            loser_id = challenge.challenger_id
        
        # Создаем матч
        match = Match(
            player1_id=challenge.challenger_id,
            player2_id=challenge.challenged_id,
            winner_id=winner_id,
            loser_id=loser_id,
            score="21:19",  # TODO: Добавить ввод счета
            is_rated=True
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        
        # Обновляем рейтинги (Elo система)
        update_ratings(winner_id, loser_id, match.id, db)
        
        # Завершаем вызов
        challenge.status = "completed"
        challenge.completed_at = datetime.now()
        challenge.match_id = match.id
        db.commit()
    
    return {"message": "Result submitted successfully"}

def update_ratings(winner_id: int, loser_id: int, match_id: int, db: Session):
    """Обновляет рейтинги игроков по системе Elo"""
    winner = db.query(User).filter(User.id == winner_id).first()
    loser = db.query(User).filter(User.id == loser_id).first()
    
    if not winner or not loser:
        return
    
    # Простая реализация Elo (можно улучшить)
    K = 32  # Коэффициент изменения рейтинга
    expected_winner = 1 / (1 + 10 ** ((loser.rating - winner.rating) / 400))
    expected_loser = 1 - expected_winner
    
    # Сохраняем старые рейтинги
    winner_rating_before = winner.rating
    loser_rating_before = loser.rating
    
    # Обновляем рейтинги
    winner.rating += int(K * (1 - expected_winner))
    loser.rating += int(K * (0 - expected_loser))
    
    # Создаем записи в истории рейтинга
    winner_history = UserRatingHistory(
        user_id=winner_id,
        match_id=match_id,
        rating_before=winner_rating_before,
        rating_after=winner.rating,
        change=winner.rating - winner_rating_before
    )
    
    loser_history = UserRatingHistory(
        user_id=loser_id,
        match_id=match_id,
        rating_before=loser_rating_before,
        rating_after=loser.rating,
        change=loser.rating - loser_rating_before
    )
    
    db.add(winner_history)
    db.add(loser_history)
    db.commit()

@router.get("/challenges")
def get_challenges(db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    challenges = db.query(Challenge).filter(
        (Challenge.challenger_id == user_id) | (Challenge.challenged_id == user_id)
    ).order_by(Challenge.created_at.desc()).all()
    
    result = []
    for challenge in challenges:
        challenger = db.query(User).filter(User.id == challenge.challenger_id).first()
        challenged = db.query(User).filter(User.id == challenge.challenged_id).first()
        
        result.append({
            "id": challenge.id,
            "challenger_username": challenger.username if challenger else "Unknown",
            "challenged_username": challenged.username if challenged else "Unknown",
            "status": challenge.status,
            "created_at": challenge.created_at,
            "is_challenger": challenge.challenger_id == user_id
        })
    
    return result 
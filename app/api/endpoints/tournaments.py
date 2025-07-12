from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Tournament, TournamentParticipant, User, Location, Match
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random

router = APIRouter()

class TournamentCreate(BaseModel):
    title: str
    spot_id: int
    datetime: datetime
    description: Optional[str] = None

class TournamentResponse(BaseModel):
    id: int
    title: str
    spot_id: int
    datetime: datetime
    description: Optional[str]
    status: str
    created_at: datetime
    participants_count: int

def is_admin(db: Session, user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    user = db.query(User).filter(User.id == user_id).first()
    return user and user.is_admin

@router.post("/tournaments")
def create_tournament(tournament: TournamentCreate, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    # Проверяем права администратора
    if not is_admin(db, user_id):
        raise HTTPException(status_code=403, detail="Only administrators can create tournaments")
    
    # Проверяем, что спот существует
    spot = db.query(Location).filter(Location.id == tournament.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    new_tournament = Tournament(
        title=tournament.title,
        spot_id=tournament.spot_id,
        datetime=tournament.datetime,
        description=tournament.description,
        created_by=user_id,
        status="open"
    )
    db.add(new_tournament)
    db.commit()
    db.refresh(new_tournament)
    
    return {"id": new_tournament.id, "message": "Tournament created successfully"}

@router.get("/tournaments")
def get_tournaments(db: Session = Depends(get_db)):
    tournaments = db.query(Tournament).order_by(Tournament.created_at.desc()).all()
    result = []
    
    for tournament in tournaments:
        participants_count = db.query(TournamentParticipant).filter(
            TournamentParticipant.tournament_id == tournament.id
        ).count()
        
        result.append({
            "id": tournament.id,
            "title": tournament.title,
            "spot_id": tournament.spot_id,
            "datetime": tournament.datetime,
            "description": tournament.description,
            "status": tournament.status,
            "created_at": tournament.created_at,
            "participants_count": participants_count
        })
    
    return result

@router.post("/tournaments/{tournament_id}/join")
def join_tournament(tournament_id: int, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    if tournament.status != "open":
        raise HTTPException(status_code=400, detail="Tournament is not open for registration")
    
    # Проверяем, что пользователь еще не зарегистрирован
    existing_participant = db.query(TournamentParticipant).filter(
        TournamentParticipant.tournament_id == tournament_id,
        TournamentParticipant.user_id == user_id
    ).first()
    
    if existing_participant:
        raise HTTPException(status_code=400, detail="Already registered for this tournament")
    
    participant = TournamentParticipant(
        tournament_id=tournament_id,
        user_id=user_id
    )
    db.add(participant)
    db.commit()
    
    return {"message": "Successfully joined tournament"}

@router.post("/tournaments/{tournament_id}/start")
def start_tournament(tournament_id: int, db: Session = Depends(get_db)):
    # TODO: Получить user_id из JWT токена
    user_id = 1  # Временно используем фиксированный ID
    
    # Проверяем права администратора
    if not is_admin(db, user_id):
        raise HTTPException(status_code=403, detail="Only administrators can start tournaments")
    
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    if tournament.status != "open":
        raise HTTPException(status_code=400, detail="Tournament is not open")
    
    participants = db.query(TournamentParticipant).filter(
        TournamentParticipant.tournament_id == tournament_id
    ).all()
    
    if len(participants) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 participants to start tournament")
    
    # Генерируем сетку (single elimination)
    generate_tournament_bracket(tournament_id, participants, db)
    
    # Обновляем статус турнира
    tournament.status = "started"
    db.commit()
    
    return {"message": "Tournament started successfully"}

def generate_tournament_bracket(tournament_id: int, participants: List[TournamentParticipant], db: Session):
    """Генерирует сетку турнира (single elimination)"""
    user_ids = [p.user_id for p in participants]
    
    # Перемешиваем участников
    random.shuffle(user_ids)
    
    # Создаем матчи для первого раунда
    for i in range(0, len(user_ids), 2):
        if i + 1 < len(user_ids):
            match = Match(
                player1_id=user_ids[i],
                player2_id=user_ids[i + 1],
                tournament_id=tournament_id,
                is_rated=False  # Турнирные матчи не влияют на рейтинг
            )
            db.add(match)
    
    db.commit() 
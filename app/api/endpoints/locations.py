from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import logging
import uuid

from app.database.database import get_db
from app.database.models import Location, Rating, User, Photo
from pydantic import BaseModel
from app.schemas.location import LocationCreate, LocationResponse, PhotoResponse

router = APIRouter()

class LocationBase(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    tables_count: int = 1
    net_type: str = "нет"
    has_roof: bool = False

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    user_id: int
    created_at: str
    author: dict
    photos: List[dict]
    average_rating: float = 0.0
    ratings_count: int = 0

    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    score: int
    comment: str = None

class RatingResponse(BaseModel):
    id: int
    score: int
    comment: str = None
    created_at: str
    user: dict

    class Config:
        from_attributes = True

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(
    db: Session = Depends(get_db),
    has_roof: bool = None,
    net_type: str = None
):
    query = db.query(Location)
    
    if has_roof is not None:
        query = query.filter(Location.has_roof == has_roof)
    if net_type:
        query = query.filter(Location.net_type == net_type)
    
    locations = query.all()
    
    # Convert locations to response model with proper datetime serialization
    response_locations = []
    for loc in locations:
        # Get author information
        author = db.query(User).filter(User.id == loc.user_id).first()
        author_info = {
            "id": author.id,
            "username": author.username,
            "telegram_id": author.telegram_id
        } if author else None
        
        # Convert photos to response model
        photos = []
        for photo in loc.photos:
            photo_dict = {
                "id": photo.id,
                "url": f"/static/photos/{photo.file_path}",
                "location_id": photo.location_id
            }
            photos.append(photo_dict)
        
        # Create location response with proper datetime serialization
        response_locations.append(LocationResponse(
            id=loc.id,
            name=loc.name,
            description=loc.description,
            latitude=loc.latitude,
            longitude=loc.longitude,
            has_roof=loc.has_roof,
            net_type=loc.net_type,
            created_at=loc.created_at.isoformat() if loc.created_at else datetime.now().isoformat(),
            user_id=loc.user_id,
            author=author_info,
            photos=photos
        ))
    
    return response_locations

@router.get("/locations/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get author information
    author = db.query(User).filter(User.id == location.user_id).first()
    author_info = {
        "id": author.id,
        "username": author.username,
        "telegram_id": author.telegram_id
    } if author else None
    
    # Convert photos to response model
    photos = []
    for photo in location.photos:
        photo_dict = {
            "id": photo.id,
            "url": f"/static/photos/{photo.file_path}",
            "location_id": photo.location_id
        }
        photos.append(photo_dict)
    
    # Create location response with proper datetime serialization
    return LocationResponse(
        id=location.id,
        name=location.name,
        description=location.description,
        latitude=location.latitude,
        longitude=location.longitude,
        has_roof=location.has_roof,
        net_type=location.net_type,
        created_at=location.created_at.isoformat() if location.created_at else datetime.now().isoformat(),
        user_id=location.user_id,
        author=author_info,
        photos=photos
    )

@router.post("/locations/{location_id}/ratings", response_model=RatingResponse)
def create_rating(
    location_id: int,
    rating: RatingCreate,
    db: Session = Depends(get_db)
):
    # В реальном приложении здесь должна быть аутентификация пользователя
    # Для демонстрации используем первого пользователя
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Проверяем, что оценка в диапазоне 1-5
    if not 1 <= rating.score <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # Проверяем, не оставлял ли пользователь уже оценку
    existing_rating = db.query(Rating).filter(
        Rating.user_id == user.id,
        Rating.location_id == location_id
    ).first()

    if existing_rating:
        # Обновляем существующую оценку
        existing_rating.score = rating.score
        existing_rating.comment = rating.comment
        db.commit()
        db.refresh(existing_rating)
        return existing_rating

    # Создаем новую оценку
    new_rating = Rating(
        user_id=user.id,
        location_id=location_id,
        score=rating.score,
        comment=rating.comment
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@router.get("/locations/{location_id}/ratings", response_model=List[RatingResponse])
def get_location_ratings(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location.ratings

@router.post("/locations", response_model=LocationResponse)
def create_location(
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    tables_count: str = Form("1"),
    net_type: str = Form(...),
    has_roof: str = Form("false"),
    photos: List[UploadFile] = File([])
):
    import logging
    logging.warning(f"has_roof={has_roof}, tables_count={tables_count}, photos={[f.filename for f in photos]}")
    # Для демонстрации используем первого пользователя
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        tables_count_int = int(tables_count)
        if tables_count_int < 1:
            tables_count_int = 1
    except Exception:
        tables_count_int = 1
    has_roof_bool = has_roof.lower() == "true"

    location = Location(
        name=name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        tables_count=tables_count_int,
        net_type=net_type,
        has_roof=has_roof_bool,
        user_id=user.id
    )
    db.add(location)
    db.commit()
    db.refresh(location)

    # Сохраняем фотографии
    static_dir = os.path.join(os.path.dirname(__file__), '../../static/photos')
    os.makedirs(static_dir, exist_ok=True)
    for file in photos:
        if not file.filename:
            continue
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{location.id}_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(static_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        photo_obj = Photo(file_path=unique_name, location_id=location.id)
        db.add(photo_obj)
    db.commit()
    db.refresh(location)

    # Формируем ответ
    author = db.query(User).filter(User.id == location.user_id).first()
    author_info = {
        "id": author.id,
        "username": author.username,
        "telegram_id": author.telegram_id
    } if author else None
    photos_response = [
        {"id": p.id, "url": f"/static/photos/{p.file_path}", "location_id": p.location_id}
        for p in location.photos
    ]
    return LocationResponse(
        id=location.id,
        name=location.name,
        description=location.description,
        latitude=location.latitude,
        longitude=location.longitude,
        has_roof=location.has_roof,
        net_type=location.net_type,
        created_at=location.created_at.isoformat() if location.created_at else datetime.now().isoformat(),
        user_id=location.user_id,
        author=author_info,
        photos=photos_response
    ) 
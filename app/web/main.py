from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, Location, Photo
import os
from dotenv import load_dotenv
import shutil
from typing import List
import uuid

load_dotenv()

app = FastAPI(title="Table Tennis Spots Map")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем директории для статических файлов и фотографий
os.makedirs("app/web/static", exist_ok=True)
os.makedirs("app/web/static/photos", exist_ok=True)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/web/templates/index.html") as f:
        return f.read()

@app.get("/api/spots")
async def get_spots(db: Session = Depends(get_db)):
    spots = db.query(Location).all()
    return spots

@app.post("/api/spots")
async def create_spot(
    name: str,
    description: str,
    latitude: float,
    longitude: float,
    user_id: int,
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Создаем новую локацию
    new_spot = Location(
        latitude=latitude,
        longitude=longitude,
        name=name,
        description=description,
        user_id=user_id
    )
    
    db.add(new_spot)
    db.commit()
    db.refresh(new_spot)
    
    # Сохраняем фотографии
    if photos:
        for photo in photos:
            # Генерируем уникальное имя файла
            file_extension = os.path.splitext(photo.filename)[1]
            file_name = f"{uuid.uuid4()}{file_extension}"
            file_path = f"photos/{file_name}"
            
            # Сохраняем файл
            with open(f"app/web/static/{file_path}", "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            
            # Создаем запись в базе данных
            new_photo = Photo(
                location_id=new_spot.id,
                file_path=file_path
            )
            db.add(new_photo)
    
    db.commit()
    return new_spot 
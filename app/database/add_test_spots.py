import os
import random
from app.database.database import SessionLocal
from app.database.models import Location, Photo

# Координаты и данные для тестовых точек
spots = [
    {
        "name": "Парк Горького",
        "description": "Стол для настольного тенниса у главного входа.",
        "latitude": 55.729876,
        "longitude": 37.603456,
        "user_id": 1,
        "tables_count": 2,
        "net_type": "металлическая",
        "has_roof": True
    },
    {
        "name": "Сокольники",
        "description": "Несколько столов рядом с прудом.",
        "latitude": 55.794229,
        "longitude": 37.678234,
        "user_id": 1,
        "tables_count": 3,
        "net_type": "нормальная",
        "has_roof": False
    },
    {
        "name": "ВДНХ",
        "description": "Стол около павильона №1.",
        "latitude": 55.829953,
        "longitude": 37.633099,
        "user_id": 1,
        "tables_count": 1,
        "net_type": "металлическая",
        "has_roof": True
    },
    {
        "name": "Парк Победы",
        "description": "Стол для тенниса у фонтана.",
        "latitude": 55.736667,
        "longitude": 37.512222,
        "user_id": 1,
        "tables_count": 2,
        "net_type": "нет сетки",
        "has_roof": False
    },
    {
        "name": "Измайловский парк",
        "description": "Стол в глубине парка, рядом с детской площадкой.",
        "latitude": 55.789444,
        "longitude": 37.781111,
        "user_id": 1,
        "tables_count": 1,
        "net_type": "нормальная",
        "has_roof": False
    }
]

PHOTOS_DIR = os.path.join(os.path.dirname(__file__), '../static/photos')


def add_spots():
    db = SessionLocal()
    # Удаляем все фото и точки
    db.query(Photo).delete()
    db.query(Location).delete()
    db.commit()

    # Получаем все фото из папки
    all_photos = [f for f in os.listdir(PHOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(all_photos)

    # Рандомно распределяем фото по точкам
    photos_per_spot = max(1, len(all_photos) // len(spots))
    photo_chunks = [all_photos[i*photos_per_spot:(i+1)*photos_per_spot] for i in range(len(spots))]
    # Если фото осталось, добавим их к первым точкам
    leftovers = all_photos[len(spots)*photos_per_spot:]
    for i, photo in enumerate(leftovers):
        photo_chunks[i % len(spots)].append(photo)

    for i, spot in enumerate(spots):
        location = Location(**spot)
        db.add(location)
        db.flush()  # Получаем ID локации
        for photo_file in photo_chunks[i]:
            photo = Photo(location_id=location.id, file_path=photo_file)
            db.add(photo)
    db.commit()
    db.close()

if __name__ == "__main__":
    add_spots()
    print("Тестовые точки пересозданы и фото раскиданы!") 
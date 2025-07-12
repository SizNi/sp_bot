from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import locations
from app.api.endpoints import auth
from app.api.endpoints import tournaments
from app.api.endpoints import challenges

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(locations.router, prefix="/api", tags=["locations"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(tournaments.router, prefix="/api", tags=["tournaments"])
app.include_router(challenges.router, prefix="/api", tags=["challenges"]) 
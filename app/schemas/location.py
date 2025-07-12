from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PhotoResponse(BaseModel):
    id: int
    url: str
    location_id: int

    class Config:
        from_attributes = True

class AuthorResponse(BaseModel):
    id: int
    username: str
    telegram_id: int

    class Config:
        from_attributes = True

class LocationBase(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    has_roof: bool
    net_type: str

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    created_at: str
    user_id: int
    author: Optional[AuthorResponse]
    photos: List[PhotoResponse]

    class Config:
        from_attributes = True 
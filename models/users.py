from pydantic import BaseModel, EmailStr
from typing import List, Optional
from models.songs import Song

class User(BaseModel):
    email: EmailStr
    password: str
    learned_songs: List[int] = []
    favorite_songs: List[int] = []
    current_language: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "securepassword123",
                "learned_songs": [1, 2],
                "favorite_songs": [1],
                "current_language": "en"
            }
        }

class UserSignIn(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "securepassword123"
            }
        }
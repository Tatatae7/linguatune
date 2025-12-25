from sqlmodel import SQLModel, Field, Column
from typing import Optional, List
from sqlalchemy import JSON
from pydantic import BaseModel

# ========== МОДЕЛЬ ДЛЯ БАЗЫ ДАННЫХ ==========
class User(SQLModel, table=True):
    """Модель пользователя для базы данных"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    current_language: Optional[str] = None
    
    # ВАЖНО: Указываем sa_column с JSON для SQLite
    learned_songs: List[int] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )


    class Config:
        arbitrary_types_allowed = True

# ========== МОДЕЛИ ДЛЯ ЗАПРОСОВ ==========
class UserCreate(BaseModel):
    """Модель для регистрации (только email и пароль)"""
    email: str
    password: str

class UserSignIn(BaseModel):
    """Модель для входа"""
    email: str
    password: str

class UserUpdate(BaseModel):
    """Модель для обновления профиля"""
    full_name: Optional[str] = None
    username: Optional[str] = None
    current_language: Optional[str] = None
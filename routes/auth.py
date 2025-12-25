from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from database.connection import get_session
from models.users import User
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

auth_router = APIRouter(
    tags=["Аутентификация"],
    responses={404: {"description": "Не найдено"}}
)

class UserSignIn(BaseModel):
    email: str
    password: str

class UserUpdateModel(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    current_language: Optional[str] = None

class PasswordChangeModel(BaseModel):
    current_password: str
    new_password: str

# ========== ЭНДПОИНТЫ ==========
@auth_router.post("/signup")
async def sign_new_user(
    user_data: User, 
    session: Session = Depends(get_session)
) -> dict:
    """Регистрация нового пользователя через API"""
    
    # Проверяем существование пользователя
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    new_user = User(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        username=user_data.username,
        current_language=user_data.current_language,
        learned_songs=user_data.learned_songs or [],
        favorite_songs=user_data.favorite_songs or []
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {
        "message": "Пользователь успешно зарегистрирован!",
        "email": new_user.email,
        "user_id": new_user.id
    }

@auth_router.post("/signin")
async def sign_user_in(
    user: UserSignIn,
    session: Session = Depends(get_session)
) -> dict:
    """Вход пользователя через API"""
    
    # Ищем пользователя
    db_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if db_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )
    
    return {
        "message": "Успешный вход в систему",
        "email": db_user.email,
        "user_id": db_user.id,
        "full_name": db_user.full_name,
        "username": db_user.username
    }

@auth_router.post("/password/change")
async def change_password(
    email: str,
    password_data: PasswordChangeModel,
    session: Session = Depends(get_session)
) -> dict:
    """Смена пароля через API"""
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Проверяем текущий пароль
    if user.password != password_data.current_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный текущий пароль"
        )
    
    # Проверяем длину нового пароля
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен содержать минимум 6 символов"
        )
    
    # Меняем пароль
    user.password = password_data.new_password
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "success": True,
        "message": "Пароль успешно изменен",
        "email": email
    }

@auth_router.get("/user/{email}")
async def get_user_info(
    email: str,
    session: Session = Depends(get_session)
) -> dict:
    """Получение информации о пользователе через API"""
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return {
        "email": user.email,
        "full_name": user.full_name,
        "username": user.username,
        "current_language": user.current_language,
        "learned_songs": user.learned_songs or [],
        "favorite_songs": user.favorite_songs or [],
        "user_id": user.id
    }

@auth_router.put("/user/{email}")
async def update_user_info(
    email: str, 
    user_data: UserUpdateModel,
    session: Session = Depends(get_session)
) -> dict:
    """Обновление информации о пользователе через API"""
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем только переданные поля
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.current_language is not None:
        user.current_language = user_data.current_language
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "success": True,
        "message": "Информация пользователя обновлена",
        "email": email,
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "current_language": user.current_language
        }
    }
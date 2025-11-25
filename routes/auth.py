from fastapi import APIRouter, HTTPException, status
from models.users import User, UserSignIn

auth_router = APIRouter(
    tags=["Аутентификация"],
    responses={404: {"description": "Не найдено"}}
)

users_db = {}

@auth_router.post("/signup")
async def sign_new_user(user_data: User) -> dict:
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )
    
    users_db[user_data.email] = user_data
    return {
        "message": "Пользователь успешно зарегистрирован!",
        "email": user_data.email
    }

@auth_router.post("/signin")
async def sign_user_in(user: UserSignIn) -> dict:
    if user.email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if users_db[user.email].password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )
    
    return {
        "message": "Успешный вход в систему",
        "email": user.email
    }
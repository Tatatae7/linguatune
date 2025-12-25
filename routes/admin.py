from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from database.connection import get_session
from pydantic import BaseModel
from typing import List, Optional

from models.users import User
from models.songs import Song
from models.languages import Language
from models.artists import Artist
from models.admins import Admin

admin_router = APIRouter(prefix="/admin", tags=["Администрирование"])

# ========== МОДЕЛИ ==========
class LanguageCreate(BaseModel):
    name: str
    code: str
    difficulty: str = "beginner"
    description: Optional[str] = None

class SongCreate(BaseModel):
    title: str
    artist: str
    language: str
    lyrics_original: str
    lyrics_translation: str
    difficulty: str = "intermediate"
    vocabulary: List[str] = []
    duration: int = 180
    genre: Optional[str] = None
    year: Optional[int] = None

class ArtistCreate(BaseModel):
    name: str
    country: str
    language: str
    genres: List[str] = []
    bio: str

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def is_admin(email: str, session: Session) -> bool:
    """Проверка, является ли пользователь админом"""
    admin = session.exec(
        select(Admin).where(Admin.user_email == email)
    ).first()
    return admin is not None

# ========== УПРАВЛЕНИЕ ЯЗЫКАМИ ==========
@admin_router.post("/language")
async def add_language(
    language_data: LanguageCreate,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Добавить новый язык"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    # Проверяем существование языка
    existing_language = session.exec(
        select(Language).where(
            (Language.code == language_data.code) | 
            (Language.name == language_data.name)
        )
    ).first()
    
    if existing_language:
        raise HTTPException(
            status_code=400,
            detail="Язык с таким кодом или названием уже существует"
        )
    
    # Создаем новый язык
    new_language = Language(**language_data.dict())
    session.add(new_language)
    session.commit()
    session.refresh(new_language)
    
    return {
        "success": True,
        "message": f"Язык '{language_data.name}' добавлен",
        "language": new_language
    }

@admin_router.delete("/language/{language_id}")
async def delete_language_admin(
    language_id: int,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Удалить язык"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    language = session.get(Language, language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Язык не найден")
    
    # Проверяем, есть ли песни на этом языке
    songs_on_language = session.exec(
        select(Song).where(Song.language == language.name)
    ).all()
    
    if songs_on_language:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Нельзя удалить язык. Есть {len(songs_on_language)} песен на языке '{language.name}'",
                "songs_count": len(songs_on_language),
                "songs": [song.title for song in songs_on_language[:5]]
            }
        )
    
    session.delete(language)
    session.commit()
    
    return {
        "success": True,
        "message": f"Язык '{language.name}' удален",
        "language_id": language_id
    }

# ========== УПРАВЛЕНИЕ ПЕСНЯМИ ==========
@admin_router.post("/song")
async def add_song(
    song_data: SongCreate,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Добавить новую песню"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    # Проверяем, существует ли уже песня с таким названием и исполнителем
    existing_song = session.exec(
        select(Song).where(
            (Song.title == song_data.title) & 
            (Song.artist == song_data.artist)
        )
    ).first()
    
    if existing_song:
        raise HTTPException(
            status_code=400,
            detail="Песня с таким названием и исполнителем уже существует"
        )
    
    # Создаем новую песню
    new_song = Song(**song_data.dict())
    session.add(new_song)
    session.commit()
    session.refresh(new_song)
    
    return {
        "success": True,
        "message": f"Песня '{song_data.title}' добавлена",
        "song": new_song
    }

@admin_router.delete("/song/{song_id}")
async def delete_song_admin(
    song_id: int,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Удалить песню"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Песня не найдена")
    
    # Удаляем песню из избранного и изученных у всех пользователей
    users = session.exec(select(User)).all()
    for user in users:
        if song_id in (user.learned_songs or []):
            user.learned_songs.remove(song_id)
        if song_id in (user.favorite_songs or []):
            user.favorite_songs.remove(song_id)
        session.add(user)
    
    session.delete(song)
    session.commit()
    
    return {
        "success": True,
        "message": f"Песня '{song.title}' удалена",
        "song_id": song_id
    }

@admin_router.put("/song/{song_id}")
async def update_song_admin(
    song_id: int,
    song_update: SongCreate,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Обновить песню"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Песня не найдена")
    
    # Обновляем поля
    update_data = song_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(song, field, value)
    
    session.add(song)
    session.commit()
    session.refresh(song)
    
    return {
        "success": True,
        "message": f"Песня '{song.title}' обновлена",
        "song": song
    }

# ========== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ==========
@admin_router.get("/users")
async def get_users(
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Получить список пользователей"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    users = session.exec(select(User)).all()
    
    users_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "current_language": user.current_language,
            "learned_songs_count": len(user.learned_songs) if user.learned_songs else 0,
            # УБИРАЕМ favorite_songs_count - этого поля больше нет
            "learned_songs": user.learned_songs or [],
            # УБИРАЕМ favorite_songs - этого поля больше нет
        }
        users_list.append(user_data)
    
    return {
        "success": True,
        "total_users": len(users_list),
        "users": users_list
    }
@admin_router.delete("/user/{user_id}")
async def delete_user_admin(
    user_id: int,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Удалить пользователя"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    session.delete(user)
    session.commit()
    
    return {
        "success": True,
        "message": f"Пользователь '{user.email}' удален",
        "user_id": user_id
    }

@admin_router.put("/user/{user_id}/admin")
async def make_user_admin(
    user_id: int,
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Сделать пользователя администратором"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем, не является ли уже администратором
    existing_admin = session.exec(
        select(Admin).where(Admin.user_email == user.email)
    ).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Пользователь уже является администратором"
        )
    
    # Создаем запись администратора
    new_admin = Admin(
        user_email=user.email,
        role="admin",
        permissions={
            "manage_users": True,
            "manage_content": True,
            "view_stats": True,
            "backup": True
        }
    )
    
    session.add(new_admin)
    session.commit()
    
    return {
        "success": True,
        "message": f"Пользователь '{user.email}' назначен администратором",
        "admin": new_admin
    }

# ========== СТАТИСТИКА ==========
@admin_router.get("/stats")
async def get_admin_stats(
    admin_email: str = Query(..., description="Email администратора"),
    session: Session = Depends(get_session)
):
    """Получить статистику системы"""
    
    if not is_admin(admin_email, session):
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    # Подсчеты
    total_users = session.exec(select(User)).count()
    total_songs = session.exec(select(Song)).count()
    total_artists = session.exec(select(Artist)).count()
    total_languages = session.exec(select(Language)).count()
    
    # Пользователи с прогрессом
    users_with_progress = 0
    total_learned_songs = 0
    
    users = session.exec(select(User)).all()
    for user in users:
        if user.learned_songs:
            users_with_progress += 1
            total_learned_songs += len(user.learned_songs)
    
    # Языки с количеством песен
    songs = session.exec(select(Song)).all()
    songs_by_language = {}
    for song in songs:
        lang = song.language
        songs_by_language[lang] = songs_by_language.get(lang, 0) + 1
    
    return {
        "success": True,
        "stats": {
            "users": {
                "total": total_users,
                "with_progress": users_with_progress,
                "progress_percentage": round((users_with_progress / total_users * 100), 2) if total_users > 0 else 0
            },
            "content": {
                "songs": total_songs,
                "artists": total_artists,
                "languages": total_languages
            },
            "learning": {
                "total_learned_songs": total_learned_songs,
                "average_songs_per_user": round(total_learned_songs / total_users, 2) if total_users > 0 else 0
            },
            "songs_by_language": songs_by_language
        }
    }
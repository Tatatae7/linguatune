from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from database.connection import get_session
import models
from models.songs import Song
from models.artists import Artist
from models.languages import Language
from typing import List

music_router = APIRouter(
    tags=["Музыка"],
    responses={404: {"description": "Не найдено"}}
)

@music_router.get("/songs")
async def get_all_songs(session: Session = Depends(get_session)):
    """Получить все песни"""
    songs = session.exec(select(Song)).all()
    return songs

@music_router.get("/songs/{language}")
async def get_songs_by_language(
    language: str,
    session: Session = Depends(get_session)
):
    """Получить песни по языку"""
    
    songs = session.exec(
        select(Song).where(Song.language.ilike(f"%{language}%"))
    ).all()
    
    if not songs:
        # Получаем все доступные языки
        all_songs = session.exec(select(Song)).all()
        available_languages = set(song.language for song in all_songs)
        
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Песни на языке '{language}' не найдены",
                "available_languages": list(available_languages)
            }
        )
    
    return songs
@music_router.post("/song")
async def create_song(
    song: Song,
    session: Session = Depends(get_session)
):
    """Создать новую песню"""
    
    # Проверяем, не существует ли уже песня с таким названием и исполнителем
    existing = session.exec(
        select(Song).where(
            (Song.title == song.title) & 
            (Song.artist == song.artist)
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Песня с таким названием и исполнителем уже существует"
        )
    
    session.add(song)
    session.commit()
    session.refresh(song)
    
    return {
        "message": "Песня успешно создана",
        "song": song
    }

@music_router.put("/song/{song_id}")
async def update_song(
    song_id: int,
    song_update: Song,
    session: Session = Depends(get_session)
):
    """Обновить песню"""
    
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(
            status_code=404,
            detail=f"Песня с ID {song_id} не найдена"
        )
    
    # Обновляем поля
    update_data = song_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(song, field, value)
    
    session.add(song)
    session.commit()
    session.refresh(song)
    
    return {
        "message": "Песня успешно обновлена",
        "song": song
    }

@music_router.delete("/song/{song_id}")
async def delete_song(
    song_id: int,
    session: Session = Depends(get_session)
):
    """Удалить песню"""
    
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(
            status_code=404,
            detail=f"Песня с ID {song_id} не найдена"
        )
    
    # Удаляем песню из избранного у всех пользователей
    from models.users import User
    users = session.exec(select(User)).all()
    for user in users:
        if song_id in (user.favorite_songs or []):
            user.favorite_songs.remove(song_id)
        if song_id in (user.learned_songs or []):
            user.learned_songs.remove(song_id)
        session.add(user)
    
    session.delete(song)
    session.commit()
    
    return {
        "message": f"Песня '{song.title}' успешно удалена"
    }
@music_router.get("/songs/{language}")
async def get_songs_by_language(
    language: str,
    session: Session = Depends(get_session)
):
    """Получить песни по языку"""
    
    print(f"🔍 Поиск песен на языке: '{language}'")
    
    # Получаем все песни
    all_songs = session.exec(select(Song)).all()
    print(f"Всего песен в базе: {len(all_songs)}")
    
    # Фильтруем песни по языку
    # Приводим к нижнему регистру для case-insensitive поиска
    language_lower = language.strip().lower()
    
    filtered_songs = []
    for song in all_songs:
        if song.language and song.language.lower() == language_lower:
            filtered_songs.append(song)
        # Также проверяем по коду языка (если нужно)
        elif song.language and song.language.lower().startswith(language_lower):
            filtered_songs.append(song)
    
    print(f"Найдено песен: {len(filtered_songs)}")
    
    if not filtered_songs:
        # Получаем уникальные языки из всех песен
        unique_languages = set()
        for song in all_songs:
            if song.language:
                unique_languages.add(song.language.lower())
        
        print(f"Доступные языки: {sorted(unique_languages)}")
        
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Песни на языке '{language}' не найдены",
                "available_languages": sorted(list(unique_languages)),
                "total_songs": len(all_songs)
            }
        )
    
    return filtered_songs
@music_router.get("/artists")
async def get_all_artists(session: Session = Depends(get_session)):
    """Получить всех исполнителей"""
    artists = session.exec(select(Artist)).all()
    return artists
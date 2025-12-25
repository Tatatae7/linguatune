from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database.connection import get_session
from models.users import User
from models.songs import Song

progress_router = APIRouter(
    tags=["Прогресс обучения"],
    responses={404: {"description": "Не найдено"}}
)

# ========== ИЗУЧЕНИЕ ПЕСЕН ==========
@progress_router.post("/user/{email}/learned/{song_id}")
async def mark_song_learned(
    email: str,
    song_id: int,
    session: Session = Depends(get_session)
):
    """Отметить песню как изученную"""
    
    print(f"🔍 Отмечаем песню {song_id} для {email}")
    
    # 1. Находим пользователя
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        print(f"❌ Пользователь {email} не найден")
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с email {email} не найден"
        )
    
    print(f"✅ Пользователь найден: {email}")
    print(f"📊 Текущие изученные песни: {user.learned_songs}")
    
    # 2. Находим песню
    song = session.get(Song, song_id)
    
    if not song:
        all_songs = session.exec(select(Song)).all()
        available_ids = [s.id for s in all_songs if s.id is not None]
        
        print(f"❌ Песня {song_id} не найдена")
        print(f"ℹ️ Доступные ID: {available_ids}")
        
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Песня с ID {song_id} не найдена",
                "available_ids": available_ids
            }
        )
    
    print(f"✅ Песня найдена: '{song.title}' (ID: {song.id})")
    
    # 3. Работаем с learned_songs
    # Создаем копию текущего списка или новый список
    current_list = []
    if user.learned_songs:
        # Если learned_songs это список, используем его
        if isinstance(user.learned_songs, list):
            current_list = user.learned_songs.copy()
        # Если это строка JSON, парсим
        elif isinstance(user.learned_songs, str):
            try:
                import json
                current_list = json.loads(user.learned_songs)
            except:
                current_list = []
    
    print(f"📊 Список после обработки: {current_list}")
    
    # 4. Проверяем, не изучена ли уже песня
    if song_id in current_list:
        print(f"ℹ️ Песня уже изучена")
        return {
            "status": "already_learned",
            "message": f"Песня '{song.title}' уже изучена",
            "email": email,
            "song_id": song_id,
            "song_title": song.title,
            "total_learned": len(current_list)
        }
    
    # 5. Добавляем песню
    current_list.append(song_id)
    user.learned_songs = current_list  # Присваиваем новый список
    
    print(f"📊 Новый список для сохранения: {user.learned_songs}")
    
    # 6. Сохраняем
    try:
        session.add(user)
        session.commit()
        print(f"💾 Сохранено в БД")
        
        # Обновляем объект
        session.refresh(user)
        print(f"🔄 Объект обновлен")
        
        # Проверяем, что сохранилось
        print(f"📊 После refresh: {user.learned_songs}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении: {str(e)}"
        )
    
    return {
        "status": "success",
        "message": f"Песня '{song.title}' отмечена как изученная",
        "email": email,
        "song_id": song_id,
        "song_title": song.title,
        "artist": song.artist,
        "language": song.language,
        "total_learned": len(user.learned_songs),
        "learned_songs": user.learned_songs  # Показываем текущий список
    }

@progress_router.delete("/user/{email}/learned/{song_id}")
async def unmark_song_learned(
    email: str,
    song_id: int,
    session: Session = Depends(get_session)
):
    """Убрать отметку 'изучено' с песни"""
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с email {email} не найден"
        )
    
    # Работаем со списком
    current_list = []
    if user.learned_songs:
        if isinstance(user.learned_songs, list):
            current_list = user.learned_songs.copy()
        elif isinstance(user.learned_songs, str):
            try:
                import json
                current_list = json.loads(user.learned_songs)
            except:
                current_list = []
    
    if song_id not in current_list:
        raise HTTPException(
            status_code=400,
            detail=f"Песня с ID {song_id} не была изучена"
        )
    
    current_list.remove(song_id)
    user.learned_songs = current_list
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "status": "success",
        "message": f"Песня удалена из изученных",
        "email": email,
        "song_id": song_id,
        "total_learned": len(user.learned_songs)
    }

@progress_router.get("/user/{email}")
async def get_user_progress(
    email: str,
    session: Session = Depends(get_session)
):
    """Получить прогресс пользователя"""
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с email {email} не найден"
        )
    
    # Получаем изученные песни
    learned_songs_details = []
    languages_learned = set()
    
    # Обрабатываем список изученных песен
    learned_song_ids = []
    if user.learned_songs:
        if isinstance(user.learned_songs, list):
            learned_song_ids = user.learned_songs
        elif isinstance(user.learned_songs, str):
            try:
                import json
                learned_song_ids = json.loads(user.learned_songs)
            except:
                learned_song_ids = []
    
    # Получаем детали песен
    for song_id in learned_song_ids:
        song = session.get(Song, song_id)
        if song:
            learned_songs_details.append({
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "language": song.language,
                "difficulty": song.difficulty,
                "duration": song.duration
            })
            languages_learned.add(song.language)
    
    # Общая статистика
    all_songs = session.exec(select(Song)).all()
    total_songs = len(all_songs)
    
    learned_count = len(learned_song_ids)
    percentage = round((learned_count / total_songs * 100), 2) if total_songs > 0 else 0
    
    return {
        "email": user.email,
        "full_name": user.full_name,
        "username": user.username,
        "current_language": user.current_language,
        "progress": {
            "learned_songs": {
                "count": learned_count,
                "songs": learned_songs_details,
                "percentage": percentage
            },
            "languages_learned": {
                "count": len(languages_learned),
                "languages": list(languages_learned)
            }
        },
        "stats": {
            "total_songs_available": total_songs,
            "user_id": user.id,
            "learned_song_ids": learned_song_ids  # Для отладки
        }
    }

@progress_router.get("/user/{email}/learned")
async def get_user_learned_songs(
    email: str,
    session: Session = Depends(get_session)
):
    """Получить изученные песни пользователя"""
    
    user = session.exec(
        select(User).where(User.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с email {email} не найден"
        )
    
    learned_songs = []
    
    # Получаем список ID изученных песен
    learned_song_ids = []
    if user.learned_songs:
        if isinstance(user.learned_songs, list):
            learned_song_ids = user.learned_songs
        elif isinstance(user.learned_songs, str):
            try:
                import json
                learned_song_ids = json.loads(user.learned_songs)
            except:
                learned_song_ids = []
    
    # Получаем песни
    for song_id in learned_song_ids:
        song = session.get(Song, song_id)
        if song:
            learned_songs.append(song)
    
    return {
        "email": email,
        "count": len(learned_songs),
        "learned_song_ids": learned_song_ids,  # Для отладки
        "songs": learned_songs
    }

# ========== СТАТИСТИКА ==========
@progress_router.get("/stats/overall")
async def get_overall_progress_stats(session: Session = Depends(get_session)):
    """Статистика прогресса всех пользователей"""
    
    users = session.exec(select(User)).all()
    songs = session.exec(select(Song)).all()
    
    total_users = len(users)
    total_songs = len(songs)
    
    total_learned = 0
    users_with_progress = 0
    
    for user in users:
        # Считаем изученные песни
        learned_count = 0
        if user.learned_songs:
            if isinstance(user.learned_songs, list):
                learned_count = len(user.learned_songs)
            elif isinstance(user.learned_songs, str):
                try:
                    import json
                    learned_list = json.loads(user.learned_songs)
                    learned_count = len(learned_list) if isinstance(learned_list, list) else 0
                except:
                    learned_count = 0
        
        total_learned += learned_count
        if learned_count > 0:
            users_with_progress += 1
    
    return {
        "total_users": total_users,
        "total_songs": total_songs,
        "users_with_progress": users_with_progress,
        "total_songs_learned": total_learned,
        "average_songs_per_user": round(total_learned / total_users, 2) if total_users > 0 else 0,
        "progress_rate": round((users_with_progress / total_users * 100), 2) if total_users > 0 else 0
    }
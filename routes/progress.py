from fastapi import APIRouter, HTTPException
from typing import Dict, List
from routes.music import songs_data

progress_router = APIRouter(
    tags=["Прогресс обучения"],
    responses={404: {"description": "Не найдено"}}
)

user_progress: Dict[str, Dict] = {}

@progress_router.post("/user/{email}/learned/{song_id}")
async def mark_song_learned(email: str, song_id: int):
    if email not in user_progress:
        user_progress[email] = {
            "learned_songs": [],
            "learned_words": []
        }
    
    if song_id not in user_progress[email]["learned_songs"]:
        user_progress[email]["learned_songs"].append(song_id)
        
        song = next((s for s in songs_data if s.id == song_id), None)
        if song:
            for word in song.vocabulary:
                if word not in user_progress[email]["learned_words"]:
                    user_progress[email]["learned_words"].append(word)
    
    return {
        "message": f"Песня {song_id} отмечена как изученная",
        "email": email
    }

@progress_router.get("/user/{email}")
async def get_user_progress(email: str):
    if email not in user_progress:
        return {
            "learned_songs": [],
            "learned_words": [],
            "stats": {
                "songs_learned": 0,
                "words_learned": 0,
                "languages_learned": 0,
                "completion_percentage": 0
            }
        }
    
    learned_songs = user_progress[email]["learned_songs"]
    learned_words = user_progress[email]["learned_words"]
    
    languages_learned = set()
    for song_id in learned_songs:
        song = next((s for s in songs_data if s.id == song_id), None)
        if song:
            languages_learned.add(song.language)
    
    total_songs = len(songs_data)
    completion_percentage = (len(learned_songs) / total_songs) * 100 if total_songs > 0 else 0
    
    return {
        "learned_songs": learned_songs,
        "learned_words": learned_words,
        "stats": {
            "songs_learned": len(learned_songs),
            "words_learned": len(learned_words),
            "languages_learned": len(languages_learned),
            "completion_percentage": round(completion_percentage, 1)
        }
    }
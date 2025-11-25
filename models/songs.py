from pydantic import BaseModel
from typing import List, Optional

class Song(BaseModel):
    id: int
    title: str
    artist: str
    language: str
    lyrics_original: str
    lyrics_translation: str
    difficulty: str
    vocabulary: List[str]
    duration: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Yesterday",
                "artist": "The Beatles",
                "language": "en",
                "lyrics_original": "Yesterday, all my troubles seemed so far away...",
                "lyrics_translation": "Вчера все мои проблемы казались такими далекими...",
                "difficulty": "beginner",
                "vocabulary": ["yesterday", "troubles", "far away", "believe"],
                "duration": 125
            }
        }
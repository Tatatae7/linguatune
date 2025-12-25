from sqlmodel import SQLModel, Field, Column
from typing import List, Optional
from sqlalchemy import JSON

class SongBase(SQLModel):
    title: str
    artist: str
    language: str
    lyrics_original: str
    lyrics_translation: str
    difficulty: str
    vocabulary: List[str] = []
    duration: int

class Song(SongBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    artist: str = Field(index=True)
    language: str = Field(index=True)
    lyrics_original: str
    lyrics_translation: str
    difficulty: str = Field(default="intermediate")
    
    vocabulary: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )
    
    duration: int = Field(default=180)
    genre: Optional[str] = None
    year: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True
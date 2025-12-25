from sqlmodel import SQLModel, Field, Column
from typing import List, Optional
from sqlalchemy import JSON

class ArtistBase(SQLModel):
    name: str
    country: str
    language: str
    genres: List[str] = []
    bio: str

class Artist(ArtistBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    country: str
    language: str = Field(index=True)
    
    genres: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )
    
    bio: str
    
    class Config:
        arbitrary_types_allowed = True
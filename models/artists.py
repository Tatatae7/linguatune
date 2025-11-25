from pydantic import BaseModel
from typing import List

class Artist(BaseModel):
    id: int
    name: str
    country: str
    language: str
    genres: List[str]
    bio: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "The Beatles",
                "country": "Великобритания",
                "language": "en",
                "genres": ["rock", "pop"],
                "bio": "Легендарная британская рок-группа"
            }
        }
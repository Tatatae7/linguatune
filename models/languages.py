from pydantic import BaseModel
from typing import List, Optional

class Language(BaseModel):
    id: int
    name: str
    code: str
    difficulty: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Английский",
                "code": "en", 
                "difficulty": "beginner"
            }
        }
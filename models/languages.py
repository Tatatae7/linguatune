from sqlmodel import SQLModel, Field
from typing import Optional

class LanguageBase(SQLModel):
    name: str
    code: str
    difficulty: str

class Language(LanguageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    code: str = Field(unique=True, index=True)
    difficulty: str = Field(default="beginner")
    description: Optional[str] = None
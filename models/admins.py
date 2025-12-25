from sqlmodel import SQLModel, Field, Column
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy import JSON

class AdminBase(SQLModel):
    user_email: str
    role: str
    permissions: Dict[str, bool]

class Admin(AdminBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(unique=True, index=True)
    role: str = Field(default="moderator")
    
    permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            "manage_users": True,
            "manage_content": True,
            "view_stats": True,
            "backup": False
        },
        sa_column=Column(JSON)
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
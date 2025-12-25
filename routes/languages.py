from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database.connection import get_session
from models.languages import Language

language_router = APIRouter(
    tags=["Языки"],
    responses={404: {"description": "Не найдено"}}
)

@language_router.get("/")
async def get_all_languages(session: Session = Depends(get_session)):
    """Получить все языки"""
    languages = session.exec(select(Language)).all()
    return languages

@language_router.get("/id/{language_id}")
async def get_language_by_id(
    language_id: int,
    session: Session = Depends(get_session)
):
    """Получить язык по ID"""
    language = session.get(Language, language_id)
    
    if not language:
        raise HTTPException(
            status_code=404,
            detail=f"Язык с ID {language_id} не найден"
        )
    
    return language
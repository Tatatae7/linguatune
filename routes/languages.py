from fastapi import APIRouter
from models.languages import Language

language_router = APIRouter(
    tags=["Языки"],
    responses={404: {"description": "Не найдено"}}
)

languages_data = [
    Language(id=1, name="Английский", code="en", difficulty="beginner"),
    Language(id=2, name="Корейский", code="ko", difficulty="intermediate"), 
    Language(id=3, name="Французский", code="fr", difficulty="intermediate")
]

@language_router.get("/")
async def get_all_languages():
    return languages_data

@language_router.get("/{language_code}")
async def get_language_by_code(language_code: str):
    for lang in languages_data:
        if lang.code == language_code:
            return lang
    return {"error": "Язык не найден"}
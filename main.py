from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from routes.auth import auth_router, users_db
from routes.languages import language_router
from routes.music import music_router, songs_data
from routes.progress import progress_router, user_progress
import os

app = FastAPI(
    title="LinguaTune",
    description="Изучение языков через музыку 🎵🌍",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

current_user = None

app.include_router(auth_router, prefix="/api/auth")
app.include_router(language_router, prefix="/api/languages")
app.include_router(music_router, prefix="/api/music")
app.include_router(progress_router, prefix="/api/progress")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_email": current_user
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/auth/signup")
async def web_signup(request: Request, email: str, password: str):
    if email in users_db:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "message": "Пользователь с таким email уже существует",
            "message_type": "error"
        })
    
    from models.users import User
    users_db[email] = User(
        email=email,
        password=password,
        learned_songs=[],
        favorite_songs=[]
    )
    
    global current_user
    current_user = email
    
    return RedirectResponse("/", status_code=303)

@app.get("/auth/signin")
async def web_signin(request: Request, email: str, password: str):
    if email not in users_db:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Пользователь не найден",
            "message_type": "error"
        })
    
    if users_db[email].password != password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Неверный пароль",
            "message_type": "error"
        })
    
    global current_user
    current_user = email
    
    return RedirectResponse("/", status_code=303)

@app.get("/logout")
async def logout():
    global current_user
    current_user = None
    return RedirectResponse("/", status_code=303)

@app.get("/learn/{song_id}")
async def learn_song(song_id: int):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    if current_user not in user_progress:
        user_progress[current_user] = {
            "learned_songs": [],
            "learned_words": []
        }
    
    if song_id not in user_progress[current_user]["learned_songs"]:
        user_progress[current_user]["learned_songs"].append(song_id)
        
        song = next((s for s in songs_data if s.id == song_id), None)
        if song:
            for word in song.vocabulary:
                if word not in user_progress[current_user]["learned_words"]:
                    user_progress[current_user]["learned_words"].append(word)
    
    return RedirectResponse("/songs", status_code=303)

@app.get("/songs", response_class=HTMLResponse)
async def read_songs(request: Request):
    learned_songs = []
    if current_user and current_user in user_progress:
        learned_songs = user_progress[current_user]["learned_songs"]
    
    songs_with_progress = []
    for song in songs_data:
        song_dict = song.dict()
        song_dict["is_learned"] = song.id in learned_songs
        songs_with_progress.append(song_dict)
    
    return templates.TemplateResponse("songs.html", {
        "request": request, 
        "songs": songs_with_progress,
        "user_email": current_user
    })

@app.get("/song/{song_id}", response_class=HTMLResponse)
async def read_song(request: Request, song_id: int):
    song = next((s for s in songs_data if s.id == song_id), None)
    if not song:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Песня не найдена",
            "user_email": current_user
        })
    
    is_learned = False
    if current_user and current_user in user_progress:
        is_learned = song_id in user_progress[current_user]["learned_songs"]
    
    song_dict = song.dict()
    song_dict["is_learned"] = is_learned
    
    return templates.TemplateResponse("song_detail.html", {
        "request": request,
        "song": song_dict,
        "user_email": current_user
    })

@app.get("/languages", response_class=HTMLResponse)
async def read_languages(request: Request):
    from routes.languages import languages_data
    return templates.TemplateResponse("languages.html", {
        "request": request,
        "languages": languages_data,
        "user_email": current_user
    })

@app.get("/progress", response_class=HTMLResponse)
async def read_progress(request: Request):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    if current_user in user_progress:
        learned_songs = user_progress[current_user]["learned_songs"]
        learned_words = user_progress[current_user]["learned_words"]
        
        languages_learned = set()
        for song_id in learned_songs:
            song = next((s for s in songs_data if s.id == song_id), None)
            if song:
                languages_learned.add(song.language)
        
        total_songs = len(songs_data)
        completion_percentage = (len(learned_songs) / total_songs) * 100 if total_songs > 0 else 0
        
        stats = {
            "songs_learned": len(learned_songs),
            "words_learned": len(learned_words),
            "languages_learned": len(languages_learned),
            "completion_percentage": round(completion_percentage, 1)
        }
        
        learned_songs_info = []
        for song_id in learned_songs:
            song = next((s for s in songs_data if s.id == song_id), None)
            if song:
                learned_songs_info.append(song.dict())
    else:
        stats = {
            "songs_learned": 0,
            "words_learned": 0,
            "languages_learned": 0,
            "completion_percentage": 0
        }
        learned_songs_info = []
    
    return templates.TemplateResponse("progress.html", {
        "request": request,
        "user_email": current_user,
        "stats": stats,
        "learned_songs": learned_songs_info,
        "total_songs": len(songs_data)
    })

@app.get("/songs/{language}", response_class=HTMLResponse)
async def read_songs_by_language(request: Request, language: str):
    filtered_songs = [s for s in songs_data if s.language == language]
    
    learned_songs = []
    if current_user and current_user in user_progress:
        learned_songs = user_progress[current_user]["learned_songs"]
    
    songs_with_progress = []
    for song in filtered_songs:
        song_dict = song.dict()
        song_dict["is_learned"] = song.id in learned_songs
        songs_with_progress.append(song_dict)
    
    return templates.TemplateResponse("songs.html", {
        "request": request,
        "songs": songs_with_progress,
        "user_email": current_user
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from database.connection import engine, create_db_and_tables, get_session
from models.users import User
from models.songs import Song
from models.languages import Language
from models.artists import Artist
from routes import auth, music, languages, progress, admin
import uvicorn
import os

app = FastAPI()

# Создаем базу данных и таблицы при старте
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("✅ База данных создана и таблицы инициализированы")

app = FastAPI(
    title="LinguaTune",
    description="Изучение языков через музыку 🎵🌍",
    version="2.0.0"
)

templates = Jinja2Templates(directory="templates")
current_user = None

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.auth_router, prefix="/auth")
app.include_router(music.music_router, prefix="/music")
app.include_router(languages.language_router, prefix="/languages")
app.include_router(progress.progress_router, prefix="/progress")
app.include_router(admin.admin_router)

@app.get("/simple-profile")
async def redirect_simple_profile():
    return RedirectResponse("/profile", status_code=301)

@app.get("/reset-password/{token}")
async def redirect_old_reset_password():
    return RedirectResponse("/forgot-password", status_code=301)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, session: Session = Depends(get_session)):
    global current_user
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_email": current_user
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    global current_user
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    global current_user
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    global current_user
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "user_email": current_user
    })

@app.post("/auth/password/reset/request-web", response_class=HTMLResponse)
async def reset_password_request(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(User).where(User.email == email)
    db_user = session.exec(statement).first()
    
    if not db_user:
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": "Пользователь с таким email не найден",
            "message_type": "error",
            "user_email": current_user
        })
    
    if new_password != confirm_password:
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": "Пароли не совпадают",
            "message_type": "error",
            "user_email": current_user
        })
    
    if len(new_password) < 6:
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": "Пароль должен быть не менее 6 символов",
            "message_type": "error",
            "user_email": current_user
        })
    
    db_user.password = new_password
    session.add(db_user)
    session.commit()
    
    current_user = email
    
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "message": f"Пароль для {email} успешно изменен! Вы вошли в систему.",
        "message_type": "success",
        "user_email": current_user
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    session: Session = Depends(get_session)
):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    statement = select(User).where(User.email == current_user)
    user = session.exec(statement).first()
    
    if not user:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Пользователь не найден",
            "user_email": None
        })
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_email": current_user,
        "user": user
    })

@app.post("/profile/update", response_class=HTMLResponse)
async def update_profile_web(
    request: Request,
    full_name: str = Form(None),
    username: str = Form(None),
    current_language: str = Form(None),
    session: Session = Depends(get_session)
):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    statement = select(User).where(User.email == current_user)
    user = session.exec(statement).first()
    
    if user:
        if full_name:
            user.full_name = full_name
        if username:
            user.username = username
        if current_language:
            user.current_language = current_language
        
        session.add(user)
        session.commit()
    
    return RedirectResponse("/profile", status_code=303)

@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "user_email": current_user
    })

@app.post("/change-password", response_class=HTMLResponse)
async def change_password_web(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session)
):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    statement = select(User).where(User.email == current_user)
    user = session.exec(statement).first()
    
    if not user:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Пользователь не найден",
            "user_email": current_user
        })
    
    if user.password != current_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "user_email": current_user,
            "message": "Неверный текущий пароль",
            "message_type": "error"
        })
    
    if new_password != confirm_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "user_email": current_user,
            "message": "Новые пароли не совпадают",
            "message_type": "error"
        })
    
    if len(new_password) < 6:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "user_email": current_user,
            "message": "Пароль должен быть не менее 6 символов",
            "message_type": "error"
        })
    
    user.password = new_password
    session.add(user)
    session.commit()
    
    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "user_email": current_user,
        "message": "Пароль успешно изменен!",
        "message_type": "success"
    })

@app.get("/auth/signup")
async def web_signup(
    request: Request,
    email: str,
    password: str,
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "message": "Пользователь с таким email уже существует",
            "message_type": "error"
        })
    
    new_user = User(
        email=email,
        password=password,
        learned_songs=[],
        favorite_songs=[]
    )
    
    session.add(new_user)
    session.commit()
    
    current_user = email
    
    return RedirectResponse("/", status_code=303)

@app.get("/auth/signin")
async def web_signin(
    request: Request,
    email: str,
    password: str,
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Пользователь не найден",
            "message_type": "error"
        })
    
    if user.password != password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Неверный пароль",
            "message_type": "error"
        })
    
    current_user = email
    
    return RedirectResponse("/", status_code=303)

@app.get("/logout")
async def logout():
    global current_user
    current_user = None
    return RedirectResponse("/", status_code=303)

@app.get("/learn/{song_id}")
async def learn_song(
    song_id: int,
    session: Session = Depends(get_session)
):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    statement = select(User).where(User.email == current_user)
    user = session.exec(statement).first()
    
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if song_id not in user.learned_songs:
        user.learned_songs.append(song_id)
        session.add(user)
        session.commit()
    
    return RedirectResponse("/songs", status_code=303)

@app.get("/songs", response_class=HTMLResponse)
async def read_songs(
    request: Request,
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(Song)
    songs_data = session.exec(statement).all()
    
    learned_songs = []
    if current_user:
        user_statement = select(User).where(User.email == current_user)
        user = session.exec(user_statement).first()
        if user:
            learned_songs = user.learned_songs
    
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
async def read_song(
    request: Request,
    song_id: int,
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(Song).where(Song.id == song_id)
    song = session.exec(statement).first()
    
    if not song:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Песня не найдена",
            "user_email": current_user
        })
    
    is_learned = False
    if current_user:
        user_statement = select(User).where(User.email == current_user)
        user = session.exec(user_statement).first()
        if user and song_id in user.learned_songs:
            is_learned = True
    
    song_dict = song.dict()
    song_dict["is_learned"] = is_learned
    
    return templates.TemplateResponse("song_detail.html", {
        "request": request,
        "song": song_dict,
        "user_email": current_user
    })

@app.get("/languages", response_class=HTMLResponse)
async def read_languages(
    request: Request,
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(Language)
    languages_data = session.exec(statement).all()
    
    return templates.TemplateResponse("languages.html", {
        "request": request,
        "languages": languages_data,
        "user_email": current_user
    })

@app.get("/progress", response_class=HTMLResponse)
async def read_progress(
    request: Request,
    session: Session = Depends(get_session)
):
    global current_user
    
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    statement = select(User).where(User.email == current_user)
    user = session.exec(statement).first()
    
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    learned_songs = user.learned_songs if user else []
    
    statement = select(Song)
    all_songs = session.exec(statement).all()
    
    languages_learned = set()
    for song_id in learned_songs:
        song_statement = select(Song).where(Song.id == song_id)
        song = session.exec(song_statement).first()
        if song:
            languages_learned.add(song.language)
    
    total_songs = len(all_songs)
    completion_percentage = (len(learned_songs) / total_songs) * 100 if total_songs > 0 else 0
    
    stats = {
        "songs_learned": len(learned_songs),
        "words_learned": 0,
        "languages_learned": len(languages_learned),
        "completion_percentage": round(completion_percentage, 1)
    }
    
    learned_songs_info = []
    for song_id in learned_songs:
        song_statement = select(Song).where(Song.id == song_id)
        song = session.exec(song_statement).first()
        if song:
            learned_songs_info.append(song.dict())
    
    return templates.TemplateResponse("progress.html", {
        "request": request,
        "user_email": current_user,
        "stats": stats,
        "learned_songs": learned_songs_info,
        "total_songs": total_songs
    })

@app.get("/songs/{language}", response_class=HTMLResponse)
async def read_songs_by_language(
    request: Request,
    language: str,
    session: Session = Depends(get_session)
):
    global current_user
    
    statement = select(Song).where(Song.language == language)
    filtered_songs = session.exec(statement).all()
    
    learned_songs = []
    if current_user:
        user_statement = select(User).where(User.email == current_user)
        user = session.exec(user_statement).first()
        if user:
            learned_songs = user.learned_songs
    
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

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(
    request: Request,
    admin_email: str = None,
    session: Session = Depends(get_session)
):
    global current_user
    
    if not admin_email:
        admin_email = current_user
    
    if not admin_email:
        return RedirectResponse("/login", status_code=303)
    
    is_admin = admin_email == "admin@linguatune.com" or admin_email == "admin@linguature.com"
    
    if not is_admin:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Доступ запрещен. Требуются права администратора.",
            "user_email": current_user
        })
    
    user_statement = select(User)
    users = session.exec(user_statement).all()
    
    song_statement = select(Song)
    songs = session.exec(song_statement).all()
    
    language_statement = select(Language)
    languages_data = session.exec(language_statement).all()
    
    stats = {
        "users": {
            "total": len(users),
            "with_progress": len([u for u in users if u.learned_songs]),
            "active": len([u for u in users if u.learned_songs])
        },
        "content": {
            "songs": len(songs),
            "languages": len(languages_data),
            "artists": len(set([s.artist for s in songs]))
        },
        "songs_by_language": {},
        "songs_by_difficulty": {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0
        }
    }
    
    for song in songs:
        lang = song.language
        stats["songs_by_language"][lang] = stats["songs_by_language"].get(lang, 0) + 1
        
        diff = song.difficulty.lower()
        if diff in stats["songs_by_difficulty"]:
            stats["songs_by_difficulty"][diff] += 1
    
    songs_list = []
    for song in songs[-10:]:
        songs_list.append({
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "language": song.language,
            "difficulty": song.difficulty
        })
    
    languages_list = []
    for lang in languages_data:
        lang_statement = select(Song).where(Song.language == lang.name)
        songs_count = len(session.exec(lang_statement).all())
        languages_list.append({
            "id": lang.id,
            "name": lang.name,
            "code": lang.code,
            "difficulty": lang.difficulty,
            "songs_count": songs_count
        })
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user_email": current_user,
        "admin_email": admin_email,
        "stats": stats,
        "songs": songs_list,
        "languages": languages_list
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
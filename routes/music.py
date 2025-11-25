from fastapi import APIRouter, HTTPException
from models.songs import Song
from models.artists import Artist

music_router = APIRouter(
    tags=["Музыка"],
    responses={404: {"description": "Не найдено"}}
)

artists_data = [
    Artist(
        id=1,
        name="The Beatles",
        country="Великобритания",
        language="en",
        genres=["rock", "pop"],
        bio="Легендарная британская рок-группа"
    ),
    Artist(
        id=2,
        name="BTS",
        country="Южная Корея", 
        language="ko",
        genres=["k-pop", "pop"],
        bio="Южнокорейский бой-бэнд"
    ),
    Artist(
        id=3,
        name="Kate Ryan",
        country="Бельгия",
        language="fr",
        genres=["pop", "dance"],
        bio="Бельгийская певица"
    ),
    Artist(
        id=4,
        name="Édith Piaf",
        country="Франция",
        language="fr", 
        genres=["chanson", "traditional"],
        bio="Знаменитая французская певица"
    ),
    Artist(
        id=5,
        name="Imagine Dragons",
        country="США",
        language="en",
        genres=["rock", "pop"],
        bio="Американская поп-рок группа"
    )
]

songs_data = [
    Song(
        id=1,
        title="Yesterday",
        artist="The Beatles",
        language="en",
        lyrics_original="Yesterday, all my troubles seemed so far away\nNow it looks as though they're here to stay\nOh, I believe in yesterday",
        lyrics_translation="Вчера все мои проблемы казались такими далекими\nТеперь похоже, что они останутся здесь\nО, я верю во вчера",
        difficulty="beginner",
        vocabulary=["yesterday", "troubles", "far away", "believe", "stay"],
        duration=125
    ),
    Song(
        id=2,
        title="Spring Day",
        artist="BTS", 
        language="ko",
        lyrics_original="보고 싶다\n이렇게 말하니까 더 보고 싶다\n너희 사진을 보고 있어도\n보고 싶다",
        lyrics_translation="Скучаю по вам\nКогда говорю это, скучаю еще больше\nДаже глядя на ваше фото\nСкучаю по вам",
        difficulty="intermediate",
        vocabulary=["보고 싶다", "말하니까", "사진", "봄", "눈", "친구"],
        duration=265
    ),
    Song(
        id=3,
        title="Voyage voyage",
        artist="Kate Ryan", 
        language="fr",
        lyrics_original="Voyage, voyage\nPlus loin que la nuit et le jour\nVoyage, voyage\nDans l'espace inouï de l'amour",
        lyrics_translation="Путешествуй, путешествуй\nДальше, чем ночь и день\nПутешествуй, путешествуй\nВ невероятное пространство любви",
        difficulty="intermediate",
        vocabulary=["voyage", "nuit", "jour", "espace", "inouï", "amour", "rêve"],
        duration=235
    ),
    Song(
        id=4,
        title="Non, je ne regrette rien",
        artist="Édith Piaf", 
        language="fr",
        lyrics_original="Non, je ne regrette rien\nNi le bien qu'on m'a fait\nNi le mal, tout ça m'est bien égal\nNon, rien de rien, non, je ne regrette rien",
        lyrics_translation="Нет, я ни о чем не сожалею\nНи о хорошем, что мне сделали\nНи о плохом, мне все совершенно безразлично\nНет, ни о чем, нет, я ни о чем не сожалею",
        difficulty="intermediate",
        vocabulary=["non", "regrette", "rien", "bien", "mal", "égal", "cœur", "amour", "larmes"],
        duration=142
    ),
    Song(
        id=5,
        title="Human",
        artist="Imagine Dragons",
        language="en",
        lyrics_original="I'm only human, I make mistakes\nI'm only human, that's all it takes\nTo put the blame in the right place",
        lyrics_translation="Я всего лишь человек, я совершаю ошибки\nЯ всего лишь человек, это все, что нужно\nЧтобы возложить вину на нужное место",
        difficulty="beginner",
        vocabulary=["human", "mistakes", "blame", "right place", "broken"],
        duration=245
    ),
    Song(
        id=6,
        title="Life Goes On",
        artist="BTS",
        language="en",
        lyrics_original="Life goes on like an echo in the forest\nLife goes on like the breeze in the meadow\nDoes life go on? Yeah, life goes on",
        lyrics_translation="Жизнь продолжается, как эхо в лесу\nЖизнь продолжается, как ветерок на лугу\nЖизнь продолжается? Да, жизнь продолжается",
        difficulty="beginner", 
        vocabulary=["life", "goes on", "echo", "forest", "breeze", "meadow"],
        duration=213
    )
]

@music_router.get("/songs")
async def get_all_songs():
    return songs_data

@music_router.get("/songs/{language}")
async def get_songs_by_language(language: str):
    filtered_songs = [song for song in songs_data if song.language == language]
    return filtered_songs

@music_router.get("/song/{song_id}")
async def get_song_by_id(song_id: int):
    for song in songs_data:
        if song.id == song_id:
            return song
    raise HTTPException(status_code=404, detail="Песня не найдена")

@music_router.get("/artists")
async def get_all_artists():
    return artists_data
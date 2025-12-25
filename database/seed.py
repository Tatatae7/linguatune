import sys
import os
from pathlib import Path

# Добавляем родительскую директорию в путь Python
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from sqlmodel import Session, select
from database.connection import engine
from models.languages import Language
from models.songs import Song
from models.artists import Artist
from models.admins import Admin
from models.users import User
from datetime import datetime
import json

def seed_initial_data():
    with Session(engine) as session:
        print("🌱 Начинаем загрузку начальных данных...")
        
        # ========== ЯЗЫКИ ==========
        languages = [
            Language(
                name="Английский",
                code="en",
                difficulty="beginner",
                description="Самый популярный язык для изучения"
            ),
            Language(
                name="Испанский",
                code="es", 
                difficulty="beginner",
                description="Второй по популярности язык в мире"
            ),
            Language(
                name="Французский",
                code="fr",
                difficulty="intermediate",
                description="Язык любви и романтики"
            ),
            Language(
                name="Немецкий",
                code="de",
                difficulty="intermediate",
                description="Язык философии и науки"
            ),
            Language(
                name="Итальянский",
                code="it",
                difficulty="intermediate",
                description="Язык искусства и музыки"
            ),
            Language(
                name="Корейский",
                code="ko",
                difficulty="advanced",
                description="Популярный азиатский язык"
            ),
            Language(
                name="Японский",
                code="ja",
                difficulty="advanced",
                description="Язык аниме и технологий"
            ),
            Language(
                name="Русский",
                code="ru",
                difficulty="intermediate",
                description="Самый распространенный славянский язык"
            )
        ]
        
        added_langs = 0
        for lang in languages:
            existing = session.exec(
                select(Language).where(Language.code == lang.code)
            ).first()
            if not existing:
                session.add(lang)
                added_langs += 1
        
        print(f"✅ Языков добавлено: {added_langs}")
        
        # ========== ИСПОЛНИТЕЛИ ==========
        artists = [
            Artist(
                name="The Beatles",
                country="Великобритания",
                language="Английский",
                genres=["Rock", "Pop"],
                bio="Легендарная британская рок-группа, оказавшая огромное влияние на развитие музыки"
            ),
            Artist(
                name="Luis Fonsi",
                country="Пуэрто-Рико",
                language="Испанский",
                genres=["Pop", "Latin"],
                bio="Пуэрториканский певец и автор песен, известный хитом 'Despacito'"
            ),
            Artist(
                name="Édith Piaf",
                country="Франция",
                language="Французский",
                genres=["Chanson", "Traditional"],
                bio="Знаменитая французская певица, икона французской музыки"
            ),
            Artist(
                name="Rammstein",
                country="Германия",
                language="Немецкий",
                genres=["Industrial Metal", "Neue Deutsche Härte"],
                bio="Немецкая индастриал-метал группа, известная своими мощными выступлениями"
            ),
            Artist(
                name="Andrea Bocelli",
                country="Италия",
                language="Итальянский",
                genres=["Classical", "Opera Pop"],
                bio="Итальянский тенор, певец и автор песен, известный во всем мире"
            ),
            Artist(
                name="BTS",
                country="Южная Корея",
                language="Корейский",
                genres=["K-Pop", "Pop", "Hip Hop"],
                bio="Южнокорейский бой-бэнд, одна из самых популярных групп в мире"
            ),
            Artist(
                name="Imagine Dragons",
                country="США",
                language="Английский",
                genres=["Rock", "Pop"],
                bio="Американская поп-рок группа из Лас-Вегаса"
            ),
            Artist(
                name="Miyuki Nakajima",
                country="Япония",
                language="Японский",
                genres=["Pop", "Folk"],
                bio="Японская певица и автор песен"
            ),
            Artist(
                name="Mikhail Krug",
                country="Россия",
                language="Русский",
                genres=["Russian Chanson", "Folk"],
                bio="Российский певец и автор песен в жанре русский шансон"
            )
        ]
        
        added_artists = 0
        for artist in artists:
            existing = session.exec(
                select(Artist).where(Artist.name == artist.name)
            ).first()
            if not existing:
                session.add(artist)
                added_artists += 1
        
        print(f"✅ Исполнителей добавлено: {added_artists}")
        
        # ========== ПЕСНИ ==========
        songs = [
            # Английские песни
            Song(
                title="Yesterday",
                artist="The Beatles",
                language="Английский",
                lyrics_original="Yesterday, all my troubles seemed so far away\nNow it looks as though they're here to stay\nOh, I believe in yesterday",
                lyrics_translation="Вчера все мои проблемы казались такими далекими\nТеперь похоже, что они останутся здесь\nО, я верю во вчера",
                difficulty="beginner",
                vocabulary=["yesterday", "troubles", "far away", "believe", "stay"],
                duration=125
            ),
            Song(
                title="Let It Be",
                artist="The Beatles",
                language="Английский",
                lyrics_original="When I find myself in times of trouble\nMother Mary comes to me\nSpeaking words of wisdom, let it be",
                lyrics_translation="Когда я нахожу себя в трудные времена\nКо мне приходит мать Мария\nГоворя слова мудрости, пусть будет так",
                difficulty="beginner",
                vocabulary=["trouble", "wisdom", "whisper", "broken-hearted", "answer"],
                duration=243
            ),
            Song(
                title="Radioactive",
                artist="Imagine Dragons",
                language="Английский",
                lyrics_original="I'm waking up to ash and dust\nI wipe my brow and I sweat my rust\nI'm breathing in the chemicals",
                lyrics_translation="Я просыпаюсь в пепле и пыли\nЯ вытираю лоб и потею ржавчиной\nЯ вдыхаю химикаты",
                difficulty="intermediate",
                vocabulary=["radioactive", "ash", "dust", "chemicals", "apocalypse"],
                duration=187
            ),
            
            # Испанские песни
            Song(
                title="Despacito",
                artist="Luis Fonsi",
                language="Испанский",
                lyrics_original="Sí, sabes que ya llevo un rato mirándote\nTengo que bailar contigo hoy\nVi que tu mirada ya estaba llamándome\nMuéstrame el camino que yo voy",
                lyrics_translation="Да, ты знаешь, что я уже некоторое время смотрю на тебя\nЯ должен танцевать с тобой сегодня\nЯ видел, что твой взгляд уже звал меня\nПокажи мне путь, и я пойду",
                difficulty="intermediate",
                vocabulary=["despacito", "quiero", "cuerpo", "bailar", "amor", "camino"],
                duration=229
            ),
            
            # Французские песни
            Song(
                title="Non, je ne regrette rien",
                artist="Édith Piaf",
                language="Французский",
                lyrics_original="Non, rien de rien\nNon, je ne regrette rien\nNi le bien qu'on m'a fait\nNi le mal, tout ça m'est bien égal",
                lyrics_translation="Нет, ни о чем\nНет, я ни о чем не сожалею\nНи о хорошем, что мне сделали\nНи о плохом, мне все совершенно безразлично",
                difficulty="intermediate",
                vocabulary=["non", "regrette", "rien", "bien", "mal", "égal", "cœur", "amour", "larmes"],
                duration=142
            ),
            
            # Немецкие песни
            Song(
                title="Du hast",
                artist="Rammstein",
                language="Немецкий",
                lyrics_original="Du hast mich gefragt\nUnd ich hab nichts gesagt\nWillst du bis der Tod euch scheidet\nTreuer sein für alle Tage",
                lyrics_translation="Ты спросил меня\nИ я ничего не сказал\nХочешь ли ты до тех пор, пока смерть не разлучит вас\nБыть верным на все дни",
                difficulty="advanced",
                vocabulary=["hast", "gefragt", "gesagt", "Tod", "scheidet", "treuer", "Tage"],
                duration=238
            ),
            
            # Итальянские песни
            Song(
                title="Con te partirò",
                artist="Andrea Bocelli",
                language="Итальянский",
                lyrics_original="Con te partirò\nPaesi che non ho mai\nVeduto e vissuto con te\nAdesso sì li vivrò",
                lyrics_translation="С тобой я уеду\nВ страны, которые я никогда\nНе видел и не жил с тобой\nТеперь да, я буду жить ими",
                difficulty="intermediate",
                vocabulary=["partirò", "paesi", "veduto", "vissuto", "vivrò", "viaggio", "mare"],
                duration=268
            ),
            
            # Корейские песни
            Song(
                title="Dynamite",
                artist="BTS",
                language="Корейский",
                lyrics_original="'Cause I, I, I'm in the stars tonight\nSo watch me bring the fire and set the night alight\nShoes on, get up in the morn'\nCup of milk, let's rock and roll",
                lyrics_translation="Потому что я, я, я сегодня среди звезд\nТак что смотри, как я приношу огонь и зажигаю ночь\nОбувь надела, встала утром\nЧашка молока, давай рок-н-ролл",
                difficulty="intermediate",
                vocabulary=["stars", "fire", "night", "alight", "milk", "rock and roll", "dynamite"],
                duration=199
            ),
            
            # Японские песни
            Song(
                title="Yuki no Hana",
                artist="Miyuki Nakajima",
                language="Японский",
                lyrics_original="Yuki no hana ga mau youni\nFutari karaeru youni\nKonna ni chikai keredo\nTooi hibi ga aru",
                lyrics_translation="Как будто танцуют снежинки\nЧтобы мы могли согреться вместе\nХотя мы так близки\nБывают дни, когда мы далеки",
                difficulty="advanced",
                vocabulary=["yuki", "hana", "mau", "futari", "atatameru", "chikai", "tooi"],
                duration=315
            ),
            
            # Русские песни
            Song(
                title="Владимирский централ",
                artist="Mikhail Krug",
                language="Русский",
                lyrics_original="Владимирский централ, ветер северный\nОн откинулся не в сказке, а наяву\nМне на нем сидеть и срок немалый отбывать\nА она все ждет и верит в нашу любовь",
                lyrics_translation="Владимирский централ, ветер северный\nОн откинулся не в сказке, а наяву\nМне на нем сидеть и срок немалый отбывать\nА она все ждет и верит в нашу любовь",
                difficulty="intermediate",
                vocabulary=["централ", "ветер", "северный", "сказка", "наяву", "срок", "отбывать", "любовь"],
                duration=246
            )
        ]
        
        added_songs = 0
        for song in songs:
            existing = session.exec(
                select(Song).where(
                    (Song.title == song.title) & 
                    (Song.artist == song.artist)
                )
            ).first()
            if not existing:
                session.add(song)
                added_songs += 1
        
        print(f"✅ Песен добавлено: {added_songs}")
        
        # ========== АДМИНИСТРАТОРЫ ==========
        admin = Admin(
            user_email="admin@linguatune.com",
            role="superadmin",
            permissions={
                "manage_users": True,
                "manage_content": True,
                "view_stats": True,
                "backup": True,
                "moderate": True,
                "configure": True
            }
        )
        
        existing_admin = session.exec(
            select(Admin).where(Admin.user_email == admin.user_email)
        ).first()
        if not existing_admin:
            session.add(admin)
            print("✅ Администратор добавлен: admin@linguatune.com")
        else:
            print("ℹ️ Администратор уже существует")
        
        # ========== ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ ==========
        test_user = User(
            email="test@linguatune.com",
            password="test123",
            full_name="Тестовый Пользователь",
            username="test_user",
            current_language="Английский",
            learned_songs=[]
        )
        
        existing_user = session.exec(
            select(User).where(User.email == test_user.email)
        ).first()
        if not existing_user:
            session.add(test_user)
            print("✅ Тестовый пользователь добавлен: test@linguatune.com")
        else:
            print("ℹ️ Тестовый пользователь уже существует")
        
        # ========== ЕЩЕ ОДИН ПОЛЬЗОВАТЕЛЬ ==========
        another_user = User(
            email="user@linguatune.com",
            password="111",
            full_name="Другой Пользователь",
            username="another_user",
            current_language="Испанский",
            learned_songs=[]
        )
        
        existing_another = session.exec(
            select(User).where(User.email == another_user.email)
        ).first()
        if not existing_another:
            session.add(another_user)
            print("✅ Пользователь добавлен: user@linguatune.com")
        else:
            print("ℹ️ Пользователь уже существует")
        
        session.commit()
        
        print("\n" + "="*50)
        print("🎉 НАЧАЛЬНЫЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ!")
        print("="*50)
        print(f"📊 ИТОГО:")
        print(f"   📚 Языков: {added_langs}")
        print(f"   🎤 Исполнителей: {added_artists}")
        print(f"   🎵 Песен: {added_songs}")
        print(f"   👑 Администраторов: 1")
        print(f"   👤 Пользователей: 2")
        print("\n🚀 Теперь запустите сервер: python main.py")
        print("🌐 Откройте в браузере: http://localhost:8000/docs")

if __name__ == "__main__":
    seed_initial_data()
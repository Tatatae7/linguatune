from .auth import auth_router
from .admin import admin_router
from .languages import language_router
from .music import music_router
from .progress import progress_router

__all__ = ["auth_router", "admin_router", "language_router", "music_router", "progress_router"]
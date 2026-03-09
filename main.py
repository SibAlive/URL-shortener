from environs import Env
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.staticfiles import StaticFiles

from services import create_db_and_tables, limiter
from routers import web, api, system


# Загружаем переменные окружения
env = Env()
env.read_env()

# Создаем БД и таблицы (если еще не созданы)
create_db_and_tables()


app = FastAPI(title="Short link creator",
              description="Сервис генерации коротких ссылок с веб-интерфейсом и API")

# Настройка ограничения частоты запросов
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=env.list("CORS_ORIGINS"), # Разрешенные источники
    allow_credentials=True, # Разрешение на передачу куки/авторизации
    allow_methods=["GET", "POST"], # Разрешенные HTTP методы
    allow_headers=["Content-Type", "Authorization"] # Разрешенные заголовки
)

# Защита от подделки хоста
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=env.list("ALLOWED_HOSTS"),
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры
app.include_router(system.router) # Системные маршруты
app.include_router(web.router) # Web маршруты
app.include_router(api.router) # API маршруты
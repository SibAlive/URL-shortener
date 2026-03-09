import sys
import os
from typing import Generator
import logging
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import Base, get_db, limiter
from main import app
import schemas
import models


logger = logging.getLogger(__name__)


# Отключаем Rate limiter для тестов
limiter.enabled = False

# Создаем тестовую БД (в памяти SQLite для тестов)
db_name = "test.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./" + db_name
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределяем зависимость get_db для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Подменяем зависимость в приложении
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Фикстура для создания и удаления тестовой БД"""
    # Создаем БД
    Base.metadata.create_all(bind=engine)
    logger.info(f"Тестовая БД {db_name} создана")

    yield

    engine.dispose() # Закрываем соединение с БД

    # Удаляем файл БД после всех тестов
    if os.path.exists(db_name):
        try:
            os.remove(db_name)
            logger.info(f"Тестовая БД {db_name} удалена")
        except PermissionError:
            logger.warning(f"Не удалось удалить {db_name} - файл используется")
        except Exception as e:
            logger.error(f"Ошибка при удалении {db_name}: {e}")


@pytest.fixture
def db_session() -> Generator:
    """Фикстура для сессии БД"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session) -> Generator:
    """Фикстура для тестового клиента"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_url():
    """Фикстура с примером URL"""
    return "https://example.com/very/long/path?with=params"


@pytest.fixture
def sample_custom_code():
    """Фикстура с примером кастомного кода"""
    return "my_test_link"
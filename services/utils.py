import secrets
import string
import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, ValidationError

from models import Link


def generate_short_code(length=6):
    """Генерирует случайный код из букв и цифр"""
    symbols = string.ascii_letters + string.digits
    return ''.join(secrets.choice(symbols) for _ in range(length))


def generate_unique_code(db: Session, length=6):
    """Генерирует уникальный код, которого еще нет в БД"""
    while True:
        code = generate_short_code(length)
        # Проверяем, существует ли данный код в БД
        existing = db.query(Link).filter(Link.short_id == code).first()
        if not existing:
            return code


def normalize_url(url: str) -> str:
    """Нормализует URL, добавляя протокол если отсутствует"""
    url = url.strip()

    if not url:
        raise ValueError("URL не может быть пустым")

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    # Проверяем корректность URL
    is_valid = check_url(url)

    if is_valid:
        return url


def check_url(url: str) -> bool:
    """Проверяет корректность ссылки"""
    # Валидация URL адреса через Pydantic
    class URLModel(BaseModel):
        url: HttpUrl

    validated = URLModel(url=url)
    validated_url = str(validated.url)

    # Проверка домена
    parsed = urlparse(validated_url)
    hostname = parsed.hostname

    if not hostname:
        raise ValueError("Отсутствует доменное имя")

    if '.' not in hostname:
        raise ValueError("Некорректный URL")

    # Проверка доменного имени
    if '.' not in hostname:
        raise ValueError("Доменное имя должно содержать точку")

    domain_parts = hostname.split('.')

    for part in domain_parts:
        if not part:
            raise ValueError("Пустая часть домена")
        if part.startswith('-') or part.endswith('-'):
            raise ValueError(f"Часть домена '{part}' не может начинаться или заканчиваться дефисом")
        if not re.match(r'[a-zA-Z0-9-]+$', part):
            raise ValueError(f"URL содержит недопустимые символы")


    # Проверка TLD
    tld = domain_parts[-1]
    if len(tld) < 2:
        raise ValueError("TLD должен содержать минимум 2 символа")
    if not tld.isalpha():
        raise ValueError("TLD должен содержать только буквы")

    return True
from sqlalchemy.orm import Session

from models import Link
from .utils import generate_unique_code


def get_link_by_code(db: Session, short_id: str):
    """Получить ссылку по короткому коду"""
    return db.query(Link).filter(Link.short_id == short_id).first()


def create_link(db: Session, original_url: str, custom_code: str = None):
    """Создаем новую короткую ссылку"""
    # Определяем код для ссылки
    if custom_code:
        # Проверяем, не занят ли кастомный код
        existing = get_link_by_code(db, custom_code)
        if existing:
            return None
        short_id = custom_code
        is_custom = True
    else:
        # Генерируем уникальный код
        short_id = generate_unique_code(db)
        is_custom = False

    # Создаем запись в БД
    db_link = Link(
        short_id=short_id,
        original_url=original_url,
        is_custom=is_custom
    )

    db.add(db_link)
    db.commit()
    db.refresh(db_link)

    return db_link


def increment_clicks(db: Session, link: Link):
    """Увеличить счетчик кликов по ссылке"""
    link.clicks += 1
    db.commit()
    db.refresh(link)
    return link
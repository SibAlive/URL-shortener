"""Модель (таблица) базы данных"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from services import Base


class Link(Base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False) # Исходный URL адрес
    short_id = Column(String, unique=True, index=True, nullable=False) # Короткая ссылка
    clicks = Column(Integer, default=0) # Количество переходов по ссылке
    created_at = Column(DateTime, default=datetime.now) # Дата и время создания
    is_custom = Column(Boolean, default=False) # Для кастомных ссылок (пользователь сам вводит короткую ссылку)
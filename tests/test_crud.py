import pytest
from sqlalchemy.orm import Session

from services import crud


class TestCRUD:
    """Тесты для CRUD операций"""

    def test_create_link_success(self, db_session: Session, sample_url):
        """Тест успешного создания ссылки"""
        link = crud.create_link(db_session, sample_url)

        assert link is not None
        assert link.original_url == sample_url
        assert link.short_id is not None
        assert len(link.short_id) == 6
        assert link.clicks == 0
        assert link.is_custom is False

    def test_create_link_with_custom_code(self, db_session: Session, sample_url, sample_custom_code):
        """Тест создания ссылки с кастомным кодом"""
        link = crud.create_link(db_session, sample_url, sample_custom_code)

        assert link is not None
        assert link.original_url == sample_url
        assert link.short_id == sample_custom_code
        assert link.is_custom is True

    def test_create_link_duplicate(self, db_session: Session, sample_url, sample_custom_code):
        """Тест попытки создания дубликата кастомного кода"""
        # Создаем первую ссылку
        crud.create_link(db_session, sample_url, sample_custom_code)

        # Пытаемся создать вторую ссылку с тем же кодом
        link_2 = crud.create_link(db_session, sample_url, sample_custom_code)

        assert link_2 is None

    def test_get_link_by_code_success(self, db_session: Session, sample_url):
        """Тест получения ссылки по коду"""
        # Создаем ссылку
        link_created = crud.create_link(db_session, sample_url)

        # Получаем ссылку по коду
        link_found = crud.get_link_by_code(db_session, link_created.short_id)

        assert link_found is not None
        assert link_found.id == link_created.id
        assert link_found.original_url == sample_url

    def test_get_link_by_code_not_found(self, db_session: Session):
        """Тест получения несуществующей ссылки"""
        link = crud.get_link_by_code(db_session, "not_existing_link")

        assert link is None

    def test_increment_clicks(self, db_session: Session, sample_url):
        """Тест увеличения счетчика кликов"""
        # Создаем ссылку
        link = crud.create_link(db_session, sample_url)
        assert link.clicks == 0

        # Увеличиваем счетчик перехода по ссылке 5 раз
        for _ in range(5):
            crud.increment_clicks(db_session, link)

        # Проверяем, что изменения сохранились в БД
        link_found = crud.get_link_by_code(db_session, link.short_id)

        assert link_found.clicks == 5
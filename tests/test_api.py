import pytest
from fastapi.testclient import TestClient


class TestAPI:
    """Тесты для API эндпоинтов"""
    def test_create_short_link_success(self, client: TestClient):
        """Тест успешного создания короткой ссылки через API"""
        response = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_code": None}
        )

        assert response.status_code == 200

        data = response.json()
        assert "short_id" in data
        assert len(data.get("short_id")) == 6

    def test_create_link_without_protocol(self, client: TestClient):
        """Тест создания ссылки без протокола"""
        response = client.post(
            "/shorten",
            json={"url": "example.com", "custom_code": None}
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("url", [
        "example?.com", # Содержит недопустимый символ
        "https://_example.com", # Начинается с _
        "htps://example.com", # Опечатка в протоколе
        "https:/example.r" # Короткий tld
    ])
    def test_create_link_invalid_url(self, client: TestClient, url):
        """Тест создания ссылки с невалидным url адресом"""
        response = client.post(
             "/shorten",
            json={"url": url, "custom_code": None}
        )
        assert response.status_code == 400

    def test_create_short_link_with_custom_code(self, client: TestClient, sample_custom_code):
        """Тест создания ссылки с кастомным кодом"""
        response = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_code": sample_custom_code}
        )

        assert response.status_code == 200

        data = response.json()
        assert data.get('short_id') == sample_custom_code

    def test_create_short_link_duplicate(self, client: TestClient, sample_custom_code):
        """Тест создания дубликата кастомного кода"""
        # Создаем первую ссылку
        client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_code": sample_custom_code}
        )

        # Пытаемся создать вторую ссылку с тем же кодом
        response = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_code": sample_custom_code}
        )

        assert response.status_code == 400

        data = response.json()
        assert f"Код '{sample_custom_code}' уже используется" in data.get('detail')

    @pytest.mark.parametrize("invalid_code", [
        "abc", # Слишком короткий код
        "a" * 51, # Слишком длинный код
        "Example!", # Невалидный символ
        "русский_текст" # Не латинские символы
    ])
    def test_create_short_link_invalid_custom_code(self, client: TestClient, invalid_code):
        """Тест создания ссылки с невалидным кастомным кодом"""
        response = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_code": invalid_code}
        )

        assert response.status_code == 400

        data = response.json()
        assert "detail" in data

    def test_stats_endpoint_success(self, client: TestClient):
        """Тест получения статистики"""
        # Создаем ссылку
        new_response = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_code": "test_stats"}
        )
        short_id = new_response.json().get("short_id")

        # Переходим по ссылке 5 раз
        for _ in range(5):
            client.get(f"/{short_id}")

        # Получаем статистику
        response = client.get(f"/stats/{short_id}")

        assert response.status_code == 200

        data = response.json()
        assert "clicks" in data
        assert data.get("clicks") == 5

    def test_redirect_endpoint_success(self, client: TestClient):
        """Тест успешного редиректа"""
        url = "https://example.com/"
        # Создаем ссылку
        new_response = client.post(
            "/shorten",
            json={"url": url, "custom_code": "test_redirect"}
        )
        short_id = new_response.json().get("short_id")

        # Проверяем редирект
        response = client.get(f"/{short_id}")

        assert response.status_code == 200

        data = response.json()
        assert data.get("original_url") == url

    def test_redirect_endpoint_not_found(self, client: TestClient):
        """Тест редиректа по несуществующей ссылке"""
        response = client.get("/not_existing_link")

        assert response.status_code == 404

        data = response.json()
        assert "Ссылка не найдена" in data.get('detail')

    def test_multiple_request_same_url(self, client: TestClient):
        """Тест создания нескольких коротких ссылок для одного URL"""
        url = "https://example.com"

        responses = []
        for _ in range(5):
            response = client.post(
                "/shorten",
                json={"url": url, "custom_code": None}
            )
            responses.append(response.json())

        # Проверяем, что все short_id разные
        short_ids = [response.get("short_id") for response in responses]
        assert len(set(short_ids)) == 5
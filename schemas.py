"""Схемы для валидации входящий данных и формирования ответов API"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Схема для создания короткой ссылки
class LinkCreate(BaseModel):
    url: str
    custom_code: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "custom_code": ""
                }
            }
        )


# Схема для ответа пользователю (возвращаем короткую ссылку)
class LinkResponse(BaseModel):
    short_id: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "short_id": "QiJ1K0"
            }
        }
    )


# Схема для статистики
class ClickStats(BaseModel):
    clicks: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "clicks": 23
            }
        }
    )
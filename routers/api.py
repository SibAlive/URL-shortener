from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from services import get_db, crud, normalize_url, limiter
from validators import validate_custom_code
import schemas


router = APIRouter(tags=["API"])


@router.post('/shorten', response_model=schemas.LinkResponse)
@limiter.limit("10/minute") # Ограничивает количество запросов пользователя (10 запросов в минуту)
async def api_create_short_link(
        request: Request,
        link_data: schemas.LinkCreate,
        db: Session = Depends(get_db)
):
    """API для создания короткой ссылки"""
    # Валидация кастомного кода (если предоставлен)
    custom_code = link_data.custom_code

    if custom_code:
        is_valid, error_message = validate_custom_code(custom_code)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=error_message
            )
        custom_code = custom_code.strip()

    # Преобразуем HttpUrl в строку
    url = str(link_data.url)

    try:
        # Нормализуем URL и проверяем корректность
        url = normalize_url(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Создаем короткую ссылку
    db_link = crud.create_link(db, url, custom_code)

    if db_link is None and link_data.custom_code:
        raise HTTPException(
            status_code=400,
            detail=f"Код '{link_data.custom_code}' уже используется"
        )

    if db_link is None:
        raise HTTPException(
            status_code=400,
            detail="Не удалось создать ссылку"
        )

    # Возвращаем короткую ссылку
    return {"short_id": db_link.short_id}


@router.get("/{short_id}")
@limiter.limit("10/minute")
async def api_redirect_to_url(
        request: Request,
        short_id: str,
        db: Session = Depends(get_db)):
    """API для редиректа по короткой ссылке"""
    link = crud.get_link_by_code(db, short_id)

    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    # Увеличиваем счетчик переходов
    crud.increment_clicks(db, link)

    # Возвращаем полный URL
    return {"original_url": link.original_url}


@router.get("/stats/{short_id}", response_model=schemas.ClickStats)
@limiter.limit("10/minute")
async def api_get_stats(
        request: Request,
        short_id: str,
        db: Session = Depends(get_db)):
    """API для получения статистики"""
    link = crud.get_link_by_code(db, short_id)

    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    # Возвращаем количество переходов
    return {"clicks": link.clicks}
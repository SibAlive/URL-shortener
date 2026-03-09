from typing import Optional
from fastapi import Request, Depends, Form, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from services import get_db, crud, normalize_url
from validators import validate_custom_code


router = APIRouter(prefix='/web', tags=["Web Interface"])
templates = Jinja2Templates(directory="templates")


@router.get('/', response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с формой"""
    return templates.TemplateResponse('index.html', {'request': request})


@router.post('/shorten', response_class=HTMLResponse)
async def create_short_link(
        request: Request,
        url: str = Form(...),
        custom_code: Optional[str] = Form(None),
        db: Session = Depends(get_db)
):
    """Обработка формы создания короткой ссылки"""
    # Валидация кастомного кода (если предоставлен)
    if custom_code:
        is_valid, error_message = validate_custom_code(custom_code)
        if not is_valid:
            return templates.TemplateResponse('index.html', {'request': request, 'error': error_message})
        custom_code = custom_code.strip()

    try:
        # Нормализуем URL и проверяем корректность
        url = normalize_url(url)
    except ValueError as e:
        return templates.TemplateResponse(
            'index.html',
            {
                'request': request,
                'error': f"Ошибка в URL: {str(e)}",
            }
        )

    # Создаем короткую ссылку
    db_link = crud.create_link(db, url, custom_code)

    if db_link is None and custom_code:
        # Если кастомный код уже занят
        return templates.TemplateResponse(
            'index.html',
            {
                'request': request,
                'error': f"Код '{custom_code}' уже занят. Пожалуйста, выберите другой."
            }
        )

    short_url = str(request.base_url) + router.prefix.lstrip('/') +'/' + db_link.short_id

    return templates.TemplateResponse(
        'index.html',
        {
            "request": request,
            "short_url": short_url,
            "original_url": url,
            "short_id": db_link.short_id,
        }
    )


@router.get('/{short_id}')
async def redirect_to_url(short_id: str, db: Session = Depends(get_db)):
    """Редирект по короткой ссылке"""
    link = crud.get_link_by_code(db, short_id)

    if not link:
        return templates.TemplateResponse(
            '404.html',
            {'request': {}, 'message': "Ссылка не найдена"},
            status_code=404
        )

    # Увеличиваем счетчик переходов
    crud.increment_clicks(db, link)

    return RedirectResponse(url=link.original_url)


@router.get('/stats/{short_id}', response_class=HTMLResponse)
async def get_stats(request: Request, short_id: str, db: Session = Depends(get_db)):
    """Страница со статистикой"""
    link = crud.get_link_by_code(db, short_id)

    if not link:
        return templates.TemplateResponse(
            '404.html',
            {'request': {}, 'message': "Ссылка не найдена"},
            status_code=404
        )

    return templates.TemplateResponse(
        'stats.html',
        {'request': request, 'link': link}
    )
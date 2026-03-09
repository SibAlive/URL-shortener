from fastapi import APIRouter


router = APIRouter(tags=["System"])


@router.get('/health')
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": 'ok', "service": "Short link creator"}


@router.get("/info")
async def get_info():
    """Информация о всех эндпоинтах"""
    return {
        "name": "Short link creator",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "info": "/info",
            "web": {
                "home": "GET /web/",
                "create_short_link": "POST /web/shorten",
                "redirect_to_url": "GET /web/{short_id}",
                "get_stats": "GET /web/stats/{short_id}"
            },
            "api": {
                "api_create_short_link": "POST /shorten",
                "api_redirect_to_url": "GET /{short_id}",
                "api_get_stats": "GET /stats/{short_id}"
            }
        }
    }
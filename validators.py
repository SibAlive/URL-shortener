import re
from typing import Optional, Tuple

def validate_custom_code(custom_code: str) -> Tuple[bool, Optional[str]]:
    """Валидация кастомного кода"""
    if not custom_code or not custom_code.strip():
        return True, None

    code = custom_code.strip()

    # Проверка длины
    if len(code) < 5:
        return False, "Код должен содержать минимум 5 символов"

    if len(code) > 50:
        return False, "Код должен содержать максимум 50 символов"

    # Проверка допустимых символов
    if not re.match(r'^[a-zA-z0-9_-]+$', code):
        return False, "Код может содержать только английские буквы, цифры, дефис (-) и подчеркивание (_)"

    return True, None
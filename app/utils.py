import os
import re
from datetime import date, datetime
from typing import Optional
from fastapi import UploadFile

from app.config import config
from app.exceptions import FileTooLargeError, ValidationError


def calculate_age(birth_date: date) -> int:
    """Вычисляет возраст"""
    today = date.today()
    age = today.year - birth_date.year
    if today.month < birth_date.month or \
       (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age


def validate_phone(phone: str) -> str:
    """Валидация телефона"""
    if not re.match(r'^\+7\d{10}$', phone):
        raise ValidationError("Телефон должен быть в формате +7XXXXXXXXXX")
    return phone


def validate_gender(gender: str) -> str:
    """Валидация пола"""
    if gender not in ['Муж', 'Жен']:
        raise ValidationError('Пол должен быть "Муж" или "Жен"')
    return gender


def parse_date(date_str: str) -> date:
    """Парсит дату из строки"""
    try:
        birth_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        raise ValidationError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

    if birth_date > date.today():
        raise ValidationError("Дата рождения не может быть в будущем")

    return birth_date


async def save_photo(photo: Optional[UploadFile]) -> Optional[str]:
    """Сохраняет фото и возвращает путь"""
    if not photo or not photo.filename:
        return None

    content = await photo.read()

    if len(content) > config.MAX_UPLOAD_SIZE:
        raise FileTooLargeError(config.MAX_UPLOAD_SIZE)

    if not photo.content_type.startswith('image/'):
        raise ValidationError("Файл должен быть изображением")

    filename = f"{datetime.now().timestamp()}_{photo.filename}"
    filepath = f"{config.UPLOAD_DIR}/{filename}"
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    with open(filepath, "wb") as buffer:
        buffer.write(content)

    return f"/uploads/{filename}"


def delete_photo(photo_path: Optional[str]) -> None:
    """Удаляет фото с диска"""
    if not photo_path:
        return

    filepath = f"static{photo_path}"
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


def parse_int_or_none(value: Optional[str]) -> Optional[int]:
    """Преобразует строку в int или возвращает None"""
    if not value:
        return None
    try:
        num = int(value)
        return num if num > 0 else None
    except (ValueError, TypeError):
        return None

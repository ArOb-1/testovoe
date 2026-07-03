from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

from app.utils import validate_phone, validate_gender, parse_date


class EmployeeBase(BaseModel):
    """Базовые поля сотрудника"""
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    phone: str
    birth_date: date
    gender: str


class EmployeeCreate(EmployeeBase):
    """Схема для создания сотрудника"""
    pass


class EmployeeUpdate(EmployeeBase):
    """Схема для обновления сотрудника"""
    pass


class Employee(EmployeeBase):
    """Схема для ответа"""
    id: int
    photo_path: Optional[str] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True


class EmployeeCreateForm(BaseModel):
    """
    Схема для валидации данных из HTML формы.
    """
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    phone: str
    birth_date: str
    gender: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Проверка формата телефона"""
        return validate_phone(v)

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Проверка пола"""
        return validate_gender(v)

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: str) -> date:
        """Проверка даты рождения"""
        return parse_date(v)

    def to_employee_create(self) -> EmployeeCreate:
        """Конвертирует в модель для создания"""
        return EmployeeCreate(
            last_name=self.last_name.strip(),
            first_name=self.first_name.strip(),
            patronymic=self.patronymic.strip() if self.patronymic else None,
            phone=self.phone.strip(),
            birth_date=self.birth_date,
            gender=self.gender
        )

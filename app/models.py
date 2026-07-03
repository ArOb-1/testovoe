from sqlalchemy import Column, Integer, String, Date, Enum, DateTime
from sqlalchemy.sql import func
from app.database import Base
import enum


class Gender(str, enum.Enum):
    MALE = 'Муж'
    FEMALE = 'Жен'

    def __str__(self):
        return self.value


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    patronymic = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    photo_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

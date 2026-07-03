from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from datetime import date

from app.utils import calculate_age


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    gender: str = None,
    age_from: int = None,
    age_to: int = None
):
    query = db.query(models.Employee)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            or_(
                models.Employee.last_name.ilike(search_term),
                models.Employee.first_name.ilike(search_term),
                models.Employee.patronymic.ilike(search_term),
                models.Employee.phone.ilike(search_term)
            )
        )
    if gender:
        query = query.filter(models.Employee.gender == gender)

    today = date.today()

    if isinstance(age_from, int) and age_from > 0:
        max_birth_date = date(today.year - age_from, today.month, today.day)
        query = query.filter(models.Employee.birth_date <= max_birth_date)

    if isinstance(age_to, int) and age_to > 0:
        min_birth_date = date(today.year - age_to - 1, today.month, today.day)
        query = query.filter(models.Employee.birth_date >= min_birth_date)

    total = query.count()
    employees = query.offset(skip).limit(limit).all()
    for employee in employees:
        employee.age = calculate_age(employee.birth_date)

    return employees, total


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def create_employee(db: Session, employee: schemas.EmployeeCreate, photo_path: str = None):
    db_employee = models.Employee(
        **employee.model_dump(),
        photo_path=photo_path
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeUpdate, photo_path: str = None):
    db_employee = get_employee(db, employee_id)

    if db_employee:
        for key, value in employee.model_dump().items():
            setattr(db_employee, key, value)
        if photo_path:
            db_employee.photo_path = photo_path
        db.commit()
        db.refresh(db_employee)
        return db_employee


def delete_employee(db: Session, employee_id: int):
    db_employee = get_employee(db, employee_id)

    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False

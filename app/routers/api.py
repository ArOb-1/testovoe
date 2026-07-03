from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app import crud, schemas, models
from app.database import get_db
from app.utils import calculate_age, parse_int_or_none, delete_photo
from app.exceptions import (
    NotFoundError,
    EmployeeAlreadyExistsError
)


router = APIRouter(prefix="/api", tags=["api"])


@router.get(
    "/employees",
    response_model=dict
)
async def get_employees(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по ФИО или телефону"),
    gender: Optional[str] = Query(None, description="Фильтр по полу (Муж/Жен)"),
    age_from: Optional[str] = Query(None, description="Минимальный возраст"),
    age_to: Optional[str] = Query(None, description="Максимальный возраст")
):
    """
    Получить список сотрудников с фильтрацией и пагинацией.
    """
    age_from_int = parse_int_or_none(age_from)
    age_to_int = parse_int_or_none(age_to)

    employees, total = crud.get_employees(
        db,
        skip=skip,
        limit=limit,
        search=search,
        gender=gender,
        age_from=age_from_int,
        age_to=age_to_int
    )

    for employee in employees:
        employee.age = calculate_age(employee.birth_date)

    return {
        "status": "success",
        "data": employees,
        "pagination": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "next": skip + limit if skip + limit < total else None,
            "pages": (total + limit - 1) // limit if total > 0 else 1
        },
        "filters": {
            "search": search,
            "gender": gender,
            "age_from": age_from_int,
            "age_to": age_to_int
        }
    }


@router.get(
    "/employees/{employee_id}",
    response_model=schemas.Employee
)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить сотрудника по ID.
    """
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise NotFoundError("Сотрудник", employee_id)

    employee.age = calculate_age(employee.birth_date)
    return employee


@router.post(
    "/employees",
    response_model=schemas.Employee,
    status_code=status.HTTP_201_CREATED
)
async def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    """
    Создание нового сотрудника.
    """
    existing = db.query(models.Employee).filter(
        models.Employee.phone == employee.phone
    ).first()

    if existing:
        raise EmployeeAlreadyExistsError(employee.phone)

    try:
        new_employee = crud.create_employee(db, employee)
        new_employee.age = calculate_age(new_employee.birth_date)
        return new_employee
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Ошибка при создании: {str(e)}"
            }
        )


@router.put(
    "/employees/{employee_id}",
    response_model=schemas.Employee
)
async def update_employee(
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление данных сотрудника.
    """
    existing = crud.get_employee(db, employee_id)
    if not existing:
        raise NotFoundError("Сотрудник", employee_id)

    if employee.phone != existing.phone:
        phone_exists = db.query(models.Employee).filter(
            models.Employee.phone == employee.phone,
            models.Employee.id != employee_id
        ).first()

        if phone_exists:
            raise EmployeeAlreadyExistsError(employee.phone)

    try:
        updated = crud.update_employee(db, employee_id, employee)
        updated.age = calculate_age(updated.birth_date)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Ошибка при обновлении: {str(e)}"
            }
        )


@router.delete(
    "/employees/{employee_id}"
)
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Удаление сотрудника.
    """
    existing = crud.get_employee(db, employee_id)
    if not existing:
        raise NotFoundError("Сотрудник", employee_id)

    try:
        if existing.photo_path:
            delete_photo(existing.photo_path)
        crud.delete_employee(db, employee_id)

        return {
            "status": "success",
            "message": f"Сотрудник #{employee_id} успешно удален",
            "deleted_id": employee_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": f"Ошибка при удалении: {str(e)}"
            }
        )

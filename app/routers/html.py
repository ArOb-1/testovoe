from fastapi import (APIRouter, Request, Depends,
                     Form, UploadFile, File, HTTPException, Query)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import crud, schemas
from app.utils import (
    parse_date, save_photo, delete_photo,
    parse_int_or_none, calculate_age
)
from app.config import config

router = APIRouter(prefix='', tags=['html'])
templates = Jinja2Templates(directory='templates')


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
    search: Optional[str] = None,
    gender: Optional[str] = None,
    age_from: Optional[str] = Query(None),
    age_to: Optional[str] = Query(None)
):
    """
    Главная страница с реестром сотрудников.
    Поддерживает пагинацию, поиск и фильтрацию.
    """
    per_page = config.PAGE_SIZE
    skip = (page - 1) * per_page

    age_from_int = parse_int_or_none(age_from)
    age_to_int = parse_int_or_none(age_to)

    employees, total = crud.get_employees(
        db,
        skip=skip,
        limit=per_page,
        search=search,
        gender=gender,
        age_from=age_from_int,
        age_to=age_to_int
    )
    for employee in employees:
        employee.age = calculate_age(employee.birth_date)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "employees": employees,
            "page": page,
            "total_pages": total_pages,
            "search": search,
            "gender": gender,
            "age_from": age_from,
            "age_to": age_to,
            "total": total
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@router.post("/create")
async def create_employee(
    request: Request,
    last_name: str = Form(...),
    first_name: str = Form(...),
    patronymic: Optional[str] = Form(None),
    phone: str = Form(...),
    birth_date: str = Form(...),
    gender: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Создание нового сотрудника.
    """
    try:
        birth_date_obj = parse_date(birth_date)
        photo_path = await save_photo(photo)

        employee_data = schemas.EmployeeCreate(
            last_name=last_name.strip(),
            first_name=first_name.strip(),
            patronymic=patronymic.strip() if patronymic else None,
            phone=phone.strip(),
            birth_date=birth_date_obj,
            gender=gender
        )

        crud.create_employee(db, employee_data, photo_path)

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "create.html",
            {"request": request, "error": f"Ошибка: {str(e)}"}
        )


@router.get("/edit/{employee_id}", response_class=HTMLResponse)
async def edit_form(
    request: Request,
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Страница редактирования сотрудника"""
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    employee.age = calculate_age(employee.birth_date)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "employee": employee}
    )


@router.post("/edit/{employee_id}")
async def edit_employee(
    request: Request,
    employee_id: int,
    last_name: str = Form(...),
    first_name: str = Form(...),
    patronymic: Optional[str] = Form(None),
    phone: str = Form(...),
    birth_date: str = Form(...),
    gender: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    delete_photo: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Обновление данных сотрудника.
    """
    try:
        employee = crud.get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")

        birth_date_obj = parse_date(birth_date)

        photo_path = employee.photo_path
        if delete_photo == "on":
            delete_photo(employee.photo_path)
            photo_path = None
        elif photo and photo.filename:
            delete_photo(employee.photo_path)
            photo_path = await save_photo(photo)

        employee_data = schemas.EmployeeUpdate(
            last_name=last_name.strip(),
            first_name=first_name.strip(),
            patronymic=patronymic.strip() if patronymic else None,
            phone=phone.strip(),
            birth_date=birth_date_obj,
            gender=gender
        )

        crud.update_employee(db, employee_id, employee_data, photo_path)

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        employee = crud.get_employee(db, employee_id)
        return templates.TemplateResponse(
            "edit.html",
            {"request": request,
             "employee": employee,
             "error": f"Ошибка: {str(e)}"}
        )


@router.post("/delete/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Удаление сотрудника с удалением фото"""
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    delete_photo(employee.photo_path)
    crud.delete_employee(db, employee_id)

    return RedirectResponse(url="/", status_code=303)

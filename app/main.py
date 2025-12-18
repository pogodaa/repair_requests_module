# app/main.py
from fastapi import FastAPI, Request, Depends, HTTPException, Form  # Request — из fastapi
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models import Base, User, RepairRequest  # модель под новым именем
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import auth
from app.crud import requests as crud_requests
from app.dependencies import require_role
from pathlib import Path
import uvicorn
from app.crud import users as crud_users
import re
from app.schemas.request import RequestCreate  # создадим его ниже

from datetime import datetime
from fastapi import Form

app = FastAPI(title="Учёт заявок на ремонт")

app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")

Base.metadata.create_all(bind=engine)

# Путь к шаблонам
templates = Jinja2Templates(directory=Path(__file__).parent / "frontend" / "templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.get("/", response_class=HTMLResponse)
# def index(request: Request, db: Session = Depends(get_db)):  # ← Request из fastapi
#     role = request.cookies.get("user_role")
#     user_id = request.cookies.get("user_id")
#     if not role or not user_id:
#         return RedirectResponse("/login")

#     user_id_int = int(user_id)
#     if role == "client":
#         requests = db.query(RepairRequest).filter(RepairRequest.clientID == user_id_int).all()
#     elif role == "specialist":
#         requests = db.query(RepairRequest).filter(RepairRequest.masterID == user_id_int).all()
#     else:
#         requests = db.query(RepairRequest).all()
    
#     users = {u.userID: u.fio for u in db.query(User).all()}

#     return templates.TemplateResponse("index.html", {
#         "request": request,  # ← важно: request из FastAPI
#         "requests": requests,
#         "user_role": role,
#         "current_user_id": user_id_int,
#         "get_user_fio": lambda uid: users.get(uid, f"ID{uid}")
#     })

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    role = request.cookies.get("user_role")
    user_id = request.cookies.get("user_id")
    if not role or not user_id:
        return RedirectResponse("/login")

    user_id_int = int(user_id)
    if role == "client":
        requests = db.query(RepairRequest).filter(RepairRequest.clientID == user_id_int).all()
    elif role == "specialist":
        requests = db.query(RepairRequest).filter(RepairRequest.masterID == user_id_int).all()
    else:
        requests = db.query(RepairRequest).all()
    
    # 🔥 Загружаем комментарии для КАЖДОЙ заявки
    for req in requests:
        req.comments = crud_requests.get_comments_by_request(db, req.requestID)
    
    users = {u.userID: u.fio for u in db.query(User).all()}

    return templates.TemplateResponse("index.html", {
        "request": request,
        "requests": requests,
        "user_role": role,
        "current_user_id": user_id_int,
        "get_user_fio": lambda uid: users.get(uid, f"ID{uid}")
    })

@app.get("/statistics", response_class=HTMLResponse)
def statistics(
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("operator", "specialist", "manager", "admin"))
):
    from app.services.statistics import calculate_avg_repair_time, count_completed_requests, get_top_equipment_types
    all_reqs = crud_requests.get_requests(db)  # ← получает из БД
    
    return templates.TemplateResponse("statistics.html", {
        "request": request,
        "completed_count": count_completed_requests(all_reqs),
        "avg_time": calculate_avg_repair_time(all_reqs),
        "top_types": get_top_equipment_types(all_reqs),
        "user_role": request.cookies.get("user_role")
    })

# app/main.py
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_role")
    response.delete_cookie("user_id")
    return response

@app.get("/assign/{request_id}")
def assign_form(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("manager", "admin"))
):
    # Только менеджер и админ могут назначать
    req = crud_requests.get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Получить всех специалистов
    specialists = db.query(User).filter(User.type == "Специалист").all()
    
    return templates.TemplateResponse("assign.html", {
        "request": request,
        "request_id": request_id,
        "specialists": specialists,
        "current_master": req.masterID
    })

@app.post("/assign/{request_id}")
def assign_master(
    request_id: int,
    masterID: int = Form(...),
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("manager", "admin"))
):
    # Обновляем заявку
    updated = crud_requests.update_request_status(db, request_id, "В процессе ремонта", master_id=masterID)
    if not updated:
        raise HTTPException(status_code=404, detail="Не удалось назначить специалиста")
    return RedirectResponse(url="/", status_code=303)

@app.get("/users", response_class=HTMLResponse)
def users_list(
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("manager", "admin"))
):
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "user_role": request.cookies.get("user_role")
    })

@app.post("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    new_role: str = Form(...),
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("manager", "admin"))
):
    crud_users.update_user_role(db, user_id, new_role)
    return RedirectResponse(url="/users", status_code=303)

app.include_router(auth.router)

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Валидаторы
def validate_fio(fio: str) -> bool:
    return 2 <= len(fio) <= 100 and re.fullmatch(r"[а-яА-ЯёЁa-zA-Z\s\-]+", fio) is not None

def validate_phone(phone: str) -> bool:
    # Убираем всё, кроме цифр
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 15

def validate_login(login: str) -> bool:
    return 3 <= len(login) <= 50 and re.fullmatch(r"[a-zA-Z0-9_-]+", login) is not None

def validate_password(password: str) -> bool:
    if not (6 <= len(password) <= 128):
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit
    
@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    fio: str = Form(...),
    phone: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # === Валидация ===
    errors = []

    if not validate_fio(fio):
        errors.append("ФИО должно содержать только буквы, пробелы и дефисы, длина 2–100 символов.")
    if not validate_phone(phone):
        errors.append("Номер телефона должен содержать 10–15 цифр.")
    if not validate_login(login):
        errors.append("Логин: 3–50 символов, только латинские буквы, цифры, _ и -.")
    if not validate_password(password):
        errors.append("Пароль: 6–128 символов, должен содержать хотя бы одну букву и одну цифру.")

    if errors:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": " • ".join(errors)},
            status_code=400
        )

    # Проверка уникальности логина
    if crud_users.get_user_by_login(db, login):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Пользователь с таким логином уже существует."},
            status_code=400
        )

    # Создание пользователя
    crud_users.create_user(db, fio, phone, login, password, role="Заказчик")
    return RedirectResponse(url="/login?registered=1", status_code=303)

@app.get("/create-request", response_class=HTMLResponse)
def create_request_form(
    request: Request,
    user_role: str = Depends(require_role("client"))
):
    # Только клиент может создавать
    return templates.TemplateResponse("create_request.html", {
        "request": request,
        "user_role": user_role,
        "current_user_id": int(request.cookies.get("user_id"))
    })

@app.post("/create-request")
def create_request(
    climateTechType: str = Form(...),
    climateTechModel: str = Form(...),
    problemDescryption: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user_id = int(request.cookies.get("user_id"))
    new_request = {
        "startDate": datetime.now().strftime("%Y-%m-%d"),
        "climateTechType": climateTechType,
        "climateTechModel": climateTechModel,
        "problemDescryption": problemDescryption,
        "requestStatus": "Новая заявка",
        "completionDate": None,
        "repairParts": None,
        "masterID": None,
        "clientID": user_id
    }
    crud_requests.create_request(db, new_request)
    return RedirectResponse(url="/", status_code=303)

# === Редактирование заявки ===
@app.get("/edit/{request_id}", response_class=HTMLResponse)
def edit_request_form(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("operator", "manager", "admin"))
):
    req = crud_requests.get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Получаем ФИО клиента
    client = db.query(User).filter(User.userID == req.clientID).first()
    client_fio = client.fio if client else f"ID{req.clientID}"
    client_login = client.login if client else ""
    
    return templates.TemplateResponse("edit_request.html", {
        "request": request,
        "req": req,
        "client_fio": client_fio,
        "client_login": client_login,
        "user_role": request.cookies.get("user_role")
    })

@app.post("/edit/{request_id}")
def edit_request(
    request_id: int,
    climateTechType: str = Form(...),
    climateTechModel: str = Form(...),
    problemDescryption: str = Form(...),
    requestStatus: str = Form(...),
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("operator", "manager", "admin"))
):
    req = crud_requests.get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Обновляем данные
    req.climateTechType = climateTechType
    req.climateTechModel = climateTechModel
    req.problemDescryption = problemDescryption
    req.requestStatus = requestStatus
    
    # Автоматически ставим дату завершения, если статус "Готова к выдаче"
    if requestStatus == "Готова к выдаче":
        if not req.completionDate:  # только если ещё не установлена
            req.completionDate = datetime.now().strftime("%Y-%m-%d")
    else:
        # Если статус НЕ "Готова к выдаче" — обнуляем дату
        req.completionDate = None

    db.commit()
    db.refresh(req)
    return RedirectResponse(url="/", status_code=303)

@app.get("/comment/{request_id}", response_class=HTMLResponse)
def comment_form(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_role: str = Depends(require_role("specialist"))
):
    # Убедимся, что специалист назначен на эту заявку
    user_id = int(request.cookies.get("user_id"))
    req = crud_requests.get_request(db, request_id)
    if not req or req.masterID != user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    return templates.TemplateResponse("add_comment.html", {
        "request": request,
        "request_id": request_id,
        "user_role": user_role
    })

@app.post("/comment/{request_id}")
def add_comment(
    request_id: int,
    message: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("specialist"))
):
    user_id = int(request.cookies.get("user_id"))
    req = crud_requests.get_request(db, request_id)
    if not req or req.masterID != user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    crud_requests.create_comment(db, request_id, user_id, message)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
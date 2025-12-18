# app/crud/users.py
from sqlalchemy.orm import Session
from app.models import User

def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Сравнивает введённый пароль с сохранённым (в открытом виде).
    """
    return plain_password == stored_password

def get_password_hash(password: str) -> str:
    """
    В учебном проекте пароль хранится в открытом виде.
    В промышленной системе здесь должно быть хеширование.
    """
    return password

def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()

def create_user(db: Session, fio: str, phone: str, login: str, password: str, role: str = "Заказчик"):
    db_user = User(
        fio=fio,
        phone=phone,
        login=login,
        password=get_password_hash(password),  # открытый пароль
        type=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, new_role: str):
    user = db.query(User).filter(User.userID == user_id).first()
    if user and user.type != "Админ":  # Защита админа
        user.type = new_role
        db.commit()
        db.refresh(user)
    return user
# app/schemas/user.py
from pydantic import BaseModel

class UserRegister(BaseModel):
    fio: str
    phone: str
    login: str
    password: str
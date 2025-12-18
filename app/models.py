# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    userID = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "Заказчик", "Оператор", "Специалист", "Менеджер"
 
class RepairRequest(Base):  #  было Request
    __tablename__ = "requests"
    requestID = Column(Integer, primary_key=True, index=True)
    startDate = Column(String, nullable=False)  # YYYY-MM-DD
    climateTechType = Column(String, nullable=False)
    climateTechModel = Column(String, nullable=False)
    problemDescryption = Column(Text, nullable=False)
    requestStatus = Column(String, nullable=False)  # "Новая заявка", "В процессе ремонта", "Готова к выдаче"
    completionDate = Column(String, nullable=True)
    repairParts = Column(Text, nullable=True)
    masterID = Column(Integer, ForeignKey("users.userID"), nullable=True)
    clientID = Column(Integer, ForeignKey("users.userID"), nullable=False)

class Comment(Base):
    __tablename__ = "comments"
    commentID = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    masterID = Column(Integer, ForeignKey("users.userID"), nullable=False)
    requestID = Column(Integer, ForeignKey("requests.requestID"), nullable=False)
    created_at = Column(String, default=datetime.now().strftime("%Y-%m-%d %H:%M"))  # ← НОВОЕ ПОЛЕ
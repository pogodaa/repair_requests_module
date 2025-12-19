# app/crud/requests.py
from sqlalchemy.orm import Session
from app.models import RepairRequest, User, Comment

def get_requests(db: Session, skip: int = 0, limit: int = 100):
    requests = db.query(RepairRequest).offset(skip).limit(limit).all()
    # Загружаем комментарии для каждой заявки
    for req in requests:
        req.comments = db.query(Comment).filter(Comment.requestID == req.requestID).all()
    return requests

def get_request(db: Session, request_id: int):
    req = db.query(RepairRequest).filter(RepairRequest.requestID == request_id).first()
    if req:
        req.comments = db.query(Comment).filter(Comment.requestID == request_id).all()
    return req

def create_request(db: Session, request_data: dict):
    db_request = RepairRequest(**request_data)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def update_request_status(db: Session, request_id: int, new_status: str, master_id: int = None):
    request = get_request(db, request_id)
    if request:
        request.requestStatus = new_status
        if master_id:
            request.masterID = master_id
        db.commit()
        db.refresh(request)
    return request

def get_comments_by_request(db: Session, request_id: int):
    return db.query(Comment).filter(Comment.requestID == request_id).all()

# def create_comment(db: Session, request_id: int, master_id: int, message: str):
#     db_comment = Comment(
#         message=message,
#         masterID=master_id,
#         requestID=request_id
#     )
#     db.add(db_comment)
#     db.commit()
#     db.refresh(db_comment)
#     return db_comment

# def get_comments_by_request(db: Session, request_id: int):
#     return db.query(Comment).filter(Comment.requestID == request_id).all()

def create_comment(db: Session, request_id: int, master_id: int, message: str):
    db_comment = Comment(
        message=message,
        masterID=master_id,
        requestID=request_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_by_request(db: Session, request_id: int):
    return db.query(Comment).filter(Comment.requestID == request_id).all()
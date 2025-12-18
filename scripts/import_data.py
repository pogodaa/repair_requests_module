# # scripts/import_data.py
# import pandas as pd
# from sqlalchemy.orm import sessionmaker
# from app.database.database import engine
# from app.models import User, RepairRequest as Request, Comment  # ← исправлено!

# Session = sessionmaker(bind=engine)
# session = Session()

# # Добавляем админа с userID = 0
# admin_exists = session.query(User).filter(User.login == "admin").first()
# if not admin_exists:
#     admin = User(
#         userID=0,  # ← именно 0, как ты просил
#         fio="Администратор Системы",
#         phone="88005553535",
#         login="admin",
#         password="admin",
#         type="Админ"
#     )
#     session.add(admin)
#     session.commit()

# def import_users():
#     df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Пользователи/inputDataUsers.xlsx")
#     for _, row in df.iterrows():
#         user = User(
#             userID=row["userID"],
#             fio=row["fio"],
#             phone=row["phone"],
#             login=row["login"],
#             password=row["password"],
#             type=row["type"]
#         )
#         session.merge(user)

# def import_requests():
#     df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Заявки/inputDataRequests.xlsx")
#     for _, row in df.iterrows():
#         req = Request(  # ← теперь это RepairRequest, но с псевдонимом Request
#             requestID=row["requestID"],
#             startDate=str(row["startDate"]),
#             climateTechType=row["climateTechType"],
#             climateTechModel=row["climateTechModel"],
#             problemDescryption=row["problemDescryption"],
#             requestStatus=row["requestStatus"],
#             completionDate=str(row["completionDate"]) if pd.notna(row["completionDate"]) else None,
#             repairParts=row["repairParts"] if pd.notna(row["repairParts"]) else None,
#             masterID=int(row["masterID"]) if pd.notna(row["masterID"]) else None,
#             clientID=int(row["clientID"])
#         )
#         session.merge(req)

# def import_comments():
#     df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Комментарии/inputDataComments.xlsx")
#     for _, row in df.iterrows():
#         comment = Comment(
#             commentID=row["commentID"],
#             message=row["message"],
#             masterID=row["masterID"],
#             requestID=row["requestID"]
#         )
#         session.merge(comment)

# if __name__ == "__main__":
#     import_users()
#     import_requests()
#     import_comments()
#     session.commit()
#     session.close()
#     print("✅ Данные успешно импортированы в SQLite")

# scripts/import_data.py
import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.database.database import engine
from app.models import User, RepairRequest as Request, Comment

Session = sessionmaker(bind=engine)
session = Session()

# Добавляем админа с userID = 0
admin_exists = session.query(User).filter(User.login == "admin").first()
if not admin_exists:
    admin = User(
        userID=0,
        fio="Администратор Системы",
        phone="88005553535",
        login="admin",
        password="admin",
        type="Админ"
    )
    session.add(admin)
    session.commit()

def import_users():
    df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Пользователи/inputDataUsers.xlsx")
    for _, row in df.iterrows():
        user = User(
            userID=row["userID"],
            fio=row["fio"],
            phone=row["phone"],
            login=row["login"],
            password=row["password"],
            type=row["type"]
        )
        session.merge(user)

def import_requests():
    df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Заявки/inputDataRequests.xlsx")
    for _, row in df.iterrows():
        req = Request(
            requestID=row["requestID"],
            startDate=str(row["startDate"]),
            climateTechType=row["climateTechType"],
            climateTechModel=row["climateTechModel"],
            problemDescryption=row["problemDescryption"],
            requestStatus=row["requestStatus"],
            completionDate=str(row["completionDate"]) if pd.notna(row["completionDate"]) else None,
            repairParts=row["repairParts"] if pd.notna(row["repairParts"]) else None,
            masterID=int(row["masterID"]) if pd.notna(row["masterID"]) else None,
            clientID=int(row["clientID"])
        )
        session.merge(req)

def import_comments():
    df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Комментарии/inputDataComments.xlsx")
    
    # Загрузим заявки в словарь для быстрого доступа
    requests_df = pd.read_excel("docs/src/Ресурсы/Кондиционеры_данные/Заявки/inputDataRequests.xlsx")
    request_dates = dict(zip(requests_df["requestID"], requests_df["startDate"]))
    
    for _, row in df.iterrows():
        # Получаем дату создания заявки
        request_id = row["requestID"]
        comment_date = str(request_dates.get(request_id, pd.Timestamp.today().strftime("%Y-%m-%d")))
        
        comment = Comment(
            commentID=row["commentID"],
            message=row["message"],
            masterID=row["masterID"],
            requestID=request_id,
            created_at=comment_date  # ← дата = дата заявки
        )
        session.merge(comment)

if __name__ == "__main__":
    import_users()
    import_requests()
    import_comments()
    session.commit()
    session.close()
    print("✅ Данные успешно импортированы в SQLite")
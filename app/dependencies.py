# app/dependencies.py
from fastapi import HTTPException, Request

def require_role(*allowed_roles: str):
    def role_checker(request: Request):
        user_role = request.cookies.get("user_role")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        return True
    return role_checker
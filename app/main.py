# uvicorn app.main:app --reload

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI(title="Учёт заявок на ремонт")

# Монтируем папку с шаблонами
templates = Jinja2Templates(directory="app/frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/statistics", response_class=HTMLResponse)
async def statistics():
    # Здесь можно передавать данные из сервиса, но для Задания 1 — просто показываем статику
    return templates.TemplateResponse("statistics.html", {"request": {}})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
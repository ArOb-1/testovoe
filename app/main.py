from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from app.database import engine
from app import models
from app.routers import html_router, api_router
from app.config import config


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Реестр сотрудников",
    description="Веб-модуль для управления сотрудниками с REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="static/uploads"), name="uploads")

app.include_router(html_router)
app.include_router(api_router)


@app.get("/info")
async def info():
    return {
        "name": "Реестр сотрудников",
        "version": "1.0.0",
        "endpoints": {
            "web": {
                "list": "/",
                "create": "/create",
                "edit": "/edit/{id}",
                "delete": "/delete/{id}"
            },
            "api": {
                "list": "GET /api/employees",
                "get": "GET /api/employees/{id}",
                "create": "POST /api/employees",
                "update": "PUT /api/employees/{id}",
                "delete": "DELETE /api/employees/{id}",
                "docs": "/api/docs"
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
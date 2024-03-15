from fastapi import APIRouter
from server.api.api_v1.endpoints import printer


api_router = APIRouter()
api_router.include_router(printer.router, tags=["Работа с принтерами"])

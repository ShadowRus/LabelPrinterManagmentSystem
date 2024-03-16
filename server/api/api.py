from fastapi import APIRouter
from server.api.api_v1.endpoints import printer
from server.api.api_v1.endpoints import sgd


api_router = APIRouter()
api_router.include_router(printer.router, tags=["Работа с принтерами"])
api_router.include_router(sgd.router, tags=["SGD команды для отправки на принтер"])

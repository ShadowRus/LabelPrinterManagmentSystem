from fastapi import APIRouter
from fastapi.responses import JSONResponse
from server.service.service import sgd_cmd,get_sgd,set_sgd,do_sgd,get_current_set,gala
router = APIRouter()

@router.get("/setvalue",summary="Изменить настройку",description="Отправка управляющей команды на принтер")
def set_sgd_to_print(host:str,port:int,set_key:str,set_value:str):
    return sgd_cmd(host,port,set_sgd(set_key,set_value))

@router.get("/getvalue",summary="Получить значение настройки",description="Получение значения настройки от принтера")
def get_sgd_to_print(host:str,port:int,get_key:str):
    return sgd_cmd(host,port,get_sgd(get_key))

@router.get("/do",summary="Вызвать действие на принтере",description="Отправить команду DО на принтер")
def do_sgd_to_print(host:str,port:int,cmd:str):
    return sgd_cmd(host,port,do_sgd(cmd))

@router.get("/current_set",summary="Получить значение текущих настроек",description="Получение значения настройки от принтера")
def get_sgd_to_print(host:str,port:int):

    return JSONResponse(status_code=200, content={'status': get_current_set(host,port,gala)})
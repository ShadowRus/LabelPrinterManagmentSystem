import json

from fastapi import APIRouter, UploadFile, File, Body, Depends, Request
from fastapi.responses import JSONResponse
from server.models.Printer import Printers, PrintersInfo,PrintersSettings
from server.schema.AddEditPrinterInfo import AddPrinter
from sqlalchemy.orm import Session
from decouple import config
from server.api import deps
from server.service.service import sgd_cmd,get_sgd,info,current_set,rename,gala,set_sgd
import os
import datetime

SGD_GALA = config('SGD_GALA')
now = datetime.datetime.now()
router = APIRouter()





@router.post("/printer", summary="Добавляем принтер в БД",
             description="Отправка на сервер файла конфигурации ")
def post_config_bd(data:AddPrinter,db: Session = Depends(deps.get_db)):
    if 2 == 2:
        # Добавляем принтер
        printer_temp = Printers(model = data.model,
                                port = data.port,
                                url = data.url,
                                in_use = data.in_use,
                                is_deleted = 0,
                                add_time = datetime.datetime.now().strftime('%y-%m-%d-%H-%M-%S'))
        db.add(printer_temp)
        db.commit()
        db.refresh(printer_temp)
        # Уточняем серийный номер принтера
        if printer_temp.serial == None:
            printer_temp.serial = sgd_cmd(printer_temp.url,printer_temp.port,get_sgd("serial_no"))
        # Уточняем модель
        if printer_temp.vendor_model == None:
            printer_temp.vendor_model = sgd_cmd(printer_temp.url, printer_temp.port, get_sgd("printer_name"))
        db.commit()
        db.refresh(printer_temp)
        printer_temp.model = rename(printer_temp.vendor_model)
        db.commit()
        db.refresh(printer_temp)
        if printer_temp.vendor_model in ['Gala', 'Glory', 'Glory-L']:
            printer_info_temp = info(printer_temp,gala)
            db.add(printer_info_temp)
            db.commit()
            db.refresh(printer_info_temp)
            printer_cur_set = current_set(printer_temp,gala)
            db.add(printer_cur_set)
            db.commit()
            db.refresh(printer_cur_set)
        return JSONResponse(status_code=200, content={'status': printer_temp.id})

@router.get("/sgd",summary="Отправка SGD",description="Отправка управляющей команды на принтер")
def set_sgd_to_print(host:str,port:int,set_key:str,set_value:str):
    print(set_sgd(set_key,set_value))
    return sgd_cmd(host,port,set_sgd(set_key,set_value))

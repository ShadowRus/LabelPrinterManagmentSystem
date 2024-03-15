from fastapi import APIRouter, UploadFile, File, Body, Depends, Request
from fastapi.responses import JSONResponse
from server.models.Printer import Printers
from server.schema.AddEditPrinterInfo import AddPrinter
from sqlalchemy.orm import Session
from decouple import config
from server.api import deps
import os
import datetime

now = datetime.datetime.now()
router = APIRouter()

def sgd_cmd(host,port,sgd):
    import socket
    mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        mysocket.connect((host,port))
        mysocket.settimeout(5)
        mysocket.send(sgd)
        return mysocket.recv(4096).decode('utf-8')[:-1]
    except:
        return None
    finally:
        mysocket.close()

def zpl_cmd(host,port,zpl):
    return

def rename(printer_name):
    if printer_name == 'Gala':
        return 'ATOL TT631'
    if printer_name == 'Glory-L':
        return 'ATOL TT621'
    if printer_name in ['HT800-203','HT830']:
        return 'ATOL TT43'
    if printer_name in ['Apollo','Apollo Pro-203']:
        return 'ATOL TT44'
    else:
        return printer_name

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
            printer_temp.serial = sgd_cmd(printer_temp.url,printer_temp.port,b'\x1b\x1c& V1 getval "serial_no"\r\n')
        # Уточняем модель
        if printer_temp.vendor_model == None:
            printer_temp.vendor_model = sgd_cmd(printer_temp.url, printer_temp.port, b'\x1b\x1c& V1 getval "printer_name"\r\n')
        db.commit()
        db.refresh(printer_temp)
        printer_temp.model = rename(printer_temp.vendor_model)
        db.commit()
        db.refresh(printer_temp)

        return JSONResponse(status_code=200, content={'status': printer_temp.id})

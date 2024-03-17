

from fastapi import APIRouter, UploadFile, File, Body, Depends, Request
from fastapi.responses import JSONResponse
from server.models.Printer import Printers, PrintersInfo,PrintersSettings
from server.schema.AddEditPrinterInfo import AddPrinter,SyhchPrinter
from sqlalchemy.orm import Session
from decouple import config
from server.api import deps
from server.service.service import sgd_cmd,get_sgd,get_info,get_current_set,rename,gala,set_sgd,do_sgd,check_ip_adresses
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

        # # Делаем проверку что такого серийника нет больше в списке, если есть, то помечаем на удаление первый встретившийся
        # if len(db.query(Printers).filter(Printers.serial == printer_temp.serial).all()) >= 2:
        #     pr_2 = db.query(Printers).filter(Printers.serial == printer_temp.serial).first()
        #     if sgd_cmd(pr_2.url, pr_2.port, get_sgd("serial_no")) != pr_2.serial:
        #         pr_2.is_deleted = 1
        #         db.commit()
        # if sgd_cmd(printer_temp.url, printer_temp.port, get_sgd("serial_no")) == printer_temp.serial:
        #     # Делаем проверку что на этом порту больше никого нет если есть, то помечаем на удаление первый встретившийся
        #     # Делаем проверку тут потому что мы только что проверили что порт отвечает и живой
        #     if len(db.query(Printers).filter(Printers.url == printer_temp.url).all()) >= 2:
        #         pr_2 = db.query(Printers).filter(Printers.url == printer_temp.url).first()
        #         pr_2.is_deleted = 1
        #         db.commit()


        # Уточняем модель
        if printer_temp.vendor_model == None:
            printer_temp.vendor_model = sgd_cmd(printer_temp.url, printer_temp.port, get_sgd("printer_name"))
        db.commit()
        db.refresh(printer_temp)
        printer_temp.model = rename(printer_temp.vendor_model)
        db.commit()
        db.refresh(printer_temp)

        if printer_temp.vendor_model in ['Gala', 'Glory', 'Glory-L']:
            printer_info_temp = get_info(printer_temp, gala)
            db.add(printer_info_temp)
            db.commit()
            db.refresh(printer_info_temp)
            printer_cur_set = get_current_set(printer_temp, gala)
            db.add(printer_cur_set)
            db.commit()
            db.refresh(printer_cur_set)
        return JSONResponse(status_code=200, content={'status': printer_temp.id})

# @router.post("/synch", summary="Синхронизация данных по принтеру",
#              description="Опрашиваем принтер и актуализируем текущие настройки в базе для принтера")
# def synch_printer_info(data: SyhchPrinter,db: Session = Depends(deps.get_db)):
#     if 'serial' in data:
#         temp = db.query(Printers).filter(Printers.serial == data.serial).first()
#         if temp != None:
#
#     if 'url' in data:
#         d=4
#     if 'printer_id' in data:
#         d=4
#     if 'inv_num' in data:
#         d = 5
#
#
#     return JSONResponse(status_code=200, content={'status': 'OK'})


@router.get('/scan',summary="Поиск подключенных принтеров",description="Сканируем локальную сеть в диапазоне, который передаем")
def scan_printers(network:str,port:int):
    printers = check_ip_adresses(network,port)
    print_res = {}
    for print in printers:
        serial = sgd_cmd(print,int(port),get_sgd(gala['getval']["serial_no"]))
        if serial != None:
            print_res[print] = serial
    return print_res





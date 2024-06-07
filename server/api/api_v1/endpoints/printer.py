
from fastapi import APIRouter, UploadFile, File, Body, Depends, Request
from fastapi.responses import JSONResponse
from server.models.Printer import Printers, PrintersInfo ,PrintersSettings
from server.schema.AddEditPrinterInfo import AddPrinter ,SyhchPrinter,PrinterID
from sqlalchemy.orm import Session
from decouple import config
from server.api import deps
from server.service.service import sgd_cmd ,get_sgd ,get_info ,update_info,get_current_set ,rename ,tt6xx,tt44_43,tt42,cmd_dict ,check_ip_adresses,SERIAL_NO,VENDOR_MODEL,get_value_or_none
import os
import datetime

now = datetime.datetime.now()
router = APIRouter()





@router.get("/printers",summary="Получаем информацию о принтерах в базе PRINTERS",
             description="Выгрузка их базы ")
def get_printers(db: Session = Depends(deps.get_db)):
    return db.query(Printers).filter(Printers.is_deleted== 0).all()


@router.get("/printers/info",summary="Получаем информацию о принтерах в базе PRINTERS_INFO",
             description="Выгрузка их базы ")
def get_printers(db: Session = Depends(deps.get_db)):
    return db.query(PrintersInfo).all()

@router.get("/printers/current_settings",summary="Получаем информацию о принтерах в базе PRINTER_CURRENT_SETTINGS",
             description="Выгрузка их из базы ")
def get_printers(db: Session = Depends(deps.get_db)):
    return db.query(PrintersSettings).all()


@router.post("/printer", summary="Добавляем принтер в БД",
             description="Добавляется серийный номер, инвентарный номер, местоположение,")
def post_printer(data: AddPrinter ,db: Session = Depends(deps.get_db)):
    try:
        if data.serial != None:
            if db.query(Printers).filter(Printers.serial == data.serial).first():
                return JSONResponse(status_code=500, content={'status': f'Serial {data.serial} is already exists'})
        # Добавляем принтер
        # Создаем запись:
        printer_temp = Printers(in_use = data.in_use,
                                is_deleted = 0,
                                add_time = datetime.datetime.now().strftime('%y-%m-%d-%H-%M-%S'))
        db.add(printer_temp)
        db.commit()
        db.refresh(printer_temp)
        # Заполянем поля, которые есть
        if data.serial != None:
            printer_temp.serial = data.serial
            db.commit()
            db.refresh(printer_temp)
        if data.location != None:
            printer_temp.location = data.location
            db.commit()
            db.refresh(printer_temp)
        if data.print_name != None:
            printer_temp.print_name = data.print_name
            db.commit()
            db.refresh(printer_temp)
        if data.inv_num != None:
            printer_temp.inv_num = data.inv_num
            db.commit()
            db.refresh(printer_temp)
        if data.in_use == 1:
            if data.url != None:
                printer_name = rename(str(repeat_sgd_cmd(host, port, get_sgd(VENDOR_MODEL))), rename_atol)
                serial = sgd_cmd(data.url, data.port, get_sgd(SERIAL_NO))
                print(f'Serial: {serial}')
                if data.serial == None:
                    if db.query(Printers).filter(Printers.serial == serial).first() == None:
                        printer_temp.serial = serial
                        db.commit()
                        db.refresh(printer_temp)
        return JSONResponse(status_code=200, content={'status': printer_temp.id})
    except:
        return JSONResponse(status_code=500, content={'status':'Try later'})


@router.post("/printer/info")
def post_printer_info(data:PrinterID,db: Session = Depends(deps.get_db)):
    try:
        printer_temp = db.query(Printers).filter(Printers.id == data.printer_id).first()
        if printer_temp != None:
            if 'url' not in dict(data) and printer_temp.serial is not None:
                # узнаем ip4-адрес принтера
                if 'network' not in dict(data):
                    data.network = '192.168.0.0/24'
                list_print = check_ip_adresses(data.network, 9100)
                data.url = list_print[printer_temp.serial]
            g1 = cmd_dict(sgd_cmd(data.url, data.port, get_sgd(VENDOR_MODEL)))
            printer_info = db.query(PrintersInfo).filter(PrintersInfo.printer_id == data.printer_id).first()
            if printer_info == None:
                printer_info = get_info(data,g1)
                db.add(printer_info)
            else:
                printer_info=update_info(data,g1)
            db.commit()
            db.refresh(printer_info)
            return JSONResponse(status_code=200, content={'status': printer_temp.id})
    except:
        return JSONResponse(status_code=500, content={'status': 'Try later'})


@router.get("printer/info",summary="Получаем информацию о принтере",
             description="Данные по принтеру: пробег, мо")
def get_pr_info(printer_id:int,db: Session = Depends(deps.get_db)):
    try:
        temp = db.query(PrintersInfo).filter(PrintersInfo.printer_id == printer_id).first()
        return temp
    except:
        return JSONResponse(status_code=500, content={'error': printer_id})

@router.put("printer/info")
def put_printer_info(db: Session = Depends(deps.get_db)):
    pass

@router.post("printer/current_set")
def post_current_set(db: Session = Depends(deps.get_db)):
    pass

@router.get("printer/current_set")
def get_current_set(db: Session = Depends(deps.get_db)):
    pass





@router.get('/scan' ,summary="Поиск подключенных принтеров"
            ,description="Сканируем локальную сеть в диапазоне, который передаем")
def scan_printers(network :str ,port :int):
    printers = check_ip_adresses(network ,port)
    print_res = {}
    for print in printers:
        serial = sgd_cmd(print ,int(port) ,get_sgd(gala['getval']["serial_no"]))
        if serial != None:
            print_res[print] = serial
    return print_res




# def post_printer(data :AddPrinter ,db: Session = Depends(deps.get_db)):
#     if 2 == 2:
#         print(f'data {data}')
#         if 'serial' in dict(data):
#             if db.query(Printers).filter(Printers.serial == data.serial).first():
#                 return JSONResponse(status_code=500, content={'status': f'Serial {data.serial} is already exists'})
#         # Добавляем принтер
#         # Создаем запись:
#         printer_temp = Printers(in_use = data.in_use,
#                                 is_deleted = 0,
#                                 add_time = datetime.datetime.now().strftime('%y-%m-%d-%H-%M-%S'))
#         db.add(printer_temp)
#         db.commit()
#         db.refresh(printer_temp)
#         # Заполянем поля, которые есть
#         if 'serial' in dict(data):
#             printer_temp.serial = data.serial
#             db.commit()
#             db.refresh(printer_temp)
#         if 'location' in dict(data):
#             printer_temp.location = data.location
#             db.commit()
#             db.refresh(printer_temp)
#         if 'print_name' in dict(data):
#             printer_temp.print_name = data.print_name
#             db.commit()
#             db.refresh(printer_temp)
#         if 'inv_num' in dict(data):
#             printer_temp.inv_num = data.inv_num
#             db.commit()
#             db.refresh(printer_temp)
#         if 'print_name' in dict(data):
#             printer_temp.print_name = data.print_name
#             db.commit()
#             db.refresh(printer_temp)
#
#         # если устройство подключено:
#         if data.in_use == 1:
#             if 'url' in dict(data):
#                 serial = sgd_cmd(data.url, data.port, get_sgd(gala['getval']["serial_no"]))
#                 # print(f'serial {serial}')
#                 if printer_temp.serial == None and serial != None:
#                     #Узнаем серийный серийный номер принтера
#                     printer_temp.serial = serial
#                     # print(f'printer_temp.serial {printer_temp.serial}')
#                     db.commit()
#                     db.refresh(printer_temp)
#                 if printer_temp.serial != None and serial != None:
#                     if printer_temp.serial != serial:
#                         data.in_use = 0
#                         data.url = None
#             if 'url' not in dict(data) and 'serial' in dict(data):
#                 # узнаем ip4-адрес принтера
#                 if 'network' not in dict(data):
#                     data.network = '192.168.0.0/24'
#                 list_print = check_ip_adresses(data.network, 9100)
#                 data.url = list_print[printer_temp.serial]
#
#         printer_info = PrintersInfo(printer_id=printer_temp.id, url=data.url,
#                                         port=data.port)
#         db.add(printer_info)
#         db.commit()
#         db.refresh(printer_info)
#         if data.in_use == 1:
#             # заполянем ИНФО о принтере
#             if printer_info.vendor_model == None:
#                 printer_info.vendor_model = sgd_cmd(printer_info.url, printer_info.port,
#                                                     get_sgd(gala['getval']["model"]))
#                 # printer_info.vendor_model = sgd_cmd(printer_info.url, printer_info.port,
#                 #                                     get_sgd("printer_name"))
#                 printer_info.model = rename(printer_info.vendor_model)
#
#
#
#
#
#             printer_info.mileage =sgd_cmd(printer_info.url, printer_info.port, get_sgd(gala['getval']['mileage']))
#             printer_info.cutter_cnt = sgd_cmd(printer_info.url, printer_info.port,
#                                               get_sgd(gala['getval']["cutter_cnt"]))
#             printer_info.dpi = sgd_cmd(printer_info.url, printer_info.port,
#                                        get_sgd(gala['getval']["dpi"]))
#             printer_info.version = sgd_cmd(printer_info.url, printer_info.port,
#                                            get_sgd(gala['getval']["printer_version"]))
#             printer_info.eth_mac = sgd_cmd(printer_info.url, printer_info.port,
#                                            get_sgd(gala['getval']["eth_mac"]))
#             printer_info.wlan_mac = sgd_cmd(printer_info.url, printer_info.port,
#                                             get_sgd(gala['getval']["wlan_mac"]))
#             db.commit()
#             db.refresh(printer_info)
#
#             printer_cur_set = get_current_set(printer_info, gala)
#             db.add(printer_cur_set)
#             db.commit()
#             db.refresh(printer_cur_set)
#             return JSONResponse(status_code=200, content={'status': printer_temp.id})
#         if printer_temp.serial == None and printer_info.url == None:
#             printer_temp.is_deleted = 1
#             db.commit()
#             db.refresh(printer_temp)
#             return JSONResponse(status_code=500, content={'status': 'Not enough data for added printer '})
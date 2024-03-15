import json

from fastapi import APIRouter, UploadFile, File, Body, Depends, Request
from fastapi.responses import JSONResponse
from server.models.Printer import Printers, PrintersInfo,PrintersSettings
from server.schema.AddEditPrinterInfo import AddPrinter
from sqlalchemy.orm import Session
from decouple import config
from server.api import deps
import os
import datetime

SGD_GALA = config('SGD_GALA')
now = datetime.datetime.now()
router = APIRouter()


def read_json_to_dict(json_file_path):
    with open(json_file_path,'r',encoding='utf-8') as file:
        return json.load(file)
gala = read_json_to_dict(SGD_GALA)

def get_sgd(get_value):
    s1 = f'\x1b\x1c& V1 getval "{get_value}"\r\n'
    return s1.encode()

def info(printer_temp,gala):
    printer_info_temp = PrintersInfo(
        printer_id=printer_temp.id,
        mileage=int(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['mileage'])), 16)*10,
        cutter_cnt=int(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['cutter_cnt']))),
        dpi=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['dpi']))),
        version=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_version']))),
        eth_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_mac']))),
        wlan_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mac'])))
    )
    return printer_info_temp

def current_set(printer_temp,gala):
    printer_settings_temp = PrintersSettings(
        printer_id = printer_temp.id,
        sw_ribbon = str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['sw_ribbon']))),
        print_mode=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['print_mode']))),
        tear_off=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['tear_off']))),
        sensor_select=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['sensor_select']))),
        media_power_up=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['media_power_up']))),
        head_close=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['head_close']))),
        buzzer=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['buzzer']))),
        speed=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['speed']))),
        density=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['density']))),
        media_sensor=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['media_sensor']))),
        ethernet_switch=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['ethernet_switch']))),
        eth_dhcp=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_dhcp']))),
        eth_ip=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_ip']))),
        eth_mask=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_mask']))),
        eth_gateway=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_gateway']))),
        eth_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_mac']))),
        wlan_mod=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mode']))),
        wlan_ssid=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_ssid']))),
        wlan_key=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_key']))),
        wlan_dhcp=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_dhcp']))),
        wlan_ip=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_ip']))),
        wlan_mask=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mask']))),
        wlan_gateway=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_gateway']))),
        wlan_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mac']))),
        wlan_key_require=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_key_require']))),
        printer_time_year=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_year']))),
        printer_time_month=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_month']))),
        printer_time_day=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_day']))),
        printer_time_hour=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_hour']))),
        printer_time_minute=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_minute']))),
        printer_time_second=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_second'])))
    )
    return printer_settings_temp

def sgd_cmd(host,port,sgd):
    import socket
    mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        mysocket.connect((host,port))
        mysocket.settimeout(5)
        mysocket.send(sgd)
        a1 = b'\x00'
        a1 = a1.decode('utf-8')
        recv = mysocket.recv(4096).decode('utf-8')
        if recv[-1] == a1:
            return recv[:-1]
        else:
            return recv
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
            # printer_info_temp = PrintersInfo(
            #     printer_id = printer_temp.id,
            #     mileage = int(sgd_cmd(printer_temp.url,printer_temp.port,get_sgd(gala['getval']['mileage'])),16),
            #     cutter_cnt = int(sgd_cmd(printer_temp.url,printer_temp.port,get_sgd(gala['getval']['cutter_cnt']))),
            #     dpi = str(sgd_cmd(printer_temp.url,printer_temp.port,get_sgd(gala['getval']['dpi']))),
            #     version=str(sgd_cmd(printer_temp.url,printer_temp.port,get_sgd(gala['getval']['printer_version']))),
            #     eth_mac=str(sgd_cmd(printer_temp.url,printer_temp.port,get_sgd(gala['getval']['eth_mac']))),
            #     wlan_mac=str(sgd_cmd(printer_temp.url,printer_temp.port,get_sgd(gala['getval']['wlan_mac'])))
            # )
            printer_info_temp = info(printer_temp,gala)
            db.add(printer_info_temp)
            db.commit()
            db.refresh(printer_info_temp)
            printer_cur_set = current_set(printer_temp,gala)
            db.add(printer_cur_set)
            db.commit()
            db.refresh(printer_cur_set)
        return JSONResponse(status_code=200, content={'status': printer_temp.id})

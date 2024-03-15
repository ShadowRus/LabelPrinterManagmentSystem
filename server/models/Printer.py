from sqlalchemy import Column, Integer, String
from server.api.deps import Base
from pydantic import BaseModel, HttpUrl, Field
from typing import Sequence, List, Optional



class Printers(Base):
    __tablename__ = "PRINTERS"
    id = Column(Integer, primary_key=True, index=True)
    print_name = Column(String)
    url = Column(String)
    port = Column(Integer)
    serial = Column(String,index=True)
    inv_num = Column(String)
    location = Column(String)
    model = Column(String)
    vendor_model = Column(String)
    add_time = Column(String)
    in_use = Column(Integer)
    profile_id = Column(Integer)
    is_deleted = Column(Integer)


class PrintersInfo(Base):
    __tablename__ = "PRINTERS_INFO"
    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer,index=True)
    mileage = Column(Integer) #723.23
    cutter_cnt = Column(Integer)
    dpi = Column(String) #203
    version = Column(String) #02.00.30
    eth_mac = Column(String)  # 84:C2:E4:A8:40:EE
    wlan_mac = Column(String)  # 00:00:00:00:00:00

class PrintersSettings(Base):
    __tablename__= "PRINTER_CURRENT_SETTINGS"
    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, index=True)
    sw_ribbon = Column(String) #off
    print_mode = Column(String) #tear гильотинный нож Оторвать этикетку   tear Отделитель этикетки peel Гильотинный нож cutter Барабанный нож recycle Смотчик roll_cutter
    tear_off = Column(String) # -120 ... 120
    sensor_select = Column(String) # автоматически auto на просвет transmissive на отражение reflective
    media_power_up = Column(String) #none промотка feed калибровка  calibration нет none
    head_close = Column(String) #calibration промотка калибровка нет
    #ppl = Column(String) #zpl
    buzzer = Column(String) #2 отключить - 0 низкий -1  стандартный - 2 громкий - 3
    speed = Column(String) #5 (2 - 12)
    density = Column(String) #10 (1 - 30)
    media_sensor = Column(String) #зазор gap непрерывный continuous черная метка black_mark
    ethernet_switch = Column(String) #on
    eth_dhcp = Column(String) #on
    eth_ip = Column(String) # 192.168.0.105
    eth_mask = Column(String) #255.255.255.0
    eth_gateway = Column(String) #192.168.0.1
    eth_mac = Column(String) #84:C2:E4:A8:40:EE
    wlan_mod = Column(String) #ap/sta
    wlan_ssid =Column(String) #ix4l
    wlan_key = Column(String) #12345678
    wlan_dhcp = Column(String) #on
    wlan_ip = Column(String) #192.168.1.1
    wlan_mask = Column(String) #255.255.255.0
    wlan_gateway = Column(String) #192.168.1.1
    wlan_mac = Column(String)  #00:00:00:00:00:00
    wlan_key_require = Column(String) #NO/YES
    printer_time_year = Column(Integer)
    printer_time_month = Column(Integer)
    printer_time_day = Column(Integer)
    printer_time_hour = Column(Integer)
    printer_time_minute = Column(Integer)
    printer_time_second = Column(Integer)
    printer_time_timezone = Column(Integer)

class PrinterProfile(Base):
    __tablename__ = "PRINTER_PROFILE"
    id = Column(Integer, primary_key=True, index=True)
    sw_ribbon = Column(String)  # off
    print_mode = Column(String)  # tear гильотинный нож Оторвать этикетку   tear Отделитель этикетки peel Гильотинный нож cutter Барабанный нож recycle Смотчик roll_cutter
    tear_off = Column(String)  # -120 ... 120
    sensor_select = Column(String)  # автоматически auto на просвет transmissive на отражение reflective
    media_power_up = Column(String)  # none промотка feed калибровка  calibration нет none
    head_close = Column(String)  # calibration промотка калибровка нет
    buzzer = Column(String)  # 2 отключить - 0 низкий -1  стандартный - 2 громкий - 3
    speed = Column(String)  # 5 (2 - 12)
    density = Column(String)  # 10 (1 - 30)
    media_sensor = Column(String)  # зазор gap непрерывный continuous черная метка black_mark
    ethernet_switch = Column(String)  # on
    eth_dhcp = Column(String)  # on
    eth_ip = Column(String)  # 192.168.0.105
    eth_mask = Column(String)  # 255.255.255.0
    eth_gateway = Column(String)  # 192.168.0.1
    wlan_mod = Column(String)  # ap/sta
    wlan_ssid = Column(String)  # ix4l
    wlan_key = Column(String)  # 12345678
    wlan_dhcp = Column(String)  # on
    wlan_ip = Column(String)  # 192.168.1.1
    wlan_mask = Column(String)  # 255.255.255.0
    wlan_gateway = Column(String)  # 192.168.1.1
    wlan_key_require = Column(String)  # NO/YES
    printer_time = Column(Integer)






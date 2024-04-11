from typing import Sequence, List, Optional
from pydantic import BaseModel,Field

class AddPrinter(BaseModel):
    serial:Optional[str] = None
    model: Optional[str] = None
    print_name:Optional[str] = None
    inv_num: Optional[str] = None
    url: Optional[str] = None
    port: int = Field(default=9100)
    location: Optional[str] = None
    in_use: int= Field(default=1)
    network: Optional[str] = None

class PrinterID(BaseModel):
    printer_id:int = Field()
    serial: Optional[str] = None
    port: int = Field(default=9100)
    url: Optional[str] = None
    inv_num: Optional[str] = None
    network: Optional[str] = None
    vendor_model:Optional[str] = None

class SyhchPrinter(BaseModel):
    serial:Optional[str] = None
    printer_id:Optional[int] =  None
    url:Optional[str]=None
    inv_num: Optional[str] =None

class EditPrinterSettings(BaseModel):
    printer_id: int= Field()
    sw_ribbon: Optional[str] = None
    print_mode: Optional[str] = None
    tear_off: Optional[int] = None
    sensor_select: Optional[str] = None  # автоматически auto на просвет transmissive на отражение reflective
    media_power_up: Optional[str] = None  # none промотка feed калибровка  calibration нет none
    head_close: Optional[str] = None # calibration промотка калибровка нет
    buzzer: Optional[str] = None  # 2 отключить - 0 низкий -1  стандартный - 2 громкий - 3
    speed: Optional[int] = None  # 5 (2 - 12)
    density: Optional[int] = None  # 10 (1 - 30)
    media_sensor: Optional[str] = None  # зазор gap непрерывный continuous черная метка black_mark
    ethernet_switch: Optional[int] = None  # on
    eth_dhcp: Optional[int] = None  # on
    eth_ip: Optional[str] = None  # 192.168.0.105
    eth_mask: Optional[str] = None  # 255.255.255.0
    eth_gateway: Optional[str] = None  # 192.168.0.1
    wlan_mod: Optional[str] = None  # ap/sta
    wlan_ssid: Optional[str] = None  # ix4l
    wlan_key: Optional[str] = None  # 12345678
    wlan_dhcp: Optional[int] = None # on
    wlan_ip: Optional[str] = None  # 192.168.1.1
    wlan_mask: Optional[str] = None  # 255.255.255.0
    wlan_gateway: Optional[str] = None  # 192.168.1.1
    wlan_key_require: Optional[int] = None  # NO/YES
    printer_time_year: Optional[int] = None
    printer_time_month: Optional[int] = None
    printer_time_day: Optional[int] = None
    printer_time_hour: Optional[int] = None
    printer_time_minute: Optional[int] = None
    printer_time_second: Optional[int] = None
    printer_time_timezone: Optional[int] = None
    reset_printer: Optional[int] =None
    factory_default:Optional[int]=None
    configguration_page:Optional[int]=None
    cutter_test:Optional[int]=None
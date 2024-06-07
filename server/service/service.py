from decouple import config
from server.models.Printer import Printers, PrintersInfo,PrintersSettings
import json
import socket
import ipaddress



def read_json_to_dict(json_file_path):
    with open(json_file_path,'r',encoding='utf-8') as file:
        return json.load(file)

SGD_TT6XX = config('SGD_GALA',default = './server/src/sgdTT6XX.json')
SGD_TT44_43 = config('SGD_APOLLO',default = './server/src/sgdTT44_43.json')
SGD_TT42 = config('SGD_TT42',default = './server/src/sgdTT42.json')
RENAME_ATOL = config('RENAME_ATOL',default = './server/src/renameATOL.json')
SERIAL_NO = config('SERIAL_NO',default='serial_no')
VENDOR_MODEL = config('VENDOR_MODEL',default='printer_name')
REPAET_RESP = config('REPAET_RESP',default = 2)
SETTIMEOUT = int(config('SETTIMEOUT',default = 2))

tt6xx = read_json_to_dict(SGD_TT6XX)
tt44_43 = read_json_to_dict(SGD_TT44_43)
tt42 = read_json_to_dict(SGD_TT42)
rename_atol= read_json_to_dict(RENAME_ATOL)


# сканируем сеть на наличии принтеров
def check_ip_adresses(network,port):
    occupied_ips=[]
    for ip in ipaddress.IPv4Network(network):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                if s.connect_ex((str(ip),int(port))) == 0:
                    occupied_ips.append(str(ip))
        except socket.error:
            pass
    return occupied_ips


def to_float(value):
    if value is None:
        return 0.0

    if isinstance(value, float):
        return value

    if isinstance(value, int):
        return float(value)

    if isinstance(value, str):
        # Удаление пробелов в начале и в конце строки
        value = value.strip()
        # Заменяем запятую на точку
        value = value.replace(',', '.')
        try:
            return float(value)
        except ValueError:
            return 0.0

    return 0.0


def to_int(value):
    if value is None:
        return 0

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        # Удаление пробелов в начале и в конце строки
        value = value.strip()
        # Заменяем запятую на точку
        value = value.replace(',', '.')
        try:
            return int(float(value))
        except ValueError:
            return 0

    return 0

def get_value_or_none(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    else:
        return None
def get_sgd(get_value):
    s1 = f'\x1b\x1c& V1 getval "{get_value}"\r\n'
    return s1.encode()

def set_sgd(key,value):
    s1 = f'\x1b\x1c& V1 setval "{key}" "{value}"\r\n'
    return s1.encode()

def do_sgd(key):
    s1 = f'\x1b\x1c& V1 do "{key}"\r\n'
    return s1.encode()

def get_key_sgd(get_value):
    s1 = f'\x1b\x1c& V1 getkey\r\n\x01"{get_value}"'
    return s1.encode()
#отправка SGD команды на принтер
def sgd_cmd(host, port, sgd):
    import socket
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mysocket.connect((host, port))
        mysocket.settimeout(SETTIMEOUT)
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

def repeat_sgd_cmd(host,port,sgd):
    i = int(REPAET_RESP)
    while i > 0:
        print(f'I = {i}')
        recv = sgd_cmd(host,port,sgd)
        if recv not in [None,'']:
            return recv
        else:
            i = i - 1
    return None

# печать ZPL-команд
def zpl_cmd(host, port, zpl):
    import socket
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mysocket.connect((host, port))
        mysocket.settimeout(SETTIMEOUT)
        mysocket.send(zpl)
        return
    except:
        return None
    finally:
        mysocket.close()
# Получаем текущие настройки принтера
def get_current_set(host,port):
    printer_name = rename(str(repeat_sgd_cmd(host, port, get_sgd(VENDOR_MODEL))),rename_atol)
    resp = {}
    if printer_name in ['ATOL TT631','ATOL TT621']:
        printer_dict = tt6xx
    elif printer_name in ['ATOL TT43','ATOL TT44']:
        printer_dict = tt44_43
    elif printer_name in ['ATOL TT42']:
        printer_dict = tt42
    else:
        return resp
    for key,value in printer_dict['getval'].items():
        resp[key] = repeat_sgd_cmd(host, port, get_sgd(printer_dict['getval'][key]))
    return resp

# переименовываем название вендор-имя на АТОЛ-имя
def rename(printer_name,rename_atol):
    if printer_name in rename_atol['ATOL TT631']:
        return 'ATOL TT631'
    if printer_name in rename_atol['ATOL TT621']:
        return 'ATOL TT621'
    if printer_name in rename_atol['ATOL TT43']:
        return 'ATOL TT43'
    if printer_name in rename_atol['ATOL TT44']:
        return 'ATOL TT44'
    if printer_name in rename_atol['ATOL TT42']:
        return 'ATOL TT42'
    else:
        return printer_name

def cmd_dict(vendor_model):
    vendor_model = rename(vendor_model,rename_atol)
    if vendor_model in ['ATOL TT631', 'ATOL TT621']:
        return tt6xx
    elif vendor_model in ['ATOL TT43', 'ATOL TT44']:
        return tt44_43
    elif vendor_model in ['ATOL TT42']:
        return tt42
    else:
        return {}


def get_info(data):
    temp = get_current_set(data.url,data.port)
    if temp != {}:
        printer_info_temp = PrintersInfo(
            printer_id=data.id,
            url = data.url,
            port = data.port,
            vendor_model = str(temp['model']),
            model = rename(temp['model'],rename_atol),
            mileage=to_float(temp['mileage']) * 0.0254,
            cutter_cnt=to_int(get_value_or_none(temp,'cutter_cnt')),
            dpi=str(get_value_or_none(temp,'dpi')),
            version=str(get_value_or_none(temp,'printer_version')),
            eth_mac=str(get_value_or_none(temp,'eth_mac')),
            wlan_mac=str(get_value_or_none(temp,'wlan_mac'))
        )
    else:
        printer_info_temp = PrintersInfo(
            printer_id=data.id,
            url=data.url,
            port=data.port
        )
    return printer_info_temp

def update_info(printer_info_temp):
    temp = get_current_set(printer_info_temp.url, printer_info_temp.port)
    if temp != {}:
        printer_info_temp.mileage=to_float(temp['mileage']) * 0.0254
        printer_info_temp.cutter_cnt=to_int(get_value_or_none(temp,'cutter_cnt'))
        printer_info_temp.dpi= str(get_value_or_none(temp,'dpi'))
        printer_info_temp.version=str(get_value_or_none(temp,'printer_version'))
        printer_info_temp.eth_mac=str(get_value_or_none(temp,'eth_mac'))
        printer_info_temp.wlan_mac=str(get_value_or_none(temp,'wlan_mac'))
    return printer_info_temp

# def get_current_set(printer_temp, gala):
#     printer_settings_temp = PrintersSettings(
#         printer_id = printer_temp.id,
#         sw_ribbon = str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['sw_ribbon']))),
#         print_mode=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['print_mode']))),
#         tear_off=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['tear_off']))),
#         sensor_select=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['sensor_select']))),
#         media_power_up=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['media_power_up']))),
#         head_close=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['head_close']))),
#         buzzer=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['buzzer']))),
#         speed=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['speed']))),
#         density=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['density']))),
#         media_sensor=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['media_sensor']))),
#         ethernet_switch=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['ethernet_switch']))),
#         eth_dhcp=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_dhcp']))),
#         eth_ip=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_ip']))),
#         eth_mask=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_mask']))),
#         eth_gateway=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_gateway']))),
#         eth_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_mac']))),
#         wlan_mod=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mode']))),
#         wlan_ssid=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_ssid']))),
#         wlan_key=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_key']))),
#         wlan_dhcp=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_dhcp']))),
#         wlan_ip=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_ip']))),
#         wlan_mask=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mask']))),
#         wlan_gateway=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_gateway']))),
#         wlan_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mac']))),
#         wlan_key_require=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_key_require']))),
#         printer_time_year=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_year']))),
#         printer_time_month=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_month']))),
#         printer_time_day=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_day']))),
#         printer_time_hour=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_hour']))),
#         printer_time_minute=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_minute']))),
#         printer_time_second=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_time_second'])))
#     )
#     return printer_settings_temp


# def sgd_cmd(host, port, sgd):
#     import socket
#     mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         mysocket.connect((host, port))
#         mysocket.settimeout(5)
#         mysocket.send(sgd)
#         a1 = b'\x00'
#         a1 = a1.decode('utf-8')
#         recv = mysocket.recv(4096).decode('utf-8')
#         if recv[-1] == a1:
#             return recv[:-1]
#         else:
#             return recv
#     except:
#         return None
#     finally:
#         mysocket.close()
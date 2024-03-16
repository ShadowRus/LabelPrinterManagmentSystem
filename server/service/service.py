from decouple import config
from server.models.Printer import Printers, PrintersInfo,PrintersSettings
import json
import socket
import ipaddress


def read_json_to_dict(json_file_path):
    with open(json_file_path,'r',encoding='utf-8') as file:
        return json.load(file)


def get_sgd(get_value):
    s1 = f'\x1b\x1c& V1 getval "{get_value}"\r\n'
    return s1.encode()

def set_sgd(key,value):
    s1 = f'\x1b\x1c& V1 setval "{key}" "{value}"\r\n'
    return s1.encode()

def do_sgd(key):
    s1 = f'\x1b\x1c& V1 do "{key}"\r\n'
    return s1.encode()

def get_info(printer_temp, gala):
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

def update_info(printer_temp, printer_info_temp,gala):
    printer_info_temp.mileage=int(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['mileage'])), 16)*10
    printer_info_temp.cutter_cnt=int(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['cutter_cnt'])))
    printer_info_temp.dpi=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['dpi'])))
    printer_info_temp.version=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['printer_version'])))
    printer_info_temp.eth_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['eth_mac'])))
    printer_info_temp.wlan_mac=str(sgd_cmd(printer_temp.url, printer_temp.port, get_sgd(gala['getval']['wlan_mac'])))
    return printer_info_temp

def get_current_set(printer_temp, gala):
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

SGD_GALA = config('SGD_GALA')
gala = read_json_to_dict(SGD_GALA)
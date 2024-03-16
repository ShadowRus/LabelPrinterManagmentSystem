import socket
from decouple import config
import pandas
import requests
import json


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

HOST_BACKEND = config('HOST_SERVER', default=extract_ip())
PORT_BACKEND = config('PORT_SERVER', default=8091)

def add_printer_response(df):
    resp={}
    for index, row in df.iterrows():
        if 'HOST' in df.columns:
            resp['url'] = str(row['HOST'])
        if 'PORT' in df.columns:
            resp['port'] = int(row['PORT'])
        if 'LOCATION' in df.columns:
            resp['location'] = str(row['LOCATION'])
        if 'INVENTORY_NUMBER' in df.columns:
            resp['inv_num'] = str(row['INVENTORY_NUMBER'])
        if 'SERIAL_NO' in df.columns:
            resp['serial'] = str(row['SERIAL_NO'])
        if 'IS ACTIVE' in df.columns:
            resp['in_use'] = int(row['IS ACTIVE'])
        url_add = str(HOST_BACKEND)+':'+str(PORT_BACKEND)+'/v1/printer'
        response = requests.post(url_add,data=json.dumps(url_add))
    return
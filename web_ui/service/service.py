import socket
from decouple import config
import pandas as pd
import requests
import json
import streamlit as st
import ipaddress


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

def read_json_to_dict(json_file_path):
    with open(json_file_path,'r',encoding='utf-8') as file:
        return json.load(file)


HOST_BACKEND = config('HOST_SERVER', default=extract_ip())
PORT_BACKEND = config('PORT_SERVER', default=8091)
SGD_GALA = config('SGD_GALA',default='./server/src/sgdTT6XX.json')
SGD_TT42 = config('SGD_TT42',default='./server/src/sgdTT42.json')
POST_SETTINGS =config('POST_SETTINGS',default='/v1/settings')
POST_PRINTER = config('POST_PRINTER',default = '/v1/printer')
GET_PRINTERS = config('GET_PRINTERS',default = '/v1/printers')
SET_VALUE = config('SET_VALUE',default = '/v1/setvalue')
DO_CMD = config('DO_CMD',default = '/v1/do')
GET_PRINTERS_INFO= config('GET_PRINTERS_INFO',default = '/v1/printers/info')
GET_PRINTER_CURR = config('GET_PRINTER_CURR',default='/v1/printer/current_set')
SCAN_NETWORK = config('SCAN_NETWORK',default = '/v1/scan')
GET_CURRENT_SET = config('GET_CURRENT_SET',default ='/v1/current_set' )

gala = read_json_to_dict(SGD_GALA)

def auto_add_printer_response(df):
    resp={}
    success_resp = {}
    error_resp = {}
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
        url_add = str('http://')+str(HOST_BACKEND)+':'+str(PORT_BACKEND)+ str(POST_PRINTER)
        response = requests.post(url_add,data=json.dumps(resp))
        if response.status_code == 200:
            if 'SERIAL_NO' in df.columns:
                success_resp.update(resp['serial'])
            else:
                success_resp.update(resp['serial'])
        else:
            if 'SERIAL_NO' in df.columns:
                error_resp.update(resp['serial'])
            else:
                error_resp.update(resp['serial'])
    return success_resp,error_resp

def manual_add_printer_response(serial,inv_num,url,port,location,in_use):
    resp={}
    if serial != None:
        resp['serial'] = serial
    if inv_num != None:
        resp['inv_num'] = inv_num
    if url != None:
        resp['url'] = str(url)
    if port != None:
        resp['port'] = int(port)
    else:
        resp['port'] = 9100
    if location != None:
        resp['location'] = location
    resp['in_use'] = int(in_use)
    print(resp)
    try:
        url_add = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(POST_PRINTER)
        response = requests.post(url_add, data=json.dumps(resp))
        response.raise_for_status()
        return response.status_code, response.json()
    except (requests.exceptions.RequestException, ValueError) as err:
        print(f"Ошибка получения данных с {str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(POST_PRINTER)} :{err}")
        return 500, {}

# def add_printer_info(printer_id,serial,url,port,network):
#     resp={}
#     if printer_id != None:
#         resp['printer_id'] = printer_id
#     if serial != None:
#         resp['serial'] = serial
#     if url != None:
#         resp['url'] = str(url)
#     if network != None:
#         resp['network'] = network
#     if port != None:
#         resp['port'] = int(port)
#     else:
#         resp['port'] = 9100
#     print(resp)
#     try:
#         url_add = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS_INFO)
#         response = requests.post(url_add, data=json.dumps(resp))
#         response.raise_for_status()
#         return response.status_code, response.json()
#     except (requests.exceptions.RequestException, ValueError) as err:
#         print(f'Ошибка получения данных с {str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS_INFO)} :{err}')
#         return 500, {}
#

def printers():
    try:
        re = requests.get(str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS))
        re.raise_for_status()
        j1 = re.json()
        df1 = pd.DataFrame.from_records(j1)
    except (requests.exceptions.RequestException,ValueError) as err:
        print(f"Ошибка получения данных с {str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS)} :{err}")
        df1 = pd.DataFrame()
    try:
        re2 = requests.get(str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS_INFO))
        re2.raise_for_status()
        j2 = re2.json()
        df2 = pd.DataFrame.from_records(j2)
    except (requests.exceptions.RequestException,ValueError) as err:
        print(f"Ошибка получения данных с {str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS_INFO)} :{err}")
        df2 = pd.DataFrame()

    if not df1.empty and not df2.empty:
        merged_df = pd.merge(df1,df2,left_on='id',right_on='printer_id')
        merged_df.set_index('id_x',inplace=True)
        merged_df = merged_df[['serial', 'mileage','cutter_cnt','url', 'port', 'model',
                               'inv_num', 'location', 'in_use','eth_mac','wlan_mac','version','profile_id']]
    else:
        merged_df = pd.DataFrame(columns=['serial', 'mileage','cutter_cnt','url', 'port', 'model',
                               'inv_num', 'location', 'in_use','eth_mac','wlan_mac','version','profile_id'])
    return merged_df


def printer_info(printer_id):
    re = requests.get(str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTERS_INFO),
                      params={"printer_id":int(printer_id)})
    if re.status_code == 200:
        j1 = re.json()
    else:
        j1 = {}
    return j1

# текущие настройки от базы
def printer_curr_set(printer_id):
    re = requests.get(str('http://') + str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_PRINTER_CURR),
                      params={"printer_id":int(printer_id)})
    if re.status_code == 200:
        j1 = re.json()
    else:
        j1 = {}
    return j1


def scan_network(network,port):
    try:
        url_add = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(SCAN_NETWORK)
        response = requests.get(url_add, params={"network":str(network), 'port':port})
        response.raise_for_status()
        return response.status_code, response.json()
    except (requests.exceptions.RequestException, ValueError) as err:
        print(f'Ошибка получения данных с http://{str(HOST_BACKEND)}:{str(PORT_BACKEND)}{str(SCAN_NETWORK)}:{err}')
        return 500, {}


def get_current_set(host,port):
    try:
        url = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(GET_CURRENT_SET)
        response = requests.get(url, params={"host":str(host), 'port':port})
        response.raise_for_status()
        return response.status_code, response.json()
    except (requests.exceptions.RequestException, ValueError) as err:
        print(f'Ошибка получения данных с http://{str(HOST_BACKEND)}:{str(PORT_BACKEND)}{str(GET_CURRENT_SET)}:{err}')
        return 500, {}

def set_value(host,port,setkey,setvalue):
    try:
        url_add = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(SET_VALUE)
        response = requests.get(url_add, params={"host":str(host), 'port':port,"set_key":setkey,"set_value":setvalue})
        response.raise_for_status()
        return response.status_code, response.json()
    except (requests.exceptions.RequestException, ValueError) as err:
        print(f'Ошибка получения данных с http://{str(HOST_BACKEND)}:{str(PORT_BACKEND)}{str(SET_VALUE)}:{err}')
        return 500, {}

def do(host,port,do_cmd):
    try:
        url_add = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + str(DO_CMD)
        response = requests.get(url_add, params={"host":str(host), 'port':port,"cmd":do_cmd})
        return
    except (requests.exceptions.RequestException, ValueError) as err:
        print(f'Ошибка получения данных с http://{str(HOST_BACKEND)}:{str(PORT_BACKEND)}{str(DO_CMD)}:{err}')
        return


def check_state(key,dict):
    if key not in dict:
        return None
    else:
        return dict[key]

class  PrinterSettings:
    def __init__(self,gala,current_settings):
        self.gala = gala
        self.cur_set = current_settings
        self.disabled = 1
        self.k_values= {}
    def change_disabled(self,i=''):
        if st.checkbox('Изменить настройки принтера',key = str(i)+'is_disabled',value=False):
            self.disabled = 0
        else:
            self.disabled=1
        return
    def table_view(self):
        pass
    def tab_view(self):
        pass

    def send_data_to_url(self,url, data, retries=3):
        for i in range(retries):
            try:
                response = requests.post(url, data=data)
                response.raise_for_status()  # Если ответ сервера не 200, вызывается HTTPError.
                return response
            except (ConnectionError, requests.HTTPError) as e:
                if i < retries - 1:  # i is zero indexed
                    continue
                else:
                    return str(e)
    def reuest_data(self):
        if st.button('Изменить настройки'):
            self.k_values['printer_id']= self.cur_set['printer_id']
            st.write(self.k_values)
        return
    def serial_no(self,i=''):
        st.text_input('Серийный номер', value=self.cur_set[self.gala['getval']['serial_no']], key=str(i) + 'serial_no', disabled=True)
        return
    def printer_version(self,i=''):
        st.text_input('Версия прошивки принтера',value=self.cur_set[self.gala['getval']['printer_version']],key=str(i)+'printer_version',disabled=True)
        return
    def dpi(self,i=''):
        st.text_input('DPI',value=self.cur_set[self.gala['getval']['dpi']],key=str(i)+'dpi',disabled=True)
        return
    def model(self,i=''):
        st.text_input('Модель принтера', value=self.cur_set[self.gala['getval']['model']], key=str(i) + 'model',
                      disabled=True)
        return
    def mileage(self,i=''):
        st.text_input('Пробег термопечатающей головы,м', value=self.cur_set[self.gala['getval']['mileage']], key=str(i) + 'mileage',
                      disabled=True)
        return
    def cutter_cnt(self,i=''):
        st.text_input('Количество отрезов ножа, шт', value=self.cur_set[self.gala['getval']['cutter_cnt']],
                      key=str(i) + 'cutter_cnt',
                      disabled=True)
        return
    def sw_ribbon(self,i=''):
        if self.cur_set[self.gala['getval']['sw_ribbon']] == 'off':
            v1 = 0
        else:
            v1= 1
        c1,c2 = st.columns(2)
        with c1:
            st.checkbox('Использовать Риббон', value=v1, disabled=bool(self.disabled), key=str(i) + 'sw_ribbon',
                      help='Использование красящей ленты(Риббона) - термотрансферная печать (ТТП), '
                           'Печать без красящей ленты - прямая термопечать (ПТП). '
                           'При переключение на ПТП с ТТП не забудьте снять риббон. \r\n'
                           '- **Термотрансферная печать**: идеально подходит для ситуаций, где требуется более высокое качество печати или долговечность этикетки.'
                           ' Этот метод использует термическую головку и цветную ленту для переноса изображения на этикетку.'
                           ' Это создает более четкое и долговечное изображение, которое устойчиво к истиранию, царапинам и ультрафиолетовому излучению. '
                           'Он идеально подходит для баркодов, этикеток на продукты питания, этикеток для одежды и других продуктов, которые подвергаются износу.\r\n'
                           '- **Прямая термопечать**: это более экономический вариант, который подходит для короткосрочных этикеток, которые не подвергаются тяжелым условиям эксплуатации.'
                           ' Этот метод использует термическую головку для непосредственного нанесения изображения на специализированный термобумажный материал. '
                           'Он идеально подходит для штрих-кодов, этикеток для доставки, квитанций и билетов.')

        with c2:
            if st.session_state[str(i) + 'sw_ribbon'] == 0:
                st.warning('Выбрана **ПрямаяТермоПечать(ПТП)**')
            else:
                st.warning('Выбрана **ТермоТрансфернаяПечать(ПТП)**')
        self.k_values['sw_ribbon'] = int(st.session_state[str(i) + 'sw_ribbon'])
        return
    def get_index(self,dict_,value):
        keys_list = list(dict_.keys())
        key = [k for k, v in dict_.items() if v == value][0]
        return keys_list.index(key)

    def print_mode(self,i=''):
        st.selectbox('Режимы печати',list(self.gala['setval']['print_mode'].keys()),
                     index=self.get_index(self.gala['setval']['print_mode'],self.cur_set[self.gala['getval']['print_mode']]),
                     key=str(i)+'print_mode',
                     disabled=bool(self.disabled), help='- **Режим отрыва**: Это самый базовый режим печати, который подходит для большинства обычных задач печати. В этом режиме принтер печатает этикетку и останавливается, позволяя пользователю вручную оторвать этикетку от принтера. '
                                                        'Это идеально подходит для небольших объемов печати, где потребность в автоматизации отсутствует.\r\n'
                                                        '- **Режим отрезания**: В этом режиме принтер автоматически режет каждую этикетку или набор этикеток после печати.'
                                                        ' Этот режим полезен при печати больших количеств этикеток, особенно когда требуется отдельная этикетка для каждого продукта или упаковки. '
                                                        'Обратите внимание, что для этого режима требуется принтер с встроенным отрезным устройством.\r\n'
                                                        '- **Режим отделителя**: Этот режим предназначен для принтеров, оснащенных дополнительным механизмом отделения, который отделяет наклейку от подложки сразу после печати. '
                                                        'Это удобно в ситуациях, когда вы хотите немедленно наклеить этикетку на продукт или упаковку.')
        self.k_values['print_mode'] =self.gala['setval']['print_mode'][st.session_state[str(i)+'print_mode']]
        return

    def sensor_select(self,i=''):
        st.selectbox('Настройка датчика', list(gala['setval']['sensor_select'].keys()),
                     index=self.get_index(gala['setval']['sensor_select'], self.cur_set[self.gala['getval']['sensor_select']]),
                     key=str(i) + 'sensor_select',
                     disabled=bool(self.disabled),help='Выберите датчик носителя, соответствующий используемому носителю. '
                                                       'Датчик отражения( **на отражение**) следует использовать только для носителя с черными метками. '
                                                       'Для других типов носителя следует использовать передающий датчик(**на просвет**).')
        self.k_values['sensor_select'] = self.gala['setval']['sensor_select'][st.session_state[str(i)+'sensor_select']]
        return
    def media_power_up(self,i=''):
        st.selectbox('Действие при включении', list(gala['setval']['media_power_up'].keys()),
                     index=self.get_index(gala['setval']['media_power_up'], self.cur_set[self.gala['getval']['media_power_up']]),
                     key=str(i) + 'media_power_up',
                     disabled=bool(self.disabled),
                     help='- **Промотка**: очень полезна, если вы регулярно меняете типы этикеток в принтере. Это позволяет обеспечить, что этикетка готова к печати сразу после включения устройства. \r\n'
                          '- **Калибровка**: необходима при первом использовании принтера, после замены рулона этикеток или при возникновении проблем с печатью. Если принтер используется с одним и тем же типом этикеток, и нет проблем с печатью, калибровка при каждом включении может быть избыточной.\r\n'
                          '- **Действие не требуется**: это подходит для стабильных рабочих сред, где тип этикеток и задачи печати не меняются часто. Это позволяет сэкономить время на подготовке к печати после включения устройства.')
        st.write(self.gala['setval']['media_power_up'][st.session_state[str(i) + 'media_power_up']])
        return
    def head_close(self,i=''):
        st.selectbox('Действие при закрытии печатающей головы', list(gala['setval']['head_close'].keys()),
                     index=self.get_index(gala['setval']['head_close'], self.cur_set[self.gala['getval']['head_close']]),
                     key=str(i) + 'head_close',
                     disabled=bool(self.disabled),
                     help=' - **Промотка**: Если вы только что вставили новый рулон этикеток, может быть полезно выполнить промотку, чтобы убедиться, что этикетки подаются правильно.\r\n'
                          '- **Калибровка**: Если после закрытия печатающей головки вы заметили проблемы с печатью (например, печать смещается или этикетки не выравниваются правильно), вам может потребоваться выполнить калибровку.\r\n'
                          '- В большинстве случаев, если принтер работает нормально и не требует обслуживания, **дополнительные действия** при закрытии печатающей головки **не требуются**.')
        self.k_values['head_close']=self.gala['setval']['head_close'][st.session_state[str(i) + 'head_close']]
        return

    def tear_off(self,i=''):
        st.slider('Отрыв.Настройка положеия остановки носителя',min_value=self.gala['setval']['tear_off']['min'],
                  max_value=self.gala['setval']['tear_off']['max'],
                  value=int(self.cur_set[self.gala['getval']['tear_off']]),
                  disabled=bool(self.disabled),
                  key=str(i)+'tear_off',help='Эта настройка позволяет точно настроить положение остановки носителя.'
                                             'Диапазон значений: от «+» до «–»')
        self.k_values['tear_off']=st.session_state[str(i)+'tear_off']
        return
    def buzzer(self,i=''):
        st.selectbox('Громкость динамика принтера', list(gala['setval']['buzzer'].keys()),
                     index=self.get_index(gala['setval']['buzzer'], self.cur_set[self.gala['getval']['buzzer']]),
                     key=str(i) + 'buzzer',
                     disabled=bool(self.disabled),
                     help='- **Отключенная**: Если принтер используется в тихой среде, такой как офис или библиотека, где шум может быть нарушающим, отключение звуковых сигналов может быть хорошим выбором. \r\n'
                          '- **Низкая**: Это может быть хорошим выбором для рабочих мест, где некоторый уровень шума допустим, но громкие звуки могут быть беспокойными. Например, в небольшом магазине или в офисном пространстве с несколькими сотрудниками. \r\n'
                          '- **Стандартная**: Большинство людей будут использовать стандартный уровень громкости. Это обеспечивает достаточно звука, чтобы быть слышимым, но не настолько громким, чтобы быть беспокойным.\r\n'
                          '- **Громкая**: Громкий уровень обычно используется в шумных средах, таких как склады или производственные площади, где тише звуки могут быть неслышны.')
        self.k_values['buzzer']= self.gala['setval']['buzzer'][st.session_state[str(i) + 'buzzer']]
        return
    def speed(self,i=''):
        st.slider('Скорость печати', min_value=self.gala['setval']['speed']['min'],
                  max_value=self.gala['setval']['speed']['max'],
                  value=int(self.cur_set[self.gala['getval']['speed']]), disabled=bool(self.disabled), key=str(i) + 'speed',
                  help='Выбор скорости печати на принтере этикеток зависит от нескольких факторов, включая качество печати, количество этикеток, которые вам нужно напечатать, и скорость, с которой вам нужны эти этикетки.\r\n'
                       '- **Высокая скорость печати**: Чем выше скорость печати, тем быстрее принтер сможет напечатать этикетки. '
                       'Это особенно полезно, если вам нужно напечатать большое количество этикеток за короткое время. '
                       'Однако, пожертвование скоростью может привести к некоторому снижению качества печати, особенно для сложных или детализированных изображений.\r\n'
                       '- **Низкая скорость печати**: Чем ниже скорость печати, тем выше будет качество печати.'
                       ' Это может быть важно, если вы печатаете этикетки с сложными деталями, такими как маленькие шрифты или сложные графические изображения.'
                       ' Однако, печать будет происходить медленнее.\r\n'
                       '- **Средняя скорость печати**: Это компромисс между скоростью и качеством печати. '
                       'Если вам нужно напечатать умеренное количество этикеток и вы хотите хорошее качество печати, это может быть хорошим выбором.')
        self.k_values['speed']= st.session_state[str(i) + 'speed']
        return
    def density(self,i=''):
        st.slider('Плотность печати', min_value=self.gala['setval']['density']['min'],
                  max_value=self.gala['setval']['density']['max'],
                  value=int(self.cur_set['density']), disabled=bool(self.disabled), key=str(i) + 'density',
                  help='Настройка плотности или температуры печати на принтере этикеток зависит от типа используемых материалов (этикетки и лента) и требуемой детализации печати.\r\n'
                       '- **Высокая плотность/температура**: Ее можно выбрать, если вы работаете с более толстыми или более трудными для печати материалами.'
                       ' Она также может помочь при печати очень детализированных изображений или мелкого текста.'
                       ' Однако стоит помнить, что увеличение температуры может привести к быстрому износу печатающей головки и увеличению расхода красящей ленты.\r\n'
                       '- **Низкая плотность/температура**: Подходит для более тонких материалов этикеток или в ситуациях, когда вы печатаете менее детализированные изображения.'
                       ' Это может помочь продлить срок службы печатающей головки и сократить расход красящей ленты.\r\n'
                       '- **Средняя плотность/температура**: Обычно это оптимальный выбор для большинства задач печати.'
                       ' Вы можете начать с этого уровня и постепенно подстраивать его в зависимости от качества получаемых этикеток.')
        self.k_values['density']= st.session_state[str(i) + 'density']
        return
    def media_sensor(self,i=''):
        st.selectbox('Тип носителя', list(gala['setval']['media_sensor'].keys()),
                     index=self.get_index(gala['setval']['media_sensor'], self.cur_set[self.gala['getval']['media_sensor']]),
                     key=str(i) + 'media_sensor',
                     disabled=bool(self.disabled),
                     help='- **С зазором**: Этикетки "с зазором" имеют небольшое пространство или зазор между каждой этикеткой. '
                          'Это наиболее распространенный тип этикеток, используемых в термопринтерах, и они идеально подходят для большинства приложений стандартной печати этикеток, таких как адресные этикетки, этикетки для посылок и бирки на товар.\r\n'
                          '- **Черная марка**: Этикетки "с черной маркой" имеют черные марки на обратной стороне, которые принтер использует в качестве сигналов для начала и окончания печати каждой этикетки. Этот тип этикеток обычно используется в специализированных приложениях, где требуется точное позиционирование печати.\r\n'
                          '- **Непрерывный**: Это рулон непрерывного материала, который можно нарезать на любую длину. Этот тип этикеток идеально подходит для приложений, где размеры этикеток могут варьироваться, например, при печати длинных баннеров или знаков.')
        self.k_values['media_sensor']=self.gala['setval']['media_sensor'][st.session_state[str(i) + 'media_sensor']]
        return
    def ethernet_switch(self,i=''):
        if self.cur_set[self.gala['getval']['ethernet_switch']] == 'off':
            v1 = 0
        else:
            v1 = 1

        st.checkbox('Подключение по Ethernet', value=v1, disabled=bool(self.disabled), key=str(i) + 'ethernet_switch',
                    help='Настройка "Подключение по Ethernet" на принтере этикеток относится к возможности принтера подключаться к сети через Ethernet. Это позволяет принтеру обмениваться данными с компьютерами и другими устройствами в сети, что позволяет печатать этикетки из любого места в сети.'
                         'Настройка "Подключение по Ethernet" может включать в себя следующие параметры:\r\n'
                         '- **IP-адрес**: уникальный адрес, который идентифицирует принтер в сети.\r\n'
                         '- **Маска подсети**: определяет, какие части IP-адреса используются для идентификации сети и хоста.\r\n'
                         '- **Шлюз по умолчанию**: это маршрутизатор, который принтер использует для подключения к другим сетям.\r\n'
                         '- **DHCP (Dynamic Host Configuration Protocol)**: Протокол динамической настройки хоста автоматически назначает IP-адрес и другие сетевые параметры принтеру, что упрощает процесс настройки сети. Если в настройках принтера выбрана опция "DHCP", принтер будет автоматически запрашивать эти данные от DHCP-сервера в сети каждый раз, когда он подключается к сети. Это может быть полезно на больших сетях, где вручную управлять IP-адресами может быть сложно.')
        self.k_values['ethernet_switch'] = int(st.session_state[str(i) + 'ethernet_switch'])
        return
    def eth_dhcp(self,i=''):
        if self.cur_set[self.gala['getval']['eth_dhcp']] == 'off':
            v1 = 0
        else:
            v1 = 1
        st.checkbox('**DHCP (Dynamic Host Configuration Protocol)**', value=v1, disabled=bool(self.disabled), key=str(i) + 'eth_dhcp',
                    help='- **DHCP (Dynamic Host Configuration Protocol)**: '
                         'Протокол динамической настройки хоста автоматически назначает IP-адрес и другие сетевые параметры принтеру, что упрощает процесс настройки сети. '
                         'Если в настройках принтера выбрана опция "DHCP", принтер будет автоматически запрашивать эти данные от DHCP-сервера в сети каждый раз, когда он подключается к сети. '
                         'Это может быть полезно на больших сетях, где вручную управлять IP-адресами может быть сложно.')
        self.k_values['eth_dhcp']= int(st.session_state[str(i) + 'eth_dhcp'])
        return

    def get_free_ip_in_subnet(self,network, port):
        import socket
        import ipaddress
        for ip in list(ipaddress.IPv4Network(network))[101:]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # timeout after 1 second
            try:
                sock.connect((str(ip), port))
                sock.close()
            except socket.error:
                return str(ip)  # return the free IP
        return None

    def eth_ip(self,i=''):
        with st.expander('Ethernet IP4'):
            if self.gala['getval']['eth_ip'] not in self.cur_set:
                if st.checkbox('Найти свободный IP4 в сети для принтера',disabled=bool(self.disabled),value=False):
                    self.cur_set[self.gala['getval']['eth_ip']] = self.get_free_ip_in_subnet('192.168.0.0/24',9100)
                else:
                   self.cur_set[self.gala['getval']['eth_ip']]=None
            else:
                if st.button('Найти свободный IP4 в сети для принтера',help='Поиск происходит в подсети 192.168.0/24'):
                    st.success(self.get_free_ip_in_subnet('192.168.0.0/24', 9100))
            st.text_input('IP4-адрес', value=self.cur_set[self.gala['getval']['eth_ip']],
                          key=str(i) + 'eth_ip',
                          disabled=bool(self.disabled))
            self.k_values['eth_ip'] = st.session_state[str(i) + 'eth_ip']
            return
    def eth_mask(self,i=''):
        if self.gala['getval']['eth_mask'] not in self.cur_set:
            self.cur_set[self.gala['getval']['eth_mask']]='255.255.255.0'
        st.text_input('Маска подсети', value=self.cur_set[self.gala['getval']['eth_mask']],
                      key=str(i) + 'eth_mask',
                      disabled=bool(self.disabled),help='Например:255.255.255.0 \r\n'
                                                        '**Маска подсети**: определяет, какие части IP-адреса используются для идентификации сети и хоста.')
        self.k_values['eth_mask']= st.session_state[str(i) + 'eth_mask']
        return
    def eth_gateway(self,i=''):
        if self.gala['getval']['eth_gateway'] not in self.cur_set:
            self.cur_set[self.gala['getval']['eth_gateway']]='192.168.0.1'
        st.text_input('Шлюз по-умолчанию', value=self.cur_set[self.gala['getval']['eth_gateway']],
                  key=str(i) + 'eth_gateway',
                  disabled=bool(self.disabled),
                      help='**Шлюз по умолчанию**: это маршрутизатор, который принтер использует для подключения к другим сетям.')
        self.k_values['eth_gateway']=st.session_state[str(i) + 'eth_gateway']
        return
    def eth_mac(self,i=''):
        st.text_input('Сетевой MAC-адрес принтера', value=self.cur_set[self.gala['getval']['eth_mac']],
                      key=str(i) + 'eth_mac',
                      disabled=True)
        return
    def wlan_dhcp(self,i=''):
        if self.cur_set[self.gala['getval']['wlan_dhcp']] == 'off':
            v1 = 0
        else:
            v1 = 1

        st.checkbox('**DHCP (Dynamic Host Configuration Protocol)**', value=v1, disabled=bool(self.disabled),
                    key=str(i) + 'wlan_dhcp',
                    help='- **DHCP (Dynamic Host Configuration Protocol)**: '
                         'Протокол динамической настройки хоста автоматически назначает IP-адрес и другие сетевые параметры принтеру, что упрощает процесс настройки сети. '
                         'Если в настройках принтера выбрана опция "DHCP", принтер будет автоматически запрашивать эти данные от DHCP-сервера в сети каждый раз, когда он подключается к сети. '
                         'Это может быть полезно на больших сетях, где вручную управлять IP-адресами может быть сложно.')
        self.k_values['wlan_dhcp']=int(st.session_state[str(i) + 'wlan_dhcp'])
        return
    def wlan_mode(self,i=''):
        st.selectbox('Режим работы WiFi', list(gala['setval']['wlan_mod'].keys()),
                     index=self.get_index(gala['setval']['wlan_mod'], self.cur_set[self.gala['getval']['wlan_mod']]),
                     key=str(i) + 'wlan_mod',
                     disabled=bool(self.disabled),
                     help='STA (Station mode): В этом режиме принтер этикеток подключается к существующей беспроводной сети, подобно тому как подключается ваш ноутбук или смартфон. '
                          'Принтер будет идентифицировать сеть по ее SSID и подключиться к ней, используя пароль, если он требуется.\r\n'
                          'AP (Access Point mode): В этом режиме принтер этикеток действует как беспроводной маршрутизатор или точка доступа, создавая свою собственную беспроводную сеть, к которой могут подключаться другие устройства. '
                          'Это может быть полезно, если вы хотите подключиться напрямую к принтеру с мобильного устройства или компьютера, не подключаясь к существующей беспроводной сети.')
        self.k_values['wlan_mod']= self.gala['setval']['wlan_mod'][st.session_state[str(i) + 'wlan_mod']]
        return
    def wlan_ssid(self,i=''):
        if self.gala['getval']['wlan_ssid'] not in self.cur_set:
            self.cur_set[self.gala['getval']['wlan_ssid']] = None
        st.text_input('SSID WiFi Net', value=self.cur_set[self.gala['getval']['wlan_ssid']],
                      key=str(i) + 'wlan_ssid',
                      disabled=bool(self.disabled))
        self.k_values['wlan_ssid']=st.session_state[str(i) + 'wlan_ssid']
        return
    def wlan_key_require(self,i=''):
        if self.cur_set[self.gala['getval']['wlan_key_require']] == 'NO':
            v1 = 0
        if self.cur_set[self.gala['getval']['wlan_key_require']] == 'YES':
            v1 = 1
        if self.cur_set[self.gala['getval']['wlan_key_require']] == '':
            v1 = ''
        st.checkbox('Требуется код подключения', value=v1, disabled=bool(self.disabled),
                    key=str(i) + 'wlan_key_require',)
        self.k_values['wlan_key_require']= int(st.session_state[str(i) + 'wlan_key_require'])
        return
    def wlan_key(self,i=''):
        if self.gala['getval']['wlan_key'] not in self.cur_set:
            self.cur_set[self.gala['getval']['wlan_key']] = None
        st.text_input('WiFi Net Password', value=self.cur_set[self.gala['getval']['wlan_key']],
                      key=str(i) + 'wlan_key',
                      disabled=bool(self.disabled),type='password')
        self.k_values['wlan_key']=st.session_state[str(i) + 'wlan_key']
    def wlan_ip(self,i=''):
        with st.expander('WLAN IP4'):
            if self.gala['getval']['wlan_ip'] not in self.cur_set:
                if st.checkbox('Найти свободный IP4 в сети для принтера', disabled=bool(self.disabled), value=False):
                    self.cur_set[self.gala['getval']['wlan_ip']] = self.get_free_ip_in_subnet('192.168.0.0/24', 9100)
                else:
                    self.cur_set[self.gala['getval']['wlan_ip']] = None
            else:
                if st.button('Найти свободный IP4 для принтера', help='Поиск происходит в подсети 192.168.0/24'):
                    st.success(self.get_free_ip_in_subnet('192.168.0.0/24', 9100))
            st.text_input('IP4-адрес', value=self.cur_set[self.gala['getval']['wlan_ip']],
                          key=str(i) + 'wlan_ip',
                          disabled=bool(self.disabled))
            self.k_values['wlan_ip']= st.session_state[str(i) + 'wlan_ip']
            return
    def wlan_mask(self,i=''):
        if self.gala['getval']['wlan_mask'] not in self.cur_set:
            self.cur_set[self.gala['getval']['wlan_mask']] = '255.255.255.0'
        st.text_input('Маска подсети', value=self.cur_set[self.gala['getval']['wlan_mask']],
                      key=str(i) + 'wlan_mask',
                      disabled=bool(self.disabled), help='Например:255.255.255.0 \r\n'
                                                         '**Маска подсети**: определяет, какие части IP-адреса используются для идентификации сети и хоста.')
        self.k_values['wlan_mask']= st.session_state[str(i) + 'wlan_mask']
        return
    def wlan_gateway(self,i=''):
        if self.gala['getval']['wlan_gateway'] not in self.cur_set:
            self.cur_set[self.gala['getval']['wlan_gateway']] = '192.168.0.1'
        st.text_input('Шлюз по-умолчанию', value=self.cur_set[self.gala['getval']['wlan_gateway']],
                      key=str(i) + 'wlan_gateway',
                      disabled=bool(self.disabled),
                      help='**Шлюз по умолчанию**: это маршрутизатор, который принтер использует для подключения к другим сетям.')
        self.k_values['wlan_gateway']= st.session_state[str(i) + 'wlan_gateway']
        return
    def wlan_mac(self,i=''):
        st.text_input('Сетевой (беспроводной) MAC-адрес принтера', value=self.cur_set[self.gala['getval']['wlan_mac']],
                      key=str(i) + 'wlan_mac',
                      disabled=True)
        return
    def printer_time(self,i=''):
        pass
    def reset_printer(self,i=''):
        pass
    def factory_default(self,i=''):
        pass
    def configguration_page(self,i=''):
        pass
    def cutter_test(self,i=''):
        pass

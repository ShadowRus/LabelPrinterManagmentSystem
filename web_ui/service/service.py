import socket
from decouple import config
import pandas
import requests
import json
import streamlit as st


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
SGD_GALA = config('SGD_GALA')
gala = read_json_to_dict(SGD_GALA)

def auto_add_printer_response(df):
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
        url_add = str('http://')+str(HOST_BACKEND)+':'+str(PORT_BACKEND)+'/v1/printer'
        response = requests.post(url_add,data=json.dumps(resp))
    return

def manual_add_printer_response(serial,inv_num,url,port,location,in_use):
    resp={}
    if serial != None:
        resp['serial'] =  serial
    if inv_num != None:
        resp['inv_num'] = inv_num
    if url != None:
        resp['url'] = str(url)
    if port != None:
        resp['port'] = int(port)
    else:
        resp['port'] =9100
    if location != None:
        resp['location'] = location
    resp['in_use'] = int(in_use)
    print(resp)
    url_add = str('http://')+str(HOST_BACKEND) + ':' + str(PORT_BACKEND) + '/v1/printer'
    response = requests.post(url_add, data=json.dumps(resp))
    return response.status_code

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
    def serial_no(self,i=''):
        st.text_input('DPI', value=self.cur_set[self.gala['getval']['serial_no']], key=str(i) + 'serial_no', disabled=True)
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
                      key=str(i) + 'mileage',
                      disabled=True)
        return
    def sw_ribbon(self,i=''):
        if self.gala['getval']['sw_ribbon'] == 'off':
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
        return
    def get_index(self,dict_,value):
        keys_list = list(dict_.keys())
        key = [k for k, v in dict_.items() if v == value][0]
        return keys_list.index(key)

    def print_mode(self,i=''):
        st.selectbox('Режимы печати',list(self.gala['setval']['print_mode'].keys()),
                     index=self.get_index(self.gala['setval']['print_mode'],self.cur_set['print_mode']),
                     key=str(i)+'print_mode',
                     disabled=bool(self.disabled), help='- **Режим отрыва**: Это самый базовый режим печати, который подходит для большинства обычных задач печати. В этом режиме принтер печатает этикетку и останавливается, позволяя пользователю вручную оторвать этикетку от принтера. '
                                                        'Это идеально подходит для небольших объемов печати, где потребность в автоматизации отсутствует.\r\n'
                                                        '- **Режим отрезания**: В этом режиме принтер автоматически режет каждую этикетку или набор этикеток после печати.'
                                                        ' Этот режим полезен при печати больших количеств этикеток, особенно когда требуется отдельная этикетка для каждого продукта или упаковки. '
                                                        'Обратите внимание, что для этого режима требуется принтер с встроенным отрезным устройством.\r\n'
                                                        '- **Режим отделителя**: Этот режим предназначен для принтеров, оснащенных дополнительным механизмом отделения, который отделяет наклейку от подложки сразу после печати. '
                                                        'Это удобно в ситуациях, когда вы хотите немедленно наклеить этикетку на продукт или упаковку.')
        st.write(self.gala['setval']['print_mode'][st.session_state[str(i)+'print_mode']])
        return

    def sensor_select(self,i=''):
        st.selectbox('Настройка датчика', list(gala['setval']['sensor_select'].keys()),
                     index=self.get_index(gala['setval']['sensor_select'], self.cur_set['sensor_select']),
                     key=str(i) + 'sensor_select',
                     disabled=bool(self.disabled),help='Выберите датчик носителя, соответствующий используемому носителю. '
                                                       'Датчик отражения( **на отражение**) следует использовать только для носителя с черными метками. '
                                                       'Для других типов носителя следует использовать передающий датчик(**на просвет**).')
        st.write(self.gala['setval']['sensor_select'][st.session_state[str(i)+'sensor_select']])
        return
    def media_power_up(self,i=''):
        st.selectbox('Действие при включении', list(gala['setval']['media_power_up'].keys()),
                     index=self.get_index(gala['setval']['media_power_up'], self.cur_set['media_power_up']),
                     key=str(i) + 'media_power_up',
                     disabled=bool(self.disabled),
                     help='- **Промотка**: очень полезна, если вы регулярно меняете типы этикеток в принтере. Это позволяет обеспечить, что этикетка готова к печати сразу после включения устройства. \r\n'
                          '- **Калибровка**: необходима при первом использовании принтера, после замены рулона этикеток или при возникновении проблем с печатью. Если принтер используется с одним и тем же типом этикеток, и нет проблем с печатью, калибровка при каждом включении может быть избыточной.\r\n'
                          '- **Действие не требуется**: это подходит для стабильных рабочих сред, где тип этикеток и задачи печати не меняются часто. Это позволяет сэкономить время на подготовке к печати после включения устройства.')
        st.write(self.gala['setval']['media_power_up'][st.session_state[str(i) + 'media_power_up']])
        return
    def head_close(self,i=''):
        st.selectbox('Действие при закрытии печатающей головы', list(gala['setval']['head_close'].keys()),
                     index=self.get_index(gala['setval']['head_close'], self.cur_set['head_close']),
                     key=str(i) + 'head_close',
                     disabled=bool(self.disabled),
                     help=' - **Промотка**: Если вы только что вставили новый рулон этикеток, может быть полезно выполнить промотку, чтобы убедиться, что этикетки подаются правильно.\r\n'
                          '- **Калибровка**: Если после закрытия печатающей головки вы заметили проблемы с печатью (например, печать смещается или этикетки не выравниваются правильно), вам может потребоваться выполнить калибровку.\r\n'
                          '- В большинстве случаев, если принтер работает нормально и не требует обслуживания, **дополнительные действия** при закрытии печатающей головки **не требуются**.')
        st.write(self.gala['setval']['head_close'][st.session_state[str(i) + 'head_close']])
        return

    def tear_off(self,i=''):
        st.slider('Отрыв.Настройка положеия остановки носителя',min_value=self.gala['setval']['tear_off']['min'],
                  max_value=self.gala['setval']['tear_off']['max'],
                  value=int(self.cur_set['tear_off']),disabled=bool(self.disabled),key=str(i)+'tear_off',help='Эта настройка позволяет точно настроить положение остановки носителя.'
                                                                                                             ' Диапазон значений: от «+» до «–»')
        st.write(st.session_state[str(i)+'tear_off'])
        return
    def buzzer(self,i=''):
        st.selectbox('Громкость динамика принтера', list(gala['setval']['buzzer'].keys()),
                     index=self.get_index(gala['setval']['buzzer'], self.cur_set['buzzer']),
                     key=str(i) + 'buzzer',
                     disabled=bool(self.disabled),
                     help='- **Отключенная**: Если принтер используется в тихой среде, такой как офис или библиотека, где шум может быть нарушающим, отключение звуковых сигналов может быть хорошим выбором. \r\n'
                          '- **Низкая**: Это может быть хорошим выбором для рабочих мест, где некоторый уровень шума допустим, но громкие звуки могут быть беспокойными. Например, в небольшом магазине или в офисном пространстве с несколькими сотрудниками. \r\n'
                          '- **Стандартная**: Большинство людей будут использовать стандартный уровень громкости. Это обеспечивает достаточно звука, чтобы быть слышимым, но не настолько громким, чтобы быть беспокойным.\r\n'
                          '- **Громкая**: Громкий уровень обычно используется в шумных средах, таких как склады или производственные площади, где тише звуки могут быть неслышны.')
        st.write(self.gala['setval']['buzzer'][st.session_state[str(i) + 'buzzer']])
        return
    def speed(self,i=''):
        st.slider('Скорость печати', min_value=self.gala['setval']['speed']['min'],
                  max_value=self.gala['setval']['speed']['max'],
                  value=int(self.cur_set['speed']), disabled=bool(self.disabled), key=str(i) + 'speed',
                  help='Выбор скорости печати на принтере этикеток зависит от нескольких факторов, включая качество печати, количество этикеток, которые вам нужно напечатать, и скорость, с которой вам нужны эти этикетки.\r\n'
                       '- **Высокая скорость печати**: Чем выше скорость печати, тем быстрее принтер сможет напечатать этикетки. '
                       'Это особенно полезно, если вам нужно напечатать большое количество этикеток за короткое время. '
                       'Однако, пожертвование скоростью может привести к некоторому снижению качества печати, особенно для сложных или детализированных изображений.\r\n'
                       '- **Низкая скорость печати**: Чем ниже скорость печати, тем выше будет качество печати.'
                       ' Это может быть важно, если вы печатаете этикетки с сложными деталями, такими как маленькие шрифты или сложные графические изображения.'
                       ' Однако, печать будет происходить медленнее.\r\n'
                       '- **Средняя скорость печати**: Это компромисс между скоростью и качеством печати. '
                       'Если вам нужно напечатать умеренное количество этикеток и вы хотите хорошее качество печати, это может быть хорошим выбором.')
        st.write(st.session_state[str(i) + 'speed'])
        return
    def density(self,i=''):
        st.slider('Скорость печати', min_value=self.gala['setval']['density']['min'],
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
        st.write(st.session_state[str(i) + 'density'])
        return
    def media_sensor(self,i=''):
        pass
    def ethernet_switch(self,i=''):
        pass
    def eth_dhcp(self,i=''):
        pass
    def eth_ip(self,i=''):
        pass
    def eth_mask(self,i=''):
        pass
    def eth_gateway(self,i=''):
        pass
    def eth_mac(self,i=''):
        pass
    def wlan_dhcp(self,i=''):
        pass
    def wlan_mod(self,i=''):
        pass
    def wlan_ssid(self,i=''):
        pass
    def wlan_key_require(self,i=''):
        pass
    def wlan_key(self,i=''):
        pass
    def wlan_ip(self,i=''):
        pass
    def wlan_mask(self,i=''):
        pass
    def wlan_gateway(self,i=''):
        pass
    def wlan_mac(self,i=''):
        pass
    def wlan_key_require(self,i=''):
        pass
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

import streamlit as st
import os
from decouple import config
import pandas as pd
from service.service import auto_add_printer_response,manual_add_printer_response,check_state,gala,PrinterSettings,printers,printer_info,scan_network,get_current_set,set_value,do


SRC_UI = config('SRC_UI',default='./web_ui/src')


def send_set_value(key,gala):
    if key in st.session_state['curr_set']:
        if key not in ['sw_ribbon','print_mode','sensor_select','media_power_up','buzzer',
                           'head_close','media_sensor','ethernet_switch','eth_dhcp','wlan_dhcp',
                           'wlan_mod','wlan_key_require']:
            if str(st.session_state[str(i) + key]) != st.session_state['curr_set'][key]:
                status, re_data = set_value(hoster, 9100, key, st.session_state[str(i) + key])
                if status == 200:
                    st.toast(f':green[Применено]: **{key}**   **:red[{st.session_state[str(i) + key]}]**')
                else:
                    st.toast(f':red[Не применено]: **{key}**   **:red[{st.session_state[str(i) + key]}]**')
        elif key == 'sw_ribbon':
            if st.session_state['curr_set']['sw_ribbon'] == 'on':
                temp1= True
            else:
                temp1 = False
            if temp1 != st.session_state[str(i) + 'sw_ribbon']:
                if st.session_state[str(i) + 'sw_ribbon'] == True:
                    temp1 = 'on'
                else:
                    temp1 = 'off'
                status, re_data = set_value(hoster, 9100, key, temp1)
                if status == 200:
                    st.toast(f':green[Применено]: **ТТП**   **:red[{temp1}]**')
                else:
                    st.toast(f':red[Не применено]: **ТТП**   **:red[{temp1}]**')
        elif key in ['print_mode','sensor_select','media_power_up','head_close','media_sensor','wlan_mod','buzzer']:
            if st.session_state['curr_set'][key] != gala['setval'][key][st.session_state[str(i) + key]]:
                status, re_data = set_value(hoster, 9100, key, gala['setval'][key][st.session_state[str(i)+key]])
                if status == 200:
                    st.toast(f':green[Применено]: **{key}**   **:red[{st.session_state[str(i)+key]}]**')
                else:
                    st.toast(f':red[Не применено]: **{key}**   **:red[{st.session_state[str(i)+key]}]**')
        # elif key == 'buzzer':
        #     st.write(st.session_state['curr_set'][key])
        #     st.write(gala['setval'][key][st.session_state[str(i) + key]])
        #     if st.session_state['curr_set'][key] != gala['setval'][key][st.session_state[str(i) + key]]:
        #         st.write(gala['setval'][key][st.session_state[str(i)+key]])
                # status, re_data = set_value(hoster, 9100, key, gala['setval'][key][st.session_state[str(i)+key]])
                # if status == 200:
                #     st.toast(f':green[Применено]: **{key}**   **:red[{st.session_state[str(i)+key]}]**')
                # else:
                #     st.toast(f':red[Не применено]: **{key}**   **:red[{st.session_state[str(i)+key]}]**')








st.image(os.path.join(SRC_UI,'Logo_cyrillic_red.png'))
st.markdown('## Принтеры',unsafe_allow_html=True)

if 'curr_set' not in st.session_state:
    st.session_state['curr_set'] = {}
if 'scan_pr' not in st.session_state:
    st.session_state['scan_pr'] = {}

with st.sidebar:
    st.selectbox('**Принтеры :red[АТОЛ]**',['Изменение настроек','Добавление принтеров',
                                            'Профили','Состояние парка','Настройки системы'],key = 'sidebar_main')

if st.session_state['sidebar_main'] == 'Добавление принтеров':

    df_printers = printers()
    if st.button('Обновить'):
        st.rerun()
    st.data_editor(df_printers)
    dict_print = df_printers['serial'].to_dict()
    st.multiselect('Choose printer',dict_print.values(),key='printer_info')
    st.write(st.session_state['printer_info'])
    for i in range(len(st.session_state['printer_info'])):
        st.write('index')
        st.write(st.session_state['printer_info'][i])
        printer_id = df_printers.loc[df_printers['serial'] == st.session_state['printer_info'][i]].index.tolist()
        #st.write(printer_id)
    #df.loc[df['col1'] == 3].index.tolist()


    st.markdown('## Выберите нужную вкладку для добавления принтеров',unsafe_allow_html=True)
    add_auto, add_manual = st.tabs(['Автоматически','Ручное добавление'])

    # Ручное добавление принтеров
    with add_manual:
        # Добавляем из файла: есть шаблон с полями, загружаем шаблон, затем его заполняем и загружаем на ресурс
        if st.checkbox('Добавить из файла',value=True):
            with open(os.path.join(SRC_UI,'template_add_printer.xlsx'), "rb") as file:
                btn = st.download_button(
                    label="Загрузить шаблон для добавления",
                    data=file,
                    file_name="template_add_printer.xlsx",
                    mime="excel/xlsx"
                )

            uploaded_file = st.file_uploader("Загрузите файл с списком адресов принтеров", type=['xlsx'],
                                             help='Для формирования файла воспользуйтесь шаблоном выше')
            if uploaded_file:
                df = pd.read_excel(uploaded_file)
                # Удаление столбцов, где нет значений
                df = df.dropna(axis=1, how='all')
                # Отображение таблицы
                st.markdown('Проверьте загруженные данные')
                st.table(df)
                if st.button('Добавить'):
                    # отправляем данные из файла на сервер
                    success_resp,error_resp = auto_add_printer_response(df)
                    st.success(success_resp)
                    st.error(error_resp)



        else:
            with st.expander('Добавить принтер'):
                st.toggle('Принтер подключен и готов к работе',help="После добавления принтера произойдет опрос принтера и загрузка требуемой конфигурации",key='in_use')
                if st.checkbox('Serial_number',value=True):
                    st.text_input('Серийный номер принтера',key='serial')
                    if st.checkbox('Добавить инвентарный номер для учета', value=False):
                        st.text_input('Инвентарный номер принетера',key='inv_num')
                if st.checkbox('HOST:PORT',value=False):
                    st.text_input('Сетевой адрес принтера',key='url')
                    st.text_input('Порт принтера', value='9100',help='По умолчанию порт принтера 9100',key='port')
                if st.checkbox('Расположение принтера',
                               help="При необходимости можно указать конкретное место,где планируется установка принтера"):
                    st.text_input('Физическое расположение принтера',key='location')
                if st.button('Добавить'):
                    status,resp_data = manual_add_printer_response(check_state('serial',st.session_state),
                                                check_state('inv_num',st.session_state),
                                                check_state('url',st.session_state),
                                                check_state('port',st.session_state),
                                                check_state('location',st.session_state),
                                                check_state('in_use',st.session_state))
                    print(f'{status}, {resp_data}')
                    if status == 200:
                        st.success('Принтер успешно добавлен')
                        st.write(resp_data['status'])
                        #status,resp_data = add_printer_info(resp_data['status'],check_state('serial',st.session_state),check_state('url',st.session_state))

                    else:
                        st.error('Добавить принтер не удалось. Повторите операцию позднее')


if st.session_state['sidebar_main'] == 'Изменение настроек':
    st.text_input('Диапазон сети',value='192.168.0.0/24',key='network_1')
    if st.button('Сканировать сеть',key='scan_net'):
        status,resp_data = scan_network(st.session_state['network_1'],9100)
        if status == 200:
            #st.write(resp_data)
            st.session_state['scan_pr'] = resp_data
    st.markdown('### Настройки', unsafe_allow_html=True)
    if st.checkbox('Указать вручную сетевой адрес принтера'):
        st.text_input('IP4',key = 'ip_4_1')
        hoster = st.session_state['ip_4_1']
    else:
        lst = {}
        for key, value in st.session_state['scan_pr'].items():
            # преобразование ключа и значения в строку и добавление в список
            lst[(str(key) + ' ('+ str(value) + ')')] = str(key)
        st.selectbox('Выберите принтер',lst.keys(),key = 'ip_4_1')
        if 'ip_4_1' in st.session_state:
            if st.session_state['ip_4_1'] != None:
                hoster = lst[st.session_state['ip_4_1']]
    if st.button('Получить текущие настройки'):
        status, resp_data = get_current_set(hoster, 9100)
        if status == 200:
            st.session_state['curr_set'] = resp_data['status']
    printer = PrinterSettings(gala, st.session_state['curr_set'])
    if st.session_state['curr_set'] != {}:
        printer.change_disabled()
        i = ''
        if 'serial_no' in st.session_state['curr_set']:
            printer.serial_no()
        if 'printer_version' in st.session_state['curr_set']:
            printer.printer_version()
        if 'model' in st.session_state['curr_set']:
            printer.model()
        if 'mileage' in st.session_state['curr_set']:
            printer.mileage()
        if 'cutter_cnt' in st.session_state['curr_set']:
            printer.cutter_cnt()
        if 'sw_ribbon' in st.session_state['curr_set']:
            printer.sw_ribbon()
        if 'print_mode' in st.session_state['curr_set']:
            printer.print_mode()
        if 'dpi' in st.session_state['curr_set']:
            printer.dpi()
        if 'tear_off' in st.session_state['curr_set']:
            printer.tear_off()
        if 'sensor_select' in st.session_state['curr_set']:
            printer.sensor_select()
        if 'media_power_up' in st.session_state['curr_set']:
            if st.session_state['curr_set']['media_power_up'] not in ['', None]:
                printer.media_power_up()
        # if 'head_close' in st.session_state['curr_set']:
        #     if st.session_state['curr_set']['head_close'] not in ['',None]:
        #         printer.head_close()
        if 'buzzer' in st.session_state['curr_set']:
            if st.session_state['curr_set']['buzzer'] not in ['', None, "None", 'none']:
                printer.buzzer()
        if 'speed' in st.session_state['curr_set']:
            printer.speed()
        if 'density' in st.session_state['curr_set']:
            printer.density()
        if 'media_sensor' in st.session_state['curr_set']:
            printer.media_sensor()
        if 'ethernet_switch' in st.session_state['curr_set']:
            printer.ethernet_switch()
        if 'eth_dhcp' in st.session_state['curr_set']:
            printer.eth_dhcp()
        if 'eth_ip' in st.session_state['curr_set']:
            printer.eth_ip()
        if 'eth_mask' in st.session_state['curr_set']:
            printer.eth_mask()
        if 'eth_gateway' in st.session_state['curr_set']:
            printer.eth_gateway()
        if 'eth_mac' in st.session_state['curr_set']:
            printer.eth_mac()
        if 'wlan_mod' in st.session_state['curr_set']:
            if st.session_state['curr_set']['buzzer'] not in ['', None, "None", 'none']:
                printer.wlan_mode()
                if 'wlan_ssid' in st.session_state['curr_set']:
                    printer.wlan_ssid()
                if 'wlan_key' in st.session_state['curr_set']:
                    printer.wlan_key()
                if 'wlan_dhcp' in st.session_state['curr_set']:
                    printer.wlan_dhcp()
                if 'wlan_ip' in st.session_state['curr_set']:
                    printer.wlan_ip()
                if 'wlan_mask' in st.session_state['curr_set']:
                    printer.wlan_mask()
                if 'wlan_gateway' in st.session_state['curr_set']:
                    printer.wlan_gateway()
                if 'wlan_mac' in st.session_state['curr_set']:
                    printer.wlan_mac()
                if 'wlan_key_require' in st.session_state['curr_set']:
                    printer.wlan_key_require()
        if st.session_state[str(i)+'is_disabled'] == True:
            if st.button('Обновить настройки'):
                st.success(f"Настройки успешно обновлены на {st.session_state['ip_4_1']} ( {st.session_state[str(i) + 'serial_no']} )")
                st.write(st.session_state)
                send_set_value('sw_ribbon',gala)
                send_set_value('print_mode', gala)
                send_set_value('tear_off', gala)
                send_set_value('sensor_select', gala)
                send_set_value('media_power_up', gala)
                send_set_value('head_close', gala)
                send_set_value('buzzer', gala)
                send_set_value('speed', gala)
                send_set_value('density', gala)
                send_set_value('media_sensor', gala)
                #send_set_value('ethernet_switch', gala)
                #send_set_value('eth_dhcp', gala)
                send_set_value('eth_ip', gala)
                send_set_value('eth_mask', gala)
                send_set_value('eth_gateway', gala)
                send_set_value('wlan_mod', gala)
                send_set_value('wlan_ssid', gala)
                send_set_value('wlan_key', gala)
                #send_set_value('wlan_dhcp', gala)
                send_set_value('wlan_ip', gala)
                send_set_value('wlan_mask', gala)
                send_set_value('wlan_gateway', gala)
                #send_set_value('wlan_key_require', gala)

        #st.write(st.session_state)














# cur_set = {
#     "printer_version":'0.0.1',
#     "sw_ribbon":'on',
#     "print_mode":"tear",
#     "sensor_select":"auto",
#     "media_power_up":'none',
#     "head_close":'feed',
#     "tear_off":14,
#     "buzzer":"3",
#     "speed":12,
#     "density":30,
#     "media_sensor":"gap",
#     "ethernet_switch":"on",
#     "eth_dhcp":"of",
#     "eth_mac":'rdrtyfuyguh',
#     "eth_gateway":None,
#     'eth_mask':None,
#     "eth_ip":'192.168.0.4',
#     "wlan_dhcp":'off',
#     "wlan_mod":'ap',
#     "wlan_key_require":'YES',
#     "wlan_mac":"wlan_mac",
#     "wlan_gateway":None,
#     "wlan_mask":None,
#     "wlan_ip":None,
#     "wlan_key":'123456788',
#     "wlan_ssid":'ATOL_GUESTS'
#
#
#
# }
# printer = PrinterSettings(gala,cur_set)
# printer.change_disabled()
# printer.printer_version()
# printer.sw_ribbon()
# printer.print_mode()
# printer.sensor_select()
# printer.media_power_up()
# printer.head_close()
# printer.tear_off()
# printer.buzzer()
# printer.speed()
# printer.density()
# printer.ethernet_switch()
# printer.eth_dhcp()
# printer.eth_mac()
# printer.eth_ip()
# printer.eth_mask()
# printer.eth_gateway()
# printer.wlan_dhcp()
# printer.wlan_ssid()
# printer.wlan_gateway()
# printer.wlan_mask()
# printer.wlan_mac()
# printer.wlan_mode()
# printer.wlan_key()
# printer.wlan_key_require()
# printer.wlan_ip()
# printer.reuest_data()


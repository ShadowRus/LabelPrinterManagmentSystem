import streamlit as st
import os
from decouple import config
import pandas as pd
from service.service import auto_add_printer_response,manual_add_printer_response,check_state,gala,PrinterSettings,printers,printer_info


SRC_UI = config('SRC_UI',default='./web_ui/src')





st.image(os.path.join(SRC_UI,'Logo_cyrillic_red.png'))

st.markdown('## Принтеры',unsafe_allow_html=True)
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

                else:
                    st.error('Добавить принтер не удалось. Повторите операцию позднее')










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


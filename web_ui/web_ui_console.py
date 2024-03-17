import streamlit as st
import os
from decouple import config
import pandas as pd
from service.service import auto_add_printer_response,manual_add_printer_response,check_state,gala,PrinterSettings


SRC_UI = config('SRC_UI',default='./web_ui/src')





st.image(os.path.join(SRC_UI,'Logo_cyrillic_red.png'))
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
                auto_add_printer_response(df)



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
                st.text_input('Физичесекое расположение принтера',key='location')
            if st.button('Добавить'):
                manual_add_printer_response(check_state('serial',st.session_state),
                                            check_state('inv_num',st.session_state),
                                            check_state('url',st.session_state),
                                            check_state('port',st.session_state),
                                            check_state('location',st.session_state),
                                            check_state('in_use',st.session_state))

cur_set = {
    "printer_version":'0.0.1',
    "sw_ribbon":'on',
    "print_mode":"tear",
    "sensor_select":"auto",
    "media_power_up":'none',
    "head_close":'feed',
    "tear_off":14,
    "buzzer":"3",
    "speed":12,
    "density":30

}
printer = PrinterSettings(gala,cur_set)
printer.change_disabled()
printer.printer_version()
printer.sw_ribbon()
printer.print_mode()
printer.sensor_select()
printer.media_power_up()
printer.head_close()
printer.tear_off()
printer.buzzer()
printer.speed()
printer.density()
import streamlit as st
import os
from decouple import config
import pandas as pd
from service.service import add_printer_response


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
                add_printer_response(df)



    else:
        with st.expander('Добавить принтер'):
            if st.checkbox('Serial_number',value=True):
                st.text_input('Серийный номер принтера')
                if st.checkbox('Добавить инвентарный номер для учета', value=False):
                    st.text_input('Инвентарный номер принетера')
            if st.checkbox('HOST:PORT',value=False):
                st.text_input('Сетевой адрес принтера',key='add_host')
                st.text_input('Порт принтера', value='9100',help='По умолчанию порт принтера 9100')
            if st.checkbox('Расположение принтера',help="")

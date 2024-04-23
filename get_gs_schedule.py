import gspread
from google.oauth2.service_account import Credentials
# В ДОСТУП к файлу - обязательно добавить e-mail клиента - из проекта Google!!!

from pprint import pprint
from datetime import datetime
import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов


scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    'E:\Trading\keys\mypython-412919-56da1c8c153b.json',    # путь к файлу json с ключом API Google
    scopes=scopes
)
gc = gspread.authorize(credentials)

#=====================================
def get_schedule_dates():
    sheet2 = gc.open('График_работы_брови').worksheet("Schedule")

    ##### поиск стартовой и конечной даты
    start_date = '23-04-2024'  # указать первую дату из dikidi
    end_date = '01-05-2024'    # указать последнюю дату из dikidi

    # Поиск значения дат в столбце 1 и получение их номера ряда
    start_date_g = sheet2.findall(start_date, in_column=1)[0]
    start_row = start_date_g.row
    end_date_g = sheet2.findall(end_date, in_column=1)[0]
    end_row = end_date_g.row

    # # Получение данных из определенного диапазона

    data_schedule = sheet2.get(f'A{start_row}:L{end_row}')

    # # Создание DataFrame из полученных данных
    columns = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18']

    df_schedule = pd.DataFrame(data_schedule)   # план работы
    # Устанавливаем первый столбец из data_schedule в качестве индекса
    df_schedule.set_index(0, inplace=True)
    df_schedule_ready = df_schedule.fillna("None")
    df_schedule_ready2 = df_schedule_ready.rename(columns={1: 8, 2: 9, 3: 10, 4: 11, 5: 12, 6: 13, 7: 14, 8: 15, 9: 16, 10: 17, 11: 18})

    # Удаление заголовка у индексного столбца
    df_schedule_ready2.index.name = None
    # Замена значений None на пустые значения
    df_schedule_ready2.replace('None', '', inplace=True)
    # Переформатирование значений даты в индексном столбце
    df_schedule_ready2.index = pd.to_datetime(df_schedule_ready2.index, format='%d-%m-%Y').strftime('%Y-%m-%d')

    # print(df_schedule_ready2)

    return df_schedule_ready2.fillna('')

print(get_schedule_dates())

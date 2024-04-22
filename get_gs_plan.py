# pip install Pyarrow


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

def get_plan_dates():
    sheet = gc.open('График_работы_брови').worksheet("Plan")

    ##### поиск стартовой и конечной даты
    start_date = '23-04-2024'  # указать первую дату из dikidi
    end_date = '02-05-2024'    # указать последнюю дату из dikidi

    # Поиск значения дат в столбце 1 и получение их номера ряда
    start_date_g = sheet.findall(start_date, in_column=1)[0]
    start_row = start_date_g.row
    end_date_g = sheet.findall(end_date, in_column=1)[0]
    end_row = end_date_g.row


    # # Получение данных из определенного диапазона
    #data = sheet.get_values(start_row, 1, end_row, 5)
    data_plan = sheet.get(f'A{start_row}:E{end_row}')
    # # Создание DataFrame из полученных данных
    df_plan_short = pd.DataFrame(data_plan, columns=None)   # план работы

    #print(df_plan_short)

    date_time_plan = {}
    for index, row in df_plan_short.iterrows():
        date_ = row[0]
        time_1 = 0
        time_2 = 0
        time_3 = 0
        time_4 = 0
        if row[1] is not None:
            time_1 = int(row[1])
        if row[2] is not None:
            time_2 = int(row[2])
        if row[3] is not None:
            time_3 = int(row[3])
        if row[4] is not None:
            time_4 = int(row[4])
        values = []
        if time_2 != 0 and time_1 != 0 and time_2 > time_1:
            for i in range(time_1, time_2):       # время работы (1) с ... и до...
                values.append(datetime.strptime(f"{i:02}:00", "%H:%M").strftime("%H:%M"))
        if time_4 !=0 and time_3 != 0 and time_2 != 0 and time_4 > time_3 > time_2:
            for y in range(time_3, time_4):       # время работы (2) с ... и до...
                values.append(datetime.strptime(f"{y:02}:00", "%H:%M").strftime("%H:%M"))

        formatted_date = datetime.strptime(date_, "%d-%m-%Y").strftime("%Y-%m-%d")
        date_time_plan[formatted_date] = values      # создали словарь с планом работы и со всеми часами доступными для записи по дням


    df_plan = pd.DataFrame(columns=['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'])
    # Загрузка данных из словаря в DataFrame
    for date, times in date_time_plan.items():
        #df_dikidi.at[date, 'Date'] = date

        for time_p in times:
            hour = int(time_p.split(':')[0])
            df_plan.at[date, str(hour)] = time_p

    # pprint(date_time_plan)
    print('Дата фрейм plan:\n', df_plan)
    return df_plan



#get_plan_dates()
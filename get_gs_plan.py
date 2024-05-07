import gspread
from google.oauth2.service_account import Credentials
# # В ДОСТУП к файлу - обязательно добавить e-mail клиента - из проекта Google!!!

from datetime import datetime
import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов

from tabulate import tabulate
import traceback

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    'keys/mypython-412919-56da1c8c153b.json',    # путь к файлу json с ключом API Google
    scopes=scopes
)
gc = gspread.authorize(credentials)

#=====================================

def get_plan_dates(date1, date2):           # date1, date2 - начальная и конечная даты (полученные из df_dikidi)
    try:
        sheet = gc.open('График_работы_брови').worksheet("Plan")

        # форматируем даты начала и конца в нужный формат
        date1_f = datetime.strptime(date1, "%Y-%m-%d").strftime("%d-%m-%Y")
        date2_f = datetime.strptime(date2, "%Y-%m-%d").strftime("%d-%m-%Y")


        # Поиск значения дат на листе gspread Plan в столбце 1 и получение их номера ряда
        start_date_g = sheet.findall(date1_f, in_column=1)[0]
        start_row = start_date_g.row
        end_date_g = sheet.findall(date2_f, in_column=1)[0]
        end_row = end_date_g.row


        # Получение данных из определенного диапазона
        data_plan = sheet.get(f'A{start_row}:E{end_row}')    # .get возвращает только непустые строки

        # Создание DataFrame из полученных данных
        df_plan_short = pd.DataFrame(data_plan, columns=None)      # график работы в ИСХОДНОМ варианте - в виде предвариетльного датафрейма

        # Собираем словарь из дат и времени (для дальнейшего формирования датафрейма)
        date_time_plan = {}
        for index, row in df_plan_short.iterrows():    # пербираем предварительный датафрейм построчно
            date_ = row[0]
            time_1 = 0
            time_2 = 0
            time_3 = 0
            time_4 = 0
            if row[1] is not None:
                time_1 = int(row[1])                    # получаем диапазоны времени работы по графику
            if row[2] is not None:
                time_2 = int(row[2])
            if row[3] is not None:
                time_3 = int(row[3])
            if row[4] is not None:
                time_4 = int(row[4])
            values = []                                 # пустой список для времени работы
            if time_2 != 0 and time_1 != 0 and time_2 > time_1:                                   # если время начала и конца работы (1 период) - не пустые..
                for i in range(time_1, time_2):                                                   # перебираем все часы от начала до конца 1 периода работы
                    values.append(datetime.strptime(f"{i:02}:00", "%H:%M").strftime("%H:%M"))     # записываем значения в список
            if time_4 !=0 and time_3 != 0 and time_2 != 0 and time_4 > time_3 > time_2:           # если время начала и конца работы (2 период) - не пустые..
                for y in range(time_3, time_4):                                                   # перебираем все часы от начала до конца 2 периода работы
                    values.append(datetime.strptime(f"{y:02}:00", "%H:%M").strftime("%H:%M"))     # записываем значения в список

            formatted_date = datetime.strptime(date_, "%d-%m-%Y").strftime("%Y-%m-%d")            # форматируем дату
            date_time_plan[formatted_date] = values    # создаем словарь с планом работы и со всеми часами доступными для записи по дням


                # создаем датафрейм с задаными именами заголовков столбцов
        df_plan = pd.DataFrame(columns=['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'])
                # Загрузка данных из словаря в DataFrame
        for date, times in date_time_plan.items():     # перебираем даты и время из словаря графика работ
            for time_p in times:
                hour = int(time_p.split(':')[0])       # отсекаем минуты
                df_plan.at[date, str(hour)] = time_p   # заполняем датафрейм

        print('Дата фрейм plan:\n',  tabulate(df_plan.fillna(''), headers='keys', tablefmt='pretty'))  # выводим разграфленный датафрейм
        return df_plan.fillna('')        # возвращаем заполненный датафрейм, заменяем None на пустые значения

    except Exception as e:
        print(traceback.print_exc())
        print("Ошибка в получении  df_plan (gspread API)")
        return None

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
# credentials = Credentials.from_service_account_file(
#     'keys/mypython-412919-56da1c8c153b.json',    # путь к файлу json с ключом API Google
#     scopes=scopes
# )

credentials_dict = {
      "type": "service_account",
      "project_id": "mypython-412919",
      "private_key_id": "56da1c8c153b37aa7e13ec79edda10c7e6391384",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC3r1ie9J5ct/+q\ni3ta/tMK7EEHpiDPjjCk/pmYQctV75Q/7Un83v6zQQNX6yi79E7tEtzvFdS7676z\nx0ZBDqcXGK4OZhMc89Lt5XgPHXh821vFGKQwY0lYFuPyE3Ftaci32ZzPOgV/30LV\nyzYN51ADBX11QzEh0UD0382kvllndZ8RxbDiZ4J04yxs28rgmIeVEAVDtYnUOpdy\nNzL1cYAcS7VfqTdBflklfMLk0jTU4kMtn5hmdWLWlNb/6KOOMchTzj9CpvhAxvBZ\nT182bhrbaAcg5n2U1TV0DZE3AIvCWykpyM6p7kGyFmMJ876ixq8+9oUru9CuvWtv\njd9wS2U9AgMBAAECggEAIkNcR8xP9PIih+y8PhlOAxnWOIfJ04WNt91BB9hwBi/q\nKrGHzVpITuYX6lC0eLjl9w1/dj6Pf91F5ZGMnoqN6v5Ay3FJa+tkY1lcN4+S/9FI\nMT/7MoZ2si6U5v0u+Y6TsQ2v1SzYxUU/WZNuGhJVh7bAs/ysX8dBc1wC51HVafmC\nhlZbwpH1ZyLgGiZAGBeNmnd7Qd52qHaHimoNvmjaFhxKayYH2aAdbR9F9B9pHPhj\notd9qGJtx9Izsdvc2vD9fiTuTrGD29zVuaVuLIFI/icWZp3fJ3gRy9iYyo/14oLq\nYawZjVPXoX2RcmI+ZLjbPlK0BAT3xNgFadh24ICjCQKBgQD1TZpCQL5xKvtDew/4\nA/uO57J2cFHLXspfzL1wErdTRK2yxin3SSSSpqo/6lpwxauXgBgzWWHcKYXeaIAM\n0Viy6QOMoSYINaQHI+MPmPVTl2lPGc+/tYApG6IsqLZyumQStwSavlEip2SxfJyX\nVHKUOWj5Voi0aJx5C8cpWvXjWQKBgQC/seFJvsTszqlb6n79pyxvWEusu5iL5IhF\n/gNB45wpUICfuNzZ+8vV2cqm4lYGVzAqiiFn/vR02ujQ5XHHCYmhEhjl7xwlnmKT\nTFGmx1bVNrTHpT8G2FajsaLbk5vDl4f/TSFgKk2f1/nM5vg+GIqQTHdGAqxz9q62\nfY6rDE2IhQKBgQCAjlzrn9aupGHuKY5i4mNxr0e9/ns/Y7wXnMsi8wwUnYeSi3vu\n1uxN1v6eZIllVJLq4PzN3GgG49P+jTGehhBAIxHzH3k5EDOYclxLDlRzrIRKKjLQ\nO6Sg5pSFZx3G3pwXmsbU+iy3Rpbk1XOTc3Rg7f1vvsQCGFj4rw1/ROZccQKBgD/8\nrGrlVu6E/VtFJyacSuTP4FLEO+NWYXabl5LC2zmfOZAXMQFCX4P+svqJypVLPTS1\n7vi7zfXDrLsuG5CIynwNgmoeKpMUD2uDqi21lHKPVEDgE+3BAQqbHPWWjAP57Nd3\nc5CaDlcwzJ1s66guoPIR1C52bgI3cZJQzvKhpK/RAoGALzf1ThHowCHNAX7+vBlX\nVZXecLDklbwXuqqGWJwyZm4MoReljalxeODoLEaB+pq7gBaTP+s1j6ZyC84Gcufz\nJXbpKJwVzLuzhtL+VNmNDVLbme1KcZ7YJwPurOi8Dc8POdoUt/NOBZP55sSFopSJ\nxcQwVJz+O2kCzjJ26Hur3IM=\n-----END PRIVATE KEY-----\n",
      "client_email": "gindoe-bot@mypython-412919.iam.gserviceaccount.com",
      "client_id": "108626574650371659949",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gindoe-bot%40mypython-412919.iam.gserviceaccount.com",
      "universe_domain": "googleapis.com"
    }

credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)



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

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
def get_schedule_dates(date1, date2):
    try:
        sheet2 = gc.open('График_работы_брови').worksheet("Schedule")

        # форматируем даты начала и конца в нужный формат
        date1_f = datetime.strptime(date1, "%Y-%m-%d").strftime("%d-%m-%Y")
        date2_f = datetime.strptime(date2, "%Y-%m-%d").strftime("%d-%m-%Y")

        # Поиск значения дат в столбце 1 и получение их номера ряда
        start_date_g = sheet2.findall(date1_f, in_column=1)[0]
        start_row = start_date_g.row
        end_date_g = sheet2.findall(date2_f, in_column=1)[0]
        end_row = end_date_g.row

        # Получение данных из определенного диапазона
        data_schedule = sheet2.get(f'A{start_row}:L{end_row}')

        df_schedule = pd.DataFrame(data_schedule)         # создали датафрейм из полученных данных Расписания
        df_schedule.set_index(0, inplace=True)            # Устанавливаем первый столбец из data_schedule в качестве индекса
        df_schedule_ready = df_schedule.fillna("None")    # Замена пустых значений на None
                # создаем новый датафрейм с замененными названиями столбцов - с цифр (по-умолчанию) на наименование часов в текстовом формате
        df_schedule_ready2 = df_schedule_ready.rename(columns={1: '8', 2: '9', 3: '10', 4: '11', 5: '12', 6: '13', 7: '14', 8: '15', 9: '16', 10: '17', 11: '18'})

        df_schedule_ready2.index.name = None                   # Удаление заголовка у индексного столбца
        df_schedule_ready2.replace('None', '', inplace=True)   # Замена значений None на пустые значения
                # Переформатирование значений даты в индексном столбце
        df_schedule_ready2.index = pd.to_datetime(df_schedule_ready2.index, format='%d-%m-%Y').strftime('%Y-%m-%d')

                # РЕИНДЕКСИРУЕМ столбцы (т.к. если в таблице нет данных в стобце по всем рядам, то они не отображаются в датафрейме)
        columns = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18']
        df_schedule_ready2 = df_schedule_ready2.reindex(columns=columns, fill_value='')
        df_schedule_ = df_schedule_ready2.fillna('')    # Замена None на пустые значения


        # Заполнение предыдущих двух ячеек и одной следующей ячейки после заполненной записью значением 'Недоступно (занято)'
        # т.е. 2 часа ДО процедуры и 1 час ПОСЛЕ процедуры - недоступны будут для записи
        for index, row in df_schedule_.iterrows():
            for column, value in row.items():
                if value != '' and value != 'Недоступно (занято)':
                    index_num = df_schedule_.index.get_loc(index)
                    column_num = df_schedule_.columns.get_loc(column)
                    if column_num >= 1:
                        if df_schedule_.iloc[index_num, column_num - 1] == '':
                            df_schedule_.iloc[index_num, column_num - 1] = 'Недоступно (занято)'  # Заполнения предыдущей ячейки -1
                    if column_num >= 2:
                        if df_schedule_.iloc[index_num, column_num - 2] == '':
                            df_schedule_.iloc[index_num, column_num - 2] = 'Недоступно (занято)'  # Заполнения предыдущей ячейки -2
                    if column_num < (df_schedule_.shape[1] - 1):                  # df_.shape[1] - кол-во столбцов в df_, df_.shape[0] - кол-во рядов в df_
                        if df_schedule_.iloc[index_num, column_num + 1] == '':
                            df_schedule_.iloc[index_num, column_num + 1] = 'Недоступно (занято)'  # Заполнения следующей ячейки +1

                # выводим разграфленный датафрейм с Расписанием
        print('Дата фрейм df_schedule_:\n', tabulate(df_schedule_.fillna(''), headers='keys', tablefmt='pretty'))

        return df_schedule_    # возвращаем сформированный датафрейм

    except Exception as e:
        print(traceback.print_exc())
        print("Ошибка в получении df_schedule (gspread API)")
        return None


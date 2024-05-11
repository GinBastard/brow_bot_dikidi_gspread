import gspread
from google.oauth2.service_account import Credentials
# # В ДОСТУП к файлу - обязательно добавить e-mail клиента - из проекта Google!!!

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

def set_schedule(date_time, procedure, place, phone, user_name, user_link, note):
    sheet2 = gc.open('График_работы_брови').worksheet("Schedule")

    date, time = date_time.split()                         # разделяем дату и время
    date_cell = sheet2.findall(date, in_column=1)[0]       # ищем дату в таблице в стобце 1
    date_row = date_cell.row                               # получаем номер ряда (координату x)

    time_hour = time.split(':')[0]                         # разделяем время на часы и минуты (получаем час)
    time_cell = sheet2.find(time_hour, in_row=2)           # ищем время в таблице в ряду 2 (заголовки)
    time_col = time_cell.col                               # получаем номер столбца (координату y)

          # формируем строку для записи в Расписание (данные получены из handlers.py)
    text = f"Запись: {procedure}, {place}, {user_name}, {phone}, {user_link}, {date_time}, {note}"
          # записываем строку в Расписание по установленным координатам ячейки
    sheet2.update_cell(date_row, time_col, text)
    sheet2.update_cell(date_row, time_col+1, text)  # заполнение второго столбца, т.к. процедура идет 2 часа

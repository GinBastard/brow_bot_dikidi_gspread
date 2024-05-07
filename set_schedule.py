import gspread
from google.oauth2.service_account import Credentials
# # В ДОСТУП к файлу - обязательно добавить e-mail клиента - из проекта Google!!!

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    'keys/mypython-412919-56da1c8c153b.json',    # путь к файлу json с ключом API Google
    scopes=scopes
)
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

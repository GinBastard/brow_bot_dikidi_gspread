import gspread
from google.oauth2.service_account import Credentials
# # В ДОСТУП к файлу - обязательно добавить e-mail клиента - из проекта Google!!!

from pprint import pprint
from datetime import datetime

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    'E:\Trading\keys\mypython-412919-56da1c8c153b.json',    # путь к файлу json с ключом API Google
    scopes=scopes
)
gc = gspread.authorize(credentials)

def set_schedule(date_time, procedure, place, phone, user_name, note):
    sheet2 = gc.open('График_работы_брови').worksheet("Schedule")

    date, time = date_time.split()
    date_cell = sheet2.findall(date, in_column=1)[0]
    date_row = date_cell.row
    #date_col = date_cell.col

    time_hour = time.split(':')[0]
    time_cell = sheet2.find(time_hour, in_row=2)
    #time_row = time_cell.row
    time_col = time_cell.col

    text = f"Запись: {procedure}, {place}, {user_name}, {phone}, {date_time}, {note}"

    sheet2.update_cell(date_row, time_col, text)

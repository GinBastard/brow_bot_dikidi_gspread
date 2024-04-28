from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from collections import defaultdict
from datetime import datetime

def create_keyboard_procedures(procedures):          # по 2 кнопки в ряду
    buttons = [KeyboardButton(text=text) for text in procedures]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    return keyboard

def create_keyboard_places(places):              # в каждом ряду - по одной кнопке
    buttons = [KeyboardButton(text=text) for text in places]
    keyboard = ReplyKeyboardMarkup(keyboard=[[button] for button in buttons], resize_keyboard=True)
    return keyboard




def create_keyboard_dates_and_times(dt):               # выводится не более 3 кнопок в ряд, группировка по дате, форматирование даты
    buttons = [KeyboardButton(text=text) for text in dt]
    buttons.sort(key=lambda x: x.text)

    button_dict = defaultdict(list)
    for button in buttons:
        date = button.text.split()[0]
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        button.text = f"{formatted_date} {button.text.split()[1]}"
        button_dict[date].append(button)

    rows = []
    for date, buttons in button_dict.items():
        current_row = []
        for i, button in enumerate(buttons):
            current_row.append(button)
            if len(current_row) == 3 or i == len(buttons) - 1:
                rows.append(current_row)
                current_row = []

    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    return keyboard
def create_keyboard_get_phone():
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер', request_contact=True)]],resize_keyboard=True)
    return keyboard

def create_keyboard_restart():
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Перезагрузить')]],resize_keyboard=True)
    return keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from collections import defaultdict
from datetime import datetime

def create_keyboard_procedures(procedures):       # по 2 кнопки в ряду
    '''
    Cоздает клавиатуру с процедурами
    1. Получаем список процедур, перебираем его и добавлем значения на кнопки
    2. Группируем кнопки в ряды по 2:
          - перебираем последовательность от 0 до длины списка процедур с шагом 2
          - Для каждого четного индекса i мы используем срез buttons[i:i + 2],
            чтобы получить два элемента из buttons, начиная с i и до i + 2.
            Затем мы добавляем этот срез в список rows.
    3. Формируем клавиатуру (передаем список списков rows (по 2 кнопки в ряд))
    :param procedures:
    :return:
    '''
    buttons = [KeyboardButton(text=text) for text in procedures]           # получаем список процедур, перебираем его и добавлем значения на кнопки
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    return keyboard

def create_keyboard_places(places):              # в каждом ряду - по одной кнопке
    '''
    Cоздает клавиатуру с местами
    1. Получаем список мест, перебираем его и добавлем значения на кнопки
    2. Формируем клавиатуру (передаем список кнопок, получая его перебором списка)
    :param places:
    :return:
    '''
    buttons = [KeyboardButton(text=text) for text in places]
    keyboard = ReplyKeyboardMarkup(keyboard=[[button] for button in buttons], resize_keyboard=True)
    return keyboard

def create_keyboard_dates_and_times(dt):               # выводится не более 3 кнопок в ряд, группировка по дате, форматирование даты
    buttons = [KeyboardButton(text=text) for text in dt]   # получаем список дат и времени, перебираем его и добавлем значения на кнопки
    buttons.sort(key=lambda x: x.text)

    button_dict = defaultdict(list)         # создаем словарь для группировки кнопок по дате
    for button in buttons:
        date = button.text.split()[0]                                               # разбиваем текст кнопки по пробеду, получаем дату
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")   # форматируем дату
        button.text = f"{formatted_date} {button.text.split()[1]}"                  # добавляем в текст отформатированную дату
        button_dict[date].append(button)                                            # добавляем кнопку (список времени) в словарь в ключи по дате

    rows = []                                                     # создаем список для рядов кнопок
    for date, buttons in button_dict.items():                     # перебираем словарь кнопок с группировкой по дате
        current_row = []                                          # создаем список для кнопок в ряду
        for i, button in enumerate(buttons):                      # перираем список со всеми кнопками
            current_row.append(button)                            # добавляем кнопку в ряд
            if len(current_row) == 3 or i == len(buttons) - 1:    # если ряд заполнен или это последняя кнопка
                rows.append(current_row)                          # добавляем ряд в список
                current_row = []

    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    return keyboard
def create_keyboard_get_phone():
    '''
    Cоздает клавиатуру для получения номера
    Кнопка "Отправить номер" с запросом Контакта TG (request_contact=True)
    :return:
    '''
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер', request_contact=True)]],resize_keyboard=True)
    return keyboard

def create_keyboard_add_note(add_note_answers):
    '''
    Cоздает клавиатуру для добавления примечания
    Получаем список сообщений для добавления примечания или отказе от него, перебираем его и добавлем значения на кнопки
    :param add_note_answers:
    :return:
    '''
    buttons = [KeyboardButton(text=text) for text in add_note_answers]
    keyboard = ReplyKeyboardMarkup(keyboard=[[button] for button in buttons], resize_keyboard=True)
    return keyboard

def create_keyboard_chat_veron():
    button = InlineKeyboardButton(text="Перейти к чату", url="https://t.me/G_Veronik")
    markup_veron = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return markup_veron

def create_keyboard_start():
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')]],
                                   resize_keyboard=True)
    return keyboard
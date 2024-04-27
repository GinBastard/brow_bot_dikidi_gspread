from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def create_keyboard_procedures(procedures):
    buttons = [KeyboardButton(text=text) for text in procedures]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True) #.add(*buttons)
    return keyboard

def create_keyboard_places(places):
    buttons = [KeyboardButton(text) for text in places]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    return keyboard

def create_keyboard_dates_and_times(dt):
    buttons = [KeyboardButton(text) for text in dt]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    return keyboard

def create_keyboard_get_phone():
    button = KeyboardButton("Отправить номер телефона", request_contact=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(button)
    return keyboard

def create_keyboard_restart():
    button = KeyboardButton("Перезагрузить")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(button)
    return keyboard
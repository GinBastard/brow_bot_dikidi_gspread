
# pip install aiohttp==3.9.0
# pip install -U aiogram
# pip install --force-reinstall -v "aiogram==2.23.1"
# pip install -v "aiogram==2.23.1"

# pip install --force-reinstall -v "aiogram==2.23.1"
# https://skillbox.ru/media/code/chatboty-v-telegram-na-python-chast-2-sozdayem-i-nastraivaem-menyu/?utm_source=media&utm_medium=link&utm_campaign=all_all_media_links_links_articles_all_all_skillbox
import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
    # Для простых тестов и отладки вы можете использовать MemoryStorage,
    # который хранит состояния и данные в памяти. Однако, на боевом сервере для продакшена лучше использовать другие хранилища, такие как RedisStorage.
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import asyncio

import result_date_time as result    # result_date_time(selected_procedure, selected_place)

# tatoo_brow_bot
# t.me/tatoo_brow_bot
API_TOKEN = '7141747698:AAHu-H6Z7w3Jm8kIvjc_6XaGyLzN5bK2x54'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


procedures = ['Межресничка', 'Волоски', 'Гиперреализм', 'Пудровое']
places = ['Звездная', 'Пушкин']


class ProcedureSelection(StatesGroup):
    procedure = State()
class PlaceSelection(StatesGroup):
    place = State()

class DateTimeSelection(StatesGroup):
    date_time = State()

class PhoneNumberSelection(StatesGroup):
    phone = State()


def create_keyboard_procedures(procedures):
    buttons = [KeyboardButton(text) for text in procedures]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
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
    button = types.KeyboardButton("Отправить номер телефона", request_contact=True)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(button)
    return keyboard

def create_keyboard_restart():
    button = types.KeyboardButton("Перезагрузить")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(button)
    return keyboard

dt = []       # список для кнопок выбора даты и времени

# Ваш код обработчиков команд и сообщений

async def restart_bot(bot, dp):
    await bot.close()
    #await bot.session.close()
    await dp.storage.close()
    await dp.storage.wait_closed()

    # Повторное создание экземпляров бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global user_name
    user = message.from_user
    user_name = user.first_name  # Получение имени пользователя

    # Сохранение имени пользователя для дальнейшего использования
    # Например, сохранение в глобальной переменной или базе данных

    await message.answer(f"Привет, {user_name}!\nЯ помогу Вам записаться на прием к мастеру Веронике.")
    await start2(bot, message)

@dp.message_handler()
async def start2(bot, message: types.Message):
    keyboard_procedures = create_keyboard_procedures(procedures)
    await bot.send_message(message.chat.id, "Пожалуйста, выберите процедуру", reply_markup=keyboard_procedures)
    await ProcedureSelection.procedure.set()


@dp.message_handler(state=ProcedureSelection.procedure)
async def process_procedure_choice(message: types.Message, state: FSMContext):
    global selected_procedure

    if message.text not in procedures:
        await message.answer("Пожалуйста, выберите процедуру из списка кнопок.")
    else:
        selected_procedure = message.text

    keyboard_places = create_keyboard_places(places)
    await message.answer(f"Выбрана процедура: {selected_procedure}. Выберите место", reply_markup=keyboard_places)
    await state.update_data(selected_procedure=selected_procedure)
    await PlaceSelection.place.set()



@dp.message_handler(state=PlaceSelection.place)
async def process_place_choice(message: types.Message, state: FSMContext):
    global selected_place

    if message.text not in places:
        await message.answer("Пожалуйста, выберите место из списка кнопок.")
    else:
        selected_place = message.text



    # Здесь вызовите вашу функцию для запуска процесса
    await message.answer(f"Выбрано место: {selected_place}. \nСейчас сверю график и вернусь к Вам (в течение 15-30 секунд), выберем дату и время процедуры.", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(selected_place=selected_place)

    # Отправка сообщения с текстом и эмодзи - песочные часы
    await bot.send_message(message.chat.id, "\U000023F3")

    df_result = result.result_date_time(selected_procedure, selected_place)  # создаем df_result - в файле result_date_time.py

    # Заполняем dt из df_result
    dates = df_result.index
    for date in dates:
        times = [time for time in df_result.loc[date] if time != '']
        if times:
            for time in times:
                dt.append(f"{date} {time}")

    keyboard_dates_and_times = create_keyboard_dates_and_times(dt)
    await message.answer(f"Спасибо за ожидание.\nВыберите дату и время", reply_markup=keyboard_dates_and_times)
    await DateTimeSelection.date_time.set()


@dp.message_handler(state=DateTimeSelection.date_time)
async def process_date_time_choice(message: types.Message, state: FSMContext):
    global selected_date_time

    # Проверка, соответствует ли ввод пользователя одному из значений списка dt
    if message.text not in dt:
        await message.answer("Пожалуйста, выберите дату и время из списка кнопок.")
    else:
        selected_date_time = message.text

    keyboard = create_keyboard_get_phone()
    await message.answer(f"Выбраны дата и время: {selected_date_time}.\nДля того, чтобы можно было подтвердить запись, пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже.", reply_markup=keyboard)
    await state.update_data(selected_date_time=selected_date_time)
    await PhoneNumberSelection.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=PhoneNumberSelection.phone)
async def process_phone_number(message: types.Message, state: FSMContext):
    global user_phone
    user_phone = message.contact.phone_number
    # Сохранение номера телефона в глобальной переменной или базе данных
    await message.answer(f"Спасибо!\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\nХорошего дня!", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(user_phone=user_phone)

    data = await state.get_data()
    selected_procedure = data.get("selected_procedure")
    selected_place = data.get("selected_place")
    selected_date_time = data.get("selected_date_time")


    print(selected_procedure)
    print(selected_place)
    print(selected_date_time)
    print(user_name)
    print(user_phone)

    # Отправка сообщения пользователю с командой /reset
    keyboard_restart = create_keyboard_restart()
    await message.answer("Нажмите Перезагрузить, чтобы сбросить настройки.", reply_markup=keyboard_restart)
    if message.text == "Перезагрузить":
        # selected_procedure = None
        # selected_place = None
        # selected_date_time = None
        # user_phone = None
        # Вызов функции перезапуска бота
        # # Сброс остальных сохраненных данных, если есть
        await state.reset_state()
        await state.finish()
        await restart_bot(bot, dp)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(restart_bot(bot, dp))
    executor.start_polling(dp, loop=loop, skip_updates=True)
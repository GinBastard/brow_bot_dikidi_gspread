
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


import result_date_time as result    # result_date_time(selected_procedure, selected_place)

# tatoo_brow_bot
# t.me/tatoo_brow_bot
API_TOKEN = '7141747698:AAHu-H6Z7w3Jm8kIvjc_6XaGyLzN5bK2x54'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())



procedures = ['Межресничка', 'Волоски', 'Гиперреализм', 'Пудровое']
places = ['Звездная', 'Пушкин']


class ProcedureSelection(StatesGroup):
    procedure = State()
class PlaceSelection(StatesGroup):
    place = State()

class DateTimeSelection(StatesGroup):
    date_time = State()

class PhoneNumberSelection(StatesGroup):
    waiting_for_phone = State()



def create_keyboard_procedures(procedures):
    buttons = [KeyboardButton(text) for text in procedures]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    return keyboard

def create_keyboard_places(places):
    buttons = [KeyboardButton(text) for text in places]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    return keyboard

async def create_keyboard_dates_and_times(df_result,  state: FSMContext):
    dt = []
    dates = df_result.index
    for date in dates:
        times = [time for time in df_result.loc[date] if time != '']
        if times:
            for time in times:
                dt.append(f"{date} {time}")
    buttons = [KeyboardButton(text) for text in dt]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    await state.update_data(dt=dt)
    return keyboard

#df_result = None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global user_name
    user = message.from_user
    user_name = user.first_name  # Получение имени пользователя

    # Сохранение имени пользователя для дальнейшего использования
    # Например, сохранение в глобальной переменной или базе данных

    await message.answer(f"Привет, {user_name}!\nЯ помогу Вам записаться на прием к мастеру Веронике.")

@dp.message_handler()
async def start2(message: types.Message):
    keyboard_procedures = create_keyboard_procedures(procedures)
    await message.answer("Пожалуйста, выберите процедуру", reply_markup=keyboard_procedures)
    await ProcedureSelection.procedure.set()


@dp.message_handler(state=ProcedureSelection.procedure)
async def process_procedure_choice(message: types.Message, state: FSMContext):
    global selected_procedure
    selected_procedure = message.text  # выбранная процедура!!

    if selected_procedure not in procedures:
        await message.answer("Пожалуйста, выберите процедуру из списка кнопок.")
        return

    keyboard_places = create_keyboard_places(places)
    await message.answer(f"Выбрана процедура: {selected_procedure}. Выберите место", reply_markup=keyboard_places)
    await state.update_data(selected_procedure=selected_procedure)
    await PlaceSelection.place.set()

@dp.message_handler(state=PlaceSelection.place)
async def process_place_choice(message: types.Message, state: FSMContext):
    global selected_place
    selected_place = message.text

    if selected_place not in places:
        await message.answer("Пожалуйста, выберите место из списка кнопок.")
        return

    # Здесь вызовите вашу функцию для запуска процесса
    await message.answer(f"Выбрано место: {selected_place}. \nСейчас сверю график и вернусь к вам (в теч. 15-30 сек.), выберем дату и время процедуры.", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(selected_place=selected_place)
    await DateTimeSelection.date_time.set()

    df_result = result.result_date_time(selected_procedure, selected_place)  # создаем df_result - в файле result_date_time.py

    keyboard_dates_and_times = create_keyboard_dates_and_times(df_result, state=)

    await message.answer("Спасибо за ожидание.\nВыберите дату и время:", reply_markup=keyboard_dates_and_times)
    await state.update_data(df_result=df_result)



@dp.message_handler(state=DateTimeSelection.date_time)
async def process_date_time_choice(message: types.Message, state: FSMContext):
    global selected_date_time
    #selected_date_time = message.text
    data = await state.get_data()
    df_result = data.get('df_result')
    dt = data.get('dt')
    # Получение доступных дат и времени из датафрейма df_result

    if df_result is not None:
        dates = df_result.index
        times = df_result.columns

    # Проверка, что сообщение пользователя соответствует одной из доступных дат и времени
    if message.text in dt:
        selected_date_time = message.text
    else:
        await message.answer("Пожалуйста, выберите дату и время из списка кнопок.")
        return

    await message.answer(f"Выбраны дата и время: {selected_date_time}.\nЯ отправлю Вашу запись Веронике и она свяжется с Вами для подтверждения в ближайшее время.",reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(selected_date_time=selected_date_time)
    # await message.answer(
    #     f"Выбранные дата и время: {selected_date_time}. \nСпасибо. Я отправлю Вашу запись Веронике и она свяжется с Вами для подтверждения в ближайшее время.",reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['get_phone'])
async def get_phone_number(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Отправить номер телефона", request_contact=True)
        keyboard.add(button)

        await message.answer("Для того, чтобы можно было подтвердить запись, пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже.", reply_markup=keyboard)
        await PhoneNumberSelection.waiting_for_phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=PhoneNumberSelection.waiting_for_phone)
async def process_phone_number(message: types.Message, state: FSMContext):
        user_phone = message.contact.phone_number
        # Сохранение номера телефона в глобальной переменной или базе данных

        await message.answer(f"Спасибо за предоставленный номер телефона: {user_phone}")

        await state.finish()
# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer('Пожалуйста, выберите параметры с помощью кнопок. \nЕсли кнопок не видно - нажмите на квадратную кнопку с 4 точками')     #message.text


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery ,InlineKeyboardButton,  InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import emoji

from datetime import datetime

import app.keyboards as kb
import result_date_time as result    # result_date_time(selected_procedure, selected_place)
import set_schedule as ss

router = Router()

class User(StatesGroup):
    user_name = State()
class ProcedureSelection(StatesGroup):
    procedure = State()
class PlaceSelection(StatesGroup):
    place = State()
class DateTimeSelection(StatesGroup):
    date_time = State()
class PhoneNumberSelection(StatesGroup):
    phone = State()


procedures = ['Межресничка', 'Волоски', 'Гиперреализм', 'Пудровое']
places = ['Звездная', 'Пушкин']
dt = []

@router.message(CommandStart())    #(CommandStart(), User.user_name)
async def start(message: Message, bot, state: FSMContext):     #(bot, message: Message,  state: FSMContext)
    #await state.clear()
    print("Бот включен.")
    #await state.set_state(User.user_name)
    user = message.from_user
    user_name = user.first_name

    await state.set_state(ProcedureSelection.procedure)

    await message.answer(f"Привет, {user_name}!\nЯ помогу Вам записаться на прием к мастеру Веронике.")
    #await state.update_data(user_name=user_name)

    keyboard_procedures = kb.create_keyboard_procedures(procedures)
    await bot.send_message(message.chat.id, f"Пожалуйста, выберите процедуру с помощью кнопок {emoji.emojize(':memo:')} 👇", reply_markup=keyboard_procedures)


@router.message(ProcedureSelection.procedure)
async def process_procedure_choice(message: Message, state: FSMContext):

    if message.text not in procedures:
        await message.answer(f"Пожалуйста, выберите процедуру из списка кнопок 👇")
    else:
        selected_procedure = message.text
    await state.update_data(procedure=selected_procedure)
    await state.set_state(PlaceSelection.place)

    keyboard_places = kb.create_keyboard_places(places)
    await message.answer(f"Выбрана процедура: {selected_procedure}. Выберите место {emoji.emojize(':compass:')} 👇", reply_markup=keyboard_places)


@router.message(PlaceSelection.place)
async def process_place_choice(message: Message, bot, state: FSMContext):

    if message.text not in places:
        await message.answer(f"Пожалуйста, выберите место из списка кнопок 👇")
    else:
        selected_place = message.text
    await state.update_data(place=selected_place)
    await state.set_state(DateTimeSelection.date_time)

    await message.answer(f"Выбрано место: {selected_place}. \nСейчас сверю график и вернусь к Вам (в течение 15-30 секунд), выберем дату и время процедуры {emoji.emojize(':man_running_facing_right:')}", reply_markup=kb.ReplyKeyboardRemove())

    # Отправка сообщения с текстом и эмодзи - песочные часы
    await bot.send_message(message.chat.id, "\U000023F3")

    data = await state.get_data()
    df_result = result.result_date_time(data["procedure"], data["place"])  # создаем df_result - в файле result_date_time.py

    # Заполняем dt из df_result
    dates = df_result.index
    for date in dates:
        times = [time for time in df_result.loc[date] if time != '']
        if times:
            for time in times:
                dt.append(f"{date} {time}")

    keyboard_dates_and_times = kb.create_keyboard_dates_and_times(dt)
    await message.answer(f"Спасибо за ожидание.\nВыберите дату и время {emoji.emojize(':calendar:')} 👇", reply_markup=keyboard_dates_and_times)


@router.message(DateTimeSelection.date_time)
async def process_date_time_choice(message: Message, state: FSMContext):

    dt_formatted = []      # форматируем даты в dt чтобы сравнивать их с текстом на кнопках для контроля ввода пользователем
    for date_time in dt:
        date, time = date_time.split()
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        formatted_date_time = f"{formatted_date} {time}"
        dt_formatted.append(formatted_date_time)

    if message.text not in dt_formatted:
        await message.answer(f"Пожалуйста, выберите дату и время из списка кнопок 👇")
    else:
        selected_date_time = message.text
    await state.update_data(date_time=selected_date_time)
    await state.set_state(PhoneNumberSelection.phone)

    keyboard_phone = kb.create_keyboard_get_phone()
    await message.answer(f"Выбраны дата и время: {selected_date_time}.\nДля того, чтобы можно было подтвердить запись, пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже ☎️ 👇", reply_markup=keyboard_phone)

@router.message(PhoneNumberSelection.phone, F.contact)
async def process_phone_number(message: Message, bot, state: FSMContext):

    await state.update_data(phone=message.contact.phone_number)

    await message.answer(f"Спасибо! {emoji.emojize(':dart:')}\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\nХорошего дня! 👍☀️❤️", reply_markup=kb.ReplyKeyboardRemove())

    data2 = await state.get_data()
    procedure = data2["procedure"]
    place = data2["place"]
    date_time = data2["date_time"]
    phone = data2["phone"]
    #user_name = data2["user_name"]

    print(procedure)
    print(place)
    print(date_time)
    print(phone)
    user = message.from_user.first_name
    print(user)

    ss.set_schedule(date_time, procedure, place, phone, user)

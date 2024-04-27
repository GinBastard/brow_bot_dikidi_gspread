from aiogram import F, Router
from aiogram.types import Message, CallbackQuery ,InlineKeyboardButton,  InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import result_date_time as result    # result_date_time(selected_procedure, selected_place)

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
async def start(message: Message, bot):     #(bot, message: Message,  state: FSMContext)
    #await state.clear()
    print("Бот включен.")
    #await state.set_state(User.user_name)
    user = message.from_user
    user_name = user.first_name


    await message.answer(f"Привет, {user_name}!\nЯ помогу Вам записаться на прием к мастеру Веронике.")
    #await state.update_data(user_name=user_name)


    keyboard_procedures = kb.create_keyboard_procedures(procedures)
    await bot.send_message(message.chat.id, "Пожалуйста, выберите процедуру", reply_markup=keyboard_procedures)


@router.message(ProcedureSelection.procedure)
async def process_procedure_choice(message: Message, state: FSMContext):
    await state.set_state(ProcedureSelection.procedure)

    if message.text not in procedures:
        await message.answer("Пожалуйста, выберите процедуру из списка кнопок.")
    else:
        selected_procedure = message.text

    keyboard_places = kb.create_keyboard_places(places)
    await message.answer(f"Выбрана процедура: {selected_procedure}. Выберите место", reply_markup=keyboard_places)
    await state.update_data(procedure=selected_procedure)



@router.message(PlaceSelection.place)
async def process_place_choice(bot, message: Message, state: FSMContext):
    await state.set_state(PlaceSelection.place)

    if message.text not in places:
        await message.answer("Пожалуйста, выберите место из списка кнопок.")
    else:
        selected_place = message.text

    await message.answer(f"Выбрано место: {selected_place}. \nСейчас сверю график и вернусь к Вам (в течение 15-30 секунд), выберем дату и время процедуры.", reply_markup=kb.ReplyKeyboardRemove())
    await state.update_data(place=selected_place)

    # Отправка сообщения с текстом и эмодзи - песочные часы
    await bot.send_message(message.chat.id, "\U000023F3")

    data = await state.get_data()
    df_result = result.result_date_time(data["selected_procedure"], data["selected_place"])  # создаем df_result - в файле result_date_time.py

    # Заполняем dt из df_result
    dates = df_result.index
    for date in dates:
        times = [time for time in df_result.loc[date] if time != '']
        if times:
            for time in times:
                dt.append(f"{date} {time}")

    keyboard_dates_and_times = kb.create_keyboard_dates_and_times(dt)
    await message.answer(f"Спасибо за ожидание.\nВыберите дату и время", reply_markup=keyboard_dates_and_times)


@router.message(DateTimeSelection.date_time)
async def process_date_time_choice(message: Message, state: FSMContext):
    await state.set_state(DateTimeSelection.date_time)

    if message.text not in dt:
        await message.answer("Пожалуйста, выберите дату и время из списка кнопок.")
    else:
        selected_date_time = message.text

    keyboard = kb.create_keyboard_get_phone()
    await message.answer(f"Выбраны дата и время: {selected_date_time}.\nДля того, чтобы можно было подтвердить запись, пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже.", reply_markup=keyboard)
    await state.update_data(date_time=selected_date_time)


@router.message(PhoneNumberSelection.phone, F.contact)
async def process_phone_number(bot, message: Message, state: FSMContext):
    await state.set_state(PhoneNumberSelection.phone)

    await state.update_data(phone=message.contact.phone_number)

    await message.answer(f"Спасибо!\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\nХорошего дня!", reply_markup=kb.ReplyKeyboardRemove())


    data2 = await state.get_data()
    procedure = data2["procedure"]
    place = data2["selected_place"]
    date_time = data2["selected_date_time"]
    phone = data2["phone"]
    #user_name = data2["user_name"]

    print(procedure)
    print(place)
    print(date_time)
    print(phone)
    #print(user_name)

    keyboard_restart = kb.create_keyboard_restart()
    await message.answer("Нажмите Перезагрузить, чтобы сбросить настройки.", reply_markup=keyboard_restart)
    if message.text == "Перезагрузить":
        await state.clear()
        await bot.send_message(message.chat.id, "/start", reply_markup=kb.ReplyKeyboardRemove())
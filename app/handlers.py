from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart    # CommandStart (/start), Command (любые другие команды)
from aiogram.fsm.state import State, StatesGroup      # состояния (для хранения переменных)
from aiogram.fsm.context import FSMContext            # контекст для состояний

import emoji

from datetime import datetime

import app.keyboards as kb
import result_date_time as result    # result_date_time(selected_procedure, selected_place)
import set_schedule as ss

router = Router()     # пробрасывает обработчика событий

# Вводим классы состояний для переменных, использующихся в коде и принимающих данные от пользователя
class User(StatesGroup):
    user_name = State()
    user_acc = State()
class ProcedureSelection(StatesGroup):
    procedure = State()
class PlaceSelection(StatesGroup):
    place = State()
class DateTimeSelection(StatesGroup):
    date_time = State()
class PhoneNumberSelection(StatesGroup):
    phone = State()
class AddNote(StatesGroup):
    add_note = State()
    note = State()

# Исходные данные бота
procedures = ['Межресничка', 'Волоски', 'Гиперреализм', 'Пудровое']
places = ['Звездная', 'Пушкин']
dt = []                          # пустой глобальный список для хранения даты и времени
add_note_answers = ["Ввести примечание", "Оформить запись"]
veron_chat_id = '1462946426'        # id чата мастера для отправки оповещений о заявках

@router.message(CommandStart())                                # ловит команду /start
async def start(message: Message, bot, state: FSMContext):     # оперирует сообщениями от юзера, сообщениями от бота, сменами состояний
    print("Бот начал общение.")
    global dt
    print(f"===== dt после запуска start = {dt}")
    dt = []   # очистка списка дат и времени
    print(f"===== dt после запуска start и очистки = {dt}")
    await state.set_state(User.user_name)                      # устанавливаем состояние для переменнной (пока пустая)
    await state.set_state(User.user_acc)  # устанавливаем состояние для переменнной (пока пустая)
    user = message.from_user
    user_name = user.first_name                                # из объекта сообщение от юзера вытаскиваем его имя
    user_acc = user.username

    await state.set_state(ProcedureSelection.procedure)        # устанавливаем состояние другой переменной

    await message.answer(f"Привет, {user_name}!\nЯ помогу Вам записаться на прием к мастеру Веронике.")
    #await state.update_data(user_name=user_name)               # записываем имя в словарь состояний (присваиваем перемененой полученное значение)

    keyboard_procedures = kb.create_keyboard_procedures(procedures)             # создаем клавиатуру (ф-ция из файла keyboards.py)
    await bot.send_message(message.chat.id, f"Пожалуйста, выберите процедуру с помощью кнопок 📝👇", reply_markup=keyboard_procedures)
            # отправили сообщение от бота и показали клавиатуру Reply (кнопки внизу) - при нажатии кнопки высылается в чат текст с кнопки

@router.message(ProcedureSelection.procedure)                  # ловит состояние для переменной из state
async def process_procedure_choice(message: Message, state: FSMContext):
    selected_procedure = ''
    if message.text not in procedures:                         # при нажатии кнопки получили сообщение от юзера, проверяем его, сравнивая со списком разрешенных значений
        await message.answer(f"Пожалуйста, выберите процедуру из списка кнопок 👇")
    else:
        selected_procedure = message.text                      # если значение ОК, то присваиваем переменной

    await state.update_data(user_name=message.from_user.first_name)    # записываем имя в словарь состояний (получили из сообщения от юзера)
    await state.update_data(user_acc=message.from_user.username)              # записываем user_acc  в словарь состояний (получили из сообщения от юзера)
    await state.update_data(procedure=selected_procedure)              # записываем выбранную процедуру в словарь состояний
    await state.set_state(PlaceSelection.place)                        # устанавливаем состояние для переменной

    keyboard_places = kb.create_keyboard_places(places)
    await message.answer(f"Выбрана процедура: {selected_procedure}. Выберите место 🧭👇", reply_markup=keyboard_places)


@router.message(PlaceSelection.place)
async def process_place_choice(message: Message, bot, state: FSMContext):
    selected_place = ''
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
    df_result = result.result_date_time(data["procedure"], data["place"])  # создаем датафрейм df_result - в файле result_date_time.py получаем final_df

    # Заполняем dt из df_result
    dates = df_result.index
    for date in dates:
        times = [time for time in df_result.loc[date] if time != '']    # формируем список
        if times:
            for time in times:
                dt.append(f"{date} {time}")
    #print(f"dt содержание из df_result: {dt}")
    keyboard_dates_and_times = kb.create_keyboard_dates_and_times(dt)
    await message.answer(f"Спасибо за ожидание.\nВыберите дату и время 📆👇", reply_markup=keyboard_dates_and_times)


@router.message(DateTimeSelection.date_time)
async def process_date_time_choice(message: Message, state: FSMContext):

    dt_formatted = []                      # форматируем даты в dt чтобы сравнивать их с текстом на кнопках для контроля ввода пользователем
    for date_time in dt:
        date, time = date_time.split()
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        formatted_date_time = f"{formatted_date} {time}"
        dt_formatted.append(formatted_date_time)

    selected_date_time = ''
    if message.text not in dt_formatted:
        await message.answer(f"Пожалуйста, выберите дату и время из списка кнопок 👇")
    else:
        selected_date_time = message.text
    await state.update_data(date_time=selected_date_time)
    await state.set_state(PhoneNumberSelection.phone)

    keyboard_phone = kb.create_keyboard_get_phone()             # вызываем клавиатуру с кнопкой, которая запрашивает Контакт телеграм
    await message.answer(f"Выбраны дата и время: {selected_date_time}.\nДля того, чтобы можно было подтвердить запись, пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже ☎️ 👇", reply_markup=keyboard_phone)

@router.message(PhoneNumberSelection.phone)
async def process_phone_number(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer("Пожалуйста, нажмите кнопку 'Отправить номер' 👇")
    else:
        phone_number = message.contact.phone_number              # получаем номер телефона из Контакта
        await state.update_data(phone=phone_number)
        await state.set_state(AddNote.add_note)

        # Предложение пользователю выбрать добавление примечания или оформление записи
        keyboard_add_note = kb.create_keyboard_add_note(add_note_answers)
        await message.answer("Номер телефона для подтверждения записи получен.\n Хотите ли Вы добавить примечание к записи?", reply_markup=keyboard_add_note)

@router.message(AddNote.add_note)                               # наличие примечания: 1 - да, 2 - нет
async def button_note_click(message: Message, bot, state: FSMContext):
    if message.text not in add_note_answers:
        await message.answer("Пожалуйста, выберите один из вариантов на кнопках 👇")
    else:
        if message.text == 'Ввести примечание':
            await message.answer("Пожалуйста, введите ваше примечание (до 60 символов):")
            await state.update_data(add_note=1)
            await state.set_state(AddNote.note)
        elif message.text == "Оформить запись":
            await state.update_data(add_note=2)

            data2 = await state.get_data()       # получение данных из состояния (записанные ранее значения переменных по ключам (переменным)
            procedure = data2["procedure"]
            place = data2["place"]
            date_time = data2["date_time"]
            phone = data2["phone"]
            user_acc = data2["user_acc"]
            user_name = data2["user_name"]
            note = "_"
            user_link = f"https://t.me/{user_acc}"


            send_to_db(date_time, procedure, place, phone, user_name, user_link, note)   # передаем данные в функцию записи заявки в Расписание
            await message.answer(f"Спасибо! 🎯\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\nХорошего дня! 👍☀️❤️",reply_markup=kb.ReplyKeyboardRemove())
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")    # форматируем текущую дату и время
                    # отправка ботом оповещения о новой записи мастеру в личный чат
            await bot.send_message(veron_chat_id,
                                   f"{formatted_now} - Записался клиент: {user_name}\nНомер телефона: {phone}\nЛинк(TG): {user_link}\n"
                                   f"Дата и время записи: {date_time}\nПроцедура: {procedure}\nМесто: {place}\n"
                                   f"Примечание: {note}")

@router.message(AddNote.note)
async def process_note(message: Message, bot, state: FSMContext):
    data0 = await state.get_data()
    add_note = data0["add_note"]
    note = message.text
    if len(note) > 60 and add_note == 1:
        await message.answer("Примечание слишком длинное. Пожалуйста, введите примечание длиной до 60 символов ⛔")
    elif len(note) <= 60 and add_note == 1:
        await state.update_data(note=note)

        data3 = await state.get_data()      # получение данных из состояния (записанные ранее значения переменных по ключам (переменным)
        procedure = data3["procedure"]
        place = data3["place"]
        date_time = data3["date_time"]
        phone = data3["phone"]
        user_acc = data3["user_acc"]
        user_name = data3["user_name"]
        if note is not None:
            note = data3["note"]
        else:
            note = "_"
        user_link = f"https://t.me/{user_acc}"

        send_to_db(date_time, procedure, place, phone, user_name, user_link, note)   # передаем данные в функцию записи заявки в Расписание
        await message.answer(f"Спасибо! 🎯\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\nХорошего дня! 👍☀️❤️", reply_markup=kb.ReplyKeyboardRemove())
        # отправка ботом оповещения о новой записи мастеру в личный чат
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        await bot.send_message(veron_chat_id, f"{formatted_now} - Записался клиент: {user_name}\nНомер телефона: {phone}\nЛинк(TG): {user_link}\n"
                                              f"Дата и время записи: {date_time}\nПроцедура: {procedure}\nМесто: {place}\n"
                                              f"Примечание: {note}")
    else:
        pass

# Ф-ция записи заявки в Расписание
def send_to_db(date_time, procedure, place, phone, user_name, user_link, note):

    print(procedure)
    print(place)
    print(date_time)
    print(phone)
    print(user_name)
    print(user_link)
    print(note)

    ss.set_schedule(date_time, procedure, place, phone, user_name, user_link, note)

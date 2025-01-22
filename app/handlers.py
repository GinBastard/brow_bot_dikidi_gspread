from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command    # CommandStart (/start), Command (любые другие команды)
from aiogram.fsm.state import State, StatesGroup      # состояния (для хранения переменных)
from aiogram.fsm.context import FSMContext            # контекст для состояний

import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов

import asyncio


from datetime import datetime, timedelta

import concurrent.futures
# concurrent.futures упрощает работу с параллельным выполнением кода, обеспечивая высокий уровень абстракции
# и удобный интерфейс для управления потоками и процессами. Он позволяет эффективно использовать ресурсы компьютера
# и ускорить выполнение задач, которые могут быть выполнены параллельно.

from aiogram import Bot
import app.keyboards as kb
import result_date_time as result    # result_date_time(selected_procedure, selected_place)
import set_schedule as ss
from app.globals import global_state

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
places_url = {
                'Звездная': 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505103&s=5918615&rl=0_0&source=widget',
                'Пушкин': 'https://dikidi.net/686867?p=2.pi-ssm-sd&o=10&m=2352562&s=10102456&rl=0_undefined'
              }
gsheet_schedule_url = 'https://docs.google.com/spreadsheets/d/1ICEBZr97FBnjnBRqb-rAxkIZn_o_tRjhjQJ_PhPoVdw/edit#gid=1468526436'

# Словарь для хранения времени последнего сообщения от бота для каждого пользователя
last_message_time_dict = {}
# Словарь для хранения информации о том, было ли уже показано сообщение пользователю
message_shown = {}


# Функция, которая будет запускаться после 5-минутной бездействия пользователя

async def clean_up_user_states(user_id, bot, state):
    # Проверяем, было ли уже показано сообщение
    if not message_shown.get(user_id):          # если значение message_shown.get(user_id) не равно True...
                                                # -> Очистка состояний пользователя и отправка сообщения
        # Очистка состояний пользователя
        global dt
        dt = []  # очистка списка дат и времени
        if state is not None:     # проверяем state на None (изначально глобальный state = None, потом наполняется в handlers.py)
            await state.clear()   # очистка состояния

        await bot.send_message(user_id, "🔺 Вы не отвечали более 5 минут. Ваши настройки очищены 🙌\n\n"
                                                "🔹 Если Вы хотите записаться заново,\n"
                                                "нажмите -> /start\n"
                                                "🔹 Если Вы хотите получить информацию по услугам,\n"
                                                "нажмите -> /info", reply_markup=kb.ReplyKeyboardRemove())
        message_shown[user_id] = True    # помечаем, что сообщение было показано конкретному пользователю


# Функция для проверки бездействия пользователей
async def check_inactive_users(bot, global_state):

    while True:                                                               # запускаем бесконечный цикл while true
        await asyncio.sleep(60)                                                # Проверяем каждую минуту

        current_time = datetime.now()                                         # получаем текущую дату и время
        for user_id, last_message_time in last_message_time_dict.items():     # проходимся по словарю с временем последнего сообщения
            if current_time - last_message_time > timedelta(seconds=300):      # если прошло больше 10 секунд
                await clean_up_user_states(user_id, bot, global_state)      # вызываем функцию очистки состояний


@router.message(CommandStart())                                # ловит команду /start
async def start(message: Message, bot, state: FSMContext):     # оперирует сообщениями от юзера, сообщениями от бота, сменами состояний
    global global_state
    global_state = state                                       # обнуляем глобальное состояние


    print("Бот начал общение.")
    global dt
    print(f"===== dt после запуска start = {dt}")
    dt = []                                                    # очистка списка дат и времени
    print(f"===== dt после запуска start и очистки = {dt}")

    await state.set_state(User.user_name)                      # устанавливаем состояние для переменнной (пока пустая)
    await state.set_state(User.user_acc)                       # устанавливаем состояние для переменнной (пока пустая)
    user = message.from_user
    user_name = user.first_name                                # из объекта сообщение от юзера вытаскиваем его имя

    # Обновляем время последнего сообщения для данного пользователя
    global message_shown
    message_shown[user.id] = False                             # обнуляем флаг показа сообщений для конкретного пользователя (ставим - НЕ ПОКАЗАНО)

    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()   # обновляем время последнего сообщения для конкретного пользователя

    await state.set_state(ProcedureSelection.procedure)        # устанавливаем состояние другой переменной
    await bot.send_message(message.chat.id, f"Привет, {user_name}!\nЯ помогу Вам записаться на прием к мастеру Веронике.")

    keyboard_procedures = kb.create_keyboard_procedures(procedures)             # создаем клавиатуру (ф-ция из файла keyboards.py)
    await bot.send_message(message.chat.id, f"Пожалуйста, выберите процедуру с помощью кнопок 📝👇", reply_markup=keyboard_procedures)
            # отправили сообщение от бота и показали клавиатуру Reply (кнопки внизу) - при нажатии кнопки высылается в чат текст с кнопки


@router.message(Command('info'))       # когда пользователь укажет команду /info - вызываем функцию показа инфо
async def info_(message: Message, bot, state: FSMContext):

    global global_state
    global_state = state     # Обновляем глобальное состояние

    global dt
    dt = []  # очистка списка дат и времени
    await state.clear()  # очистка состояния

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()

    await bot.send_message(message.chat.id, f"Мои услуги:\n"
                                            f"✨Полное восстановление бровей Техники «Гиперреализм» / «волоски + тень» / «микрoблeйлинг» - 10000₽\n"
                                            f"✨ Перманeнтный мaкияж Tеxникa «пудровое нaпылeние брoвeй» - 8000₽\n"
                                            f"✨ межресничка (классика) - 6000 ₽\n\n"
                                            
                                            f"✨ коррекция через 1-2 месяца:\n"
                                            f"▪️ Техника волоски + тень / Техника пудровое напыление бровей – 4000/3000 ₽\n"
                                            f"▪️Межресничка (классика) - 2000 ₽.\n\n"
                                            
                                            f"Принимаю в г. Пушкин или по договоренности в коворкинге метро Московская/Звездная ❤️\n", reply_markup=kb.ReplyKeyboardRemove())

    await bot.send_message(message.chat.id, f"Если хотите уточнить информацию у Вероники, нажмите кнопку 'Перейти к чату'", reply_markup=kb.create_keyboard_chat_veron())
    await asyncio.sleep(5)  # Добавляем задержку в 5 секунд
    await bot.send_message(message.chat.id, f"Если хотите записаться на приём, нажмите на -> '/start' 😉😘")

    @router.message(lambda message: message.text not in ['/start', '/info'])
    async def handle_other_messages(message: Message):
        # Обработка всех сообщений, кроме "/start" и "/info"
        # Проверяем, было ли отправлено сообщение от пользователя
        await message.answer(f"Простите, мне не разрешено общаться в этом разделе или НЕ по теме.\n"
                             f"Пожалуйста, посмотрите мои сообщения выше и выберите, что Вас интересует 💁‍♂️")

        # Обновляем время последнего сообщения для данного пользователя
        global last_message_time_dict
        last_message_time_dict[message.chat.id] = datetime.now()

@router.message(ProcedureSelection.procedure)                  # ловит состояние для переменной из state
async def process_procedure_choice(message: Message, bot, state: FSMContext):

    global global_state
    global_state = state    # Обновляем глобальное состояние

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()
    global message_shown


    if message.text not in procedures and message_shown[message.chat.id] == False:                         # при нажатии кнопки получили сообщение от юзера, проверяем его, сравнивая со списком разрешенных значений
        await bot.send_message(message.chat.id, f"Пожалуйста, выберите процедуру из списка кнопок 👇")
    elif message_shown[message.chat.id] == True:
        await bot.send_message(message.chat.id, f"Вас не было больше 5 минут 💔 Пожалуйста, начните запись заново \n-> /start")
    else:
        selected_procedure = message.text                      # если значение ОК, то присваиваем переменной

        await state.update_data(user_name=message.from_user.first_name)    # записываем имя в словарь состояний (получили из сообщения от юзера)
        await state.update_data(user_acc=message.from_user.username)              # записываем user_acc  в словарь состояний (получили из сообщения от юзера)
        await state.update_data(procedure=selected_procedure)              # записываем выбранную процедуру в словарь состояний
        await state.set_state(PlaceSelection.place)                        # устанавливаем состояние для переменной

        keyboard_places = kb.create_keyboard_places(places)
        await bot.send_message(message.chat.id, f"Выбрана процедура: {selected_procedure}. Выберите место 🧭👇", reply_markup=keyboard_places)

        # Обновляем время последнего сообщения для данного пользователя
        last_message_time_dict[message.chat.id] = datetime.now()


@router.message(PlaceSelection.place)
async def process_place_choice(message: Message, bot, state: FSMContext):

    global global_state
    global_state = state   # Обновляем глобальное состояние

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()
    global message_shown

    if message.text not in places and message_shown[message.chat.id] == False:
        await bot.send_message(message.chat.id, f"Пожалуйста, выберите место из списка кнопок 👇")
    elif message_shown[message.chat.id] == True:
        await bot.send_message(message.chat.id,
                               f"Вас не было больше 5 минут 💔 Пожалуйста, начните запись заново \n-> /start")
    else:
        selected_place = message.text
        await state.update_data(place=selected_place)
        await state.set_state(DateTimeSelection.date_time)

        await bot.send_message(message.chat.id, f"Выбрано место: {selected_place}. \nСейчас сверю график и вернусь к Вам (в течение 15-30 секунд), выберем дату и время процедуры 🏃‍♂️‍➡️", reply_markup=kb.ReplyKeyboardRemove())

        # Отправка сообщения с текстом и эмодзи - песочные часы
        await bot.send_message(message.chat.id, "\U000023F3")

        data = await state.get_data()

        # Запускаем асинхронную функцию с таймаутом (запуск процесса асинхронно и проверка его завершения)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(result.result_date_time, data["procedure"], data["place"])  # передаём нужную функцию и параметры (отдельно)
            wait_time = 60            # устанавливаем допустимое время выполнения функции
            try:
                df_final = future.result(timeout=wait_time)    # если время ожидания выполнения ф-ции не истечено, то получаем результат
            except concurrent.futures.TimeoutError:             # если таймаут превышен - прерываем процесс и иформируем пользователя
                future.cancel()                                 # прерываем процесс
                await bot.send_message(message.chat.id,
                    "⏰ Время ожидания данных превышено. Возможно, технические неполадки 🤷‍♂️\nПожалуйста, попробуйте ещё раз попозже 🙏\n"
                    "Чтобы перезагрузить бота - выберите 'Начать сначала' из меню СЛЕВА в строке ввода сообщений 👈")
                # global dt
                # dt = []  # очистка списка дат и времени
                await state.clear()  # очистка состояния
                return                                         # завершаем выполнение програмы (можно перезагрузить бота из TG)
            except Exception as e:                             # если ф-ция вернула ошибку (сбой), то информируем пользователя также
                print(e)
                await bot.send_message(message.chat.id,
                    "❌ В процессе запроса данных произошла ошибка. Возможно, технические неполадки 🤷‍♂️\nПожалуйста, попробуйте ещё раз попозже 🙏\n"
                    "Чтобы перезагрузить бота - выберите 'Начать сначала' из меню СЛЕВА в строке ввода сообщений 👈")
                # global dt
                # dt = []  # очистка списка дат и времени
                await state.clear()  # очистка состояния
                return                                         # завершаем выполнение програмы (можно перезагрузить бота из TG)


                # Если ошибок при выполнении result.result_date_time не было, то выполняем код дальше:
            global dt  # объявляем, что берем глобальную переменную dt

            # Если получили пустой датафреейм df_final (всё время занято в расписании, то выводим сообщение:
            # Проверка, является ли датафрейм "пустым"

            # Проверка, является ли датафрейм "пустым"
            is_empty = df_final.replace("", pd.NA).dropna(axis=0, how='all').empty

            if is_empty:
                print('Финальный датафрейм пуст!')
                link = "https://t.me/G_Veronik"
                escaped_link = link.replace("_", r"\_")  # экранируем символ подчеркивания

                await bot.send_message(message.chat.id, f"В настоящее время нет свободных записей на процедуры 🙁\n"
                                     f"Пожалуйста, выберите другое место и попробуйте снова -> /start\n"
                                     f"или свяжитесь с Вероникой.\n\n"
                                     f"График разработан на ближайшие 9 дней, можно договориться на более позднюю дату 😉\n"
                                     f"Свяжитесь с [Вероникой]({link}) - что-нибудь придумаем 👌 \n"
                                                        f"{escaped_link}", parse_mode="Markdown")   # опция parse_mode="Markdown" - подставляем в [текст](нужный url) Markdown-синтаксис
                global dt
                dt = []  # очистка списка дат и времени
                await state.clear()  # очистка состояния
            else:
                dates = df_final.index
                for date in dates:
                    times = [time for time in df_final.loc[date] if time != '']  # формируем список
                    if times:
                        for time in times:
                            dt.append(f"{date} {time}")

                keyboard_dates_and_times = kb.create_keyboard_dates_and_times(dt)
                await bot.send_message(message.chat.id, f"Спасибо за ожидание.\nВыберите дату и время 📆👇",
                                             reply_markup=keyboard_dates_and_times)

@router.message(DateTimeSelection.date_time)
async def process_date_time_choice(message: Message, bot, state: FSMContext):

    global global_state
    global_state = state     # Обновляем глобальное состояние

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()
    global message_shown

    dt_formatted = []                      # форматируем даты в dt чтобы сравнивать их с текстом на кнопках для контроля ввода пользователем
    for date_time in dt:
        date, time = date_time.split()
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        formatted_date_time = f"{formatted_date} {time}"
        dt_formatted.append(formatted_date_time)

    if message.text not in dt_formatted and message_shown[message.chat.id] == False:
        await bot.send_message(message.chat.id, f"Пожалуйста, выберите дату и время из списка кнопок 👇")
    elif message_shown[message.chat.id] == True:
        await bot.send_message(message.chat.id,
                               f"Вас не было больше 5 минут 💔 Пожалуйста, начните запись заново \n-> /start")
    else:
        selected_date_time = message.text
        await state.update_data(date_time=selected_date_time)
        await state.set_state(PhoneNumberSelection.phone)

        keyboard_phone = kb.create_keyboard_get_phone()             # вызываем клавиатуру с кнопкой, которая запрашивает Контакт телеграм
        await bot.send_message(message.chat.id, f"Выбраны дата и время: {selected_date_time}")
        await bot.send_message(message.chat.id, "Для того, чтобы можно было подтвердить запись, пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже ☎️ 👇", reply_markup=keyboard_phone)

@router.message(PhoneNumberSelection.phone)
async def process_phone_number(message: Message, bot,state: FSMContext):

    global global_state
    global_state = state   # Обновляем глобальное состояние

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()
    global message_shown


    if not message.contact and message_shown[message.chat.id] == False:
        await bot.send_message(message.chat.id, "Пожалуйста, нажмите кнопку 'Отправить номер' 👇")
    elif message_shown[message.chat.id] == True:
        await bot.send_message(message.chat.id,
                               f"Вас не было больше 5 минут 💔 Пожалуйста, начните запись заново \n-> /start")
    else:
        phone_number = message.contact.phone_number              # получаем номер телефона из Контакта
        await state.update_data(phone=phone_number)
        await state.set_state(AddNote.add_note)

        # Предложение пользователю выбрать добавление примечания или оформление записи
        keyboard_add_note = kb.create_keyboard_add_note(add_note_answers)
        await bot.send_message(message.chat.id, "Номер телефона для подтверждения записи получен.\n Хотите ли Вы добавить примечание к записи?", reply_markup=keyboard_add_note)

@router.message(AddNote.add_note)                               # наличие примечания: 1 - да, 2 - нет
async def button_note_click(message: Message, bot, state: FSMContext):

    global global_state
    global_state = state    # Обновляем глобальное состояние

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()
    global message_shown

    # проверяем ЧТО ввел юзер из списка и проверяем что не вылезало сообщений о превышении таймаута
    if message.text not in add_note_answers and message_shown[message.chat.id] == False:
        await bot.send_message(message.chat.id, "Пожалуйста, выберите один из вариантов на кнопках 👇")
    elif message_shown[message.chat.id] == True:
        await bot.send_message(message.chat.id,
                               f"Вас не было больше 5 минут 💔 Пожалуйста, начните запись заново \n-> /start")
    else:
        if message.text == 'Ввести примечание':
            await bot.send_message(message.chat.id, "Пожалуйста, введите ваше примечание (до 60 символов):")
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
            escaped_user_link = user_link.replace("_", r"\_")  # экранируем символ подчеркивания

            for key, value in places_url.items():     # перебираем словарь место-url
                if key == place:                      # выбираем url по ключу места
                    url_cow = value


            send_to_db(date_time, procedure, place, phone, user_name, user_link, note)   # передаем данные в функцию записи заявки в Расписание
            await bot.send_message(message.chat.id, f"Спасибо! 🎯\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\nХорошего дня! 👍☀️❤️",reply_markup=kb.ReplyKeyboardRemove())

            message_shown[message.chat.id] = True  # отмечаем - как будто сообщение о превышенном таймауте было показано, чтобы не повторялось

            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")    # форматируем текущую дату и время

            # Отправка ботом оповещения о новой записи мастеру в личный чат
            await bot.send_message(veron_chat_id,
                                   f"{formatted_now} - Записался клиент: {user_name}\nНомер телефона: {phone}\nЛинк(TG): {escaped_user_link}\n"
                                   f"Дата и время записи: {date_time}\nПроцедура: {procedure}\nМесто: [{place}]({url_cow})\n"
                                   f"Примечание: {note}\nТекущее [расписание]({gsheet_schedule_url})", parse_mode="Markdown")         # опция parse_mode="Markdown" - подставляем в [текст](нужный url) Markdown-синтаксис


            await asyncio.sleep(5)  # Добавляем задержку в 5 секунд
            await bot.send_message(message.chat.id, f"Если захотите записаться ещё раз, нажмите -> /start  😘")

            global dt
            dt = []  # очистка списка дат и времени
            await state.clear()  # очистка состояния

@router.message(AddNote.note)
async def process_note(message: Message, bot, state: FSMContext):

    global global_state
    global_state = state    # Обновляем глобальное состояние

    data0 = await state.get_data()
    add_note = data0["add_note"]
    note = message.text

    # Обновляем время последнего сообщения для данного пользователя
    global last_message_time_dict
    last_message_time_dict[message.chat.id] = datetime.now()
    global message_shown

    if len(note) > 60 and add_note == 1 and message_shown[message.chat.id] == False:
        await bot.send_message(message.chat.id, "Примечание слишком длинное. Пожалуйста, введите примечание длиной до 60 символов ⛔")
    elif message_shown[message.chat.id] == True:
        await bot.send_message(message.chat.id,
                               f"Вас не было больше 5 минут 💔 Пожалуйста, начните запись заново \n-> /start")
    elif len(note) <= 60 and add_note == 1 and message_shown[message.chat.id] == False:
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
        escaped_user_link = user_link.replace("_", r"\_")  # экранируем символ подчеркивания

        for key, value in places_url.items():         # перебираем словарь место-url
            if key == place:                          # выбираем url по ключу места
                url_cow = value

        # Передаем данные в функцию записи заявки в Расписание (Schedule)
        send_to_db(date_time, procedure, place, phone, user_name, user_link, note)
        await bot.send_message(message.chat.id, f"Спасибо! 🎯\nВероника свяжется с Вами для подтверждения записи в ближайшее время.\n"
                                                f"Хорошего дня! 👍☀️❤️", reply_markup=kb.ReplyKeyboardRemove())

        message_shown[message.chat.id] = True   # отмечаем - как будто сообщение о превышенном таймауте было показано, чтобы не повторялось

        # отправка ботом оповещения о новой записи мастеру в личный чат
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        await bot.send_message(veron_chat_id, f"{formatted_now} - Записался клиент: {user_name}\nНомер телефона: {phone}\nЛинк(TG): {escaped_user_link}\n"
                                              f"Дата и время записи: {date_time}\nПроцедура: {procedure}\nМесто: [{place}]({url_cow})\n"
                                              f"Примечание: {note}\nТекущее [расписание]({gsheet_schedule_url})", parse_mode="Markdown")     # опция parse_mode="Markdown" - подставляем в [текст](нужный url) Markdown-синтаксис

        await asyncio.sleep(5)  # Добавляем задержку в 5 секунд
        await bot.send_message(message.chat.id, f"Если захотите записаться ещё раз, нажмите -> /start  😘")

        global dt
        dt = []  # очистка списка дат и времени
        await state.clear()  # очистка состояния

@router.message(lambda message: message.text not in ['/start', '/info'])
async def handle_other_messages(message: Message):
        # Обработка всех сообщений, кроме "/start" и "/info"
        # Проверяем, было ли отправлено сообщение от пользователя
        await message.answer(f"Простите, мне не разрешено общаться в этом разделе или НЕ по теме.\n"
                             f"Пожалуйста, посмотрите мои сообщения выше и выберите, что Вас интересует 💁‍♂️")
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

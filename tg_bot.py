
# pip install aiohttp==3.9.0
# pip install -U aiogram
# pip install --force-reinstall -v "aiogram==2.23.1"
# pip install -v "aiogram==2.23.1"

# pip install --force-reinstall -v "aiogram==2.23.1"
# https://skillbox.ru/media/code/chatboty-v-telegram-na-python-chast-2-sozdayem-i-nastraivaem-menyu/?utm_source=media&utm_medium=link&utm_campaign=all_all_media_links_links_articles_all_all_skillbox


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
places = ['Звездная', 'Пушкин', 'Московская']


class ProcedureSelection(StatesGroup):
    procedure = State()
class PlaceSelection(StatesGroup):
    place = State()


def create_keyboard_procedures(procedures):
    buttons = [KeyboardButton(text) for text in procedures]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    return keyboard

def create_keyboard_places(places):
    buttons = [KeyboardButton(text) for text in places]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    return keyboard


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard_procedures = create_keyboard_procedures(procedures)
    await message.answer("Выберите процедуру", reply_markup=keyboard_procedures)
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
    await message.answer(f"Выбрано место: {selected_place}. \nСейчас сверю график и вернусь к вам (в теч. 10-15 сек.), выберем дату и время процедуры.", reply_markup=types.ReplyKeyboardRemove())

    await state.finish()



# далее:
# передать в функцию result_date_time:    selected_procedure и selected_procedure
# в result_date_time происходит:
# 1) Выбор ссылки на dikidi в зависимости от выбранной процедуры и места - получаем url
# 2) Запуск функции get_dikidi_dates(url) (из get_dikidi.py) - получаем df_dikidi
# 3) Запуск функции get_plan_dates() (из get_gs_plan.py) - получаем df_plan
# 4) Запуск функции get_schedule_dates() (из get_gs_schedule.py) - получаем df_schedule
# 5) Соединение df_dikidi, df_plan, df_schedule
# 6) Возвращаем СЮДА df_result с подготвленными допустимыми датами и временем
# 7) Из df_result вытаскиваем даты (в которых есть допустимое время)  - и показываем клиенту кнопки с этими датами
# 8) После выбора даты selected_date - вытаскиваем из df_result время для этой даты - и показываем клиенту кнопки с этими временами
# 9) После выбора времени selected_time - показываем клиенту сообщение с выбранными датой и временем и другими выбранными ранее параметрами,
# 10) ...а также отправляем мастеру сообщение о новой записи и размещаем в таблице Schedule отметки о записи.
#

df_result = result.result_date_time(selected_procedure, selected_place)  # создаем df_result - в файле result_date_time.py

def create_keyboard_dates_and_times(df_result):
    keyboard = types.InlineKeyboardMarkup()
    dates = df_result.index.unique()
    for date in dates:
        times = df_result.loc[date].dropna().unique()
        button = types.InlineKeyboardButton(
            f"{date} {times[0]}",
            callback_data=f"date_{date}_{times[0]}",
        )
        keyboard.add(button)
    return keyboard

# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer('Пожалуйста, выберите параметры с помощью кнопок. \nЕсли кнопок не видно - нажмите на квадратную кнопку с 4 точками')     #message.text


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
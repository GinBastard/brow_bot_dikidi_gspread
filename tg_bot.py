
# pip install aiohttp==3.9.0
# pip install -U aiogram
# pip install --force-reinstall -v "aiogram==2.23.1"
# pip install -v "aiogram==2.23.1"

# pip install --force-reinstall -v "aiogram==2.23.1"
# https://skillbox.ru/media/code/chatboty-v-telegram-na-python-chast-2-sozdayem-i-nastraivaem-menyu/?utm_source=media&utm_medium=link&utm_campaign=all_all_media_links_links_articles_all_all_skillbox


from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import get_dikidi as dikidi          # get_dikidi_dates(url)
import get_gs_plan as plan           # get_plan_dates()
import get_gs_schedule as schedule   # get_schedule_dates()


# tatoo_brow_bot
# t.me/tatoo_brow_bot
API_TOKEN = '7141747698:AAHu-H6Z7w3Jm8kIvjc_6XaGyLzN5bK2x54'




url_4h = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505101&s=5918559&rl=0_0&source=widget'  # Замените URL на адрес нужного веб-сайта

#dikidi.get_dikidi_dates(url_4h)       # запуск функции из файла get_dikidi.py - Замените URL на адрес нужного веб-сайта


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



procedures = ['Межресничка', 'Волоски', 'Гиперреализм', 'Пудровое']
places = ['Звездная', 'Пушкин', 'Московская']

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
    # chat_id = message.chat.id
    # await bot.send_message(chat_id, "Выберите процедуру", reply_markup=keyboard)
    keyboard_procedures = create_keyboard_procedures(procedures)
    await message.answer("Выберите процедуру", reply_markup=keyboard_procedures)


@dp.message_handler()
async def process_choice(message: types.Message):
    global selected_procedure
    global selected_place

    if message.text in procedures:
        selected_procedure = message.text     # выбранная процедура!!
        keyboard_places = create_keyboard_places(places)
        await message.answer(f"Выбрана процедура: {selected_procedure}. Выберите место", reply_markup=keyboard_places)
    elif message.text in places:
        selected_place = message.text
        await message.answer(f"Выбрано место: {selected_place}. Сейчас сверю график и вернусь к вам (в теч. 10-15 сек.), выберем дату и время процедуры.")


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



# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer('Пожалуйста, выберите параметры с помощью кнопок. \nЕсли кнопок не видно - нажмите на квадратную кнопку с 4 точками')     #message.text


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
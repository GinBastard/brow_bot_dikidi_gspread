import asyncio

from aiogram import Bot, Dispatcher     # Dispatcher - обработчик событий

from app.handlers import router         # импортируем обработчика событий из другого файла, где он используется handlers.py
from app.handlers import check_inactive_users
from app.globals import global_state


# tatoo_brow_bot
# t.me/tatoo_brow_bot
TG_API_TOKEN = '7141747698:AAHu-H6Z7w3Jm8kIvjc_6XaGyLzN5bK2x54'

# bot = Bot(token=TG_API_TOKEN)
dp = Dispatcher()


async def main():
    #session = AiohttpSession(proxy="http://proxy.mtproto.co:443")
    #bot = Bot(token=TG_API_TOKEN, session=session)  # создаем бота c прокси

    bot = Bot(token=TG_API_TOKEN)     # создаем бота без прокси

    dp.include_router(router)        # подключаем обработчика событий из handlers.py к Dispatcher

    # Запускаем проверку бездействия пользователей в отдельном потоке в цикле
    asyncio.ensure_future(check_inactive_users(bot, global_state))
    # Запускаем бота
    await dp.start_polling(bot)      # запускаем бота



if __name__ == '__main__':
    print('Бот Brow-bot запущен.\nЕсли вы используете отдельное приложение для бота, чтобы завершить его работу - просто закройте окно.\n')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен.')

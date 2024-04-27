import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов

import asyncio

from aiogram import Bot, Dispatcher
from app.handlers import router



# tatoo_brow_bot
# t.me/tatoo_brow_bot
API_TOKEN = '7141747698:AAHu-H6Z7w3Jm8kIvjc_6XaGyLzN5bK2x54'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен.')

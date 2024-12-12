from aiogram import Bot, Dispatcher, types
import requests
import asyncio
from aiogram.filters import Command
from aiogram.types.web_app_info import WebAppInfo

BOT_TOKEN = '8070461641:AAHfwtiyvn7gmToWrf3A3WMMp5Ir7ZZ73EE'
FLASK_URL = 'https://app.cazav.ru/'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    kb = [
        [types.KeyboardButton(text='Hola', web_app=WebAppInfo(url=FLASK_URL))]
    ]
    kb = types.ReplyKeyboardMarkup(
        keyboard=kb
    )
    await message.answer('Привет! Открой приложение!', reply_markup=kb)

# asyncio.run(dp.start_polling(bot, skip_updates=False))

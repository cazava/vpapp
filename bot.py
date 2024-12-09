from aiogram import Bot, Dispatcher, types
import requests
import asyncio

API_TOKEN = '8070461641:AAHfwtiyvn7gmToWrf3A3WMMp5Ir7ZZ73EE'
FLASK_URL = 'http://127.0.0.1:5000/check'  # Замените на URL вашего Flask-приложения, если необходимо

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    # Отправляем POST-запрос к Flask-приложению
    response = requests.post(FLASK_URL, json={'user_id': user_id})
    response_data = response.json()

    # Отправляем результат пользователю
    await message.answer(response_data['response'])


if __name__ == '__main__':
    from aiogram import executor

    asyncio.run(dp.start_polling())

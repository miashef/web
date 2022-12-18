from aiogram import Bot, Dispatcher, executor, types
import asyncio
import sqlite3
import requests

def convert_degree(fah):
    return 5.0*(fah - 32) / 9


TOKEN = "5940376300:AAExIiEkKAiKq4MEsPY4TzUcXM22zYfTC6w"
MSG = "Ghbdnt lhe;bot? {}"


bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name
    await message.answer(f"Привет, {user_full_name}! Этот бот поможет узнавать погоду каждый день по отслеживаемым городам. Начнем?")

@dp.message_handler(commands=["cities"])
async def get_cities(message: types.Message):
    con = sqlite3.connect("db.sqlite3")
    cursor = con.cursor()
    cursor.execute("SELECT name FROM weather_city")
    rows = cursor.fetchall()
    message_cities = f"<b>Ваши выбранные города:</b>\n🏙️ " + "\n🏙️ ".join([i[0] for i in rows])
    await message.answer(message_cities, parse_mode='HTML')

@dp.message_handler(commands=["weather"])
async def get_weather(message: types.Message):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1&lang=ru'
    con = sqlite3.connect("db.sqlite3")
    cursor = con.cursor()
    cursor.execute("SELECT name FROM weather_city")
    cities = [i[0] for i in cursor.fetchall()]
    for city in cities:
        r = requests.get(url.format(city)).json()

        city_weather = {
            'city' : city,
            'temperature' : str(round(convert_degree(r['main']['temp']))) + "° С",
            'description' : r['weather'][0]['description'].capitalize(),
        }
        message_weather = f"<b>{city_weather['city']}</b>\n☁ {city_weather['description']}, {city_weather['temperature']}"
        await message.answer(message_weather, parse_mode='HTML')

@dp.message_handler(commands=["remind"])
async def remind(message: types.Message):
    message_remind = "Теперь сообщения о погоде приходят каждый 12 часов"
    await message.answer(message_remind, parse_mode='HTML')
    
    for i in range(7):
        await asyncio.sleep(60*60*12)
        await get_weather(message)

if __name__ == "__main__":
    executor.start_polling(dp)
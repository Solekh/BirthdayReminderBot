from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from db.wheather import Weather
from bot.buttons import get_cities
from deep_translator import GoogleTranslator  # Import from deep_translator

weather_router = Router()


@weather_router.message(Command("weather"))
async def weather(message: Message):
    cities = await Weather().objects
    if cities:
        await message.answer("Интихоб кунед:", reply_markup=get_cities(cities))
    else:
        await message.answer("Шаҳрҳо ёфт нашуд!")


@weather_router.callback_query(F.data.startswith("city_"))
async def city_callback(call: CallbackQuery):
    city_name = call.data.split("_")[1]
    city_link = await Weather().city_link(city_name)
    if city_link:
        # Get the weather information in Uzbek
        today_weather = await Weather().city_forecast(city_link)
        weekly_weather = await Weather().weekly_forecast(city_link)
        full_weather_report = f"{today_weather}\n\n{weekly_weather}"

        # Translate the weather report to Tajik using deep-translator
        translator = GoogleTranslator(source="uz", target="tg")
        translated_report = translator.translate(full_weather_report)

        # Send the translated weather report
        await call.message.edit_text(translated_report)
    else:
        await call.message.edit_text(f"Шаҳри {city_name} ёфт нашуд.")

import logging
import config
import parser
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import pytz

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Сохранение идентификаторов чатов
chat_ids = set()

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Когда гонка?"))
keyboard.add(KeyboardButton("Все гонки"))


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    chat_ids.add(message.chat.id)
    await message.reply(
        "Бот для уведомлений о начале гонок Формулы 1. Вам будет отправлено уведомление за 5 минут до начала каждой гонки.",
        reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Когда гонка?')
async def when_is_race(message: types.Message):
    next_race = parser.get_next_race()
    if next_race:
        race_time = next_race['start'].astimezone(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M')
        await message.reply(
            f"Следующая гонка Формулы 1 '{next_race['summary']}' состоится {race_time} по московскому времени.")
    else:
        await message.reply("Информация о следующей гонке недоступна.")


@dp.message_handler(lambda message: message.text == 'Все гонки')
async def all_races(message: types.Message):
    calendar = parser.load_calendar()
    races = []
    for event in calendar.events:
        race_time = event.begin.astimezone(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M')
        races.append(f"{event.summary} - {race_time}")
    races_text = '\n'.join(races)
    await message.reply(f"Список всех гонок:\n{races_text}")


async def send_notifications():
    while True:
        next_race = parser.get_next_race()
        if next_race and parser.is_race_in_5_minutes(next_race):
            for chat_id in chat_ids:
                race_time = next_race['start'].astimezone(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M')
                await bot.send_message(chat_id=chat_id,
                                       text=f"Гонка Формулы 1 '{next_race['summary']}' начнется через 5 минут ({race_time} по московскому времени)!")
        await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_notifications())

    executor.start_polling(dp, skip_updates=True)

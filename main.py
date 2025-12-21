import os
import asyncio
from flask import Flask
from threading import Thread

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram import F

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@tajalnijomnjf"
CAPTION = "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة ✨"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    await bot.send_photo(
        chat_id=CHANNEL,
        photo=message.photo[-1].file_id,
        caption=CAPTION
    )
    await message.answer("✔️ تم نشر الصورة في القناة")

@dp.message(F.text == "نشر الآن")
async def post_now(message: types.Message):
    await bot.send_message(CHANNEL, CAPTION)
    await message.answer("✔️ تم نشر الرسالة الآن في القناة")

async def start_bot():
    await dp.start_polling(bot)

def run():
    app.run(host="0.0.0.0", port=10000)

def start_web():
    Thread(target=run).start()

if __name__ == "__main__":
    start_web()
    asyncio.run(start_bot())

from aiogram import Bot, Dispatcher, types
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@tajalnijomnjf"
CAPTION = "وصول بضاعه جديدة داخل الشركة متوفرة الان بكميات محدودة"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message()
async def receive(msg: types.Message):
    if msg.photo:
        await bot.send_photo(CHANNEL, msg.photo[-1].file_id, CAPTION)
        await msg.answer("تم النشر تلقائياً 🟢")

    elif msg.text == "نشر الآن":
        await bot.send_message(CHANNEL, CAPTION)
        await msg.answer("تم النشر بنجاح ✔")

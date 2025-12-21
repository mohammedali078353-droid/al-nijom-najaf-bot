import asyncio
from aiogram import Bot, Dispatcher, types
from flask import Flask
import threading
import logging
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@tajalnijomnjf"
CAPTION = "وصول بضاعه جديدة داخل الشركة متوفرة الان بكميات محدودة"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

jobs = []

@dp.message()
async def receive(msg: types.Message):
    if msg.photo:
        if msg.caption and msg.caption.isdigit():
            post_time = int(msg.caption)
            jobs.append({"photo": msg.photo[-1].file_id, "time": post_time})
            await msg.answer(f"تم جدولة الصورة للنشر خلال {post_time} دقيقة ⏳")
            await asyncio.sleep(post_time * 60)
            await bot.send_photo(CHANNEL, msg.photo[-1].file_id, CAPTION)
            await msg.answer("تم النشر بنجاح في القناة 📢")
        else:
            await msg.answer("⚠ يرجى كتابة الوقت فقط داخل الكابشن ⏱")

    elif msg.text == "نشر الآن":
        await bot.send_message(CHANNEL, CAPTION)
        await msg.answer("تم النشر الآن بنجاح ✔")

async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, CallbackQueryHandler, filters
import datetime

# ===== استقبال صور + فيديو =====
async def receive_media(update, context):
    message = update.message

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    else:
        return

    context.user_data["file_id"] = file_id
    context.user_data["media_type"] = media_type
    context.user_data["caption"] = message.caption or ""

    keyboard = [
        [
            InlineKeyboardButton("▶️ نشر الآن", callback_data="publish_now"),
            InlineKeyboardButton("🔁 إعادة نشر (5 أيام)", callback_data="repost_5")
        ],
        [
            InlineKeyboardButton("📦 البضاعة نفدت", callback_data="sold_out"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
        ]
    ]

    await message.reply_text(
        "📌 اختر الإجراء المطلوب:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== أزرار التحكم =====
async def buttons_handler(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "publish_now":
        await query.edit_message_text("✅ سيتم النشر الآن (التنفيذ القادم).")

    elif data == "repost_5":
        await query.edit_message_text("🔁 تم تفعيل إعادة النشر بعد 5 أيام.")

    elif data == "sold_out":
        await query.edit_message_text("📦 تم إيقاف المنشور بسبب نفاد الكمية.")

    elif data == "cancel":
        await query.edit_message_text("❌ تم إلغاء العملية.")

# ===== إضافة الهاندلرز =====
application.add_handler(
    MessageHandler(filters.PHOTO | filters.VIDEO, receive_media)
)
application.add_handler(
    CallbackQueryHandler(buttons_handler)
)

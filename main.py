import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ================== إعدادات عامة ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # مثال: @tajalnijomnjf
FIXED_CAPTION = os.getenv(
    "CAPTION_FIXED",
    "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ================== استقبال صورة / فيديو ==================
async def receive_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    else:
        await message.reply_text("❌ الرجاء إرسال صورة أو فيديو فقط.")
        return

    caption = message.caption or ""
    final_caption = f"{caption}\n\n{FIXED_CAPTION}"

    context.user_data.clear()
    context.user_data.update({
        "file_id": file_id,
        "media_type": media_type,
        "caption": final_caption
    })

    keyboard = [
        [
            InlineKeyboardButton("▶️ نشر الآن", callback_data="publish_now"),
            InlineKeyboardButton("🔁 إعادة نشر (5 أيام)", callback_data="repost_5"),
        ],
        [
            InlineKeyboardButton("📦 البضاعة نفدت", callback_data="sold_out"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel"),
        ],
    ]

    await message.reply_text(
        "📌 اختر الإجراء المطلوب:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================== أزرار التحكم ==================
async def buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "publish_now":
        await publish_to_channel(query, context)

    elif data == "repost_5":
        context.user_data["repost"] = True
        await query.edit_message_text(
            "🔁 تم تفعيل إعادة النشر بعد 5 أيام.\n"
            "اضغط (نشر الآن) لإرسال المنشور."
        )

    elif data == "sold_out":
        context.user_data.clear()
        await query.edit_message_text("📦 تم إيقاف المنشور بسبب نفاد الكمية.")

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم إلغاء العملية.")

# ================== النشر بالقناة ==================
async def publish_to_channel(query, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    if not data:
        await query.edit_message_text("❌ لا يوجد منشور جاهز للنشر.")
        return

    bot = context.bot
    media_type = data["media_type"]
    file_id = data["file_id"]
    caption = data["caption"]

    if media_type == "photo":
        await bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=file_id,
            caption=caption,
        )
    elif media_type == "video":
        await bot.send_video(
            chat_id=CHANNEL_USERNAME,
            video=file_id,
            caption=caption,
        )

    await query.edit_message_text("✅ تم النشر بنجاح في القناة.")
    context.user_data.clear()

# ================== تشغيل البوت ==================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN غير موجود في Environment Variables")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, receive_media))
    app.add_handler(CallbackQueryHandler(buttons_handler))

    print("🤖 Bot is running...")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

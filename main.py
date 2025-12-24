import asyncio
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 أهلاً بك\n\n"
        "📸 أرسل صورة أو فيديو مع كابشن\n"
        "⏰ أو اضغط (نشر الآن)\n\n"
        "✅ البوت شغال وجاهز"
    )

# ================== استقبال صورة / فيديو ==================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 نشر الآن", callback_data="publish_now")]
    ])

    await message.reply_text(
        "📌 تم استلام المحتوى\n"
        "اختر ما تريد:",
        reply_markup=keyboard
    )

    # نحفظ آخر رسالة مؤقتاً
    context.user_data["last_message"] = message

# ================== زر نشر الآن ==================
async def publish_now_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = context.user_data.get("last_message")
    if not message:
        await query.edit_message_text("❌ لا يوجد محتوى للنشر")
        return

    caption = message.caption or "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة"

    # صورة
    if message.photo:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=message.photo[-1].file_id,
            caption=caption
        )

    # فيديو
    elif message.video:
        await context.bot.send_video(
            chat_id=CHANNEL,
            video=message.video.file_id,
            caption=caption
        )

    # تقرير للإدمن
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "✅ تم النشر بنجاح\n\n"
            f"👤 بواسطة: {message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🕒 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    )

    await query.edit_message_text("✅ تم النشر في القناة بنجاح")

# ================== التشغيل ==================
def main():
    print("🤖 البوت يعمل الآن...")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    application.add_handler(CallbackQueryHandler(publish_now_callback, pattern="^publish_now$"))

    application.run_polling()

# ================== Entry ==================
if __name__ == "__main__":
    main()

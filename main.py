from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ========= الإعدادات =========
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ========= كيبورد سفلي =========
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["🚀 نشر الآن"]],
    resize_keyboard=True
)

# ========= /start =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🤖 البوت جاهز\n\n"
        "📸 أرسل صورة أو فيديو\n"
        "🚀 ثم اضغط (نشر الآن)",
        reply_markup=MAIN_KEYBOARD
    )

# ========= استقبال صورة / فيديو =========
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["media"] = update.message

    await update.message.reply_text(
        "📌 تم استلام المحتوى\n"
        "اضغط 🚀 نشر الآن للنشر"
    )

# ========= زر نشر الآن (نصي) =========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "🚀 نشر الآن":
        return

    media_msg = context.user_data.get("media")

    if not media_msg:
        await update.message.reply_text("❌ لم يتم إرسال صورة أو فيديو")
        return

    caption = media_msg.caption or "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة"

    # نشر صورة
    if media_msg.photo:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=media_msg.photo[-1].file_id,
            caption=caption
        )

    # نشر فيديو
    elif media_msg.video:
        await context.bot.send_video(
            chat_id=CHANNEL,
            video=media_msg.video.file_id,
            caption=caption
        )

    # تقرير للإدمن
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "✅ تم النشر بنجاح\n\n"
            f"👤 {media_msg.from_user.full_name}\n"
            f"🆔 {media_msg.from_user.id}\n"
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    )

    context.user_data.clear()
    await update.message.reply_text("✅ تم النشر بنجاح")

# ========= التشغيل =========
def main():
    print("🤖 BOT STARTED")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()

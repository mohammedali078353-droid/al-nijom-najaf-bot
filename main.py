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

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ================== كيبورد سفلي ==================
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🚀 نشر الآن", "📊 حالة البوت"],
        ["⏰ جدولة", "⌛ المنشورات المجدولة"]
    ],
    resize_keyboard=True
)

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 أهلاً بك\n"
        "أرسل صورة أو فيديو ثم اختر ما تريد 👇",
        reply_markup=MAIN_KEYBOARD
    )

# ================== استقبال صورة / فيديو ==================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_message"] = update.message

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 نشر الآن", callback_data="publish_now")]
    ])

    await update.message.reply_text(
        "📌 تم استلام المحتوى\nاختر طريقة النشر:",
        reply_markup=inline_keyboard
    )

# ================== أزرار نصية (Reply Keyboard) ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚀 نشر الآن":
        await publish_content(update, context)

    elif text == "📊 حالة البوت":
        await update.message.reply_text("✅ البوت يعمل بشكل طبيعي")

    elif text == "⏰ جدولة":
        await update.message.reply_text("⏳ ميزة الجدولة قيد التطوير")

    elif text == "⌛ المنشورات المجدولة":
        await update.message.reply_text("📭 لا توجد منشورات مجدولة حالياً")

# ================== زر الإنلاين ==================
async def publish_now_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await publish_content(update, context, inline=True)

# ================== منطق النشر ==================
async def publish_content(update, context, inline=False):
    message = context.user_data.get("last_message")

    if not message:
        if inline:
            await update.callback_query.edit_message_text("❌ لا يوجد محتوى للنشر")
        else:
            await update.message.reply_text("❌ لا يوجد محتوى للنشر")
        return

    caption = message.caption or "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة"

    if message.photo:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=message.photo[-1].file_id,
            caption=caption
        )

    elif message.video:
        await context.bot.send_video(
            chat_id=CHANNEL,
            video=message.video.file_id,
            caption=caption
        )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "✅ تم النشر\n"
            f"👤 {message.from_user.full_name}\n"
            f"🆔 {message.from_user.id}\n"
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    )

    if inline:
        await update.callback_query.edit_message_text("✅ تم النشر بنجاح")
    else:
        await update.message.reply_text("✅ تم النشر بنجاح")

# ================== التشغيل ==================
def main():
    print("🤖 البوت يعمل الآن...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(publish_now_callback, pattern="^publish_now$"))

    app.run_polling()

if __name__ == "__main__":
    main()

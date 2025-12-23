from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "ضع_التوكن_مالتك_هنا"
CHANNEL = "@tajalnijomnjf"

# الكيبورد
keyboard = ReplyKeyboardMarkup(
    [
        ["📤 نشر الآن"],
        ["📊 حالة البوت", "⏳ المنشورات المجدولة"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 أهلاً بك\nاختر الأمر من الأزرار 👇",
        reply_markup=keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📤 نشر الآن" or text == "انشر الان":
        if context.user_data.get("last_photo"):
            await context.bot.send_photo(
                chat_id=CHANNEL,
                photo=context.user_data["last_photo"],
                caption=context.user_data.get(
                    "caption",
                    "وصول بضاعه جديدة داخل الشركة متوفرة الان بكميات محدودة"
                )
            )
            await update.message.reply_text("✅ تم النشر بنجاح", reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ ماكو صورة محفوظة للنشر", reply_markup=keyboard)

    elif text == "📊 حالة البوت":
        await update.message.reply_text("🟢 البوت يعمل بشكل طبيعي", reply_markup=keyboard)

    elif text == "⏳ المنشورات المجدولة":
        await update.message.reply_text("📭 حالياً لا توجد منشورات مجدولة", reply_markup=keyboard)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption

    context.user_data["last_photo"] = photo
    context.user_data["caption"] = caption

    await update.message.reply_text(
        "📸 تم استلام الصورة\nاختر من الأزرار 👇",
        reply_markup=keyboard
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()

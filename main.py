import random
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ========= الإعدادات =========
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ========= الكابشنات =========
CAPTIONS = [
    "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة",
    "منتج مميز بجودة عالية وسعر منافس",
    "الكمية محدودة – سارع بالحجز",
    "متوفر الآن داخل مخازن الشركة",
    "أفضل اختيار لأصحاب المشاريع",
    # كمل لحد 25 كابشن
]

# ========= كيبورد =========
KEYBOARD = ReplyKeyboardMarkup(
    [["🚀 نشر الآن"]],
    resize_keyboard=True
)

# ========= /start =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🤖 البوت جاهز\n"
        "📸 أرسل كل الصور أو الفيديوهات\n"
        "🚀 ثم اضغط نشر الآن",
        reply_markup=KEYBOARD
    )

# ========= استقبال ميديا =========
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    media_list = context.user_data.get("media_list", [])
    media_list.append(update.message)
    context.user_data["media_list"] = media_list

    await update.message.reply_text(
        f"📥 تم استلام ({len(media_list)}) ملف\n"
        "عند الانتهاء اضغط 🚀 نشر الآن"
    )

# ========= نشر =========
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "🚀 نشر الآن":
        return

    media_list = context.user_data.get("media_list")

    if not media_list:
        await update.message.reply_text("❌ ماكو محتوى للنشر")
        return

    count = 0

    for msg in media_list:
        caption = random.choice(CAPTIONS)

        if msg.photo:
            await context.bot.send_photo(
                chat_id=CHANNEL,
                photo=msg.photo[-1].file_id,
                caption=caption
            )

        elif msg.video:
            await context.bot.send_video(
                chat_id=CHANNEL,
                video=msg.video.file_id,
                caption=caption
            )

        count += 1
        await asyncio.sleep(2)  # فاصل حتى ما ينضغط البوت

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"✅ تم نشر {count} منشور\n"
            f"👤 {update.message.from_user.full_name}\n"
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    )

    context.user_data.clear()
    await update.message.reply_text(f"✅ تم نشر {count} منشور بنجاح")

# ========= تشغيل =========
def main():
    print("🤖 BOT STARTED")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()

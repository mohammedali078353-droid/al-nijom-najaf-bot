from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
import re
from datetime import datetime, timedelta

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ================== كابشن ثابت ==================
FIXED_CAPTION = "وصول بضاعه جديدة داخل الشركة متوفرة الان بكميات محدودة"

# ================== كيبورد ==================
keyboard = ReplyKeyboardMarkup(
    [["📤 نشر الآن", "⏰ جدولة"]],
    resize_keyboard=True
)

# ================== بدء البوت ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["photos"] = []
    await update.message.reply_text(
        "👋 أهلاً بك\n\n"
        "📸 أرسل الصور الآن\n"
        "⏰ أو حدد وقت بالنص مثل: 5:30\n"
        "📤 أو اضغط (نشر الآن)",
        reply_markup=keyboard
    )

# ================== استقبال الصور ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id

    if "photos" not in context.user_data:
        context.user_data["photos"] = []

    context.user_data["photos"].append(photo)

    await update.message.reply_text(
        f"✅ تم استلام الصورة ({len(context.user_data['photos'])})"
    )

# ================== نشر الآن ==================
async def publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = context.user_data.get("photos", [])

    if not photos:
        await update.message.reply_text("❌ لم يتم استلام أي صور")
        return

    for photo in photos:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=photo,
            caption=FIXED_CAPTION
        )
        await asyncio.sleep(1)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"✅ تم نشر {len(photos)} صورة بنجاح"
    )

    context.user_data["photos"].clear()

    await update.message.reply_text("✅ تم النشر بنجاح")

# ================== جدولة ==================
async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    match = re.search(r'(\d{1,2}):(\d{2})', text)
    if not match:
        await update.message.reply_text("❌ اكتب الوقت مثل 5:30")
        return

    hour = int(match.group(1))
    minute = int(match.group(2))

    now = datetime.now()
    publish_time = now.replace(hour=hour, minute=minute, second=0)

    if publish_time < now:
        publish_time += timedelta(days=1)

    delay = (publish_time - now).total_seconds()

    photos = context.user_data.get("photos", [])

    if not photos:
        await update.message.reply_text("❌ لا توجد صور مجدولة")
        return

    await update.message.reply_text(
        f"⏰ تم جدولة {len(photos)} صورة\n"
        f"🕒 وقت النشر: {publish_time.strftime('%H:%M')}"
    )

    asyncio.create_task(publish_later(context, photos.copy(), delay))

    context.user_data["photos"].clear()

# ================== نشر مؤجل ==================
async def publish_later(context, photos, delay):
    await asyncio.sleep(delay)

    for photo in photos:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=photo,
            caption=FIXED_CAPTION
        )
        await asyncio.sleep(1)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"⏰ تم نشر {len(photos)} صورة مجدولة بنجاح"
    )

# ================== أوامر نصية ==================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "نشر" in text:
        await publish_now(update, context)
    elif re.search(r'\d{1,2}:\d{2}', text):
        await schedule_handler(update, context)

# ================== تشغيل البوت ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ البوت يعمل بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()

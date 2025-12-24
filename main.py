from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import datetime
import hashlib
import random

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ================== تخزين ==================
last_media = {}   # يخزن آخر صورة/فيديو لكل مستخدم
sent_hashes = set()

# ================== كابشنات احتياطية ==================
AUTO_CAPTIONS = [
    "وصول بضاعة جديدة داخل الشركة متوفرة الآن وبكميات محدودة.",
    "منتج عملي بجودة عالية ومتوفر حاليًا داخل الشركة.",
    "خيار مثالي للاستخدام العملي وبسعر منافس.",
    "متوفر الآن – جودة مضمونة وتسليم فوري.",
]

def get_caption(caption):
    if caption:
        return caption.strip()
    return random.choice(AUTO_CAPTIONS)

def hash_bytes(data: bytes):
    return hashlib.md5(data).hexdigest()

# ================== الكيبورد الثابت ==================
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🚀 نشر الآن", "⏰ انشر بعد دقيقة"],
        ["📊 تقرير فوري"]
    ],
    resize_keyboard=True
)

# ================== أوامر ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 بوت النشر شغّال\n"
        "أرسل صورة أو فيديو ثم اضغط 🚀 نشر الآن",
        reply_markup=MAIN_KEYBOARD
    )

# ================== استقبال صورة ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    data = await file.download_as_bytearray()
    h = hash_bytes(data)

    if h in sent_hashes:
        await update.message.reply_text(
            "⚠️ هذه الصورة نُشرت سابقًا",
            reply_markup=MAIN_KEYBOARD
        )
        return

    caption = get_caption(update.message.caption)

    last_media[update.message.from_user.id] = {
        "type": "photo",
        "file_id": photo.file_id,
        "caption": caption,
        "hash": h
    }

    await update.message.reply_text(
        "✅ تم حفظ الصورة\nاضغط 🚀 نشر الآن",
        reply_markup=MAIN_KEYBOARD
    )

# ================== استقبال فيديو ==================
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = get_caption(update.message.caption)

    last_media[update.message.from_user.id] = {
        "type": "video",
        "file_id": update.message.video.file_id,
        "caption": caption,
        "hash": None
    }

    await update.message.reply_text(
        "✅ تم حفظ الفيديو\nاضغط 🚀 نشر الآن",
        reply_markup=MAIN_KEYBOARD
    )

# ================== نشر المحتوى ==================
async def publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in last_media:
        await update.message.reply_text(
            "❌ ماكو محتوى محفوظ للنشر",
            reply_markup=MAIN_KEYBOARD
        )
        return

    media = last_media.pop(uid)

    if media["type"] == "photo":
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=media["file_id"],
            caption=media["caption"]
        )
        sent_hashes.add(media["hash"])

    elif media["type"] == "video":
        await context.bot.send_video(
            chat_id=CHANNEL,
            video=media["file_id"],
            caption=media["caption"]
        )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📢 تم نشر محتوى\n"
            f"👤 بواسطة: {update.message.from_user.full_name}\n"
            f"🕒 {datetime.now().strftime('%H:%M:%S')}"
        )
    )

    await update.message.reply_text(
        "✅ تم النشر بنجاح",
        reply_markup=MAIN_KEYBOARD
    )

# ================== نشر بعد دقيقة ==================
async def publish_after_minute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in last_media:
        await update.message.reply_text(
            "❌ ماكو محتوى محفوظ",
            reply_markup=MAIN_KEYBOARD
        )
        return

    await update.message.reply_text(
        "⏳ سيتم النشر بعد دقيقة",
        reply_markup=MAIN_KEYBOARD
    )

    await context.job_queue.run_once(
        callback=scheduled_publish,
        when=60,
        data={"uid": uid, "chat_id": update.message.chat_id}
    )

async def scheduled_publish(context: ContextTypes.DEFAULT_TYPE):
    job = context.job.data
    uid = job["uid"]

    if uid not in last_media:
        return

    media = last_media.pop(uid)

    if media["type"] == "photo":
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=media["file_id"],
            caption=media["caption"]
        )
        sent_hashes.add(media["hash"])
    else:
        await context.bot.send_video(
            chat_id=CHANNEL,
            video=media["file_id"],
            caption=media["caption"]
        )

# ================== تقرير فوري ==================
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 البوت شغّال والنظام مستقر",
        reply_markup=MAIN_KEYBOARD
    )

# ================== النصوص ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚀 نشر الآن":
        await publish_now(update, context)
    elif text == "⏰ انشر بعد دقيقة":
        await publish_after_minute(update, context)
    elif text == "📊 تقرير فوري":
        await report(update, context)
    else:
        await update.message.reply_text(
            "ℹ️ أرسل صورة أو فيديو ثم استخدم الأزرار",
            reply_markup=MAIN_KEYBOARD
        )

# ================== تشغيل البوت ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🤖 Bot is running...")
app.run_polling()

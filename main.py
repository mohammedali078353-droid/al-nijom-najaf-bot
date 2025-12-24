from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import asyncio
import random
import hashlib
from datetime import datetime, timedelta

# ================== الإعدادات الثابتة ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ================== التخزين المؤقت ==================
image_hashes = set()
pending_posts = {}

# ================== كابشنات افتراضية (Fallback) ==================
AUTO_CAPTIONS = [
    "وصول بضاعة جديدة داخل الشركة متوفرة الآن وبكميات محدودة.",
    "منتج عملي بجودة عالية ومتوفر حالياً داخل الشركة.",
    "خيار مثالي للاستخدام العملي وبسعر منافس.",
    "متوفر الآن – جودة مضمونة وتسليم فوري.",
]

# ================== أدوات مساعدة ==================
def hash_file(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()

def smart_caption_fallback():
    return random.choice(AUTO_CAPTIONS)

# ================== ذكاء صناعي (معزول وآمن) ==================
def ai_generate_caption():
    try:
        # هنا مكان ربط API مستقبلاً
        return smart_caption_fallback()
    except:
        return smart_caption_fallback()

def ai_improve_caption(text: str):
    try:
        return text.strip() + " ✔️"
    except:
        return text

def ai_video_caption():
    try:
        return smart_caption_fallback()
    except:
        return smart_caption_fallback()

# ================== الأوامر ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 بوت النشر الذكي شغّال\n"
        "أرسل صورة أو فيديو مع كابشن (أو بدونه)\n"
        "والباقي علينا 💪"
    )

# ================== استقبال الصور ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    data = await file.download_as_bytearray()
    h = hash_file(data)

    if h in image_hashes:
        await update.message.reply_text("⚠️ هذه الصورة مكررة وتم منع نشرها")
        return

    image_hashes.add(h)

    caption = update.message.caption
    if not caption:
        caption = ai_generate_caption()

    caption = ai_improve_caption(caption)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 نشر الآن", callback_data="publish_now")],
        [InlineKeyboardButton("📊 تقرير فوري", callback_data="report")]
    ])

    pending_posts[update.message.from_user.id] = (photo.file_id, caption)

    await update.message.reply_text(
        "✅ تم استلام الصورة\nاختر الإجراء:",
        reply_markup=keyboard
    )

# ================== استقبال الفيديو ==================
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption
    if not caption:
        caption = ai_video_caption()

    await context.bot.send_video(
        chat_id=CHANNEL,
        video=update.message.video.file_id,
        caption=caption
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📹 تم نشر فيديو\n👤 بواسطة: {update.message.from_user.full_name}"
    )

# ================== الأزرار ==================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if query.data == "publish_now":
        if uid not in pending_posts:
            await query.edit_message_text("❌ لا يوجد محتوى للنشر")
            return

        file_id, caption = pending_posts.pop(uid)

        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=file_id,
            caption=caption
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📸 تم نشر صورة بنجاح\n"
                f"👤 الموظف: {query.from_user.full_name}\n"
                f"🕒 الوقت: {datetime.now().strftime('%H:%M:%S')}"
            )
        )

        await query.edit_message_text("✅ تم النشر بنجاح")

    elif query.data == "report":
        await query.edit_message_text("📊 التقرير أُرسل للأدمن")

# ================== فهم أوامر نصية ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "نشر" in text or "انشر" in text:
        await update.message.reply_text("📌 أرسل الصورة أو الفيديو المراد نشره")
    else:
        await update.message.reply_text("🤖 لم أفهم الأمر، أرسل صورة أو فيديو")

# ================== التشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_buttons))

print("🤖 Bot is running...")
app.run_polling()

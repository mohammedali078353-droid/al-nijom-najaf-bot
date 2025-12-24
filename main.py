from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from datetime import datetime, timedelta
import re

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"

# ✅ ADMIN ID (محفوظ ومعتمد)
ADMIN_ID = 304764998

AUTO_CAPTION = "وصول بضاعة جديدة داخل الشركة متوفرة الان بكميات محدودة"

TOTAL_POSTS = 0

# ================== استخراج الوقت ==================
def extract_time(text):
    match = re.search(r'(\d{1,2})[:٫](\d{2})', text)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))

    now = datetime.now()
    publish_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if publish_time < now:
        publish_time += timedelta(days=1)

    return publish_time

# ================== إرسال تقرير ==================
async def send_report(context, user, post_type, caption, method):
    global TOTAL_POSTS
    TOTAL_POSTS += 1

    name = user.full_name
    username = f"@{user.username}" if user.username else "بدون معرف"
    time_now = datetime.now().strftime("%H:%M")

    text = (
        "📢 تقرير نشر جديد\n\n"
        f"👤 الناشر: {name}\n"
        f"🔖 المعرف: {username}\n"
        f"🗂️ النوع: {'صورة' if post_type == 'photo' else 'فيديو'}\n"
        f"🚀 طريقة النشر: {method}\n"
        f"🕒 وقت النشر: {time_now}\n"
        f"🔢 العدد الكلي للمنشورات: {TOTAL_POSTS}\n\n"
        f"📝 الكابشن:\n{caption}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

# ================== مهمة النشر المجدول ==================
async def publish_job(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    user = data["user"]

    try:
        if data["type"] == "photo":
            await context.bot.send_photo(
                chat_id=CHANNEL,
                photo=data["file_id"],
                caption=data["caption"]
            )

        elif data["type"] == "video":
            await context.bot.send_video(
                chat_id=CHANNEL,
                video=data["file_id"],
                caption=data["caption"]
            )

        await send_report(
            context,
            user,
            data["type"],
            data["caption"],
            "جدولة"
        )

    except Exception as e:
        print("❌ خطأ بالنشر المجدول:", e)

# ================== استقبال صورة / فيديو ==================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    caption = message.caption or AUTO_CAPTION
    publish_time = extract_time(caption)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 نشر الآن", callback_data="publish_now")]
    ])

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"

    elif message.video:
        file_id = message.video.file_id
        media_type = "video"

    else:
        return

    post_data = {
        "type": media_type,
        "file_id": file_id,
        "caption": caption,
        "user": message.from_user
    }

    context.bot_data["pending_post"] = post_data

    if publish_time:
        context.job_queue.run_once(
            publish_job,
            publish_time,
            data=post_data
        )

        await message.reply_text(
            f"✅ تم جدولة المنشور\n⏰ وقت النشر: {publish_time.strftime('%H:%M')}",
            reply_markup=keyboard
        )
    else:
        await message.reply_text(
            "⚠️ لم يتم العثور على وقت في الكابشن\nاضغط (نشر الآن)",
            reply_markup=keyboard
        )

# ================== زر نشر الآن ==================
async def publish_now_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if "pending_post" not in context.bot_data:
        await query.edit_message_text("❌ لا يوجد منشور جاهز.")
        return

    post = context.bot_data.pop("pending_post")

    try:
        if post["type"] == "photo":
            await context.bot.send_photo(
                chat_id=CHANNEL,
                photo=post["file_id"],
                caption=post["caption"]
            )

        elif post["type"] == "video":
            await context.bot.send_video(
                chat_id=CHANNEL,
                video=post["file_id"],
                caption=post["caption"]
            )

        await send_report(
            context,
            query.from_user,
            post["type"],
            post["caption"],
            "نشر فوري"
        )

        await query.edit_message_text("✅ تم النشر الآن بنجاح.")

    except Exception as e:
        await query.edit_message_text(f"❌ فشل النشر:\n{e}")

# ================== التشغيل ==================
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(
        MessageHandler(filters.PHOTO | filters.VIDEO, handle_media)
    )

    application.add_handler(
        CallbackQueryHandler(publish_now_callback, pattern="^publish_now$")
    )

    print("🤖 البوت يعمل الآن...")
    application.run_polling()

if __name__ == "__main__":
    main()

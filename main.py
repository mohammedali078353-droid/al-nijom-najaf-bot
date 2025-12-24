from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
import random
import re
from datetime import datetime, timedelta

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
CHANNEL = "@tajalnijomnjf"
ADMIN_ID = 304764998

# ================== كابشنات تلقائية ==================
AUTO_CAPTIONS = [
    "وصول بضاعة جديدة وبمواصفات عالية، متوفرة الآن وبكميات محدودة.",
    "منتج عملي بجودة مضمونة، مناسب للاستخدام اليومي وبسعر منافس.",
    "الاختيار الأمثل لأصحاب العمل الباحثين عن الجودة والاعتمادية.",
    "متوفر الآن داخل الشركة، جودة عالية تلبي جميع الاحتياجات.",
    "منتج مميز يجمع بين القوة والكفاءة، جاهز للتسليم الفوري.",
    "حل عملي وموثوق لأصحاب المشاريع والمحلات التجارية.",
]

# ================== الأزرار ==================
keyboard = ReplyKeyboardMarkup(
    [
        ["📤 نشر الآن", "⏰ جدولة"],
        ["📊 حالة البوت", "⏳ المنشورات المجدولة"],
    ],
    resize_keyboard=True,
)

# ================== التخزين المؤقت ==================
scheduled_posts = []

# ================== تحليل الوقت ==================
def parse_time(text: str):
    now = datetime.now()
    text = text.lower()

    m = re.search(r"بعد\s+(\d+)\s*دقيقة", text)
    if m:
        return now + timedelta(minutes=int(m.group(1)))

    if "بعد ساعة" in text:
        return now + timedelta(hours=1)

    m = re.search(r"(\d{1,2}):(\d{2})", text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return now.replace(hour=h, minute=mi, second=0)

    return None

# ================== المجدول (Scheduler) ==================
async def scheduler(app):
    while True:
        now = datetime.now()
        for post in scheduled_posts[:]:
            if now >= post["time"]:
                if len(post["photos"]) == 1:
                    await app.bot.send_photo(
                        chat_id=CHANNEL,
                        photo=post["photos"][0],
                        caption=post["caption"],
                    )
                else:
                    media = [{"type": "photo", "media": p} for p in post["photos"]]
                    media[0]["caption"] = post["caption"]
                    await app.bot.send_media_group(CHANNEL, media)

                await app.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        "⏰ تم النشر حسب الجدولة\n"
                        f"🖼️ عدد الصور: {len(post['photos'])}\n"
                        f"🕒 وقت النشر: {datetime.now().strftime('%H:%M')}"
                    ),
                )

                scheduled_posts.remove(post)
        await asyncio.sleep(10)

async def post_init(application):
    application.create_task(scheduler(application))

# ================== الأوامر ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 البوت جاهز للعمل\nاختر من الأزرار 👇",
        reply_markup=keyboard,
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = context.user_data.get("photos", [])
    photos.append(update.message.photo[-1].file_id)
    context.user_data["photos"] = photos

    if update.message.caption and update.message.caption.strip():
        context.user_data["caption"] = update.message.caption
    else:
        context.user_data["caption"] = random.choice(AUTO_CAPTIONS)

    await update.message.reply_text(
        f"📸 تم استلام الصورة ({len(photos)})\nاختر نشر الآن أو جدولة ⏰",
        reply_markup=keyboard,
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # نشر الآن
    if text == "📤 نشر الآن":
        photos = context.user_data.get("photos")
        if not photos:
            await update.message.reply_text("❌ ماكو صور جاهزة", reply_markup=keyboard)
            return

        caption = context.user_data["caption"]

        if len(photos) == 1:
            await context.bot.send_photo(CHANNEL, photos[0], caption=caption)
        else:
            media = [{"type": "photo", "media": p} for p in photos]
            media[0]["caption"] = caption
            await context.bot.send_media_group(CHANNEL, media)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📤 تم النشر الفوري\n"
                f"🖼️ عدد الصور: {len(photos)}\n"
                f"🕒 وقت النشر: {datetime.now().strftime('%H:%M')}"
            ),
        )

        context.user_data.clear()
        await update.message.reply_text("✅ تم النشر بنجاح", reply_markup=keyboard)
        return

    # طلب جدولة
    if text == "⏰ جدولة":
        await update.message.reply_text("✍️ اكتب وقت النشر بأي صيغة")
        return

    # إدخال وقت الجدولة
    if "photos" in context.user_data:
        t = parse_time(text)
        if t:
            scheduled_posts.append(
                {
                    "photos": context.user_data["photos"],
                    "caption": context.user_data["caption"],
                    "time": t,
                }
            )
            context.user_data.clear()
            await update.message.reply_text(
                f"⏰ تم جدولة النشر على {t.strftime('%H:%M')}",
                reply_markup=keyboard,
            )
            return

    # حالة البوت
    if text == "📊 حالة البوت":
        await update.message.reply_text("🟢 البوت يعمل بشكل طبيعي", reply_markup=keyboard)
        return

    # عرض المجدول
    if text == "⏳ المنشورات المجدولة":
        if not scheduled_posts:
            await update.message.reply_text("📭 لا توجد منشورات مجدولة", reply_markup=keyboard)
        else:
            msg = "⏳ المنشورات المجدولة:\n"
            for p in scheduled_posts:
                msg += f"- {p['time'].strftime('%H:%M')} ({len(p['photos'])} صور)\n"
            await update.message.reply_text(msg, reply_markup=keyboard)
        return

# ================== التشغيل ==================
app = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()

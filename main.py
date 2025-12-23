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

# ================== كابشنات تلقائية ==================
AUTO_CAPTIONS = [
    "وصول بضاعة جديدة وبمواصفات عالية، متوفرة الآن وبكميات محدودة.",
    "منتج عملي بجودة مضمونة، مناسب للاستخدام اليومي وبسعر منافس.",
    "الاختيار الأمثل لأصحاب العمل الباحثين عن الجودة والاعتمادية.",
    "متوفر الآن داخل الشركة، جودة عالية تلبي جميع الاحتياجات.",
    "منتج مميز يجمع بين القوة والكفاءة، جاهز للتسليم الفوري.",
    "نوفر لكم أفضل الحلول العملية بأفضل الأسعار في السوق.",
    "متوفر بكميات محدودة مع إمكانية التجهيز السريع.",
    "جودة مضمونة وتجربة موثوقة، خيارك الأفضل للعمل المتواصل.",
    "منتج مصمم ليدوم، مناسب للأعمال الشاقة والاستخدام الطويل.",
    "حل عملي وموثوق لأصحاب المشاريع والمحلات التجارية.",
    "متوفر حالياً مع عروض خاصة للكميات الكبيرة.",
    "أداء ثابت، جودة عالية، وسعر يناسب الجميع.",
    "اختيار مثالي للباحثين عن الاعتمادية والكفاءة.",
    "منتج معتمد ومجرب، متوفر الآن داخل مخازن الشركة.",
    "نلتزم بتوفير منتجات تلبي متطلبات السوق وبأفضل جودة.",
]

# ================== الأزرار ==================
keyboard = ReplyKeyboardMarkup(
    [
        ["📤 نشر الآن", "⏰ جدولة"],
        ["📊 حالة البوت", "⏳ المنشورات المجدولة"],
    ],
    resize_keyboard=True,
)

# ================== التخزين ==================
scheduled_posts = []

# ================== تحليل الوقت ==================
def parse_time(text: str):
    now = datetime.now()
    if not text:
        return None

    text = text.lower()

    # بعد X دقيقة
    m = re.search(r"بعد\s+(\d+)\s*دقيقة", text)
    if m:
        return now + timedelta(minutes=int(m.group(1)))

    # بعد ساعة
    if "بعد ساعة" in text:
        return now + timedelta(hours=1)

    # hh:mm
    m = re.search(r"(\d{1,2}):(\d{2})", text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return now.replace(hour=h, minute=mi, second=0)

    # رقم فقط (ساعة)
    m = re.search(r"\b(\d{1,2})\b", text)
    if m:
        h = int(m.group(1))
        return now.replace(hour=h, minute=0, second=0)

    return None

# ================== المجدول ==================
async def scheduler(app):
    while True:
        now = datetime.now()
        for post in scheduled_posts[:]:
            if now >= post["time"]:
                await app.bot.send_photo(
                    chat_id=CHANNEL,
                    photo=post["photo"],
                    caption=post["caption"],
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
    context.user_data["photo"] = update.message.photo[-1].file_id

    if update.message.caption and update.message.caption.strip():
        context.user_data["caption"] = update.message.caption
        context.user_data["caption_type"] = "user"
    else:
        context.user_data["caption"] = random.choice(AUTO_CAPTIONS)
        context.user_data["caption_type"] = "auto"

    await update.message.reply_text(
        "📸 تم استلام الصورة\nاختر نشر الآن أو جدولة ⏰",
        reply_markup=keyboard,
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # نشر الآن
    if text == "📤 نشر الآن":
        if "photo" not in context.user_data:
            await update.message.reply_text("❌ ماكو صورة جاهزة", reply_markup=keyboard)
            return

        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=context.user_data["photo"],
            caption=context.user_data["caption"],
        )

        caption_info = (
            "✍️ كابشنك"
            if context.user_data.get("caption_type") == "user"
            else "🤖 كابشن تلقائي"
        )

        context.user_data.clear()
        await update.message.reply_text(
            f"✅ تم النشر بنجاح\n{caption_info}",
            reply_markup=keyboard,
        )
        return

    # طلب جدولة
    if text == "⏰ جدولة":
        await update.message.reply_text("✍️ اكتب الوقت بأي صيغة")
        return

    # إدخال وقت للجدولة
    if "photo" in context.user_data:
        t = parse_time(text)
        if t:
            scheduled_posts.append(
                {
                    "photo": context.user_data["photo"],
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
                msg += f"- {p['time'].strftime('%H:%M')}\n"
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

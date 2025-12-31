from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from datetime import datetime, timedelta
import random
import json
import os
import re

# ================== الإعدادات الأساسية ==================
TOKEN = "7813783471:AAEipNjiTWntDapCLN7Zz3HVuhKWL-UivUE"
CHANNEL = "@tajalnijomnjf"

ADMIN_ID = 304764998   # المدير الوحيد
EMPLOYEES = set()      # أيدي الموظفين (تنضاف ديناميكياً)

DATA_FILE = "scheduled_posts.json"

# ================== كابشنات متغيرة (2025) ==================
AUTO_CAPTIONS = [
    "🔧 تجهيز حديث وبمواصفات قوية – متوفر الآن داخل الشركة.",
    "⚙️ معدات أصلية بتشغيل مستقر واعتمادية عالية.",
    "💪 حل عملي للأعمال الثقيلة والخفيفة – جاهز للتسليم.",
    "🚜 أداء قوي يناسب العمل المستمر والضغط العالي.",
    "🔋 كفاءة تشغيل عالية مع استهلاك محسوب.",
    "🏗️ اختيار مثالي لأصحاب المشاريع والمقاولين.",
    "📦 متوفر الآن بكميات محدودة – اطلبه قبل النفاد.",
    "🛠️ جودة تصنيع عالية مع نتائج مضمونة.",
    "⚡ قوة، ثبات، واعتمادية في جهاز واحد.",
    "🔥 من التجهيزات المطلوبة لسنة 2025."
]

last_caption = None

def get_smart_caption():
    global last_caption
    options = [c for c in AUTO_CAPTIONS if c != last_caption]
    caption = random.choice(options) if options else random.choice(AUTO_CAPTIONS)
    last_caption = caption
    return caption

# ================== التخزين ==================
def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, default=str)

def load_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for p in data:
            p["post_time"] = datetime.fromisoformat(p["post_time"])
        return data

scheduled_posts = load_posts()
publishing_paused = False

# ================== الصلاحيات ==================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def is_employee(user_id: int) -> bool:
    return user_id == ADMIN_ID or user_id in EMPLOYEES

# ================== قراءة الوقت ==================
def extract_time(text):
    now = datetime.now()

    match = re.search(r'(\d{1,2}):(\d{2})', text)
    if match:
        h, m = map(int, match.groups())
        t = now.replace(hour=h, minute=m, second=0)
        return t if t > now else t + timedelta(days=1)

    match = re.search(r'(\d{1,2})\s*ونص', text)
    if match:
        h = int(match.group(1))
        t = now.replace(hour=h, minute=30, second=0)
        return t if t > now else t + timedelta(days=1)

    match = re.search(r'(\d{1,2})\s*(م|ص)', text)
    if match:
        h = int(match.group(1))
        if match.group(2) == "م" and h < 12:
            h += 12
        t = now.replace(hour=h, minute=0, second=0)
        return t if t > now else t + timedelta(days=1)

    return None

# ================== الكيبورد الرئيسي ==================
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 نشر الآن", callback_data="publish_now"),
            InlineKeyboardButton("📋 عرض المجدول", callback_data="list_schedule"),
        ],
        [
            InlineKeyboardButton("❌ إلغاء آخر جدولة", callback_data="cancel_last"),
            InlineKeyboardButton("♻️ تغيير الكابشن", callback_data="change_caption"),
        ],
        [
            InlineKeyboardButton("⏸️ إيقاف النشر", callback_data="pause"),
            InlineKeyboardButton("▶️ تشغيل النشر", callback_data="resume"),
        ],
        [
            InlineKeyboardButton("📊 تقرير اليوم", callback_data="daily_report"),
            InlineKeyboardButton("👤 إضافة موظف", callback_data="add_employee"),
        ],
        [
            InlineKeyboardButton("⚙️ إعدادات", callback_data="settings"),
        ]
    ])

# ================== استقبال الصور ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_employee(user_id):
        return

    photo = update.message.photo[-1]
    caption = update.message.caption or ""

    post_time = extract_time(caption)

    if not post_time:
        # نشر فوري
        smart_caption = caption if caption.strip() else get_smart_caption()
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=photo.file_id,
            caption=smart_caption
        )
        await update.message.reply_text("✅ تم النشر فوراً", reply_markup=main_keyboard())

        # تقرير للمدير فقط
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="📤 تقرير نشر\nتم نشر صورة فوراً بنجاح."
        )
        return

    clean_caption = re.sub(
        r'(\d{1,2}:\d{2}|\d+\s*ونص|\d+\s*(?:م|ص))',
        '',
        caption
    ).strip()

    if not clean_caption:
        clean_caption = get_smart_caption()

    scheduled_posts.append({
        "file_id": photo.file_id,
        "caption": clean_caption,
        "post_time": post_time
    })
    save_posts(scheduled_posts)

    await update.message.reply_text(
        f"⏰ تم جدولة الصورة\n🕒 {post_time.strftime('%H:%M')}",
        reply_markup=main_keyboard()
    )

# ================== أزرار التحكم ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global publishing_paused

    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if not is_employee(user_id):
        return

    if query.data == "pause":
        publishing_paused = True
        await query.edit_message_text("⏸️ تم إيقاف النشر مؤقتاً")

    elif query.data == "resume":
        publishing_paused = False
        await query.edit_message_text("▶️ تم تشغيل النشر")

    elif query.data == "list_schedule":
        if not scheduled_posts:
            await query.edit_message_text("📋 ماكو منشورات مجدولة حالياً")
        else:
            text = "📋 المنشورات المجدولة:\n"
            for i, p in enumerate(scheduled_posts, 1):
                text += f"{i}) {p['post_time'].strftime('%H:%M')}\n"
            await query.edit_message_text(text)

    elif query.data == "cancel_last":
        if scheduled_posts:
            scheduled_posts.pop()
            save_posts(scheduled_posts)
            await query.edit_message_text("❌ تم إلغاء آخر جدولة")
        else:
            await query.edit_message_text("❌ ماكو شي للإلغاء")

    elif query.data == "change_caption":
        await query.edit_message_text(f"♻️ كابشن جديد:\n{get_smart_caption()}")

    elif query.data == "daily_report" and is_admin(user_id):
        await query.edit_message_text(
            f"📊 تقرير اليوم\n"
            f"📌 مجدول حالياً: {len(scheduled_posts)} منشور"
        )

    elif query.data == "add_employee" and is_admin(user_id):
        context.user_data["await_employee_id"] = True
        await query.edit_message_text("✏️ دز ID الموظف لإضافته")

# ================== إضافة موظف ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    if context.user_data.get("await_employee_id"):
        try:
            emp_id = int(update.message.text.strip())
            EMPLOYEES.add(emp_id)
            context.user_data["await_employee_id"] = False
            await update.message.reply_text(f"✅ تم إضافة الموظف ID: {emp_id}")
        except:
            await update.message.reply_text("❌ ID غير صحيح")

# ================== فحص الجدولة ==================
async def check_schedule(context: ContextTypes.DEFAULT_TYPE):
    if publishing_paused:
        return

    now = datetime.now()
    for post in scheduled_posts[:]:
        if now >= post["post_time"]:
            await context.bot.send_photo(
                chat_id=CHANNEL,
                photo=post["file_id"],
                caption=post["caption"]
            )

            # تقرير للمدير فقط
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="📊 تقرير نشر\n✅ تم نشر منشور مجدول بنجاح"
            )

            scheduled_posts.remove(post)
            save_posts(scheduled_posts)

# ================== التشغيل ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(check_schedule, interval=10, first=5)

    app.run_polling()

if __name__ == "__main__":
    main()
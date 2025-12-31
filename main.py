from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime, timedelta
import re
import json
import os

# ================== الإعدادات ==================
TOKEN = "7813783471:AAEtUMHRB18_eJjMtOs0cIOeUijSi8QDQa8"
ADMIN_ID = 304764998   # غيّر إذا تحب

DATA_FILE = "scheduled_posts.json"

AUTO_CAPTIONS = [
    "وصول بضاعة جديدة داخل الشركة متوفرة الآن بكميات محدودة.",
    "منتج عملي بجودة مضمونة، جاهز للتسليم.",
    "الخيار الأمثل لأصحاب العمل الباحثين عن الاعتمادية.",
]

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

# ================== قراءة الوقت بأي صيغة ==================
def extract_time(text):
    text = text.replace("مساءً", "م").replace("صباحاً", "ص")
    now = datetime.now()

    patterns = [
        r'(\d{1,2}):(\d{2})',
        r'(\d{1,2})\s*ونص',
        r'(\d{1,2})\s*(م|ص)',
        r'الساعة\s*(\d{1,2})'
    ]

    for p in patterns:
        match = re.search(p, text)
        if match:
            if ":" in p:
                h, m = map(int, match.groups())
            elif "ونص" in p:
                h, m = int(match.group(1)), 30
            else:
                h = int(match.group(1))
                m = 0
                if len(match.groups()) > 1 and match.group(2) == "م" and h < 12:
                    h += 12

            t = now.replace(hour=h, minute=m, second=0)
            return t if t > now else t + timedelta(days=1)

    return None

# ================== استقبال الصور ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    caption = update.message.caption or ""

    post_time = extract_time(caption)

    # نشر فوري
    if not post_time:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=photo.file_id,
            caption=caption or AUTO_CAPTIONS[0]
        )
        await update.message.reply_text("✅ تم النشر فوراً")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="📤 نشر فوري\n🖼️ صورة بدون جدولة"
        )
        return

    # تنظيف الكابشن من الوقت
    clean_caption = re.sub(
        r'(\d{1,2}:\d{2}|\d+\s*ونص|\d+\s*(?:م|ص)|الساعة\s*\d+)',
        '',
        caption
    ).strip()

    if not clean_caption:
        clean_caption = AUTO_CAPTIONS[len(scheduled_posts) % len(AUTO_CAPTIONS)]

    scheduled_posts.append({
        "file_id": photo.file_id,
        "caption": clean_caption,
        "post_time": post_time
    })
    save_posts(scheduled_posts)

    await update.message.reply_text(
        f"✅ تم جدولة الصورة\n🕒 {post_time.strftime('%H:%M')}"
    )

# ================== فحص الجدولة (JobQueue) ==================
async def check_schedule(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    for post in scheduled_posts[:]:
        if now >= post["post_time"]:
            await context.bot.send_photo(
                chat_id=CHANNEL,
                photo=post["file_id"],
                caption=post["caption"]
            )

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "📊 تقرير نشر\n"
                    f"🕒 {post['post_time'].strftime('%H:%M')}\n"
                    "✅ تم النشر بنجاح"
                )
            )

            scheduled_posts.remove(post)
            save_posts(scheduled_posts)

# ================== التشغيل ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # JobQueue هي الحل الصحيح
    app.job_queue.run_repeating(check_schedule, interval=10, first=5)

    app.run_polling()

if __name__ == "__main__":
    main()
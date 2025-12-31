from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import asyncio
import re
import json
import os
from datetime import datetime, timedelta

# ================== الإعدادات ==================
TOKEN = "PUT_YOUR_TOKEN_HERE"
CHANNEL = "@tajalnijomnjf"

DATA_FILE = "scheduled_posts.json"

AUTO_CAPTIONS = [
    "وصول بضاعة جديدة داخل الشركة متوفرة الآن بكميات محدودة.",
    "منتج عملي بجودة مضمونة، جاهز للتسليم.",
    "الخيار الأمثل لأصحاب العمل الباحثين عن الاعتمادية.",
]

# ================== الحفظ والتحميل ==================
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

    # 15:30 أو 3:30
    match = re.search(r'(\d{1,2}):(\d{2})', text)
    if match:
        h, m = map(int, match.groups())
        t = now.replace(hour=h, minute=m, second=0)
        return t if t > now else t + timedelta(days=1)

    # 3 ونص
    match = re.search(r'(\d{1,2})\s*ونص', text)
    if match:
        h = int(match.group(1))
        t = now.replace(hour=h, minute=30, second=0)
        return t if t > now else t + timedelta(days=1)

    # 4 م / 10 ص
    match = re.search(r'(\d{1,2})\s*(م|ص)', text)
    if match:
        h = int(match.group(1))
        if match.group(2) == "م" and h < 12:
            h += 12
        t = now.replace(hour=h, minute=0, second=0)
        return t if t > now else t + timedelta(days=1)

    # الساعة 4
    match = re.search(r'الساعة\s*(\d{1,2})', text)
    if match:
        h = int(match.group(1))
        t = now.replace(hour=h, minute=0, second=0)
        return t if t > now else t + timedelta(days=1)

    return None

# ================== استقبال الصور ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    caption = update.message.caption or ""

    post_time = extract_time(caption)

    # إذا ماكو وقت → ينشر فوراً
    if not post_time:
        caption_to_send = caption or AUTO_CAPTIONS[0]
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=photo.file_id,
            caption=caption_to_send
        )
        await update.message.reply_text("✅ تم النشر فوراً")
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
        f"✅ تم جدولة الصورة\n🕒 وقت النشر: {post_time.strftime('%H:%M')}"
    )

# ================== النشر التلقائي ==================
async def scheduler(app):
    while True:
        now = datetime.now()
        for post in scheduled_posts[:]:
            if now >= post["post_time"]:
                await app.bot.send_photo(
                    chat_id=CHANNEL,
                    photo=post["file_id"],
                    caption=post["caption"]
                )
                scheduled_posts.remove(post)
                save_posts(scheduled_posts)
        await asyncio.sleep(10)

# ================== تشغيل البوت ==================
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    asyncio.create_task(scheduler(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}

CHANNEL_LINK = "https://t.me/wenaymahramm"
GROUP_LINK = "https://t.me/+kn-C8uk4zQxmY2E6"
ADMIN_CONTACT = "@XORT404"

WELCOME_TEXT = (
    "سلاو، بەخێربێیت بۆ ئەم بۆتە ❤️\n\n"
    "تێبینی❗️: لەوانەیە هەندێ جار کار نەکات، ئەویش بەهۆی لە خەت ڕۆشتنی ئەدمینەوەیە. "
    "هەر کاتێک ئەدمین بێتەوە خەت، بۆتەکە چالاک دەبێت و ئۆتۆماتیکی ڤیدیۆکان دەگاتە دەستت.💙\n\n"
    f"ئەگەر پرسیارتان هەیە یان بۆتەکە کاری نەکرد، نامە بۆ ئەدمین بنێرن 👈🏻 {ADMIN_CONTACT}"
)

CHANNEL_GROUP_TEXT = (
    "📢 چەنال و گرووپ\n\n"
    f"چەنال:\n{CHANNEL_LINK}\n\n"
    f"گرووپ:\n{GROUP_LINK}"
)

NO_NEW_POSTS_TEXT = "هیچ بابەتێکی نوێ نییە."
NO_OLD_POSTS_TEXT = "هیچ بابەتێکی پێشتر بوونی نییە."

USERS_PER_PAGE = 20
OLD_POSTS_HOURS = 48

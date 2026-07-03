from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import USERS_PER_PAGE

def user_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🆕 نوێ", callback_data="user:new"))
    kb.row(InlineKeyboardButton(text="📂 پێشتر", callback_data="user:old"))
    kb.row(InlineKeyboardButton(text="📢 چەنال و گرووپ", callback_data="user:channels"))
    return kb.as_markup()

def admin_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📤 Broadcast to All", callback_data="admin:broadcast"))
    kb.row(InlineKeyboardButton(text="👥 Send to Selected Users", callback_data="admin:select_users"))
    kb.row(InlineKeyboardButton(text="📦 Saved Posts", callback_data="admin:saved_posts"))
    kb.row(InlineKeyboardButton(text="👤 Users", callback_data="admin:users"))
    kb.row(InlineKeyboardButton(text="📊 Statistics", callback_data="admin:stats"))
    kb.row(InlineKeyboardButton(text="⚙️ Settings", callback_data="admin:settings"))
    return kb.as_markup()

def admin_back_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 Back", callback_data="admin:back"))
    return kb.as_markup()

def cancel_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❌ Cancel", callback_data="admin:cancel"))
    return kb.as_markup()

def user_selection_keyboard(users, page=0, selected=None):
    if selected is None:
        selected = set()
    kb = InlineKeyboardBuilder()
    start = page * USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    page_users = users[start:end]

    for user in page_users:
        uid = user["telegram_id"]
        name = user["first_name"]
        uname = user.get("username")
        check = "☑" if uid in selected else "☐"
        if uname:
            label = f"{check} {name} (@{uname})"
        else:
            label = f"{check} {name} (ID: {uid})"
        kb.row(InlineKeyboardButton(text=label, callback_data=f"select:{uid}"))

    total_pages = max(1, (len(users) + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅ Previous", callback_data=f"page:{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡", callback_data=f"page:{page + 1}"))
    if nav_buttons:
        kb.row(*nav_buttons)

    kb.row(InlineKeyboardButton(text="✅ Select All", callback_data="select:all"))
    kb.row(InlineKeyboardButton(text="✅ Continue", callback_data="select:continue"))
    kb.row(InlineKeyboardButton(text="❌ Cancel", callback_data="admin:cancel"))
    return kb.as_markup()

def channels_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🆕 نوێ", callback_data="user:new"))
    kb.row(InlineKeyboardButton(text="📂 پێشتر", callback_data="user:old"))
    kb.row(InlineKeyboardButton(text="📢 چەنال و گرووپ", callback_data="user:channels"))
    return kb.as_markup()

import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database import (
    get_all_users, get_all_posts, get_user_count, get_post_count,
    get_viewed_count,
)
from keyboards import (
    admin_main_keyboard, admin_back_keyboard, cancel_keyboard,
    user_selection_keyboard,
)
from states import AdminStates
from media import (
    send_post_to_user, save_admin_post,
    STATUS_SENT, STATUS_FAILED, STATUS_BLOCKED,
)
import database as db

logger = logging.getLogger(__name__)
router = Router()

_selection_sessions: dict = {}

def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(F.text == "/start")
async def admin_start(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "👑 Admin Panel\n\nSelect an action:",
        reply_markup=admin_main_keyboard(),
    )

@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text(
        "👑 Admin Panel\n\nSelect an action:",
        reply_markup=admin_main_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await state.clear()
    if callback.from_user.id in _selection_sessions:
        del _selection_sessions[callback.from_user.id]
    await callback.message.edit_text(
        "❌ Operation cancelled.",
        reply_markup=admin_main_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.waiting_for_broadcast_content)
    await callback.message.edit_text(
        "📤 Broadcast to All\n\nSend the content you want to broadcast to all users.\n\n"
        "Supported: Text, Photo, Video, Album, Document, Audio, Voice, Animation",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_broadcast_content, F.from_user.id == ADMIN_ID)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    await state.clear()

    post = await save_admin_post(message, db)
    if not post:
        await message.answer("❌ Failed to save post.", reply_markup=admin_main_keyboard())
        return

    users = await get_all_users()
    sent, failed, blocked = await _deliver_to_users(bot, post, [u["telegram_id"] for u in users])

    await message.answer(
        f"✅ Sent: {sent}\n❌ Failed: {failed}\n🚫 Blocked: {blocked}",
        reply_markup=admin_main_keyboard(),
    )

@router.callback_query(F.data == "admin:select_users")
async def admin_select_users_start(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await state.clear()
    users = await get_all_users()
    if not users:
        await callback.message.edit_text("No registered users yet.", reply_markup=admin_back_keyboard())
        await callback.answer()
        return

    _selection_sessions[callback.from_user.id] = {
        "users": users,
        "selected": set(),
        "page": 0,
    }
    await callback.message.edit_text(
        "👥 Send to Selected Users\n\nSelect users to send content to:",
        reply_markup=user_selection_keyboard(users, 0, set()),
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select:"))
async def admin_toggle_select(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    session = _selection_sessions.get(callback.from_user.id)
    if not session:
        await callback.answer("Session expired. Please restart.", show_alert=True)
        return

    action = callback.data.split(":", 1)[1]

    if action == "all":
        all_ids = {u["telegram_id"] for u in session["users"]}
        if session["selected"] == all_ids:
            session["selected"] = set()
        else:
            session["selected"] = all_ids
        await callback.message.edit_reply_markup(
            reply_markup=user_selection_keyboard(
                session["users"], session["page"], session["selected"]
            )
        )
    elif action == "continue":
        if not session["selected"]:
            await callback.answer("No users selected!", show_alert=True)
            return
        await state.set_state(AdminStates.waiting_for_selected_content)
        await callback.message.edit_text(
            f"✅ {len(session['selected'])} user(s) selected.\n\n"
            "Now send the content you want to send to them.\n\n"
            "Supported: Text, Photo, Video, Album, Document, Audio, Voice, Animation",
            reply_markup=cancel_keyboard(),
        )
    else:
        uid = int(action)
        if uid in session["selected"]:
            session["selected"].discard(uid)
        else:
            session["selected"].add(uid)
        await callback.message.edit_reply_markup(
            reply_markup=user_selection_keyboard(
                session["users"], session["page"], session["selected"]
            )
        )

    await callback.answer()

@router.callback_query(F.data.startswith("page:"))
async def admin_change_page(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    session = _selection_sessions.get(callback.from_user.id)
    if not session:
        await callback.answer("Session expired. Please restart.", show_alert=True)
        return

    page = int(callback.data.split(":", 1)[1])
    session["page"] = page
    await callback.message.edit_reply_markup(
        reply_markup=user_selection_keyboard(
            session["users"], page, session["selected"]
        )
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_selected_content, F.from_user.id == ADMIN_ID)
async def admin_selected_content_send(message: Message, state: FSMContext, bot: Bot):
    session = _selection_sessions.get(message.from_user.id)
    if not session or not session.get("selected"):
        await state.clear()
        await message.answer("❌ No users selected. Operation cancelled.", reply_markup=admin_main_keyboard())
        return

    await state.clear()
    selected_ids = list(session["selected"])
    del _selection_sessions[message.from_user.id]

    post = await save_admin_post(message, db)
    if not post:
        await message.answer("❌ Failed to save post.", reply_markup=admin_main_keyboard())
        return

    sent, failed, blocked = await _deliver_to_users(bot, post, selected_ids)

    await message.answer(
        f"✅ Sent: {sent}\n❌ Failed: {failed}\n🚫 Blocked: {blocked}",
        reply_markup=admin_main_keyboard(),
    )

async def _deliver_to_users(bot: Bot, post: dict, user_ids: list) -> tuple:
    sent = 0
    failed = 0
    blocked = 0
    for uid in user_ids:
        result = await send_post_to_user(bot, post, uid)
        if result == STATUS_SENT:
            sent += 1
        elif result == STATUS_BLOCKED:
            blocked += 1
        else:
            failed += 1
    return sent, failed, blocked

@router.callback_query(F.data == "admin:saved_posts")
async def admin_saved_posts(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    posts = await get_all_posts()
    if not posts:
        await callback.message.edit_text(
            "📦 No saved posts yet.", reply_markup=admin_back_keyboard()
        )
        await callback.answer()
        return

    text_lines = [f"📦 Saved Posts ({len(posts)} total)\n"]
    for i, post in enumerate(posts[:20], 1):
        ct = post.get("content_type", "unknown")
        cap = (post.get("caption") or "")[:50]
        text_lines.append(f"{i}. [{ct}] {cap}")

    if len(posts) > 20:
        text_lines.append(f"\n... and {len(posts) - 20} more")

    await callback.message.edit_text(
        "\n".join(text_lines),
        reply_markup=admin_back_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    users = await get_all_users()
    if not users:
        await callback.message.edit_text("👤 No registered users.", reply_markup=admin_back_keyboard())
        await callback.answer()
        return

    lines = [f"👤 Registered Users ({len(users)} total)\n"]
    for user in users:
        name = user.get("first_name", "Unknown")
        uname = user.get("username")
        uid = user.get("telegram_id")
        join = user.get("join_date", "")[:10] if user.get("join_date") else ""
        if uname:
            lines.append(f"• {name} (@{uname})\n  ID: {uid}\n  Joined: {join}")
        else:
            lines.append(f"• {name}\n  ID: {uid}\n  Joined: {join}")

    text = "\n\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n\n... (truncated)"

    await callback.message.edit_text(text, reply_markup=admin_back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    user_count = await get_user_count()
    post_count = await get_post_count()
    viewed_count = await get_viewed_count()

    await callback.message.edit_text(
        f"📊 Statistics\n\n"
        f"👥 Total Users: {user_count}\n"
        f"📦 Total Posts: {post_count}\n"
        f"👁 Total Views: {viewed_count}",
        reply_markup=admin_back_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "admin:settings")
async def admin_settings(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "⚙️ Settings\n\n"
        f"Admin ID: {ADMIN_ID}\n"
        f"Bot is running and operational.\n\n"
        "No additional settings available at this time.",
        reply_markup=admin_back_keyboard(),
    )
    await callback.answer()

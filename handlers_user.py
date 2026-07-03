import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from config import (
    WELCOME_TEXT, CHANNEL_GROUP_TEXT, NO_NEW_POSTS_TEXT, NO_OLD_POSTS_TEXT,
    ADMIN_ID,
)
from database import (
    upsert_user, get_unviewed_posts, get_recent_posts, mark_post_viewed,
)
from keyboards import user_main_keyboard, channels_keyboard
from media import send_post_to_user

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        return

    await upsert_user(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name or "",
        username=message.from_user.username,
    )
    await message.answer(WELCOME_TEXT, reply_markup=user_main_keyboard())

@router.callback_query(F.data == "user:new")
async def cb_new_posts(callback: CallbackQuery):
    user_id = callback.from_user.id
    posts = await get_unviewed_posts(user_id)

    if not posts:
        await callback.message.answer(NO_NEW_POSTS_TEXT)
        await callback.answer()
        return

    await callback.answer("نوێ...")

    for post in posts:
        await send_post_to_user(callback.bot, post, user_id)
        await mark_post_viewed(user_id, post["id"])

    await callback.message.answer(
        "ئەوانە هەموو بابەتە نوێیەکان بوون ✅",
        reply_markup=user_main_keyboard(),
    )

@router.callback_query(F.data == "user:old")
async def cb_old_posts(callback: CallbackQuery):
    user_id = callback.from_user.id
    posts = await get_recent_posts(hours=48)

    if not posts:
        await callback.message.answer(NO_OLD_POSTS_TEXT)
        await callback.answer()
        return

    await callback.answer("پێشتر...")

    for post in posts:
        await send_post_to_user(callback.bot, post, user_id)

    await callback.message.answer(
        "ئەوانە بابەتەکانی ٤٨ کاتژمێری ڕابردوو بوون ✅",
        reply_markup=user_main_keyboard(),
    )

@router.callback_query(F.data == "user:channels")
async def cb_channels(callback: CallbackQuery):
    await callback.message.answer(CHANNEL_GROUP_TEXT, reply_markup=channels_keyboard())
    await callback.answer()

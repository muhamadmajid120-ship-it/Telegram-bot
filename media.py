import logging

logger = logging.getLogger(__name__)

STATUS_SENT = "sent"
STATUS_FAILED = "failed"
STATUS_BLOCKED = "blocked"

async def send_post_to_user(bot, post, chat_id: int) -> str:
    """Send a saved post to a user using copyMessage (no forwarding header).
    Returns one of STATUS_SENT, STATUS_FAILED, STATUS_BLOCKED."""
    try:
        from_chat_id = post["admin_chat_id"]
        message_id = post["post_id"]
        caption = post.get("caption")

        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption if caption else None,
        )
        return STATUS_SENT
    except Exception as e:
        err_str = str(e).lower()
        if "blocked" in err_str or "forbidden" in err_str or "chat not found" in err_str or "user is deactivated" in err_str:
            logger.info(f"User {chat_id} blocked/deactivated: {e}")
            return STATUS_BLOCKED
        logger.error(f"Failed to send post to {chat_id}: {e}")
        return STATUS_FAILED

async def save_admin_post(message, database) -> dict | None:
    """When admin sends content, save it to the database.
    Handles text, photo, video, document, audio, voice, animation, and albums."""
    try:
        admin_chat_id = message.chat.id
        message_id = message.message_id
        caption = message.caption if message.caption else None

        content_type = None
        file_ids = None

        if message.photo:
            content_type = "photo"
            file_ids = [message.photo[-1].file_id]
        elif message.video:
            content_type = "video"
            file_ids = [message.video.file_id]
        elif message.document:
            content_type = "document"
            file_ids = [message.document.file_id]
        elif message.audio:
            content_type = "audio"
            file_ids = [message.audio.file_id]
        elif message.voice:
            content_type = "voice"
            file_ids = [message.voice.file_id]
        elif message.animation:
            content_type = "animation"
            file_ids = [message.animation.file_id]
        elif message.text:
            content_type = "text"
        elif message.media_group_id:
            content_type = "album"
            if message.photo:
                file_ids = [message.photo[-1].file_id]
            elif message.video:
                file_ids = [message.video.file_id]
        else:
            content_type = "text"

        post = await database.insert_post(
            post_id=message_id,
            admin_chat_id=admin_chat_id,
            caption=caption,
            content_type=content_type,
            file_ids=file_ids,
        )
        return post
    except Exception as e:
        logger.error(f"Failed to save admin post: {e}")
        return None

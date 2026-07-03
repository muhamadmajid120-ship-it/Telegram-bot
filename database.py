import logging
from datetime import datetime, timedelta, timezone

import httpx

from config import SUPABASE_URL, SUPABASE_HEADERS

logger = logging.getLogger(__name__)

async def _supabase_select(table, columns="*", filters=None, order=None, limit=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={columns}"
    if filters:
        for col, val in filters.items():
            url += f"&{col}=eq.{val}"
    if order:
        url += f"&order={order}"
    if limit:
        url += f"&limit={limit}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=SUPABASE_HEADERS)
        resp.raise_for_status()
        return resp.json()

async def _supabase_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {**SUPABASE_HEADERS, "Prefer": "return=representation"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()

async def _supabase_upsert(table, data, on_conflict: str):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        **SUPABASE_HEADERS,
        "Prefer": "return=representation,resolution=merge-duplicates",
        "on_conflict": on_conflict,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()

async def _supabase_delete(table, filters=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if filters:
        first = True
        for col, val in filters.items():
            url += ("?" if first else "&") + f"{col}=eq.{val}"
            first = False
    async with httpx.AsyncClient() as client:
        resp = await client.delete(url, headers=SUPABASE_HEADERS)
        resp.raise_for_status()
        return resp.json()

# ── Users ──

async def upsert_user(telegram_id: int, first_name: str, username: str | None):
    data = await _supabase_upsert(
        "bot_users",
        {
            "telegram_id": telegram_id,
            "first_name": first_name,
            "username": username,
        },
        on_conflict="telegram_id",
    )
    return data[0] if data else None

async def get_user(telegram_id: int):
    data = await _supabase_select("bot_users", filters={"telegram_id": telegram_id})
    return data[0] if data else None

async def get_all_users():
    return await _supabase_select("bot_users", order="join_date.asc")

async def get_user_count():
    data = await _supabase_select("bot_users", columns="telegram_id")
    return len(data)

# ── Posts ──

async def insert_post(post_id: int, admin_chat_id: int, caption: str | None,
                      content_type: str, file_ids: list | None):
    data = await _supabase_insert("posts", {
        "post_id": post_id,
        "admin_chat_id": admin_chat_id,
        "caption": caption,
        "content_type": content_type,
        "file_ids": file_ids,
    })
    return data[0] if data else None

async def get_all_posts(order="upload_time.desc"):
    return await _supabase_select("posts", order=order)

async def get_recent_posts(hours: int = 48):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    url = (
        f"{SUPABASE_URL}/rest/v1/posts?select=*&"
        f"upload_time=gte.{cutoff}&order=upload_time.desc"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=SUPABASE_HEADERS)
        resp.raise_for_status()
        return resp.json()

async def get_unviewed_posts(user_id: int):
    viewed_url = (
        f"{SUPABASE_URL}/rest/v1/viewed_posts?select=post_id&user_id=eq.{user_id}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(viewed_url, headers=SUPABASE_HEADERS)
        resp.raise_for_status()
        viewed = resp.json()
    viewed_ids = {v["post_id"] for v in viewed}
    all_posts = await _supabase_select("posts", order="upload_time.asc")
    return [p for p in all_posts if p["id"] not in viewed_ids]

async def get_post_count():
    data = await _supabase_select("posts", columns="id")
    return len(data)

async def mark_post_viewed(user_id: int, post_id: str):
    try:
        await _supabase_insert("viewed_posts", {
            "user_id": user_id,
            "post_id": post_id,
        })
    except Exception as e:
        logger.debug(f"mark_post_viewed (may be duplicate): {e}")

# ── Viewed posts ──

async def get_viewed_count():
    data = await _supabase_select("viewed_posts", columns="id")
    return len(data)

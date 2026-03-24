# Cleaned + Premium UI + Auto Manage Panel

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from pyrogram.errors import UserNotParticipant

from info import Config
from bot.database.force_db import force_db


# -----------------------------------------------------------
# UTILITY
# -----------------------------------------------------------

def auto_title(index: int) -> str:
    return f"Channel {index}"

def paginate(items, page, per_page=5):
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], page, total_pages

async def safe_edit(msg, text, kb=None):
    try:
        return await msg.edit_text(text, reply_markup=kb)
    except:
        pass

def get_channel_index(channel_id, all_channels):
    for index, ch in enumerate(all_channels, 1):
        if ch["channel_id"] == channel_id:
            return index
    return None


# -----------------------------------------------------------
# 🔥 PREMIUM UI KEYBOARDS
# -----------------------------------------------------------

def panel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📜 Channels", callback_data="list:1", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("➕ Add", callback_data="add_channel", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("🔄 Status", callback_data="admin_status", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("❌ Close", callback_data="close", style=ButtonStyle.DANGER)
        ]
    ])


def channel_keyboard(ch_id, mode="request"):
    toggle_text = "🔁 Switch → FSUB" if mode == "request" else "🔁 Switch → REQUEST"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(toggle_text, callback_data=f"toggle:{ch_id}", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🔗 Regenerate", callback_data=f"regen:{ch_id}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🗑 Delete", callback_data=f"remove:{ch_id}", style=ButtonStyle.DANGER)
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="list:1", style=ButtonStyle.DEFAULT)
        ]
    ])


def pagination_keyboard(page, total):
    nav = []

    if page > 1:
        nav.append(
            InlineKeyboardButton("⬅ Prev", callback_data=f"list:{page-1}", style=ButtonStyle.DEFAULT)
        )

    nav.append(
        InlineKeyboardButton(f"📄 {page}/{total}", callback_data="noop", style=ButtonStyle.DEFAULT)
    )

    if page < total:
        nav.append(
            InlineKeyboardButton("Next ➡", callback_data=f"list:{page+1}", style=ButtonStyle.DEFAULT)
        )

    return InlineKeyboardMarkup([
        nav,
        [InlineKeyboardButton("⬅ Back", callback_data="fsub_setting", style=ButtonStyle.DEFAULT)]
    ])


# -----------------------------------------------------------
# Invite Link Generator
# -----------------------------------------------------------

async def create_links(client, channel_id):
    normal = None
    req = None

    try:
        normal = (await client.create_chat_invite_link(channel_id, creates_join_request=False)).invite_link
    except:
        pass

    try:
        req = (await client.create_chat_invite_link(channel_id, creates_join_request=True)).invite_link
    except:
        pass

    return normal, req


# -----------------------------------------------------------
# TEXT BUILDER (NO PERMISSIONS)
# -----------------------------------------------------------

def build_manage_text(ch, all_channels):
    ch_id = ch["channel_id"]
    index = get_channel_index(ch_id, all_channels)
    title = auto_title(index or 0)

    mode = ch.get("mode", "request")
    mode_label = "🔒 FSUB" if mode == "fsub" else "📨 Request"

    normal = ch.get("invite_link_normal")
    req = ch.get("invite_link_request")
    active = normal if mode == "fsub" else req

    return (
        f"**⚙ {title}**\n\n"
        f"🆔 `{ch_id}`\n"
        f"Mode: {mode_label}\n"
        f"Active: {active or 'None'}\n\n"
        f"**Links:**\n"
        f"• Normal: {normal or 'None'}\n"
        f"• Request: {req or 'None'}"
    )


# -----------------------------------------------------------
# HANDLERS
# -----------------------------------------------------------

@Client.on_message(filters.command("fsub_setting") & filters.user(Config.ADMINS))
async def panel_entry(client, message):
    await message.reply("**🛠 FSUB Dashboard**", reply_markup=panel_keyboard())


@Client.on_callback_query(filters.regex("^fsub_setting$"))
async def back_panel(client, query):
    await safe_edit(query.message, "**🛠 FSUB Dashboard**", panel_keyboard())


# ---------------- LIST ----------------

@Client.on_callback_query(filters.regex(r"^list:(\d+)$"))
async def list_channels(client, query):
    page = int(query.matches[0].group(1))
    channels = await force_db.get_all_channels()

    if not channels:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel", style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("⬅ Back", callback_data="fsub_setting", style=ButtonStyle.DEFAULT)]
        ])
        return await safe_edit(query.message, "⚠️ No channels added.", kb)

    sliced, page, total = paginate(channels, page)

    text = "**📜 Channels:**\n\n"
    buttons = []

    for index, ch in enumerate(sliced, start=(page - 1) * 5 + 1):
        title = auto_title(index)
        mode = "🔒 FSUB" if ch.get("mode") == "fsub" else "📨 Request"
        ch_id = ch["channel_id"]

        text += f"**{index}. {title}**\n`{ch_id}` • {mode}\n\n"

        buttons.append([
            InlineKeyboardButton(f"⚙ {title}", callback_data=f"manage:{ch_id}", style=ButtonStyle.PRIMARY)
        ])

    kb = InlineKeyboardMarkup(buttons + pagination_keyboard(page, total).inline_keyboard)
    await safe_edit(query.message, text, kb)


# ---------------- MANAGE ----------------

@Client.on_callback_query(filters.regex(r"^manage:(-?\d+)$"))
async def manage_channel(client, query):
    ch_id = int(query.matches[0].group(1))
    ch = await force_db.get_channel(ch_id)

    if not ch:
        return await query.answer("Channel not found!", show_alert=True)

    all_channels = await force_db.get_all_channels()

    await safe_edit(
        query.message,
        build_manage_text(ch, all_channels),
        channel_keyboard(ch_id, ch.get("mode", "request"))
    )


# ---------------- TOGGLE ----------------

@Client.on_callback_query(filters.regex(r"^toggle:(-?\d+)$"))
async def toggle_mode(client, query):
    ch_id = int(query.matches[0].group(1))
    ch = await force_db.get_channel(ch_id)

    new_mode = "request" if ch["mode"] == "fsub" else "fsub"
    await force_db.update_channel_mode(ch_id, new_mode)

    ch = await force_db.get_channel(ch_id)
    all_channels = await force_db.get_all_channels()

    await safe_edit(
        query.message,
        build_manage_text(ch, all_channels),
        channel_keyboard(ch_id, ch.get("mode"))
    )


# ---------------- REGEN ----------------

@Client.on_callback_query(filters.regex(r"^regen:(-?\d+)$"))
async def regenerate_links(client, query):
    ch_id = int(query.matches[0].group(1))

    normal, req = await create_links(client, ch_id)
    await force_db.update_links(ch_id, normal, req)

    ch = await force_db.get_channel(ch_id)
    all_channels = await force_db.get_all_channels()

    await safe_edit(
        query.message,
        build_manage_text(ch, all_channels),
        channel_keyboard(ch_id, ch.get("mode"))
    )


# ---------------- REMOVE ----------------

@Client.on_callback_query(filters.regex(r"^remove:(-?\d+)$"))
async def remove_channel(client, query):
    ch_id = int(query.matches[0].group(1))
    await force_db.delete_channel(ch_id)

    query.data = "list:1"
    return await list_channels(client, query)


# ---------------- ADD (AUTO MANAGE PANEL) ----------------

@Client.on_callback_query(filters.regex("^add_channel$"))
async def add_channel(client, query):
    admin_id = query.from_user.id

    msg = await safe_edit(
        query.message,
        "➕ Send:\n`-10012345 fsub`\n`-10012345 request`\n\n/cancel",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back", callback_data="fsub_setting", style=ButtonStyle.DEFAULT)]
        ])
    )

    try:
        res = await client.listen(chat_id=admin_id, timeout=60)
    except asyncio.TimeoutError:
        return await safe_edit(msg, "⏳ Timeout.")

    if res.text == "/cancel":
        return await safe_edit(msg, "❌ Cancelled.")

    try:
        channel_id = int(res.text.split()[0])
        mode = res.text.split()[1].lower()
    except:
        return await safe_edit(msg, "❌ Invalid format.")

    normal, req = await create_links(client, channel_id)
    await force_db.add_channel_full(channel_id, mode, normal, req)

    # 🔥 AUTO OPEN MANAGE PANEL
    ch = await force_db.get_channel(channel_id)
    all_channels = await force_db.get_all_channels()

    return await safe_edit(
        msg,
        build_manage_text(ch, all_channels),
        channel_keyboard(channel_id, mode)
    )
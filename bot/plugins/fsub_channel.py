# Cleaned & Refactored by @Mak0912 (TG)

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant

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
# CREATE KEYBOARDS MANUALLY
# -----------------------------------------------------------

def panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 List Channels", callback_data="list:1")],
        [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")],
        [InlineKeyboardButton("🔄 Admin Status", callback_data="admin_status")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])


def channel_keyboard(ch_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Toggle Mode", callback_data=f"toggle:{ch_id}")],
        [InlineKeyboardButton("🔗 Regenerate Links", callback_data=f"regen:{ch_id}")],
        [InlineKeyboardButton("🗑 Remove", callback_data=f"remove:{ch_id}")],
        [InlineKeyboardButton("⬅ Back", callback_data="list:1")]
    ])


def pagination_keyboard(page, total):
    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton("⬅ Prev", callback_data=f"list:{page-1}"))

    if page < total:
        buttons.append(InlineKeyboardButton("Next ➡", callback_data=f"list:{page+1}"))

    rows = []
    if buttons:
        rows.append(buttons)

    # Always add back button only
    rows.append([InlineKeyboardButton("⬅ Back", callback_data="fsub_setting")])

    return InlineKeyboardMarkup(rows)



# -----------------------------------------------------------
# Invite Link Generator
# -----------------------------------------------------------

async def create_links(client, channel_id):
    """Generate both normal and join-request links."""
    normal = None
    req = None

    try:
        normal = (await client.create_chat_invite_link(
            channel_id, creates_join_request=False
        )).invite_link
    except:
        pass

    try:
        req = (await client.create_chat_invite_link(
            channel_id, creates_join_request=True
        )).invite_link
    except:
        pass

    return normal, req



# -----------------------------------------------------------
# Permission Helper
# -----------------------------------------------------------

def format_perm(flag, text):
    return f"{'✅' if flag else '❌'} {text}"

async def get_bot_permissions(client, ch_id):
    try:
        member = await client.get_chat_member(ch_id, "me")

        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return f"⚠️ Status: {member.status.name} (Not Admin)"

        priv = member.privileges
        if not priv:
            return "⚠️ No privileges found"

        perms = [
            format_perm(priv.can_invite_users, "Invite Users"),
            format_perm(priv.can_post_messages, "Post Messages"),
            format_perm(priv.can_edit_messages, "Edit Messages"),
            format_perm(priv.can_delete_messages, "Delete Messages"),
            format_perm(priv.can_manage_video_chats, "Manage Video Chats"),
            format_perm(priv.can_change_info, "Change Channel Info"),
            format_perm(priv.can_promote_members, "Promote Members"),
            format_perm(priv.can_restrict_members, "Restrict Members"),
        ]

        return "\n".join(f"• {p}" for p in perms)

    except UserNotParticipant:
        return "❌ Bot not in channel"
    except Exception as e:
        return f"❌ Error: `{e}`"



# -----------------------------------------------------------
# Text builder
# -----------------------------------------------------------

def build_manage_text(ch, all_channels, permissions_text):
    ch_id = ch["channel_id"]
    index = get_channel_index(ch_id, all_channels)
    title = auto_title(index or 0)

    mode = ch.get("mode", "request")
    mode_label = "🔒 FSUB" if mode == "fsub" else "📨 Request"

    normal = ch.get("invite_link_normal")
    req = ch.get("invite_link_request")
    active = normal if mode == "fsub" else req

    return (
        f"**⚙ Manage {title}**\n\n"
        f"**🆔 Channel ID:** `{ch_id}`\n"
        f"**Mode:** {mode_label}\n"
        f"**Active Invite:** {active or 'None'}\n\n"
        f"**Stored Links:**\n"
        f"• Normal: {normal or 'None'}\n"
        f"• Request: {req or 'None'}\n\n"
        f"**Permissions:**\n{permissions_text}"
    )



# -----------------------------------------------------------
# Handlers
# -----------------------------------------------------------

@Client.on_message(filters.command("fsub_setting") & filters.user(Config.ADMINS))
async def panel_entry(client, message):
    await message.reply(
        "**🛠 Force Subscribe Settings**",
        reply_markup=panel_keyboard()
    )


@Client.on_callback_query(filters.regex("^fsub_setting$"))
async def back_panel(client, query):
    await safe_edit(query.message, "**Force Subscribe Settings**", panel_keyboard())



# -------------------- LIST CHANNELS --------------------

@Client.on_callback_query(filters.regex(r"^list:(\d+)$"))
async def list_channels(client, query):
    page = int(query.matches[0].group(1))
    channels = await force_db.get_all_channels()

    if not channels:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")],
            [InlineKeyboardButton("⬅ Back", callback_data="fsub_setting")]
        ])
        return await safe_edit(query.message, "⚠️ No channels added.", kb)

    sliced, page, total = paginate(channels, page)

    text = "**📜 Force Subscribe Channels:**\n\n"
    buttons = []

    for index, ch in enumerate(sliced, start=(page - 1) * 5 + 1):
        title = auto_title(index)
        mode = ch.get("mode", "request")
        mode_label = "🔒 FSUB" if mode == "fsub" else "📨 Request"
        ch_id = ch["channel_id"]

        text += f"**{index}. {title}**\n🆔 `{ch_id}`\nMode: {mode_label}\n\n"
        buttons.append([InlineKeyboardButton(f"⚙ Manage {title}", callback_data=f"manage:{ch_id}")])

    kb = InlineKeyboardMarkup(buttons + pagination_keyboard(page, total).inline_keyboard)
    await safe_edit(query.message, text, kb)



# -------------------- MANAGE --------------------

@Client.on_callback_query(filters.regex(r"^manage:(-?\d+)$"))
async def manage_channel(client, query):
    ch_id = int(query.matches[0].group(1))
    ch = await force_db.get_channel(ch_id)

    if not ch:
        return await query.answer("Channel not found!", show_alert=True)

    perms = await get_bot_permissions(client, ch_id)
    all_channels = await force_db.get_all_channels()

    await safe_edit(
        query.message,
        build_manage_text(ch, all_channels, perms),
        channel_keyboard(ch_id)
    )



# -------------------- TOGGLE --------------------

@Client.on_callback_query(filters.regex(r"^toggle:(-?\d+)$"))
async def toggle_mode(client, query):
    ch_id = int(query.matches[0].group(1))
    ch = await force_db.get_channel(ch_id)

    new_mode = "request" if ch["mode"] == "fsub" else "fsub"
    await force_db.update_channel_mode(ch_id, new_mode)
    await query.answer(f"Mode → {new_mode.upper()}", show_alert=True)

    ch = await force_db.get_channel(ch_id)
    perms = await get_bot_permissions(client, ch_id)
    all_channels = await force_db.get_all_channels()

    await safe_edit(
        query.message,
        build_manage_text(ch, all_channels, perms),
        channel_keyboard(ch_id)
    )



# -------------------- REGENERATE LINKS --------------------

@Client.on_callback_query(filters.regex(r"^regen:(-?\d+)$"))
async def regenerate_links(client, query):
    ch_id = int(query.matches[0].group(1))

    normal, req = await create_links(client, ch_id)
    await force_db.update_links(ch_id, normal, req)

    await query.answer("Links regenerated!")

    ch = await force_db.get_channel(ch_id)
    perms = await get_bot_permissions(client, ch_id)
    all_channels = await force_db.get_all_channels()

    await safe_edit(
        query.message,
        build_manage_text(ch, all_channels, perms),
        channel_keyboard(ch_id)
    )



# -------------------- REMOVE --------------------

@Client.on_callback_query(filters.regex(r"^remove:(-?\d+)$"))
async def remove_channel(client, query):
    ch_id = int(query.matches[0].group(1))
    await force_db.delete_channel(ch_id)
    await query.answer(f"{ch_id} Has Been Removed!", show_alert=True)

    query.data = "list:1"
    return await list_channels(client, query)



# -------------------- ADD CHANNEL --------------------

@Client.on_callback_query(filters.regex("^add_channel$"))
async def add_channel(client, query):
    admin_id = query.from_user.id
    
    if admin_id not in Config.ADMINS:
        return
        
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back", callback_data="fsub_setting")]
    ])

    msg = await safe_edit(
        query.message,
        "➕ **Send Channel ID and Mode**\n"
        "`-10012345 fsub`\n"
        "`-10012345 request`\n\n"
        "/cancel to stop",
        kb
    )

    try:
        # Use listen instead of ask
        res = await client.listen(
            chat_id=admin_id,
            timeout=60
        )
    except asyncio.TimeoutError:
        return await safe_edit(msg, "⏳ Timeout.", kb)

    if res.text and res.text.strip() == "/cancel":
        return await safe_edit(msg, "❌ Cancelled.", kb)

    try:
        channel_id = int(res.text.split()[0])
        mode = res.text.split()[1].lower()
    except:
        return await safe_edit(msg, "❌ Invalid format.", kb)

    if mode not in ("fsub", "request"):
        return await safe_edit(msg, "❌ Mode must be: fsub / request", kb)

    if await force_db.exists(channel_id):
        return await safe_edit(msg, "⚠️ Already exists.", kb)

    try:
        await client.get_chat_member(channel_id, "me")
    except:
        return await safe_edit(msg, "❌ Bot isn't in channel.", kb)

    normal, req = await create_links(client, channel_id)

    await force_db.add_channel_full(channel_id, mode, normal, req)

    active = normal if mode == "fsub" else req

    return await safe_edit(msg, f"✅ Added!\n🆔 `{channel_id}`\nMode: {mode.upper()}\nActive Link: {active}", kb)

# -------------------- ADMIN STATUS --------------------

async def check_single_status(client, index, ch_id):
    title = auto_title(index)
    try:
        member = await client.get_chat_member(ch_id, "me")
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            status = "✅ Admin"
        else:
            status = f"⚠️ {member.status.name}"
    except UserNotParticipant:
        status = "❌ Not in channel"
    except Exception as e:
        status = f"❌ Error: {e}"

    return f"**{title}**\n`{ch_id}` → {status}"


@Client.on_callback_query(filters.regex("^admin_status$"))
async def admin_status(client, query):
    channels = await force_db.get_all_channels()

    if not channels:
        return await safe_edit(query.message, "⚠️ No channels.", panel_keyboard())

    await query.answer("Checking…")

    tasks = [
        check_single_status(client, i, ch["channel_id"])
        for i, ch in enumerate(channels, 1)
    ]

    results = await asyncio.gather(*tasks)

    text = "**🔄 Bot Admin Status:**\n\n" + "\n\n".join(results)

    await safe_edit(query.message, text, panel_keyboard())

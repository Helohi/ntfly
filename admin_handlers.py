import os
from functools import wraps
from typing import Callable, Coroutine, Any

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

import list_db

ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))


# ── decorator ──────────────────────────────────────────────────────────────────

def admin_only(
    func: Callable[[Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]]
) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]]:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("⛔ Access denied.")
            return
        await func(update, context)
    return wrapper


# ── admin commands ─────────────────────────────────────────────────────────────

@admin_only
async def cmd_list_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available events with subscriber count."""
    if not list_db.events:
        await update.message.reply_text("No events configured.")
        return
    lines = [f"📋 *Events ({len(list_db.events)}):*"]
    for e in list_db.events:
        lines.append(
            f"• `{e.id}` — *{e.name}*  |  👥 {len(e.subscriber_telegram_ids)} subscriber(s)"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


@admin_only
async def cmd_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all registered users."""
    if not list_db.users:
        await update.message.reply_text("No users registered yet.")
        return
    lines = [f"👥 *Users ({len(list_db.users)}):*"]
    for u in list_db.users:
        lines.append(f"• ID={u.id}  TG={u.telegram_id}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


@admin_only
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast a message to all registered users. Usage: /broadcast <message>"""
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    text = " ".join(context.args)
    sent = 0
    for user in list_db.users:
        try:
            await context.bot.send_message(user.telegram_id, f"📢 *Broadcast:*\n{text}", parse_mode="Markdown")
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {sent} user(s).")


@admin_only
async def cmd_event_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show subscribers for a specific event. Usage: /event_subs <event_id>"""
    if not context.args:
        await update.message.reply_text("Usage: /event_subs <event_id>")
        return
    event_id = context.args[0]
    for event in list_db.events:
        if event.id == event_id:
            subs = event.subscriber_telegram_ids
            if not subs:
                await update.message.reply_text(f"No subscribers for *{event.name}*.", parse_mode="Markdown")
            else:
                lines = [f"👥 Subscribers for *{event.name}*:"] + [f"• `{tid}`" for tid in subs]
                await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
            return
    await update.message.reply_text(f"❌ Event `{event_id}` not found.", parse_mode="Markdown")


# ── handler factory ────────────────────────────────────────────────────────────

def get_admin_handlers() -> list:
    return [
        CommandHandler("list_events", cmd_list_events),
        CommandHandler("list_users", cmd_list_users),
        CommandHandler("broadcast", cmd_broadcast),
        CommandHandler("event_subs", cmd_event_subscribers),
    ]

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from typing import List

import list_db
from models import User, Event
from keyboards import get_menu_keyboard


# ── helpers ────────────────────────────────────────────────────────────────────

def get_or_create_user(telegram_id: int) -> User:
    for u in list_db.users:
        if u.telegram_id == telegram_id:
            return u
    user = User(id=len(list_db.users) + 1, telegram_id=telegram_id)
    list_db.users.append(user)
    return user


def get_subscribed_events(telegram_id: int) -> List[Event]:
    return [e for e in list_db.events if telegram_id in e.subscriber_telegram_ids]


def get_available_events(telegram_id: int) -> List[Event]:
    return [e for e in list_db.events if telegram_id not in e.subscriber_telegram_ids]


# ── command handlers ────────────────────────────────────────────────────────────

async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_or_create_user(update.effective_user.id)
    has_subs = bool(get_subscribed_events(user.telegram_id))
    await update.message.reply_text(
        "📋 *Main Menu*", parse_mode="Markdown",
        reply_markup=get_menu_keyboard(has_subs),
    )


async def cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /subscribe <event_id>")
        return
    event_id = context.args[0]
    user = get_or_create_user(update.effective_user.id)
    for event in list_db.events:
        if event.id == event_id:
            if user.telegram_id not in event.subscriber_telegram_ids:
                event.subscriber_telegram_ids.append(user.telegram_id)
                await update.message.reply_text(
                    f"✅ Subscribed to *{event.name}*", parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"ℹ️ Already subscribed to *{event.name}*", parse_mode="Markdown"
                )
            return
    await update.message.reply_text(f"❌ Event `{event_id}` not found.", parse_mode="Markdown")


async def cmd_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /unsubscribe <event_id>")
        return
    event_id = context.args[0]
    user = get_or_create_user(update.effective_user.id)
    for event in list_db.events:
        if event.id == event_id:
            if user.telegram_id in event.subscriber_telegram_ids:
                event.subscriber_telegram_ids.remove(user.telegram_id)
                await update.message.reply_text(
                    f"✅ Unsubscribed from *{event.name}*", parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"ℹ️ Not subscribed to *{event.name}*", parse_mode="Markdown"
                )
            return
    await update.message.reply_text(f"❌ Event `{event_id}` not found.", parse_mode="Markdown")


async def cmd_unsubscribe_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_or_create_user(update.effective_user.id)
    count = 0
    for event in list_db.events:
        if user.telegram_id in event.subscriber_telegram_ids:
            event.subscriber_telegram_ids.remove(user.telegram_id)
            count += 1
    msg = (
        f"✅ Unsubscribed from all *{count}* event(s)."
        if count else "ℹ️ You have no active subscriptions."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


def get_command_handlers() -> list:
    return [
        CommandHandler("menu", cmd_menu),
        CommandHandler("subscribe", cmd_subscribe),
        CommandHandler("unsubscribe", cmd_unsubscribe),
        CommandHandler("unsubscribe_all", cmd_unsubscribe_all),
    ]

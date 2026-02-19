from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

import list_db
from keyboards import (
    get_menu_keyboard,
    get_subscribe_keyboard,
    get_unsubscribe_keyboard,
)
from user_interactions import (
    get_available_events,
    get_or_create_user,
    get_subscribed_events,
)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data: str = query.data
    tid: int = update.effective_user.id
    get_or_create_user(tid)

    # ── Main menu ──────────────────────────────────────────────────────────────
    if data == "menu":
        has_subs = bool(get_subscribed_events(tid))
        await query.edit_message_text(
            "📋 *Main Menu*",
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard(has_subs),
        )

    # ── Subscribe flow ─────────────────────────────────────────────────────────
    elif data == "subscribe_start":
        available = get_available_events(tid)
        await query.delete_message()
        if not available:
            await context.bot.send_message(tid, "ℹ️ No new subscriptions available.")
            return
        await context.bot.send_message(
            tid,
            "📋 *Choose a subscription:*",
            parse_mode="Markdown",
            reply_markup=get_subscribe_keyboard(available, 0),
        )

    elif data.startswith("subscribe_page:"):
        page = int(data.split(":")[1])
        available = get_available_events(tid)
        await query.edit_message_text(
            "📋 *Choose a subscription:*",
            parse_mode="Markdown",
            reply_markup=get_subscribe_keyboard(available, page),
        )

    elif data.startswith("do_subscribe:"):
        event_id = data.split(":")[1]
        if event_id.isdigit():
            event_id = int(event_id)
            for event in list_db.events:
                if event.id == event_id:
                    if tid not in event.subscriber_telegram_ids:
                        event.subscriber_telegram_ids.append(tid)
                    await query.edit_message_text(
                        f"✅ Subscribed to *{event.name}*!", parse_mode="Markdown"
                    )
                    return
        await query.edit_message_text("❌ Event not found.")

    # ── Unsubscribe flow ───────────────────────────────────────────────────────
    elif data == "unsubscribe_start":
        subs = get_subscribed_events(tid)
        await query.delete_message()
        if not subs:
            await context.bot.send_message(tid, "ℹ️ You have no active subscriptions.")
            return
        await context.bot.send_message(
            tid,
            "🔕 *Choose a subscription to remove:*",
            parse_mode="Markdown",
            reply_markup=get_unsubscribe_keyboard(subs, 0),
        )

    elif data.startswith("unsubscribe_page:"):
        page = int(data.split(":")[1])
        subs = get_subscribed_events(tid)
        await query.edit_message_text(
            "🔕 *Choose a subscription to remove:*",
            parse_mode="Markdown",
            reply_markup=get_unsubscribe_keyboard(subs, page),
        )

    elif data.startswith("do_unsubscribe:"):
        event_id = data.split(":")[1]
        for event in list_db.events:
            if event.id == event_id:
                if tid in event.subscriber_telegram_ids:
                    event.subscriber_telegram_ids.remove(tid)
                await query.edit_message_text(
                    f"✅ Unsubscribed from *{event.name}*!", parse_mode="Markdown"
                )
                return
        await query.edit_message_text("❌ Event not found.")

    # ── Cancel all ─────────────────────────────────────────────────────────────
    elif data == "cancel_all":
        count = 0
        for event in list_db.events:
            if tid in event.subscriber_telegram_ids:
                event.subscriber_telegram_ids.remove(tid)
                count += 1
        await query.edit_message_text(
            f"✅ Unsubscribed from all *{count}* notification(s).\n\n📋 *Main Menu*",
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard(False),
        )


def get_callback_handlers() -> list:
    return [CallbackQueryHandler(callback_handler)]

import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application, ApplicationBuilder

import list_db
from admin_handlers import get_admin_handlers
from callback_handlers import get_callback_handlers
from di import time_trigger
from models import Event, TimeSlot
from user_interactions import get_command_handlers

load_dotenv()

TOKEN: str = os.environ["BOT_TOKEN"]
ADMIN_ID: int = int(os.environ["ADMIN_ID"])

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── notification callback used by the scheduler ────────────────────────────────


async def notify_subscribers(event: Event, slot: TimeSlot) -> None:
    """Invoked by APSchedulerTimeTrigger when a scheduled time-slot fires."""
    bot = application.bot
    text = f"🔔 *{event.name}*\n🕐 {slot.time}\n📝 {slot.description}"
    for telegram_id in event.subscriber_telegram_ids:
        try:
            await bot.send_message(telegram_id, text, parse_mode="Markdown")
        except Exception as exc:
            logger.warning("Could not notify user %s: %s", telegram_id, exc)


# ── lifecycle hooks ────────────────────────────────────────────────────────────


async def post_init(app: Application) -> None:
    """Start scheduler and load all events once the event-loop is running."""
    from time_trigger import APSchedulerTimeTrigger

    if isinstance(time_trigger, APSchedulerTimeTrigger):
        time_trigger.start()

    await time_trigger.import_triggers(list_db.events, notify_subscribers)
    logger.info("Registered %d event trigger(s).", len(list_db.events))

    try:
        await app.bot.send_message(ADMIN_ID, "✅ Bot is activated 🚀")
    except Exception as exc:
        logger.error("Admin startup notification failed: %s", exc)


async def post_shutdown(app: Application) -> None:
    """Gracefully remove all triggers and notify admin."""
    await time_trigger.remove_all_triggers()
    try:
        await app.bot.send_message(ADMIN_ID, "💥 Bot is crashed / stopped 🛑")
    except Exception as exc:
        logger.error("Admin shutdown notification failed: %s", exc)


# ── application setup ──────────────────────────────────────────────────────────

application: Application = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(post_init)
    .post_shutdown(post_shutdown)
    .build()
)

for handler in get_command_handlers():
    application.add_handler(handler)

for handler in get_admin_handlers():
    application.add_handler(handler)

for handler in get_callback_handlers():
    application.add_handler(handler)


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Starting bot polling…")
    application.run_polling(drop_pending_updates=True)

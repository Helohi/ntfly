from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from models import Event

PAGE_SIZE = 5


def get_menu_keyboard(has_subscriptions: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📋 Subscribe", callback_data="subscribe_start")],
        [InlineKeyboardButton("🔕 Unsubscribe", callback_data="unsubscribe_start")],
    ]
    if has_subscriptions:
        buttons.append(
            [InlineKeyboardButton("❌ Cancel All Notifications", callback_data="cancel_all")]
        )
    return InlineKeyboardMarkup(buttons)


def get_subscribe_keyboard(
    events: List[Event],
    page: int,
) -> InlineKeyboardMarkup:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_events = events[start:end]

    buttons: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(e.name, callback_data=f"do_subscribe:{e.id}")]
        for e in page_events
    ]

    nav: List[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"subscribe_page:{page - 1}"))
    if end < len(events):
        nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"subscribe_page:{page + 1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)


def get_unsubscribe_keyboard(
    events: List[Event],
    page: int,
) -> InlineKeyboardMarkup:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_events = events[start:end]

    buttons: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(e.name, callback_data=f"do_unsubscribe:{e.id}")]
        for e in page_events
    ]

    nav: List[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"unsubscribe_page:{page - 1}"))
    if end < len(events):
        nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"unsubscribe_page:{page + 1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_IDS


def _main_kb(user_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📅  View Reminders", callback_data="view:reminders")],
        [InlineKeyboardButton("📝  New Log Entry",  callback_data="log:start")],
        [InlineKeyboardButton("🍳  Browse Recipes", callback_data="recipe:categories")],
    ]
    if user_id in ADMIN_IDS:
        rows.append([InlineKeyboardButton("⚙️  Admin Panel", callback_data="admin:menu")])
    return InlineKeyboardMarkup(rows)


def _back_kb(cb: str = "main:menu", label: str = "« Back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=cb)]])


def _admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅  Reminders",         callback_data="admin:rem:menu")],
        [InlineKeyboardButton("📝  Log Categories",    callback_data="admin:lcat:menu")],
        [InlineKeyboardButton("🍳  Recipe Categories", callback_data="admin:rcat:menu")],
        [InlineKeyboardButton("📖  Add Recipe",        callback_data="admin:rec:add")],
        [InlineKeyboardButton("« Main Menu",           callback_data="main:menu")],
    ])

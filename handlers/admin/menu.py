from telegram import Update
from telegram.ext import ContextTypes

from handlers.guards import _require_admin
from handlers.keyboards import _admin_kb


async def cb_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return
    await query.edit_message_text(
        "⚙️ *Admin Panel*\n\nSelect a section:",
        reply_markup=_admin_kb(),
        parse_mode="Markdown",
    )

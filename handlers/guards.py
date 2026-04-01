from telegram import Update
from config import ADMIN_IDS


async def _require_admin(update: Update) -> bool:
    """Return True if caller is admin; otherwise respond and return False."""
    if update.effective_user.id in ADMIN_IDS:
        return True
    if update.callback_query:
        await update.callback_query.answer("⛔ Admin access required.", show_alert=True)
    else:
        await update.effective_message.reply_text("⛔ You don't have admin access.")
    return False

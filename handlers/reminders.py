from telegram import Update
from telegram.ext import ContextTypes

import database as db
from handlers.keyboards import _back_kb


async def cb_view_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    reminders = db.get_reminders(active_only=True)
    if not reminders:
        text = "📅 *Reminders*\n\nNo active reminders are configured yet."
    else:
        parts = ["📅 *Active Reminders*\n"]
        for r in reminders:
            parts.append(
                f"*#{r['id']}*  ⏰ `{r['cron_expression']}`\n"
                f"  📢 Channel: `{r['channel_id']}`\n"
                f"  💬 {r['message']}"
            )
        text = "\n\n".join(parts)

    await query.edit_message_text(text, reply_markup=_back_kb(), parse_mode="Markdown")

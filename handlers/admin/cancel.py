from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from handlers.keyboards import _admin_kb


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "✖ Cancelled.", reply_markup=_admin_kb()
        )
    else:
        await update.message.reply_text("✖ Cancelled.", reply_markup=_admin_kb())
    return ConversationHandler.END

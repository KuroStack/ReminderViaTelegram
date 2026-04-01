from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import _main_kb


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hey *{name}*! I'm your all-in-one assistant bot.\n\nWhat would you like to do?",
        reply_markup=_main_kb(uid),
        parse_mode="Markdown",
    )


async def cb_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    name = update.effective_user.first_name
    await query.edit_message_text(
        f"👋 Hey *{name}*! What would you like to do?",
        reply_markup=_main_kb(uid),
        parse_mode="Markdown",
    )

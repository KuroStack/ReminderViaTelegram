from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from handlers.guards import _require_admin
from handlers.keyboards import _admin_kb

# Conversation state (range 20-29)
ALCAT_NAME = 20


async def cb_admin_lcat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return

    cats = db.get_log_categories()
    if cats:
        body = "\n".join(f"  • {c['name']}" for c in cats)
        text = f"📝 *Log Categories*\n\n{body}"
    else:
        text = "📝 *Log Categories*\n\nNo categories yet."

    kb = [
        [InlineKeyboardButton("➕  Add Category", callback_data="admin:lcat:add")],
        [InlineKeyboardButton("« Admin Panel",    callback_data="admin:menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def cb_admin_lcat_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return ConversationHandler.END

    await query.edit_message_text(
        "📝 *Add Log Category*\n\nEnter the category name:\n\n_/cancel to abort_",
        parse_mode="Markdown",
    )
    return ALCAT_NAME


async def msg_alcat_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    try:
        db.add_log_category(name)
        await update.message.reply_text(
            f"✅ Log category *{name}* created!",
            reply_markup=_admin_kb(),
            parse_mode="Markdown",
        )
    except Exception as exc:
        await update.message.reply_text(
            f"❌ Failed: `{exc}`\n\nThis name may already exist.",
            reply_markup=_admin_kb(),
            parse_mode="Markdown",
        )
    return ConversationHandler.END

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from handlers.guards import _require_admin
from handlers.keyboards import _admin_kb

# Conversation state (range 30-39)
ARCAT_NAME = 30


async def cb_admin_rcat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return

    cats = db.get_recipe_categories()
    if cats:
        body = "\n".join(f"  • {c['name']}" for c in cats)
        text = f"🍳 *Recipe Categories*\n\n{body}"
    else:
        text = "🍳 *Recipe Categories*\n\nNo categories yet."

    kb = [
        [InlineKeyboardButton("➕  Add Category", callback_data="admin:rcat:add")],
        [InlineKeyboardButton("« Admin Panel",    callback_data="admin:menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def cb_admin_rcat_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return ConversationHandler.END

    await query.edit_message_text(
        "🍳 *Add Recipe Category*\n\nEnter the category name:\n\n_/cancel to abort_",
        parse_mode="Markdown",
    )
    return ARCAT_NAME


async def msg_arcat_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    try:
        db.add_recipe_category(name)
        await update.message.reply_text(
            f"✅ Recipe category *{name}* created!",
            reply_markup=_admin_kb(),
            parse_mode="Markdown",
        )
    except Exception as exc:
        await update.message.reply_text(
            f"❌ Failed: `{exc}`",
            reply_markup=_admin_kb(),
            parse_mode="Markdown",
        )
    return ConversationHandler.END

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from handlers.keyboards import _back_kb, _main_kb

# Conversation states (range 0-9)
LOG_CAT, LOG_SUBJECT, LOG_MESSAGE = range(3)


async def cb_log_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    cats = db.get_log_categories()
    if not cats:
        await query.edit_message_text(
            "📝 No log categories exist yet.\nAsk an admin to add some first!",
            reply_markup=_back_kb(),
        )
        return ConversationHandler.END

    kb = [[InlineKeyboardButton(c["name"], callback_data=f"log:cat:{c['id']}")] for c in cats]
    kb.append([InlineKeyboardButton("✖ Cancel", callback_data="log:cancel")])
    await query.edit_message_text(
        "📝 *New Log Entry*\n\n*Step 1 of 3* — Choose a category:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )
    return LOG_CAT


async def cb_log_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    cat_id = int(query.data.split(":")[2])
    context.user_data["log_cat_id"] = cat_id

    cats = db.get_log_categories()
    cat_name = next((c["name"] for c in cats if c["id"] == cat_id), "?")
    context.user_data["log_cat_name"] = cat_name

    await query.edit_message_text(
        f"📝 *New Log Entry*  —  {cat_name}\n\n"
        "*Step 2 of 3* — Type your *subject* (one line):\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return LOG_SUBJECT


async def msg_log_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["log_subject"] = update.message.text.strip()
    cat_name = context.user_data.get("log_cat_name", "")
    await update.message.reply_text(
        f"📝 *New Log Entry*  —  {cat_name}\n\n"
        "*Step 3 of 3* — Type your *message / details*:\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return LOG_MESSAGE


async def msg_log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    cat_id = context.user_data["log_cat_id"]
    cat_name = context.user_data["log_cat_name"]
    subject = context.user_data["log_subject"]
    message = update.message.text.strip()

    db.add_log(cat_id, subject, message, uid)
    context.user_data.clear()

    await update.message.reply_text(
        f"✅ *Log saved!*\n\n"
        f"📂 *Category:* {cat_name}\n"
        f"📌 *Subject:* {subject}\n"
        f"💬 *Message:* {message}",
        reply_markup=_main_kb(uid),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def log_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    uid = update.effective_user.id
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "✖ Log entry cancelled.", reply_markup=_main_kb(uid)
        )
    else:
        await update.message.reply_text("✖ Log entry cancelled.", reply_markup=_main_kb(uid))
    return ConversationHandler.END

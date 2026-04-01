from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from handlers.guards import _require_admin
from handlers.keyboards import _admin_kb, _back_kb

# Conversation states (range 40-49)
AREC_CAT, AREC_NAME, AREC_CONT = range(40, 43)


async def cb_admin_rec_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return ConversationHandler.END

    cats = db.get_recipe_categories()
    if not cats:
        await query.edit_message_text(
            "❌ Create at least one *recipe category* first!",
            reply_markup=_back_kb("admin:menu"),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    kb = [[InlineKeyboardButton(c["name"], callback_data=f"admin:rec:cat:{c['id']}")] for c in cats]
    kb.append([InlineKeyboardButton("✖ Cancel", callback_data="admin:menu")])
    await query.edit_message_text(
        "📖 *Add New Recipe*\n\n*Step 1 of 3* — Choose a category:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )
    return AREC_CAT


async def cb_admin_rec_cat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    cat_id = int(query.data.split(":")[3])
    cat = db.get_recipe_category(cat_id)
    context.user_data["rec_cat_id"] = cat_id
    context.user_data["rec_cat_name"] = cat["name"] if cat else "?"

    await query.edit_message_text(
        f"📖 *Add New Recipe*  —  {context.user_data['rec_cat_name']}\n\n"
        "*Step 2 of 3* — Enter the *recipe name*:\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return AREC_NAME


async def msg_arec_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["rec_name"] = update.message.text.strip()
    cat_name = context.user_data.get("rec_cat_name", "")
    await update.message.reply_text(
        f"📖 *Add New Recipe*  —  {cat_name}\n\n"
        "*Step 3 of 3* — Enter the *full recipe content*:\n"
        "(ingredients, steps, notes — anything you like, multi-line OK)\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return AREC_CONT


async def msg_arec_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cat_id = context.user_data.pop("rec_cat_id", None)
    name = context.user_data.pop("rec_name", "")
    content = update.message.text.strip()
    context.user_data.clear()

    try:
        db.add_recipe(cat_id, name, content)
        await update.message.reply_text(
            f"✅ Recipe *{name}* added successfully!",
            reply_markup=_admin_kb(),
            parse_mode="Markdown",
        )
    except Exception as exc:
        await update.message.reply_text(
            f"❌ Failed to save recipe: `{exc}`",
            reply_markup=_admin_kb(),
            parse_mode="Markdown",
        )
    return ConversationHandler.END

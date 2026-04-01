from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import database as db
from handlers.keyboards import _back_kb


async def cb_recipe_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    cats = db.get_recipe_categories()
    if not cats:
        await query.edit_message_text(
            "🍳 No recipe categories yet. Ask an admin to add some!",
            reply_markup=_back_kb(),
        )
        return

    kb = [[InlineKeyboardButton(f"🗂  {c['name']}", callback_data=f"recipe:list:{c['id']}")] for c in cats]
    kb.append([InlineKeyboardButton("« Back", callback_data="main:menu")])
    await query.edit_message_text(
        "🍳 *Recipes*\n\nChoose a category:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def cb_recipe_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    cat_id = int(query.data.split(":")[2])
    cat = db.get_recipe_category(cat_id)
    recipes = db.get_recipes_by_category(cat_id)

    cat_name = cat["name"] if cat else "Unknown"
    if not recipes:
        await query.edit_message_text(
            f"🗂 *{cat_name}*\n\nNo recipes here yet.",
            reply_markup=_back_kb("recipe:categories"),
            parse_mode="Markdown",
        )
        return

    kb = [[InlineKeyboardButton(f"🍽  {r['name']}", callback_data=f"recipe:view:{r['id']}")] for r in recipes]
    kb.append([InlineKeyboardButton("« Categories", callback_data="recipe:categories")])
    await query.edit_message_text(
        f"🗂 *{cat_name}*  ({len(recipes)} recipe{'s' if len(recipes) != 1 else ''})\n\nPick a recipe:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def cb_recipe_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    recipe_id = int(query.data.split(":")[2])
    recipe = db.get_recipe(recipe_id)
    if not recipe:
        await query.edit_message_text("❌ Recipe not found.", reply_markup=_back_kb("recipe:categories"))
        return

    text = (
        f"🍽 *{recipe['name']}*\n"
        f"_{recipe['category_name']}_\n"
        f"{'─' * 28}\n\n"
        f"{recipe['content']}"
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("« Back to list", callback_data=f"recipe:list:{recipe['category_id']}")
    ]])
    if len(text) > 4000:
        text = text[:3997] + "…"
    await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import database as db
import scheduler as sched
from handlers.guards import _require_admin
from handlers.keyboards import _admin_kb

# Conversation states (range 10-19)
AREM_MSG, AREM_CRON, AREM_CHAN = range(10, 13)


async def _render_rem_menu(query, *, refresh: bool = False) -> None:
    reminders = db.get_reminders(active_only=True)

    if reminders:
        parts = ["📅 *Reminders Manager*\n"]
        for r in reminders:
            parts.append(
                f"*#{r['id']}*  `{r['cron_expression']}`\n"
                f"  📢 `{r['channel_id']}`\n"
                f"  💬 {r['message']}"
            )
        text = "\n\n".join(parts)
    else:
        text = "📅 *Reminders Manager*\n\nNo active reminders."

    kb: list[list] = [[InlineKeyboardButton("➕  Add Reminder", callback_data="admin:rem:add")]]
    for r in reminders:
        short = r["message"][:28] + "…" if len(r["message"]) > 28 else r["message"]
        kb.append([InlineKeyboardButton(f"🗑  #{r['id']}: {short}", callback_data=f"admin:rem:del:{r['id']}")])
    kb.append([InlineKeyboardButton("« Admin Panel", callback_data="admin:menu")])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def cb_admin_rem_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return
    await _render_rem_menu(query)


async def cb_admin_rem_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not await _require_admin(update):
        await query.answer()
        return

    reminder_id = int(query.data.split(":")[3])
    db.delete_reminder(reminder_id)
    sched.remove_scheduled_reminder(reminder_id)
    await query.answer(f"✅ Reminder #{reminder_id} deleted!", show_alert=False)
    await _render_rem_menu(query)


async def cb_admin_rem_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if not await _require_admin(update):
        return ConversationHandler.END

    await query.edit_message_text(
        "📅 *Add New Reminder*\n\n"
        "*Step 1 of 3* — Enter the reminder *message text*:\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return AREM_MSG


async def msg_arem_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["arem_msg"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 *Add New Reminder*\n\n"
        "*Step 2 of 3* — Enter the *cron schedule*:\n"
        "Format: `minute  hour  day  month  weekday`\n\n"
        "Examples:\n"
        "  `0 9 * * 1`      → Every Monday 09:00 UTC\n"
        "  `30 8 * * *`     → Daily at 08:30 UTC\n"
        "  `0 12 1 * *`     → 1st of month at noon UTC\n"
        "  `*/30 * * * *`   → Every 30 minutes\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return AREM_CRON


async def msg_arem_cron(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cron = update.message.text.strip()
    if len(cron.split()) != 5:
        await update.message.reply_text(
            "❌ Invalid — must be exactly *5 fields* separated by spaces.\n"
            "Try again or /cancel:",
            parse_mode="Markdown",
        )
        return AREM_CRON

    context.user_data["arem_cron"] = cron
    await update.message.reply_text(
        "📅 *Add New Reminder*\n\n"
        "*Step 3 of 3* — Enter the *channel/chat ID* to post to:\n\n"
        "How to find it:\n"
        "  • Groups/channels: forward a message to @userinfobot\n"
        "  • Your own DMs: your Telegram user ID\n"
        "  • Example: `-1001234567890`\n\n"
        "_The bot must be a member (and admin for channels)._\n\n"
        "_/cancel to abort_",
        parse_mode="Markdown",
    )
    return AREM_CHAN


async def msg_arem_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    channel_id = update.message.text.strip()
    msg = context.user_data.pop("arem_msg", "")
    cron = context.user_data.pop("arem_cron", "")

    rid = db.add_reminder(msg, cron, channel_id)
    reminder = {"id": rid, "message": msg, "cron_expression": cron, "channel_id": channel_id}

    try:
        sched.schedule_reminder(context.bot, reminder)
        note = "✅ Reminder saved and *scheduled*!"
    except Exception as exc:
        note = f"✅ Saved to DB, but scheduling failed:\n`{exc}`"

    await update.message.reply_text(
        f"{note}\n\n"
        f"⏰ Cron:    `{cron}`\n"
        f"📢 Channel: `{channel_id}`\n"
        f"💬 Message: {msg}",
        reply_markup=_admin_kb(),
        parse_mode="Markdown",
    )
    return ConversationHandler.END

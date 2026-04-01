from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

import scheduler as sched
from config import BOT_TOKEN

from handlers.menu import cmd_start, cb_main_menu
from handlers.reminders import cb_view_reminders
from handlers.recipes import cb_recipe_categories, cb_recipe_list, cb_recipe_view
from handlers.log_entry import (
    LOG_CAT, LOG_SUBJECT, LOG_MESSAGE,
    cb_log_start, cb_log_category, msg_log_subject, msg_log_message, log_cancel,
)
from handlers.admin.menu import cb_admin_menu
from handlers.admin.reminders import (
    AREM_MSG, AREM_CRON, AREM_CHAN,
    cb_admin_rem_menu, cb_admin_rem_delete,
    cb_admin_rem_add_start, msg_arem_message, msg_arem_cron, msg_arem_channel,
)
from handlers.admin.log_categories import (
    ALCAT_NAME,
    cb_admin_lcat_menu, cb_admin_lcat_add_start, msg_alcat_name,
)
from handlers.admin.recipe_categories import (
    ARCAT_NAME,
    cb_admin_rcat_menu, cb_admin_rcat_add_start, msg_arcat_name,
)
from handlers.admin.recipes import (
    AREC_CAT, AREC_NAME, AREC_CONT,
    cb_admin_rec_add_start, cb_admin_rec_cat, msg_arec_name, msg_arec_content,
)
from handlers.admin.cancel import admin_cancel

_ALL_STATES = [
    LOG_CAT, LOG_SUBJECT, LOG_MESSAGE,
    AREM_MSG, AREM_CRON, AREM_CHAN,
    ALCAT_NAME,
    ARCAT_NAME,
    AREC_CAT, AREC_NAME, AREC_CONT,
]
assert len(_ALL_STATES) == len(set(_ALL_STATES)), \
    "Conversation state integer collision detected!"


def _build_app() -> Application:
    async def _post_init(app: Application) -> None:
        sched.setup_scheduler(app.bot)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )

    # Conversation: Log Entry
    log_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_log_start, pattern="^log:start$")],
        states={
            LOG_CAT: [
                CallbackQueryHandler(cb_log_category, pattern=r"^log:cat:\d+$"),
                CallbackQueryHandler(log_cancel,      pattern="^log:cancel$"),
            ],
            LOG_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_log_subject)],
            LOG_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_log_message)],
        },
        fallbacks=[
            CommandHandler("cancel", log_cancel),
            CallbackQueryHandler(log_cancel, pattern="^(main:menu|log:cancel)$"),
        ],
        per_message=False,
    )

    # Conversation: Admin › Add Reminder
    arem_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_admin_rem_add_start, pattern="^admin:rem:add$")],
        states={
            AREM_MSG:  [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_arem_message)],
            AREM_CRON: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_arem_cron)],
            AREM_CHAN:  [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_arem_channel)],
        },
        fallbacks=[
            CommandHandler("cancel", admin_cancel),
            CallbackQueryHandler(admin_cancel, pattern="^(admin:menu|main:menu)$"),
        ],
        per_message=False,
    )

    # Conversation: Admin › Add Log Category
    alcat_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_admin_lcat_add_start, pattern="^admin:lcat:add$")],
        states={
            ALCAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_alcat_name)],
        },
        fallbacks=[
            CommandHandler("cancel", admin_cancel),
            CallbackQueryHandler(admin_cancel, pattern="^(admin:menu|main:menu)$"),
        ],
        per_message=False,
    )

    # Conversation: Admin › Add Recipe Category
    arcat_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_admin_rcat_add_start, pattern="^admin:rcat:add$")],
        states={
            ARCAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_arcat_name)],
        },
        fallbacks=[
            CommandHandler("cancel", admin_cancel),
            CallbackQueryHandler(admin_cancel, pattern="^(admin:menu|main:menu)$"),
        ],
        per_message=False,
    )

    # Conversation: Admin › Add Recipe
    arec_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_admin_rec_add_start, pattern="^admin:rec:add$")],
        states={
            AREC_CAT:  [CallbackQueryHandler(cb_admin_rec_cat, pattern=r"^admin:rec:cat:\d+$")],
            AREC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_arec_name)],
            AREC_CONT: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_arec_content)],
        },
        fallbacks=[
            CommandHandler("cancel", admin_cancel),
            CallbackQueryHandler(admin_cancel, pattern="^(admin:menu|main:menu)$"),
        ],
        per_message=False,
    )

    # Conversations first (take priority over plain CallbackQueryHandlers)
    app.add_handler(log_conv)
    app.add_handler(arem_conv)
    app.add_handler(alcat_conv)
    app.add_handler(arcat_conv)
    app.add_handler(arec_conv)

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))

    # Plain callbacks
    app.add_handler(CallbackQueryHandler(cb_main_menu,          pattern="^main:menu$"))
    app.add_handler(CallbackQueryHandler(cb_view_reminders,     pattern="^view:reminders$"))
    app.add_handler(CallbackQueryHandler(cb_recipe_categories,  pattern="^recipe:categories$"))
    app.add_handler(CallbackQueryHandler(cb_recipe_list,        pattern=r"^recipe:list:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_recipe_view,        pattern=r"^recipe:view:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_menu,         pattern="^admin:menu$"))
    app.add_handler(CallbackQueryHandler(cb_admin_rem_menu,     pattern="^admin:rem:menu$"))
    app.add_handler(CallbackQueryHandler(cb_admin_rem_delete,   pattern=r"^admin:rem:del:\d+$"))
    app.add_handler(CallbackQueryHandler(cb_admin_lcat_menu,    pattern="^admin:lcat:menu$"))
    app.add_handler(CallbackQueryHandler(cb_admin_rcat_menu,    pattern="^admin:rcat:menu$"))

    return app

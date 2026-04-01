#!/usr/bin/env python3
import logging

from telegram.ext import Update

import database as db
from config import DROP_PENDING_UPDATES, LOG_LEVEL
from handlers import _build_app

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=LOG_LEVEL,
)
logger = logging.getLogger(__name__)


def main() -> None:
    db.init_db()
    app = _build_app()
    logger.info("🤖 Bot is starting — polling for updates …")
    app.run_polling(drop_pending_updates=DROP_PENDING_UPDATES, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

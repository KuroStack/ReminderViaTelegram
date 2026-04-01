"""
scheduler.py — APScheduler-based cron reminder engine.
Loads all active reminders on startup and schedules them.
New reminders can be hot-added via schedule_reminder().
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import database as db
from config import SCHEDULER_TIMEZONE

logger = logging.getLogger(__name__)

# Single shared scheduler instance
_scheduler = AsyncIOScheduler(timezone=SCHEDULER_TIMEZONE)


# ─── Job function ─────────────────────────────────────────────────────────────

async def _fire_reminder(bot, channel_id: str, message: str) -> None:
    """Coroutine executed by APScheduler when a reminder fires."""
    try:
        await bot.send_message(chat_id=channel_id, text=f"🔔 *Reminder*\n\n{message}", parse_mode="Markdown")
        logger.info("Reminder sent to %s: %s", channel_id, message[:40])
    except Exception as exc:
        logger.error("Failed to send reminder to %s: %s", channel_id, exc)


# ─── Public API ───────────────────────────────────────────────────────────────

def schedule_reminder(bot, reminder: dict) -> None:
    """Add (or replace) a scheduled job for the given reminder dict."""
    parts = reminder["cron_expression"].split()
    if len(parts) != 5:
        raise ValueError(f"Cron must have 5 fields, got: '{reminder['cron_expression']}'")

    minute, hour, day, month, day_of_week = parts
    trigger = CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        timezone=SCHEDULER_TIMEZONE,
    )

    _scheduler.add_job(
        _fire_reminder,
        trigger=trigger,
        kwargs={"bot": bot, "channel_id": reminder["channel_id"], "message": reminder["message"]},
        id=f"reminder_{reminder['id']}",
        replace_existing=True,
        misfire_grace_time=120,
        coalesce=True,
    )
    logger.info(
        "Scheduled reminder #%s — cron=%s  channel=%s",
        reminder["id"], reminder["cron_expression"], reminder["channel_id"],
    )


def remove_scheduled_reminder(reminder_id: int) -> None:
    """Remove the APScheduler job for a deleted reminder."""
    job_id = f"reminder_{reminder_id}"
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
        logger.info("Removed scheduled reminder #%s", reminder_id)


def setup_scheduler(bot) -> None:
    """
    Called once at bot startup.
    Loads all active reminders from DB and schedules them, then starts the scheduler.
    """
    reminders = db.get_reminders(active_only=True)
    loaded = 0
    for reminder in reminders:
        try:
            schedule_reminder(bot, reminder)
            loaded += 1
        except Exception as exc:
            logger.error("Could not schedule reminder #%s: %s", reminder["id"], exc)

    if not _scheduler.running:
        _scheduler.start()

    logger.info("Scheduler started — %d/%d reminder(s) loaded", loaded, len(reminders))

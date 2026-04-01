# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires .env file with BOT_TOKEN, ADMIN_IDS, DB_PATH)
python bot.py

# Run with Docker
docker-compose up --build

# Run detached
docker-compose up -d
```

## Environment Setup

Copy `.env.example` to `.env` and fill in:
- `BOT_TOKEN` — from Telegram's BotFather
- `ADMIN_IDS` — comma-separated Telegram user IDs (e.g., `123456,789012`)
- `DB_PATH` — SQLite file path (defaults to `data/bot.db`)

## Architecture

**`bot.py`** — Thin entry point: initialises DB, builds app, starts polling.

**`config.py`** — Loads `.env` (via `load_dotenv`) and exports `BOT_TOKEN` and `ADMIN_IDS`. All other modules import from here; `load_dotenv` is called only once.

**`database.py`** — SQLite CRUD with WAL mode and foreign keys. Five tables: `reminders`, `log_categories`, `logs`, `recipe_categories`, `recipes`. Each function opens and closes its own connection. Reminders use soft deletes (`active=0`).

**`scheduler.py`** — APScheduler `AsyncIOScheduler` (UTC). `setup_scheduler()` loads all active reminders from DB on startup. `schedule_reminder()` adds/replaces jobs at runtime without restart. Cron expressions are 5-field (minute, hour, day, month, day_of_week).

**`handlers/`** — All Telegram handler logic:

| File | Contents |
|---|---|
| `__init__.py` | `_build_app()` — app factory, all `ConversationHandler` wiring, handler registration |
| `keyboards.py` | `_main_kb`, `_back_kb`, `_admin_kb` shared UI helpers |
| `guards.py` | `_require_admin()` permission check |
| `menu.py` | `/start`, main menu callback |
| `reminders.py` | User-facing reminder view |
| `recipes.py` | Recipe browsing (categories → list → view) |
| `log_entry.py` | Log entry conversation (states 0–9) |
| `admin/menu.py` | Admin panel menu |
| `admin/reminders.py` | Reminder manager + add-reminder conversation (states 10–19) |
| `admin/log_categories.py` | Log category manager + add conversation (state 20) |
| `admin/recipe_categories.py` | Recipe category manager + add conversation (state 30) |
| `admin/recipes.py` | Add recipe conversation (states 40–42) |
| `admin/cancel.py` | Shared `admin_cancel` fallback for all admin conversations |

Conversation state integers are partitioned by range (0-9, 10-19, 20-29, 30-39, 40-49) and asserted non-overlapping at import time in `handlers/__init__.py`.

## Callback Data Convention

Inline keyboard callbacks follow `module:action:param` format (e.g., `recipe:view:123`, `admin:rem:del:5`). Regex patterns in `handlers/__init__.py` match groups of related callbacks. Handler registration order matters: conversations are added before plain `CallbackQueryHandler`s.

## Data Persistence (Docker)

The `docker-compose.yml` mounts a `./data` volume at `/data` in the container. `DB_PATH` is set to `/data/bot.db` so the SQLite file survives container restarts.

# 🤖 Telegram Multi-Purpose Bot

A single Telegram bot with three core modules: **Reminders**, **Logging**, and **Recipes** — all managed through an inline keyboard UI with full admin controls.

---

## ✨ Features

### User Features
| Module | What it does |
|---|---|
| 📅 **Reminders** | View all active cron-scheduled reminders |
| 📝 **Log Entry** | Create categorised log entries (subject + message) |
| 🍳 **Recipes** | Browse a recipe library by category |

### Admin Features (restricted by Telegram user ID)
| Action | Description |
|---|---|
| ➕ Add Reminder | Set a message, cron schedule, and target channel |
| 🗑 Delete Reminder | Instantly removes from DB and live scheduler |
| 📝 Add Log Category | Create new categories for log entries |
| 🍳 Add Recipe Category | Create new categories for recipes |
| 📖 Add Recipe | Write a recipe into any existing category |

---

## 🚀 Quick Start

### 1 — Create your bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** you receive

### 2 — Find your Telegram user ID

Message [@userinfobot](https://t.me/userinfobot) — it replies with your numeric user ID.

### 3 — Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789          # your user ID (comma-separate for multiple admins)
DB_PATH=data/bot.db

# Optional
SCHEDULER_TIMEZONE=UTC       # any IANA timezone, e.g. America/New_York
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
DROP_PENDING_UPDATES=true    # discard updates received while bot was offline
```

### 4a — Run with Docker (recommended)

```bash
docker compose up -d
```

That's it. The bot runs, restarts on crash, and persists data in a Docker volume.

```bash
# View logs
docker compose logs -f

# Stop
docker compose down
```

### 4b — Run locally (Python 3.11+)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

---

## 📅 Cron Expression Guide

Reminders use standard 5-field cron syntax. Times are interpreted in the timezone set by `SCHEDULER_TIMEZONE` (default: UTC):

```
┌─── minute (0-59)
│  ┌─── hour (0-23)
│  │  ┌─── day of month (1-31)
│  │  │  ┌─── month (1-12)
│  │  │  │  ┌─── day of week (0=Sun … 6=Sat, or mon/tue/…)
│  │  │  │  │
*  *  *  *  *
```

| Expression | Meaning |
|---|---|
| `0 9 * * 1` | Every Monday at 09:00 |
| `30 8 * * *` | Every day at 08:30 |
| `0 12 1 * *` | 1st of every month at noon |
| `*/15 * * * *` | Every 15 minutes |
| `0 18 * * 5` | Every Friday at 18:00 |

---

## 📢 Adding the Bot to a Channel/Group

For the bot to **post reminders** to a channel or group:

1. Add the bot as a **member** of the group
2. For channels, make it an **administrator** with "Post Messages" permission
3. Get the **chat ID** — forward any message from that chat to [@userinfobot](https://t.me/userinfobot)
4. Use that ID (e.g. `-1001234567890`) when creating a reminder

---

## 🗂 Project Structure

```
.
├── bot.py              # Entry point
├── config.py           # All environment variable configuration
├── database.py         # SQLite persistence layer
├── scheduler.py        # APScheduler cron reminder engine
├── handlers/
│   ├── __init__.py     # App factory & handler registration
│   ├── keyboards.py    # Shared inline keyboard helpers
│   ├── guards.py       # Admin permission check
│   ├── menu.py         # /start and main menu
│   ├── reminders.py    # User reminder view
│   ├── recipes.py      # Recipe browsing
│   ├── log_entry.py    # Log entry conversation
│   └── admin/          # Admin-only handlers
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🛡 Notes

- All data is stored in a SQLite file (default: `data/bot.db`)
- Deleted reminders are soft-deleted (marked inactive, not physically removed)
- Bot conversation state is kept in memory — restarting the bot will end any active conversations
- Recipe content supports plain text with newlines (Markdown formatting is rendered)

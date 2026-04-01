# ReminderViaTelegram

Laravel-based Telegram reminder bot. Uses SQLite for storage and the `irazasyed/telegram-bot-sdk` package.

## Architecture

- `app/Telegram/` — bot logic: `BotHandler.php`, `ConversationManager.php`, `Guards.php`, `Keyboards.php`, `Handlers/`
- `routes/api.php` — webhook endpoint
- Queue driver: database (reminders dispatched as jobs)
- Cache/session: database

## Key env vars

```
TELEGRAM_BOT_TOKEN=   # required
TELEGRAM_ADMIN_IDS=   # comma-separated Telegram user IDs with admin access
SCHEDULER_TIMEZONE=   # timezone for scheduled reminders (default: UTC)
```

## Setup

```bash
composer run setup    # installs deps, copies .env, migrates, builds assets
composer run dev      # starts server + queue worker + vite + log tail
```

## Docker

```bash
# Copy and configure env first
cp .env.example .env
# Edit .env — set TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_IDS

docker compose up --build
```

The `app` service runs `php artisan serve` on port 8000.
The `queue` service runs the queue worker for dispatched reminder jobs.

SQLite database is bind-mounted so data persists across container restarts.

## Telegram webhook

After starting, register the webhook with Telegram:

```bash
php artisan telegram:webhook:set --url=https://your-domain.com/api/webhook
```

## Testing

```bash
composer test
```

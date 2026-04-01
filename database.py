"""
database.py — SQLite persistence layer for the Telegram bot.
Tables: reminders, log_categories, logs, recipe_categories, recipes
"""

import sqlite3
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/bot.db")


# ─── Connection ───────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ─── Initialise Schema ────────────────────────────────────────────────────────

def init_db() -> None:
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS reminders (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            message          TEXT    NOT NULL,
            cron_expression  TEXT    NOT NULL,
            channel_id       TEXT    NOT NULL,
            active           INTEGER NOT NULL DEFAULT 1,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS log_categories (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL REFERENCES log_categories(id),
            subject     TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            user_id     INTEGER NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recipe_categories (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recipes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL REFERENCES recipe_categories(id),
            name        TEXT    NOT NULL,
            content     TEXT    NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialised at %s", DB_PATH)


# ─── Reminders ────────────────────────────────────────────────────────────────

def add_reminder(message: str, cron_expression: str, channel_id: str) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO reminders (message, cron_expression, channel_id) VALUES (?, ?, ?)",
        (message, cron_expression, channel_id),
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid


def get_reminders(active_only: bool = True) -> list[dict]:
    conn = _get_conn()
    if active_only:
        rows = conn.execute("SELECT * FROM reminders WHERE active = 1 ORDER BY id").fetchall()
    else:
        rows = conn.execute("SELECT * FROM reminders ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_reminder(reminder_id: int) -> None:
    conn = _get_conn()
    conn.execute("UPDATE reminders SET active = 0 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


# ─── Log Categories ───────────────────────────────────────────────────────────

def add_log_category(name: str) -> int:
    conn = _get_conn()
    cur = conn.execute("INSERT INTO log_categories (name) VALUES (?)", (name,))
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return cid


def get_log_categories() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM log_categories ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_log_category(cat_id: int) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM log_categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()


# ─── Logs ─────────────────────────────────────────────────────────────────────

def add_log(category_id: int, subject: str, message: str, user_id: int) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO logs (category_id, subject, message, user_id) VALUES (?, ?, ?, ?)",
        (category_id, subject, message, user_id),
    )
    lid = cur.lastrowid
    conn.commit()
    conn.close()
    return lid


def get_logs(category_id: int | None = None, limit: int = 50) -> list[dict]:
    conn = _get_conn()
    if category_id:
        rows = conn.execute(
            """SELECT l.*, lc.name AS category_name
               FROM logs l JOIN log_categories lc ON l.category_id = lc.id
               WHERE l.category_id = ?
               ORDER BY l.created_at DESC LIMIT ?""",
            (category_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT l.*, lc.name AS category_name
               FROM logs l JOIN log_categories lc ON l.category_id = lc.id
               ORDER BY l.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Recipe Categories ────────────────────────────────────────────────────────

def add_recipe_category(name: str) -> int:
    conn = _get_conn()
    cur = conn.execute("INSERT INTO recipe_categories (name) VALUES (?)", (name,))
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return cid


def get_recipe_categories() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM recipe_categories ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recipe_category(cat_id: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM recipe_categories WHERE id = ?", (cat_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_recipe_category(cat_id: int) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM recipes WHERE category_id = ?", (cat_id,))
    conn.execute("DELETE FROM recipe_categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()


# ─── Recipes ──────────────────────────────────────────────────────────────────

def add_recipe(category_id: int, name: str, content: str) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO recipes (category_id, name, content) VALUES (?, ?, ?)",
        (category_id, name, content),
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid


def get_recipes_by_category(category_id: int) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM recipes WHERE category_id = ? ORDER BY name",
        (category_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recipe(recipe_id: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        """SELECT r.*, rc.name AS category_name
           FROM recipes r JOIN recipe_categories rc ON r.category_id = rc.id
           WHERE r.id = ?""",
        (recipe_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_recipe(recipe_id: int) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    conn.close()

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from src.database.crypto_manager import VaultCryptoManager


class PrivateVaultDB:
    """
    Local SQLite storage engine with transparent field-level encryption
    for personal secrets, daily reflections, and scheduled reminders.
    """

    def __init__(self, db_path: str = "database/vault.db", crypto: VaultCryptoManager | None = None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.crypto = crypto or VaultCryptoManager()
        self._init_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS secrets_vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    encrypted_content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    due_datetime TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    is_completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

    # --- Tool 1: Save Secret / Private Note ---
    def save_secret(self, title: str, content: str, category: str = "general") -> dict[str, Any]:
        encrypted_content = self.crypto.encrypt(content)
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO secrets_vault (category, title, encrypted_content, created_at) VALUES (?, ?, ?, ?)",
                (category, title.strip(), encrypted_content, now),
            )
            return {"status": "success", "id": cursor.lastrowid, "title": title, "category": category}

    # --- Tool 2: Retrieve & Decrypt Secret ---
    def get_secret(self, query: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, category, title, encrypted_content, created_at FROM secrets_vault WHERE title LIKE ?",
                (f"%{query.strip()}%",),
            ).fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "category": row["category"],
                "title": row["title"],
                "content": self.crypto.decrypt(row["encrypted_content"]),
                "created_at": row["created_at"],
            })
        return results

    # --- Tool 3: Add Reminder / Task ---
    def add_reminder(self, task: str, due_datetime: str, priority: str = "medium") -> dict[str, Any]:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO reminders (task, due_datetime, priority, created_at) VALUES (?, ?, ?, ?)",
                (task.strip(), due_datetime.strip(), priority.lower(), now),
            )
            return {"status": "success", "id": cursor.lastrowid, "task": task, "due_datetime": due_datetime}

    # --- Tool 4: List Active Reminders ---
    def get_pending_reminders(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, task, due_datetime, priority FROM reminders WHERE is_completed = 0 ORDER BY due_datetime ASC"
            ).fetchall()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    vault = PrivateVaultDB()

    # 1. تجربة حفظ سر وتذكير
    print("Saving encrypted secret...")
    print(vault.save_secret(title="باسورد السيرفر", content="X99#Dev_Secret2026", category="credentials"))
    print(vault.add_reminder(task="مراجعة كود الـ LoRA قبل التدريب", due_datetime="2026-11-22 20:00", priority="high"))

    # 2. تجربة الاسترجاع وفك التشفير
    print("\nRetrieving decrypted secret:")
    print(vault.get_secret("السيرفر"))

    print("\nPending reminders:")
    print(vault.get_pending_reminders())
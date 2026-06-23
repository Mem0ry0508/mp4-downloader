"""
history.py — 下載歷史紀錄模組（擴充功能）
使用 SQLite 儲存每次下載的紀錄，包含 URL、檔名、畫質、狀態與時間。
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "history.db"


def _get_conn() -> sqlite3.Connection:
    """取得資料庫連線，並確保資料表已建立。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS download_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            url       TEXT    NOT NULL,
            filename  TEXT,
            quality   TEXT,
            status    TEXT    NOT NULL DEFAULT 'pending',
            created_at TEXT   NOT NULL
        )
    """)
    conn.commit()
    return conn


def add_record(url: str, filename: str | None, quality: str | None, status: str) -> int:
    """新增一筆下載紀錄，回傳新紀錄的 id。"""
    now = datetime.now(timezone.utc).isoformat()
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO download_history (url, filename, quality, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (url, filename, quality, status, now),
        )
        return cur.lastrowid


def update_record(record_id: int, filename: str | None = None, status: str | None = None) -> None:
    """更新指定紀錄的檔名或狀態。"""
    with _get_conn() as conn:
        if filename is not None:
            conn.execute("UPDATE download_history SET filename = ? WHERE id = ?", (filename, record_id))
        if status is not None:
            conn.execute("UPDATE download_history SET status = ? WHERE id = ?", (status, record_id))


def list_records(limit: int = 50) -> list[dict]:
    """取得最近 N 筆下載紀錄，由新到舊排列。"""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM download_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def delete_record(record_id: int) -> bool:
    """刪除指定紀錄，回傳是否成功刪除。"""
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM download_history WHERE id = ?", (record_id,))
        return cur.rowcount > 0
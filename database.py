import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "gs_bot.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'Gündem',
                media_type TEXT DEFAULT 'none',
                media_url TEXT,
                status TEXT DEFAULT 'draft',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                published_at TEXT,
                tweet_id TEXT
            )
        """)
        conn.commit()

def create_draft(title: str, content: str, category: str = 'Gündem', media_type: str = 'none', media_url: str = None) -> int:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO drafts (title, content, category, media_type, media_url, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
        """, (title, content, category, media_type, media_url, now, now))
        conn.commit()
        return cursor.lastrowid

def get_drafts(status: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM drafts WHERE status = ? ORDER BY id DESC", (status,))
        else:
            cursor.execute("SELECT * FROM drafts ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_draft_by_id(draft_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_draft(draft_id: int, content: str = None, status: str = None, media_url: str = None, tweet_id: str = None):
    now = datetime.now().isoformat()
    updates = []
    params = []
    
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
        if status == 'published':
            updates.append("published_at = ?")
            params.append(now)
    if media_url is not None:
        updates.append("media_url = ?")
        params.append(media_url)
    if tweet_id is not None:
        updates.append("tweet_id = ?")
        params.append(tweet_id)
        
    updates.append("updated_at = ?")
    params.append(now)
    
    params.append(draft_id)
    query = f"UPDATE drafts SET {', '.join(updates)} WHERE id = ?"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        conn.commit()

def delete_draft(draft_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
        conn.commit()

def get_stats():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM drafts GROUP BY status
        """)
        rows = cursor.fetchall()
        stats = {'draft': 0, 'approved': 0, 'published': 0, 'rejected': 0}
        for r in rows:
            stats[r['status']] = r['count']
        return stats

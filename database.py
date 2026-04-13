import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import config


def get_sqlite_conn():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """SQLiteテーブルとFTS5全文検索を初期化"""
    conn = get_sqlite_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            url TEXT,
            source TEXT,
            published_at TEXT,
            collected_at TEXT NOT NULL,
            language TEXT DEFAULT 'unknown'
        )
    """)
    # FTS5全文検索テーブル
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts
        USING fts5(id, title, summary, source, content='articles', content_rowid='rowid')
    """)
    # お気に入りテーブル
    conn.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            article_id TEXT PRIMARY KEY,
            added_at TEXT NOT NULL,
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    """)
    # 手動メモテーブル
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    # 自動収集ログ
    conn.execute("""
        CREATE TABLE IF NOT EXISTS auto_collect_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at TEXT NOT NULL,
            new_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def make_article_id(url: str, title: str) -> str:
    raw = f"{url}:{title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def article_exists(article_id: str) -> bool:
    conn = get_sqlite_conn()
    row = conn.execute("SELECT 1 FROM articles WHERE id = ?", (article_id,)).fetchone()
    conn.close()
    return row is not None


def save_article(article_id: str, title: str, summary: str, url: str,
                 source: str, published_at: str, language: str = "unknown"):
    now = datetime.now().isoformat()
    conn = get_sqlite_conn()
    conn.execute(
        "INSERT OR IGNORE INTO articles (id, title, summary, url, source, published_at, collected_at, language) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (article_id, title, summary, url, source, published_at, now, language),
    )
    conn.execute(
        "INSERT OR IGNORE INTO articles_fts (id, title, summary, source) "
        "VALUES (?, ?, ?, ?)",
        (article_id, title, summary or "", source),
    )
    conn.commit()
    conn.close()


def search_articles(query: str, top_k: int = None):
    if top_k is None:
        top_k = config.RAG_TOP_K
    conn = get_sqlite_conn()
    try:
        words = query.strip().split()
        fts_query = " OR ".join(words) if words else query
        rows = conn.execute("""
            SELECT a.*, rank
            FROM articles_fts fts
            JOIN articles a ON a.id = fts.id
            WHERE articles_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, top_k)).fetchall()
    except Exception:
        like_pattern = f"%{query}%"
        rows = conn.execute("""
            SELECT * FROM articles
            WHERE title LIKE ? OR summary LIKE ?
            ORDER BY collected_at DESC
            LIMIT ?
        """, (like_pattern, like_pattern, top_k)).fetchall()
    conn.close()

    articles = []
    for r in rows:
        row = dict(r)
        doc_text = f"[{row.get('source', '')}] {row.get('title', '')}"
        if row.get("summary"):
            doc_text += f"\n{row['summary']}"
        articles.append({
            "text": doc_text,
            "source": row.get("source", ""),
            "url": row.get("url", ""),
            "published_at": row.get("published_at", ""),
        })
    return articles


def get_article_count() -> int:
    conn = get_sqlite_conn()
    row = conn.execute("SELECT COUNT(*) FROM articles").fetchone()
    conn.close()
    return row[0]


def get_recent_articles(limit: int = 20):
    conn = get_sqlite_conn()
    rows = conn.execute(
        "SELECT * FROM articles ORDER BY collected_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_source_stats():
    conn = get_sqlite_conn()
    rows = conn.execute(
        "SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return {r["source"]: r["count"] for r in rows}


# ===== お気に入り機能 =====
def toggle_favorite(article_id: str) -> bool:
    """お気に入りの追加/解除。追加ならTrue、解除ならFalseを返す"""
    conn = get_sqlite_conn()
    exists = conn.execute("SELECT 1 FROM favorites WHERE article_id = ?", (article_id,)).fetchone()
    if exists:
        conn.execute("DELETE FROM favorites WHERE article_id = ?", (article_id,))
        conn.commit()
        conn.close()
        return False
    else:
        conn.execute("INSERT INTO favorites (article_id, added_at) VALUES (?, ?)",
                     (article_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True


def is_favorite(article_id: str) -> bool:
    conn = get_sqlite_conn()
    row = conn.execute("SELECT 1 FROM favorites WHERE article_id = ?", (article_id,)).fetchone()
    conn.close()
    return row is not None


def get_favorite_ids() -> set:
    conn = get_sqlite_conn()
    rows = conn.execute("SELECT article_id FROM favorites").fetchall()
    conn.close()
    return {r["article_id"] for r in rows}


def get_favorite_articles():
    conn = get_sqlite_conn()
    rows = conn.execute("""
        SELECT a.* FROM articles a
        JOIN favorites f ON a.id = f.article_id
        ORDER BY f.added_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ===== メモ機能 =====
def save_memo(title: str, content: str, category: str = ""):
    conn = get_sqlite_conn()
    conn.execute(
        "INSERT INTO memos (title, content, category, created_at) VALUES (?, ?, ?, ?)",
        (title, content, category, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_memos(limit: int = 50):
    conn = get_sqlite_conn()
    rows = conn.execute("SELECT * FROM memos ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_memo(memo_id: int):
    conn = get_sqlite_conn()
    conn.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
    conn.commit()
    conn.close()


# ===== トレンド分析 =====
def get_daily_counts(days: int = 14):
    """過去N日間の日別・ソース別記事数"""
    conn = get_sqlite_conn()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = conn.execute("""
        SELECT DATE(collected_at) as date, source, COUNT(*) as count
        FROM articles
        WHERE DATE(collected_at) >= ?
        GROUP BY DATE(collected_at), source
        ORDER BY date
    """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_total(days: int = 14):
    """過去N日間の日別合計記事数"""
    conn = get_sqlite_conn()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = conn.execute("""
        SELECT DATE(collected_at) as date, COUNT(*) as count
        FROM articles
        WHERE DATE(collected_at) >= ?
        GROUP BY DATE(collected_at)
        ORDER BY date
    """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_counts():
    """カテゴリ別の記事数"""
    stats = get_source_stats()
    categories = config.CATEGORIES
    result = {}
    for cat_name, keywords in categories.items():
        if keywords is None:
            continue
        count = sum(v for k, v in stats.items()
                    if any(kw.lower() in k.lower() for kw in keywords))
        result[cat_name] = count
    return result


# ===== 自動収集ログ =====
def log_auto_collect(new_count: int, error_count: int):
    conn = get_sqlite_conn()
    conn.execute(
        "INSERT INTO auto_collect_log (collected_at, new_count, error_count) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), new_count, error_count),
    )
    conn.commit()
    conn.close()


def get_last_auto_collect():
    conn = get_sqlite_conn()
    row = conn.execute(
        "SELECT * FROM auto_collect_log ORDER BY collected_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def should_auto_collect(interval_hours: int = 12) -> bool:
    """前回の自動収集からN時間以上経過しているか"""
    last = get_last_auto_collect()
    if not last:
        return True
    last_time = datetime.fromisoformat(last["collected_at"])
    return datetime.now() - last_time > timedelta(hours=interval_hours)


# 起動時にDBを初期化
init_db()

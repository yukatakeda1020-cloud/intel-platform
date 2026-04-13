import sqlite3
import hashlib
from datetime import datetime
import config


def get_sqlite_conn():
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
    conn.commit()
    conn.close()


def make_article_id(url: str, title: str) -> str:
    """記事の一意IDを生成"""
    raw = f"{url}:{title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def article_exists(article_id: str) -> bool:
    """記事が既に保存済みか確認"""
    conn = get_sqlite_conn()
    row = conn.execute("SELECT 1 FROM articles WHERE id = ?", (article_id,)).fetchone()
    conn.close()
    return row is not None


def save_article(article_id: str, title: str, summary: str, url: str,
                 source: str, published_at: str, language: str = "unknown"):
    """記事をSQLiteに保存"""
    now = datetime.now().isoformat()

    conn = get_sqlite_conn()
    conn.execute(
        "INSERT OR IGNORE INTO articles (id, title, summary, url, source, published_at, collected_at, language) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (article_id, title, summary, url, source, published_at, now, language),
    )
    # FTS5にも同期
    conn.execute(
        "INSERT OR IGNORE INTO articles_fts (id, title, summary, source) "
        "VALUES (?, ?, ?, ?)",
        (article_id, title, summary or "", source),
    )
    conn.commit()
    conn.close()


def search_articles(query: str, top_k: int = None):
    """全文検索で関連記事を取得"""
    if top_k is None:
        top_k = config.RAG_TOP_K
    conn = get_sqlite_conn()

    # FTS5検索を試行、失敗時はLIKE検索にフォールバック
    try:
        # クエリをFTS5用に変換（各単語をOR検索）
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
        # LIKE検索にフォールバック
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
    """蓄積記事数を取得"""
    conn = get_sqlite_conn()
    row = conn.execute("SELECT COUNT(*) FROM articles").fetchone()
    conn.close()
    return row[0]


def get_recent_articles(limit: int = 20):
    """最新の記事一覧を取得"""
    conn = get_sqlite_conn()
    rows = conn.execute(
        "SELECT * FROM articles ORDER BY collected_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_source_stats():
    """ソースごとの記事数を取得"""
    conn = get_sqlite_conn()
    rows = conn.execute(
        "SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return {r["source"]: r["count"] for r in rows}


# 起動時にDBを初期化
init_db()

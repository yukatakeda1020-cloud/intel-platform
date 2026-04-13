import sqlite3
import hashlib
from datetime import datetime
import chromadb
from chromadb.config import Settings
import config


def get_sqlite_conn():
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """SQLiteテーブルを初期化"""
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
    conn.commit()
    conn.close()


def get_chroma_collection():
    """ChromaDBコレクションを取得"""
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    collection = client.get_or_create_collection(
        name="articles",
        metadata={"hnsw:space": "cosine"},
    )
    return collection


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
    """記事をSQLite + ChromaDBに保存"""
    now = datetime.now().isoformat()

    # SQLiteに保存
    conn = get_sqlite_conn()
    conn.execute(
        "INSERT OR IGNORE INTO articles (id, title, summary, url, source, published_at, collected_at, language) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (article_id, title, summary, url, source, published_at, now, language),
    )
    conn.commit()
    conn.close()

    # ChromaDBに保存（タイトル+要約をドキュメントとして）
    doc_text = f"[{source}] {title}"
    if summary:
        doc_text += f"\n{summary}"

    collection = get_chroma_collection()
    collection.upsert(
        ids=[article_id],
        documents=[doc_text],
        metadatas=[{
            "source": source,
            "url": url or "",
            "published_at": published_at or "",
            "language": language,
        }],
    )


def search_articles(query: str, top_k: int = None):
    """ベクトル類似検索で関連記事を取得"""
    if top_k is None:
        top_k = config.RAG_TOP_K
    collection = get_chroma_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(top_k, collection.count()))
    articles = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        dist = results["distances"][0][i] if results.get("distances") else None
        articles.append({
            "text": doc,
            "source": meta.get("source", ""),
            "url": meta.get("url", ""),
            "published_at": meta.get("published_at", ""),
            "distance": dist,
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

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import database
import config


def detect_language(text: str) -> str:
    """簡易言語判定（日本語文字が含まれるかどうか）"""
    for ch in text:
        if '\u3040' <= ch <= '\u9fff':
            return "ja"
    return "en"


def parse_published_date(entry) -> str:
    """RSSエントリから公開日を抽出"""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6]).isoformat()
        except Exception:
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6]).isoformat()
        except Exception:
            pass
    return datetime.now().isoformat()


def clean_html(html_text: str) -> str:
    """HTMLタグを除去してプレーンテキストに"""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def collect_from_feed(feed_name: str, feed_url: str) -> dict:
    """単一のRSSフィードから記事を収集"""
    result = {"name": feed_name, "new": 0, "skipped": 0, "errors": 0}

    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            result["errors"] = 1
            return result

        for entry in feed.entries:
            try:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                url = entry.get("link", "")
                summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
                published_at = parse_published_date(entry)
                language = detect_language(title + summary)

                article_id = database.make_article_id(url, title)
                if database.article_exists(article_id):
                    result["skipped"] += 1
                    continue

                database.save_article(
                    article_id=article_id,
                    title=title,
                    summary=summary[:500],  # 要約は500文字まで
                    url=url,
                    source=feed_name,
                    published_at=published_at,
                    language=language,
                )
                result["new"] += 1

            except Exception:
                result["errors"] += 1

    except Exception:
        result["errors"] += 1

    return result


def collect_all_feeds(progress_callback=None) -> list:
    """全RSSフィードから記事を収集"""
    results = []
    feeds = list(config.RSS_FEEDS.items())

    for i, (name, url) in enumerate(feeds):
        if progress_callback:
            progress_callback(i / len(feeds), f"収集中: {name}")

        result = collect_from_feed(name, url)
        results.append(result)
        time.sleep(0.2)  # サーバーへの負荷軽減

    if progress_callback:
        progress_callback(1.0, "収集完了")

    return results

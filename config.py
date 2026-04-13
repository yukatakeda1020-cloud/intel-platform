import os

try:
    import streamlit as st
    _secrets = st.secrets if hasattr(st, "secrets") else {}
except Exception:
    _secrets = {}

# Claude API設定
ANTHROPIC_API_KEY = (
    _secrets.get("ANTHROPIC_API_KEY", "")
    or os.environ.get("ANTHROPIC_API_KEY", "")
)
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# データベース設定
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "articles.db")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")

# RSSフィード一覧
RSS_FEEDS = {
    # ===== 総合ニュース =====
    "NHK ニュース": "https://www.nhk.or.jp/rss/news/cat0.xml",
    "NHK ビジネス": "https://www.nhk.or.jp/rss/news/cat3.xml",
    "NHK 国際": "https://www.nhk.or.jp/rss/news/cat6.xml",
    "Yahoo! 経済": "https://news.yahoo.co.jp/rss/topics/business.xml",
    "Yahoo! 国際": "https://news.yahoo.co.jp/rss/topics/world.xml",
    "Yahoo! IT": "https://news.yahoo.co.jp/rss/topics/it.xml",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters Technology": "https://feeds.reuters.com/reuters/technologyNews",
    "Reuters World": "https://feeds.reuters.com/reuters/worldNews",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "BBC Technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",

    # ===== エネルギー業界 =====
    "OILPRICE": "https://oilprice.com/rss/main",
    "Renewable Energy World": "https://www.renewableenergyworld.com/feed/",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "Greentech Media": "https://www.greentechmedia.com/feed/",
    "Energy Voice": "https://www.energyvoice.com/feed/",
    "PV Magazine": "https://www.pv-magazine.com/feed/",
    "Electrek (EV/エネルギー)": "https://electrek.co/feed/",
    "Carbon Brief": "https://www.carbonbrief.org/feed/",
    "環境ビジネス": "https://www.kankyo-business.jp/news/rss",
    "スマートジャパン": "https://rss.itmedia.co.jp/rss/2.0/smartjapan.xml",
    "自然エネルギー財団": "https://www.renewable-ei.org/activities/feed/",

    # ===== AI業界 =====
    "TechCrunch": "https://techcrunch.com/feed/",
    "Hacker News": "https://hnrss.org/frontpage",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "Anthropic News": "https://www.anthropic.com/rss.xml",
    "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "Ledge.ai": "https://ledge.ai/feed/",
    "AINOW": "https://ainow.ai/feed/",

    # ===== シニア業界（高齢者・介護・ヘルスケア） =====
    "介護ニュース Joint": "https://www.joint-kaigo.com/rss/",
    "高齢者住宅新聞": "https://www.koureisha-jutaku.com/feed/",
    "ケアマネタイムス": "https://caremanager.jp/feed",
    "シルバー産業新聞": "https://www.care-news.jp/feed",
    "みんなの介護": "https://www.minnanokaigo.com/feed/",
    "McKnight's Senior Living": "https://www.mcknightsseniorliving.com/feed/",
    "Aging Care": "https://www.agingcare.com/feed",
    "Senior Housing News": "https://seniorhousingnews.com/feed/",
    "Next Avenue (PBS シニア)": "https://www.nextavenue.org/feed/",
    "日経ヘルスケア": "https://medical.nikkeibp.co.jp/inc/all/healthnews/rss/index.rdf",
}

# RAG設定
RAG_TOP_K = 10  # 検索で返す上位件数
RAG_MAX_CONTEXT_CHARS = 8000  # コンテキストに含める最大文字数

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

# =============================================================
# RSSフィード一覧 — Team Energy向けに最適化
# =============================================================
RSS_FEEDS = {
    # ===== 再生可能エネルギー・地熱・脱炭素 =====
    "スマートジャパン": "https://rss.itmedia.co.jp/rss/2.0/smartjapan.xml",
    "環境ビジネス": "https://www.kankyo-business.jp/news/rss",
    "自然エネルギー財団": "https://www.renewable-ei.org/activities/feed/",
    "PV Magazine": "https://www.pv-magazine.com/feed/",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "Carbon Brief": "https://www.carbonbrief.org/feed/",
    "Electrek (EV/再エネ)": "https://electrek.co/feed/",
    "Renewable Energy World": "https://www.renewableenergyworld.com/feed/",
    "OILPRICE": "https://oilprice.com/rss/main",
    "Energy Voice": "https://www.energyvoice.com/feed/",

    # ===== スタートアップ・起業・経営 =====
    "TechCrunch": "https://techcrunch.com/feed/",
    "BRIDGE (起業)": "https://thebridge.jp/feed",
    "PR TIMES": "https://prtimes.jp/index.rdf",
    "DIAMOND online": "https://diamond.jp/list/feed/rss",
    "東洋経済": "https://toyokeizai.net/list/feed/rss",

    # ===== AI・テクノロジー =====
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "AINOW": "https://ainow.ai/feed/",

    # ===== 地方創生・地域活性化 =====
    "地方創生 NHK": "https://www.nhk.or.jp/rss/news/cat7.xml",
    "NHK ビジネス": "https://www.nhk.or.jp/rss/news/cat3.xml",

    # ===== 高齢者・介護・ヘルスケア =====
    "介護ニュース Joint": "https://www.joint-kaigo.com/rss/",
    "高齢者住宅新聞": "https://www.koureisha-jutaku.com/feed/",
    "Senior Housing News": "https://seniorhousingnews.com/feed/",
    "Next Avenue (シニア)": "https://www.nextavenue.org/feed/",

    # ===== ESG・サステナビリティ =====
    "GreenBiz": "https://www.greenbiz.com/rss/all",
    "ESG Journal": "https://esg-journal.com/feed/",
}

# RAG設定
RAG_TOP_K = 10
RAG_MAX_CONTEXT_CHARS = 8000

import os

try:
    import streamlit as st
    _secrets = st.secrets if hasattr(st, "secrets") else {}
except Exception:
    _secrets = {}

# Gemini API設定
GOOGLE_API_KEY = (
    _secrets.get("GOOGLE_API_KEY", "")
    or os.environ.get("GOOGLE_API_KEY", "")
)
GEMINI_MODEL = "gemini-1.5-flash"

# データベース設定
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "articles.db")

# =============================================================
# RSSフィード — Team Energy 5領域特化
# =============================================================
RSS_FEEDS = {
    # ─────────────────────────────────────────────
    # 1. 再生可能エネルギー（地熱中心）・脱炭素
    # ─────────────────────────────────────────────
    "スマートジャパン": "https://rss.itmedia.co.jp/rss/2.0/smartjapan.xml",
    "環境ビジネス": "https://www.kankyo-business.jp/news/rss",
    "自然エネルギー財団": "https://www.renewable-ei.org/activities/feed/",
    "PV Magazine": "https://www.pv-magazine.com/feed/",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "Electrek (EV/再エネ)": "https://electrek.co/feed/",
    "Renewable Energy World": "https://www.renewableenergyworld.com/feed/",
    "Energy Voice": "https://www.energyvoice.com/feed/",
    "ThinkGeoEnergy (地熱)": "https://www.thinkgeoenergy.com/feed/",
    "Carbon Brief": "https://www.carbonbrief.org/feed/",
    "OILPRICE": "https://oilprice.com/rss/main",

    # ─────────────────────────────────────────────
    # 2. カーボンクレジット・ESG・サステナビリティ
    # ─────────────────────────────────────────────
    "GreenBiz": "https://www.greenbiz.com/rss/all",
    "ESG Journal": "https://esg-journal.com/feed/",
    "Sustainable Japan": "https://sustainablejapan.jp/feed",
    "環境省 報道発表": "https://www.env.go.jp/press/press.rdf",
    "CDP / Climate": "https://www.cdp.net/en/articles/rss",

    # ─────────────────────────────────────────────
    # 3. AI・テクノロジー
    # ─────────────────────────────────────────────
    "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "AINOW": "https://ainow.ai/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",

    # ─────────────────────────────────────────────
    # 4. シニア・介護・ヘルスケア
    # ─────────────────────────────────────────────
    "介護ニュース Joint": "https://www.joint-kaigo.com/rss/",
    "高齢者住宅新聞": "https://www.koureisha-jutaku.com/feed/",
    "Senior Housing News": "https://seniorhousingnews.com/feed/",
    "Next Avenue (シニア)": "https://www.nextavenue.org/feed/",
    "McKnight's Senior Living": "https://www.mcknightsseniorliving.com/feed/",

    # ─────────────────────────────────────────────
    # 5. M&A・スタートアップ・経営戦略
    # ─────────────────────────────────────────────
    "M&A Online": "https://maonline.jp/rss",
    "MARR Online (M&A)": "https://www.marr.jp/rss",
    "BRIDGE (スタートアップ)": "https://thebridge.jp/feed",
    "PR TIMES": "https://prtimes.jp/index.rdf",
    "DIAMOND online": "https://diamond.jp/list/feed/rss",
    "東洋経済": "https://toyokeizai.net/list/feed/rss",
    "NHK ビジネス": "https://www.nhk.or.jp/rss/news/cat3.xml",
}

# カテゴリ定義（UIとanalyzerで共用）
CATEGORIES = {
    "🌍 すべて": None,
    "🌋 再エネ・地熱・脱炭素": [
        "スマート", "環境ビジネス", "自然エネ", "PV Magazine", "Clean",
        "Electrek", "Renewable", "Energy Voice", "ThinkGeo", "Carbon Brief", "OIL",
    ],
    "🌱 カーボンクレジット・ESG": [
        "GreenBiz", "ESG", "Sustainable", "環境省", "CDP",
    ],
    "🤖 AI・テクノロジー": [
        "ITmedia AI", "MIT Tech", "VentureBeat", "AI News",
        "Google AI", "AINOW", "TechCrunch",
    ],
    "👴 シニア・介護": [
        "介護", "高齢者", "Senior", "Next Avenue", "McKnight",
    ],
    "💼 M&A・経営戦略": [
        "M&A", "MARR", "BRIDGE", "PR TIMES", "DIAMOND", "東洋経済", "NHK ビジネス",
    ],
}

# RAG設定
RAG_TOP_K = 10
RAG_MAX_CONTEXT_CHARS = 8000

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
GEMINI_MODEL = "gemini-2.5-flash"

# データベース設定
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "articles.db")

# =============================================================
# RSSフィード — Team Energy 5領域 + グローバル情報網
# =============================================================
RSS_FEEDS = {
    # ═══════════════════════════════════════════════
    # 1. 再生可能エネルギー・地熱・脱炭素 (25ソース)
    # ═══════════════════════════════════════════════
    # 日本
    "スマートジャパン": "https://rss.itmedia.co.jp/rss/2.0/smartjapan.xml",
    "環境ビジネス": "https://www.kankyo-business.jp/news/rss",
    "自然エネルギー財団": "https://www.renewable-ei.org/activities/feed/",
    "経産省 エネルギー": "https://www.meti.go.jp/press/index.rdf",
    "電気新聞": "https://www.denkishimbun.com/feed",
    # 地熱特化
    "ThinkGeoEnergy (地熱)": "https://www.thinkgeoenergy.com/feed/",
    "Geothermal Rising": "https://geothermal.org/feed",
    # 次世代地熱・クローズドループ（Google News検索）
    "次世代地熱 (JP)": "https://news.google.com/rss/search?q=%E6%AC%A1%E4%B8%96%E4%BB%A3%E5%9C%B0%E7%86%B1%E7%99%BA%E9%9B%BB+OR+%E3%82%AF%E3%83%AD%E3%83%BC%E3%82%BA%E3%83%89%E3%83%AB%E3%83%BC%E3%83%97%E5%9C%B0%E7%86%B1+OR+%E5%BC%B7%E5%8C%96%E5%9C%B0%E7%86%B1&hl=ja&gl=JP&ceid=JP:ja",
    "Closed-Loop Geothermal": "https://news.google.com/rss/search?q=%22closed+loop+geothermal%22+OR+%22advanced+geothermal+systems%22&hl=en-US&gl=US&ceid=US:en",
    "Enhanced Geothermal (EGS)": "https://news.google.com/rss/search?q=%22enhanced+geothermal+systems%22+OR+%22EGS+geothermal%22&hl=en-US&gl=US&ceid=US:en",
    "Eavor (クローズドループ)": "https://news.google.com/rss/search?q=Eavor+geothermal&hl=en-US&gl=US&ceid=US:en",
    "Fervo Energy": "https://news.google.com/rss/search?q=%22Fervo+Energy%22&hl=en-US&gl=US&ceid=US:en",
    "ふるさと熱電": "https://news.google.com/rss/search?q=%E3%81%B5%E3%82%8B%E3%81%95%E3%81%A8%E7%86%B1%E9%9B%BB+OR+%E5%9C%B0%E7%86%B1%E7%99%BA%E9%9B%BB&hl=ja&gl=JP&ceid=JP:ja",
    # 再エネ・グローバル
    "PV Magazine": "https://www.pv-magazine.com/feed/",
    "PV Magazine Global": "https://www.pv-magazine.com/feed/",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "Electrek (EV/再エネ)": "https://electrek.co/feed/",
    "Renewable Energy World": "https://www.renewableenergyworld.com/feed/",
    "Energy Voice": "https://www.energyvoice.com/feed/",
    "Carbon Brief": "https://www.carbonbrief.org/feed/",
    "OILPRICE": "https://oilprice.com/rss/main",
    "Utility Dive": "https://www.utilitydive.com/feeds/news/",
    "Energy Monitor": "https://www.energymonitor.ai/feed/",
    "Canary Media": "https://www.canarymedia.com/feed",
    "Recharge News": "https://www.rechargenews.com/rss",
    "S&P Global Energy": "https://www.spglobal.com/commodityinsights/en/rss-feed/energy",
    # 水素・蓄電
    "Hydrogen Insight": "https://www.hydrogeninsight.com/rss",
    "Energy Storage News": "https://www.energy-storage.news/feed/",
    # アジア
    "Asia Power": "https://asian-power.com/rss.xml",
    "Nikkei Asia Energy": "https://asia.nikkei.com/rss/feed/Business/Energy",

    # ═══════════════════════════════════════════════
    # 2. カーボンクレジット・ESG・サステナビリティ (18ソース)
    # ═══════════════════════════════════════════════
    # 日本
    "ESG Journal": "https://esg-journal.com/feed/",
    "Sustainable Japan": "https://sustainablejapan.jp/feed",
    "環境省 報道発表": "https://www.env.go.jp/press/press.rdf",
    "サステナブル経営": "https://sustainable.exblog.jp/index.xml",
    "日経ESG": "https://project.nikkeibp.co.jp/ESG/rss/index.rdf",
    # グローバル
    "GreenBiz": "https://www.greenbiz.com/rss/all",
    "CDP / Climate": "https://www.cdp.net/en/articles/rss",
    "Climate Home News": "https://www.climatechangenews.com/feed/",
    "Carbon Pulse": "https://carbon-pulse.com/feed/",
    "Eco-Business": "https://www.eco-business.com/rss/",
    "Responsible Investor": "https://www.responsible-investor.com/feed/",
    "ESG Today": "https://www.esgtoday.com/feed/",
    "Sustainable Brands": "https://sustainablebrands.com/rss",
    "Climate Action": "https://www.climateaction.org/rss",
    "UNFCCC News": "https://unfccc.int/rss.xml",
    # カーボンマーケット
    "Voluntary Carbon Markets": "https://vcmintegrity.org/feed/",
    "IETA": "https://www.ieta.org/feed/",
    "Gold Standard": "https://www.goldstandard.org/feed",

    # ═══════════════════════════════════════════════
    # 3. AI・テクノロジー (30ソース)
    # ═══════════════════════════════════════════════
    # 日本
    "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "AINOW": "https://ainow.ai/feed/",
    "Ledge.ai": "https://ledge.ai/feed/",
    "ASCII AI": "https://ascii.jp/rss.xml",
    "日経 XTECH AI": "https://xtech.nikkei.com/rss/xtech-ai.rdf",
    # 米国・グローバルメディア
    "TechCrunch": "https://techcrunch.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "Hacker News": "https://hnrss.org/frontpage",
    "The Information": "https://www.theinformation.com/feed",
    "Semafor Tech": "https://www.semafor.com/vertical/tech/rss",
    "404 Media": "https://www.404media.co/rss/",
    # AI企業公式
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "Anthropic News": "https://www.anthropic.com/rss.xml",
    "Microsoft AI Blog": "https://blogs.microsoft.com/ai/feed/",
    "NVIDIA Blog": "https://blogs.nvidia.com/feed/",
    "Meta AI Blog": "https://ai.meta.com/blog/rss/",
    "Amazon Science": "https://www.amazon.science/index.rss",
    "Apple ML Research": "https://machinelearning.apple.com/rss.xml",
    "Samsung AI": "https://research.samsung.com/feed",
    # AI研究・論文
    "DeepMind Blog": "https://deepmind.google/blog/rss.xml",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "Papers With Code": "https://paperswithcode.com/latest/rss",
    "Towards Data Science": "https://towardsdatascience.com/feed",
    "Synced AI": "https://syncedreview.com/feed/",

    # ═══════════════════════════════════════════════
    # 4. シニア・介護・ヘルスケア (22ソース)
    # ═══════════════════════════════════════════════
    # 日本
    "介護ニュース Joint": "https://www.joint-kaigo.com/rss/",
    "高齢者住宅新聞": "https://www.koureisha-jutaku.com/feed/",
    "ケアマネタイムス": "https://caremanager.jp/feed",
    "みんなの介護": "https://www.minnanokaigo.com/feed/",
    "シルバー産業新聞": "https://www.care-news.jp/feed",
    "日経ヘルスケア": "https://medical.nikkeibp.co.jp/inc/all/healthnews/rss/index.rdf",
    "介護のほんね": "https://www.kaigonohonne.com/feed",
    "CBnews (医療介護)": "https://www.cbnews.jp/rss/index.rdf",
    # 海外シニアリビング
    "Senior Housing News": "https://seniorhousingnews.com/feed/",
    "McKnight's Senior Living": "https://www.mcknightsseniorliving.com/feed/",
    "McKnight's Long-Term Care": "https://www.mcknights.com/feed/",
    "Next Avenue (シニア)": "https://www.nextavenue.org/feed/",
    "Aging Care": "https://www.agingcare.com/feed",
    "Home Health Care News": "https://homehealthcarenews.com/feed/",
    "Skilled Nursing News": "https://skillednursingnews.com/feed/",
    "AARP": "https://www.aarp.org/rss/",
    "AgingInPlace.org": "https://aginginplace.org/feed/",
    # ヘルステック・デジタルヘルス
    "MobiHealthNews": "https://www.mobihealthnews.com/feed",
    "Healthcare IT News": "https://www.healthcareitnews.com/feed",
    "Digital Health Age": "https://digitalhealthage.com/feed/",
    "Fierce Healthcare": "https://www.fiercehealthcare.com/rss",
    "Healthcare Dive": "https://www.healthcaredive.com/feeds/news/",

    # ═══════════════════════════════════════════════
    # 5. M&A・スタートアップ・経営戦略 (28ソース)
    # ═══════════════════════════════════════════════
    # 日本M&A
    "M&A Online": "https://maonline.jp/rss",
    "MARR Online (M&A)": "https://www.marr.jp/rss",
    "M&A Bank": "https://mabank.jp/feed/",
    "ストライク M&A": "https://www.strike.co.jp/feed/",
    "日本M&Aセンター": "https://www.nihon-ma.co.jp/columns/feed/",
    # スタートアップ・VC 日本
    "BRIDGE (スタートアップ)": "https://thebridge.jp/feed",
    "INITIAL (スタートアップDB)": "https://initial.inc/articles/rss",
    "TechCrunch Japan": "https://jp.techcrunch.com/feed/",
    # スタートアップ・VC グローバル
    "Crunchbase News": "https://news.crunchbase.com/feed/",
    "PitchBook News": "https://pitchbook.com/news/feed",
    "Sifted (EU スタートアップ)": "https://sifted.eu/feed",
    "TechInAsia": "https://www.techinasia.com/feed",
    "KrASIA (アジア)": "https://kr-asia.com/feed",
    "e27 (東南アジア)": "https://e27.co/feed/",
    # 経営・ビジネス戦略 日本
    "NHK ビジネス": "https://www.nhk.or.jp/rss/news/cat3.xml",
    "Harvard Business Review JP": "https://dhbr.diamond.jp/list/feed/rss",
    "日経ビジネス": "https://business.nikkei.com/rss/sns/nb.rdf",
    # 経営・ビジネス グローバル
    "Financial Times": "https://www.ft.com/rss/home",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Mergermarket": "https://www.mergermarket.com/rss",
    "Harvard Business Review": "https://hbr.org/feed",
}

# カテゴリ定義（UIとanalyzerで共用）
CATEGORIES = {
    "🌍 すべて": None,
    "🌋 再エネ・地熱・脱炭素": [
        "スマート", "環境ビジネス", "自然エネ", "経産省", "電気新聞",
        "ThinkGeo", "Geothermal",
        "次世代地熱", "Closed-Loop", "Enhanced Geothermal", "Eavor", "Fervo", "ふるさと熱電",
        "PV Magazine", "Clean", "Electrek", "Renewable", "Energy Voice",
        "Carbon Brief", "OIL", "Utility Dive", "Energy Monitor",
        "Canary", "Recharge", "S&P Global", "Hydrogen", "Energy Storage",
        "Asia Power", "Nikkei Asia",
    ],
    "🌱 カーボンクレジット・ESG": [
        "ESG", "Sustainable", "環境省", "サステナブル", "日経ESG",
        "GreenBiz", "CDP", "Climate Home", "Carbon Pulse", "Eco-Business",
        "Responsible Investor", "ESG Today", "Sustainable Brands",
        "Climate Action", "UNFCCC", "Voluntary Carbon", "IETA", "Gold Standard",
    ],
    "🤖 AI・テクノロジー": [
        "ITmedia AI", "AINOW", "Ledge", "ASCII", "日経 XTECH",
        "TechCrunch", "VentureBeat", "MIT Tech", "Verge AI", "Ars Technica",
        "Wired", "AI News", "Hacker News", "The Information", "Semafor", "404 Media",
        "Google AI", "OpenAI", "Anthropic", "Microsoft AI", "NVIDIA", "Meta AI",
        "Amazon Science", "Apple ML", "Samsung AI",
        "DeepMind", "Hugging Face", "Papers With Code", "Towards Data", "Synced",
    ],
    "👴 シニア・介護": [
        "介護", "高齢者", "ケアマネ", "みんなの介護", "シルバー", "日経ヘルス",
        "ほんね", "CBnews",
        "Senior", "McKnight", "Next Avenue", "Aging", "Home Health",
        "Skilled Nursing", "AARP", "AgingInPlace",
        "MobiHealth", "Healthcare IT", "Digital Health", "Fierce", "Healthcare Dive",
    ],
    "💼 M&A・経営戦略": [
        "M&A", "MARR", "Bank", "ストライク", "日本M&Aセンター",
        "BRIDGE", "INITIAL", "TechCrunch Japan",
        "Crunchbase", "PitchBook", "Sifted", "TechInAsia", "KrASIA", "e27",
        "NHK ビジネス", "Harvard", "日経ビジネス",
        "Financial Times", "Bloomberg", "Reuters", "Mergermarket",
    ],
}

# RAG設定
RAG_TOP_K = 10
RAG_MAX_CONTEXT_CHARS = 8000

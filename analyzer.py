import google.generativeai as genai
import database
import config


def build_context(articles: list) -> str:
    if not articles:
        return "（関連する蓄積情報はありません）"

    context_parts = []
    total_chars = 0
    for i, article in enumerate(articles, 1):
        text = article["text"]
        source = article.get("source", "")
        published = article.get("published_at", "")[:10]
        url = article.get("url", "")

        entry = f"【記事{i}】({source}, {published})\n{text}"
        if url:
            entry += f"\nURL: {url}"

        if total_chars + len(entry) > config.RAG_MAX_CONTEXT_CHARS:
            break
        context_parts.append(entry)
        total_chars += len(entry)

    return "\n\n".join(context_parts)


SYSTEM_PROMPT = (
    "あなたはTeam Energyグループの経営判断を支援する情報分析アシスタントです。\n"
    "\n"
    "Team Energyの主要事業領域:\n"
    "1. 再生可能エネルギー（特に地熱発電）— ふるさと熱電株式会社\n"
    "2. カーボンクレジット・脱炭素コンサル — Bywill株式会社\n"
    "3. AI活用・DX推進\n"
    "4. シニア向け事業（介護・高齢者住宅）\n"
    "5. M&A・スタートアップ投資・グループ経営\n"
    "\n"
    "回答ルール:\n"
    "- 蓄積された記事情報をもとに、正確かつ簡潔に回答する\n"
    "- Team Energyの事業にとっての影響・示唆を含める\n"
    "- 参考にした記事番号を明示する\n"
    "- 日本語で回答する\n"
    "- 経営者が意思決定に使える具体的な情報を優先する"
)


def _get_model():
    genai.configure(api_key=config.GOOGLE_API_KEY)
    return genai.GenerativeModel(
        model_name=config.GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )


def analyze(query: str, use_rag: bool = True) -> dict:
    """蓄積情報を活用してGeminiで分析・回答"""
    if not config.GOOGLE_API_KEY:
        return {
            "answer": "⚠️ GOOGLE_API_KEY が設定されていません。\n\n"
                      "Streamlit CloudのSettings → Secretsに以下を追加してください:\n"
                      "```\nGOOGLE_API_KEY = \"AIzaSy...\"\n```",
            "sources": [],
        }

    sources = []
    context = ""
    if use_rag:
        sources = database.search_articles(query)
        context = build_context(sources)

    if context:
        user_message = (
            f"以下は蓄積された関連情報です:\n\n{context}\n\n"
            f"---\n\n上記の情報を踏まえて、以下の質問に回答してください:\n{query}"
        )
    else:
        user_message = query

    try:
        model = _get_model()
        response = model.generate_content(user_message)
        answer = response.text
    except Exception as e:
        answer = f"⚠️ Gemini APIエラー: {type(e).__name__}\n\n再度お試しください。"

    return {
        "answer": answer,
        "sources": sources,
    }


def summarize_in_japanese(title: str, summary: str, source: str = "") -> str:
    """英語記事を日本語で要約"""
    if not config.GOOGLE_API_KEY:
        return ""
    try:
        model = _get_model()
        prompt = (
            f"以下の英語ニュース記事を日本語で3行以内に要約してください。\n"
            f"Team Energyの事業（地熱発電・カーボンクレジット・AI・シニア・M&A）に"
            f"関連する示唆があれば一言添えてください。\n\n"
            f"タイトル: {title}\n"
            f"内容: {summary}\n"
            f"ソース: {source}"
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return ""

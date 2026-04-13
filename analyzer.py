import anthropic
import database
import config


def build_context(articles: list) -> str:
    """検索結果の記事をコンテキスト文字列にまとめる"""
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


def analyze(query: str, use_rag: bool = True) -> dict:
    """蓄積情報を活用してClaudeで分析・回答"""
    if not config.ANTHROPIC_API_KEY:
        return {
            "answer": "⚠️ ANTHROPIC_API_KEY が設定されていません。\n\n"
                      "環境変数に設定してください:\n"
                      "```\nexport ANTHROPIC_API_KEY=sk-ant-...\n```",
            "sources": [],
        }

    # RAG: 関連記事を検索
    sources = []
    context = ""
    if use_rag:
        sources = database.search_articles(query)
        context = build_context(sources)

    # プロンプト構築
    system_prompt = (
        "あなたはエグゼクティブ向けの情報分析アシスタントです。\n"
        "蓄積された情報をもとに、正確かつ簡潔に回答してください。\n"
        "情報源がある場合は、どの記事を参考にしたか明示してください。\n"
        "日本語で回答してください。"
    )

    if context:
        user_message = (
            f"以下は蓄積された関連情報です:\n\n{context}\n\n"
            f"---\n\n上記の情報を踏まえて、以下の質問に回答してください:\n{query}"
        )
    else:
        user_message = query

    # Claude API呼び出し
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    answer = response.content[0].text

    return {
        "answer": answer,
        "sources": sources,
    }

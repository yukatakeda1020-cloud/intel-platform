import streamlit as st
import database
import collector
import analyzer

# ページ設定
st.set_page_config(
    page_title="Intel Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .article-card {
        border-left: 3px solid #1a73e8;
        padding-left: 12px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ----- サイドバー -----
with st.sidebar:
    st.markdown("## 📡 情報収集")

    if st.button("🔄 ニュースを収集", use_container_width=True, type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(pct, msg):
            progress_bar.progress(pct)
            status_text.text(msg)

        results = collector.collect_all_feeds(progress_callback=update_progress)

        total_new = sum(r["new"] for r in results)
        total_skipped = sum(r["skipped"] for r in results)
        total_errors = sum(r["errors"] for r in results)

        st.success(f"✅ 収集完了: 新規 {total_new}件 / スキップ {total_skipped}件")
        if total_errors > 0:
            st.warning(f"⚠️ エラー: {total_errors}件")

        with st.expander("詳細を見る"):
            for r in results:
                if r["new"] > 0:
                    st.write(f"📰 {r['name']}: +{r['new']}件")

    st.divider()

    # 蓄積状況
    st.markdown("## 📊 蓄積状況")
    try:
        article_count = database.get_article_count()
        st.metric("蓄積記事数", f"{article_count:,}件")

        source_stats = database.get_source_stats()
        if source_stats:
            st.markdown("**ソース別:**")
            for source, count in list(source_stats.items())[:10]:
                st.write(f"• {source}: {count}件")
    except Exception:
        st.info("まだ記事が蓄積されていません")

    st.divider()
    st.markdown("## ⚙️ 設定")
    st.caption(f"モデル: {analyzer.config.CLAUDE_MODEL}")
    api_key_set = bool(analyzer.config.ANTHROPIC_API_KEY)
    st.caption(f"API Key: {'✅ 設定済み' if api_key_set else '❌ 未設定'}")

# ----- メインエリア -----
st.markdown('<div class="main-header">🔍 Intel Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">パーソナル情報蓄積・分析プラットフォーム</div>', unsafe_allow_html=True)

# タブ切り替え
tab_chat, tab_news = st.tabs(["💬 チャット分析", "📰 最新ニュース"])

# ----- チャットタブ -----
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📎 参照ソース ({len(msg['sources'])}件)"):
                    for src in msg["sources"]:
                        source_name = src.get("source", "")
                        url = src.get("url", "")
                        pub = src.get("published_at", "")[:10]
                        if url:
                            st.markdown(f"• [{source_name}]({url}) ({pub})")
                        else:
                            st.write(f"• {source_name} ({pub})")

    if prompt := st.chat_input("蓄積情報について質問してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("分析中..."):
                result = analyzer.analyze(prompt)

            st.markdown(result["answer"])

            sources = result.get("sources", [])
            if sources:
                with st.expander(f"📎 参照ソース ({len(sources)}件)"):
                    for src in sources:
                        source_name = src.get("source", "")
                        url = src.get("url", "")
                        pub = src.get("published_at", "")[:10]
                        if url:
                            st.markdown(f"• [{source_name}]({url}) ({pub})")
                        else:
                            st.write(f"• {source_name} ({pub})")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": sources,
        })

# ----- ニュースタブ -----
with tab_news:
    try:
        source_stats = database.get_source_stats()

        # カテゴリ分類
        categories = {
            "🌍 すべて": None,
            "⚡ エネルギー": ["OILPRICE", "Renewable", "CleanTechnica", "Greentech", "Energy Voice",
                          "PV Magazine", "Electrek", "Carbon Brief", "環境ビジネス", "スマート", "自然エネルギー"],
            "🤖 AI": ["TechCrunch", "Hacker", "MIT Tech", "VentureBeat", "Verge AI", "Ars Technica",
                     "AI News", "Google AI", "OpenAI", "Anthropic", "ITmedia AI", "Ledge", "AINOW"],
            "👴 シニア": ["介護", "高齢者", "ケアマネ", "シルバー", "みんなの介護",
                       "McKnight", "Aging", "Senior Housing", "Next Avenue", "日経ヘルス"],
            "📺 総合": ["NHK", "Yahoo!", "BBC", "Reuters"],
        }

        # カテゴリ選択
        col_filter1, col_filter2 = st.columns([2, 3])
        with col_filter1:
            selected_category = st.selectbox("カテゴリ", list(categories.keys()))
        with col_filter2:
            keyword_filter = st.text_input("🔍 キーワード検索", placeholder="例: 再生可能エネルギー")

        # カテゴリに該当するソースを特定
        cat_keywords = categories[selected_category]

        def match_category(source_name, keywords):
            if keywords is None:
                return True
            return any(k.lower() in source_name.lower() for k in keywords)

        # 記事取得
        if keyword_filter:
            articles = database.search_articles(keyword_filter, top_k=50)
            display_articles = []
            for a in articles:
                display_articles.append({
                    "title": a["text"].split("\n")[0],
                    "summary": a["text"].split("\n")[1] if "\n" in a["text"] else "",
                    "url": a.get("url", ""),
                    "source": a.get("source", ""),
                    "published_at": a.get("published_at", ""),
                })
        else:
            all_articles = database.get_recent_articles(200)
            display_articles = [a for a in all_articles if match_category(a.get("source", ""), cat_keywords)]

        # 件数表示
        st.caption(f"表示: {len(display_articles)}件")

        # 記事一覧
        if display_articles:
            for article in display_articles[:50]:
                col1, col2 = st.columns([5, 1])
                with col1:
                    title = article.get("title", "")
                    # タイトルから [ソース名] プレフィックスを除去
                    if title.startswith("["):
                        bracket_end = title.find("]")
                        if bracket_end > 0:
                            title = title[bracket_end + 1:].strip()
                    url = article.get("url", "")
                    if url:
                        st.markdown(f"**[{title}]({url})**")
                    else:
                        st.markdown(f"**{title}**")
                    summary = article.get("summary", "")
                    if summary:
                        st.caption(summary[:150] + "..." if len(summary) > 150 else summary)
                with col2:
                    src = article.get("source", "")
                    st.caption(f"📰 {src}")
                    pub = article.get("published_at", "")
                    if pub:
                        st.caption(pub[:10])
                st.divider()
        else:
            st.info("該当する記事がありません。")
    except Exception as e:
        st.info("まだ記事がありません。サイドバーの「ニュースを収集」ボタンで記事を取得してください。")

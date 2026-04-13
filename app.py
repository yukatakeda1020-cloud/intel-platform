import streamlit as st
import database
import collector
import analyzer

# ページ設定
st.set_page_config(
    page_title="Intel Platform | Team Energy",
    page_icon="⚡",
    layout="centered",  # centeredでスマホ対応
    initial_sidebar_state="collapsed",  # スマホではサイドバー閉じる
)

# スマホ対応CSS
st.markdown("""
<style>
    /* スマホ対応 */
    .block-container {
        padding: 1rem 1rem !important;
        max-width: 100% !important;
    }
    /* ヘッダー */
    .main-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1a1a2e;
    }
    .sub-title {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 1rem;
    }
    /* 記事カード */
    .article-source {
        font-size: 0.7rem;
        color: #1565c0;
        background: #e3f2fd;
        padding: 1px 6px;
        border-radius: 3px;
        display: inline-block;
    }
    .article-date {
        font-size: 0.7rem;
        color: #999;
    }
    /* サイドバーの幅 */
    [data-testid="stSidebar"] {
        min-width: 250px;
        max-width: 300px;
    }
    /* ボタンサイズ */
    .stButton > button {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ----- ヘッダー -----
st.markdown('<div class="main-title">⚡ Intel Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Team Energy | 情報蓄積・分析</div>', unsafe_allow_html=True)

# ----- タブ -----
tab_news, tab_chat, tab_collect = st.tabs(["📰 ニュース", "💬 分析", "📡 収集"])

# ----- 収集タブ -----
with tab_collect:
    st.markdown("### 📡 ニュース収集")

    if st.button("🔄 最新ニュースを収集", use_container_width=True, type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(pct, msg):
            progress_bar.progress(pct)
            status_text.text(msg)

        results = collector.collect_all_feeds(progress_callback=update_progress)

        total_new = sum(r["new"] for r in results)
        total_skipped = sum(r["skipped"] for r in results)
        total_errors = sum(r["errors"] for r in results)

        st.success(f"✅ 新規 {total_new}件 / スキップ {total_skipped}件")
        if total_errors > 0:
            st.warning(f"⚠️ エラー: {total_errors}件")

        with st.expander("詳細"):
            for r in results:
                if r["new"] > 0:
                    st.write(f"📰 {r['name']}: +{r['new']}件")

    st.divider()

    # 蓄積状況
    st.markdown("### 📊 蓄積状況")
    try:
        article_count = database.get_article_count()
        st.metric("蓄積記事数", f"{article_count:,}件")

        source_stats = database.get_source_stats()
        if source_stats:
            with st.expander("ソース別の内訳"):
                for source, count in source_stats.items():
                    st.write(f"• {source}: {count}件")
    except Exception:
        st.info("まだ記事がありません。上のボタンで収集してください。")

    st.divider()
    st.markdown("### ⚙️ 設定")
    api_key_set = bool(analyzer.config.ANTHROPIC_API_KEY)
    st.write(f"モデル: `{analyzer.config.CLAUDE_MODEL}`")
    st.write(f"API Key: {'✅ 設定済み' if api_key_set else '❌ 未設定'}")

# ----- ニュースタブ -----
with tab_news:
    try:
        # カテゴリ分類（Team Energy向け）
        categories = {
            "🌍 すべて": None,
            "⚡ エネルギー・脱炭素": ["スマート", "環境", "自然エネ", "PV", "Clean", "Carbon",
                               "Electrek", "Renewable", "OIL", "Energy Voice", "GreenBiz", "ESG"],
            "🚀 スタートアップ・経営": ["TechCrunch", "BRIDGE", "PR TIMES", "DIAMOND", "東洋経済"],
            "🤖 AI・テクノロジー": ["MIT Tech", "VentureBeat", "AI News", "ITmedia AI",
                              "Google AI", "AINOW"],
            "🏘️ 地方創生": ["地方創生", "NHK"],
            "👴 シニア・介護": ["介護", "高齢者", "Senior", "Next Avenue"],
        }

        # フィルターUI（スマホでも見やすい1列）
        selected_category = st.selectbox("カテゴリで絞り込み", list(categories.keys()))
        keyword_filter = st.text_input("🔍 キーワード検索", placeholder="例: 地熱発電, AI活用")

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
                lines = a["text"].split("\n")
                display_articles.append({
                    "title": lines[0] if lines else "",
                    "summary": lines[1] if len(lines) > 1 else "",
                    "url": a.get("url", ""),
                    "source": a.get("source", ""),
                    "published_at": a.get("published_at", ""),
                })
        else:
            all_articles = database.get_recent_articles(200)
            display_articles = [a for a in all_articles if match_category(a.get("source", ""), cat_keywords)]

        st.caption(f"{len(display_articles)}件")

        # 記事一覧（スマホ対応：1カラム表示）
        if display_articles:
            for article in display_articles[:50]:
                title = article.get("title", "")
                if title.startswith("["):
                    bracket_end = title.find("]")
                    if bracket_end > 0:
                        title = title[bracket_end + 1:].strip()

                url = article.get("url", "")
                src = article.get("source", "")
                pub = article.get("published_at", "")[:10]

                # ソースタグ + 日付
                meta = f'<span class="article-source">{src}</span> <span class="article-date">{pub}</span>'
                st.markdown(meta, unsafe_allow_html=True)

                # タイトル（リンク付き）
                if url:
                    st.markdown(f"**[{title}]({url})**")
                else:
                    st.markdown(f"**{title}**")

                # 要約
                summary = article.get("summary", "")
                if summary:
                    display_summary = summary[:120] + "..." if len(summary) > 120 else summary
                    st.caption(display_summary)

                st.markdown("---")
        else:
            st.info("該当する記事がありません。「📡 収集」タブでニュースを取得してください。")
    except Exception:
        st.info("まだ記事がありません。「📡 収集」タブでニュースを取得してください。")

# ----- チャット分析タブ -----
with tab_chat:
    st.markdown("### 💬 蓄積情報を分析")
    st.caption("収集したニュースをもとにAIが回答します")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📎 参照 ({len(msg['sources'])}件)"):
                    for src in msg["sources"]:
                        url = src.get("url", "")
                        name = src.get("source", "")
                        if url:
                            st.markdown(f"• [{name}]({url})")
                        else:
                            st.write(f"• {name}")

    if prompt := st.chat_input("質問してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("分析中..."):
                result = analyzer.analyze(prompt)

            st.markdown(result["answer"])

            sources = result.get("sources", [])
            if sources:
                with st.expander(f"📎 参照 ({len(sources)}件)"):
                    for src in sources:
                        url = src.get("url", "")
                        name = src.get("source", "")
                        if url:
                            st.markdown(f"• [{name}]({url})")
                        else:
                            st.write(f"• {name}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": sources,
        })

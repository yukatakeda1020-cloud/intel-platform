import streamlit as st
import database
import collector
import analyzer

st.set_page_config(
    page_title="Intel Platform | Team Energy",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# スマホ最適化CSS
st.markdown("""
<style>
    .block-container { padding: 0.5rem 0.8rem !important; }
    [data-testid="stSidebar"] { display: none; }
    h1, h2, h3 { margin-top: 0.5rem !important; }

    /* 記事カード */
    .news-card {
        border-left: 3px solid #1a73e8;
        padding: 8px 12px;
        margin-bottom: 12px;
        background: #fafafa;
        border-radius: 0 6px 6px 0;
    }
    .news-card a {
        color: #1a1a2e;
        text-decoration: none;
        font-weight: bold;
        font-size: 0.95rem;
        line-height: 1.4;
        display: block;
    }
    .news-card a:hover { color: #1a73e8; }
    .news-meta {
        font-size: 0.7rem;
        color: #888;
        margin-top: 4px;
    }
    .news-tag {
        background: #e3f2fd;
        color: #1565c0;
        padding: 1px 6px;
        border-radius: 3px;
        font-size: 0.65rem;
        margin-right: 4px;
    }
    .news-summary {
        font-size: 0.8rem;
        color: #555;
        margin-top: 4px;
        line-height: 1.3;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("## ⚡ Intel Platform")
st.caption("Team Energy | 情報蓄積・分析")

# タブ
tab_news, tab_chat, tab_collect = st.tabs(["📰 ニュース", "💬 分析", "📡 収集"])

# ===== ニュースタブ =====
with tab_news:
    try:
        categories = analyzer.config.CATEGORIES
        selected_category = st.selectbox("カテゴリ", list(categories.keys()), label_visibility="collapsed")
        keyword_filter = st.text_input("🔍 キーワード", placeholder="例: 地熱発電, カーボンクレジット", label_visibility="collapsed")

        cat_keywords = categories[selected_category]

        def match_cat(src, keys):
            if keys is None:
                return True
            return any(k.lower() in src.lower() for k in keys)

        if keyword_filter:
            results = database.search_articles(keyword_filter, top_k=50)
            display = []
            for a in results:
                lines = a["text"].split("\n")
                title = lines[0] if lines else ""
                if title.startswith("["):
                    idx = title.find("]")
                    if idx > 0:
                        title = title[idx + 1:].strip()
                display.append({
                    "title": title,
                    "summary": lines[1] if len(lines) > 1 else "",
                    "url": a.get("url", ""),
                    "source": a.get("source", ""),
                    "published_at": a.get("published_at", ""),
                })
        else:
            all_articles = database.get_recent_articles(200)
            display = [a for a in all_articles if match_cat(a.get("source", ""), cat_keywords)]

        st.caption(f"{len(display)}件")

        # 記事をHTMLカードで表示（タップしやすく）
        for article in display[:50]:
            title = article.get("title", "")
            if title.startswith("["):
                idx = title.find("]")
                if idx > 0:
                    title = title[idx + 1:].strip()

            url = article.get("url", "")
            src = article.get("source", "")
            pub = article.get("published_at", "")[:10]
            summary = article.get("summary", "")
            if summary and len(summary) > 100:
                summary = summary[:100] + "..."

            # HTMLカードでリンクをタップ可能に
            link_html = f'<a href="{url}" target="_blank">{title}</a>' if url else f'<span style="font-weight:bold">{title}</span>'
            summary_html = f'<div class="news-summary">{summary}</div>' if summary else ""

            card = f'''<div class="news-card">
                {link_html}
                <div class="news-meta"><span class="news-tag">{src}</span> {pub}</div>
                {summary_html}
            </div>'''
            st.markdown(card, unsafe_allow_html=True)

        if not display:
            st.info("記事がありません。「📡 収集」タブでニュースを取得してください。")

    except Exception:
        st.info("「📡 収集」タブでニュースを取得してください。")

# ===== チャット分析タブ =====
with tab_chat:
    st.caption("蓄積ニュースをもとにAIが分析・回答します")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📎 参照 ({len(msg['sources'])}件)"):
                    for s in msg["sources"]:
                        u = s.get("url", "")
                        n = s.get("source", "")
                        if u:
                            st.markdown(f"• [{n}]({u})")
                        else:
                            st.write(f"• {n}")

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
                    for s in sources:
                        u = s.get("url", "")
                        n = s.get("source", "")
                        if u:
                            st.markdown(f"• [{n}]({u})")
                        else:
                            st.write(f"• {n}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": sources,
        })

# ===== 収集タブ =====
with tab_collect:
    if st.button("🔄 最新ニュースを収集", use_container_width=True, type="primary"):
        progress = st.progress(0)
        status = st.empty()

        def cb(pct, msg):
            progress.progress(pct)
            status.text(msg)

        results = collector.collect_all_feeds(progress_callback=cb)
        total_new = sum(r["new"] for r in results)
        total_err = sum(r["errors"] for r in results)

        st.success(f"✅ 新規 {total_new}件を収集しました")
        if total_err:
            st.warning(f"⚠️ {total_err}件のフィードでエラー")

        with st.expander("詳細"):
            for r in results:
                if r["new"] > 0:
                    st.write(f"• {r['name']}: +{r['new']}件")

        st.info("👆「📰 ニュース」タブに切り替えて記事を読めます")

    st.divider()
    st.markdown("### 📊 蓄積状況")
    try:
        count = database.get_article_count()
        st.metric("蓄積記事数", f"{count:,}件")
        stats = database.get_source_stats()
        if stats:
            with st.expander("ソース別の内訳"):
                for src, cnt in stats.items():
                    st.write(f"• {src}: {cnt}件")
    except Exception:
        st.info("まだ記事がありません")

    st.divider()
    api_ok = bool(analyzer.config.GOOGLE_API_KEY)
    st.caption(f"Gemini API: {'✅ 設定済み' if api_ok else '❌ 未設定（分析タブに必要）'}")

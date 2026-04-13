import streamlit as st
import database
import collector
import analyzer
from datetime import datetime

# 新テーブルが確実に作成されるよう再初期化
database.init_db()

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
    .news-card {
        border-left: 3px solid #1a73e8;
        padding: 8px 12px;
        margin-bottom: 12px;
        background: #fafafa;
        border-radius: 0 6px 6px 0;
    }
    .news-card a {
        color: #1a1a2e; text-decoration: none;
        font-weight: bold; font-size: 0.95rem;
        line-height: 1.4; display: block;
    }
    .news-card a:hover { color: #1a73e8; }
    .news-meta { font-size: 0.7rem; color: #888; margin-top: 4px; }
    .news-tag {
        background: #e3f2fd; color: #1565c0;
        padding: 1px 6px; border-radius: 3px;
        font-size: 0.65rem; margin-right: 4px;
    }
    .news-summary { font-size: 0.8rem; color: #555; margin-top: 4px; line-height: 1.3; }
    .fav-card { border-left: 3px solid #f5a623; }
    .memo-card {
        border-left: 3px solid #4caf50;
        padding: 8px 12px; margin-bottom: 10px;
        background: #f9fdf9; border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== 初回アクセス時に自動収集 =====
try:
    if database.get_article_count() == 0 and "auto_collected" not in st.session_state:
        st.session_state.auto_collected = True
        with st.spinner("⚡ 初回ニュース収集中...（1〜2分かかります）"):
            results = collector.collect_all_feeds()
            total_new = sum(r["new"] for r in results)
            total_err = sum(r["errors"] for r in results)
            database.log_auto_collect(total_new, total_err)
        if total_new > 0:
            st.toast(f"⚡ 自動収集完了: {total_new}件", icon="📡")
            st.rerun()
    elif database.should_auto_collect(interval_hours=12):
        results = collector.collect_all_feeds()
        total_new = sum(r["new"] for r in results)
        total_err = sum(r["errors"] for r in results)
        database.log_auto_collect(total_new, total_err)
        if total_new > 0:
            st.toast(f"⚡ 自動収集: {total_new}件の新着", icon="📡")
except Exception:
    pass

# ヘッダー
st.markdown("## ⚡ Intel Platform")
st.caption("Team Energy | 情報蓄積・分析")

# タブ
tab_news, tab_chat, tab_dash, tab_memo, tab_fav, tab_collect = st.tabs(
    ["📰 ニュース", "💬 分析", "📊 トレンド", "📝 メモ", "⭐ お気に入り", "📡 収集"]
)


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
                    "id": "", "title": title,
                    "summary": lines[1] if len(lines) > 1 else "",
                    "url": a.get("url", ""), "source": a.get("source", ""),
                    "published_at": a.get("published_at", ""),
                    "language": "unknown",
                })
        else:
            all_articles = database.get_recent_articles(200)
            display = [a for a in all_articles if match_cat(a.get("source", ""), cat_keywords)]

        # お気に入りID一覧を取得
        fav_ids = database.get_favorite_ids()

        st.caption(f"{len(display)}件")

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
            art_id = article.get("id", "")
            lang = article.get("language", "unknown")

            if summary and len(summary) > 100:
                summary = summary[:100] + "..."

            link_html = f'<a href="{url}" target="_blank">{title}</a>' if url else f'<span style="font-weight:bold">{title}</span>'
            summary_html = f'<div class="news-summary">{summary}</div>' if summary else ""

            card = f'''<div class="news-card">
                {link_html}
                <div class="news-meta"><span class="news-tag">{src}</span> {pub}</div>
                {summary_html}
            </div>'''
            st.markdown(card, unsafe_allow_html=True)

            # お気に入り＆翻訳ボタン（同一行）
            if art_id:
                col_fav, col_trans = st.columns([1, 1])
                with col_fav:
                    is_fav = art_id in fav_ids
                    label = "⭐ 保存済み" if is_fav else "☆ 保存"
                    if st.button(label, key=f"fav_{art_id}", use_container_width=True):
                        result = database.toggle_favorite(art_id)
                        st.rerun()
                with col_trans:
                    if lang == "en" or (not any('\u3040' <= c <= '\u9fff' for c in title)):
                        if st.button("🌐 日本語要約", key=f"tr_{art_id}", use_container_width=True):
                            with st.spinner("翻訳中..."):
                                jp = analyzer.summarize_in_japanese(title, summary, src)
                            if jp:
                                st.info(jp)

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
            "role": "assistant", "content": result["answer"], "sources": sources,
        })


# ===== トレンド分析ダッシュボード =====
with tab_dash:
    st.markdown("### 📊 トレンド分析")
    try:
        # カテゴリ別の記事数
        cat_counts = database.get_category_counts()
        if cat_counts:
            st.markdown("**カテゴリ別蓄積数**")
            import json
            # 横棒グラフ風にテキスト表示
            max_count = max(cat_counts.values()) if cat_counts else 1
            for cat, count in cat_counts.items():
                bar_len = int(count / max_count * 20)
                bar = "█" * bar_len
                st.markdown(f"{cat} **{count}件** {bar}")

        st.divider()

        # 日別収集推移
        daily = database.get_daily_total(days=14)
        if daily:
            st.markdown("**過去14日間の収集推移**")
            chart_data = {d["date"]: d["count"] for d in daily}
            st.bar_chart(chart_data)

        st.divider()

        # ソース別Top10
        stats = database.get_source_stats()
        if stats:
            st.markdown("**ソース別 Top10**")
            top10 = dict(list(stats.items())[:10])
            st.bar_chart(top10)

        # 総蓄積数
        total = database.get_article_count()
        st.metric("蓄積記事総数", f"{total:,}件")

        # 最終自動収集
        last = database.get_last_auto_collect()
        if last:
            st.caption(f"最終自動収集: {last['collected_at'][:16]} (新規{last['new_count']}件)")

    except Exception as e:
        st.info("データが不足しています。ニュースを収集してください。")


# ===== メモタブ =====
with tab_memo:
    st.markdown("### 📝 メモ・非公開情報")
    st.caption("会議メモ、社内情報、アイデアなどを蓄積")

    # メモ入力フォーム
    with st.expander("✏️ 新しいメモを追加", expanded=False):
        memo_title = st.text_input("タイトル", placeholder="例: 経営会議メモ 2026/4")
        memo_cat = st.selectbox("カテゴリ", ["全般", "エネルギー", "カーボンクレジット", "AI", "シニア", "M&A", "その他"])
        memo_content = st.text_area("内容", height=150, placeholder="メモの内容を入力...")
        if st.button("💾 保存", use_container_width=True):
            if memo_title and memo_content:
                database.save_memo(memo_title, memo_content, memo_cat)
                st.success("✅ メモを保存しました")
                st.rerun()
            else:
                st.warning("タイトルと内容を入力してください")

    st.divider()

    # メモ一覧
    memos = database.get_memos()
    if memos:
        for memo in memos:
            card = f'''<div class="memo-card">
                <strong>{memo["title"]}</strong>
                <div class="news-meta"><span class="news-tag">{memo.get("category", "")}</span> {memo["created_at"][:10]}</div>
                <div class="news-summary">{memo["content"][:200]}{"..." if len(memo["content"]) > 200 else ""}</div>
            </div>'''
            st.markdown(card, unsafe_allow_html=True)
            if st.button("🗑️ 削除", key=f"del_memo_{memo['id']}"):
                database.delete_memo(memo["id"])
                st.rerun()
    else:
        st.info("まだメモがありません。上の「新しいメモを追加」から作成できます。")


# ===== お気に入りタブ =====
with tab_fav:
    st.markdown("### ⭐ お気に入り記事")
    st.caption("ニュースタブで「☆ 保存」した記事が表示されます")

    try:
        favs = database.get_favorite_articles()
        if favs:
            st.caption(f"{len(favs)}件保存中")
            for article in favs:
                title = article.get("title", "")
                url = article.get("url", "")
                src = article.get("source", "")
                pub = article.get("published_at", "")[:10]
                summary = article.get("summary", "")
                if summary and len(summary) > 100:
                    summary = summary[:100] + "..."

                link_html = f'<a href="{url}" target="_blank">{title}</a>' if url else f'<span style="font-weight:bold">{title}</span>'
                summary_html = f'<div class="news-summary">{summary}</div>' if summary else ""

                card = f'''<div class="news-card fav-card">
                    {link_html}
                    <div class="news-meta"><span class="news-tag">{src}</span> {pub}</div>
                    {summary_html}
                </div>'''
                st.markdown(card, unsafe_allow_html=True)

                if st.button("⭐ 解除", key=f"unfav_{article['id']}"):
                    database.toggle_favorite(article["id"])
                    st.rerun()
        else:
            st.info("お気に入り記事がありません。\n\n📰 ニュースタブで「☆ 保存」ボタンを押すと、ここに表示されます。")
    except Exception:
        st.info("お気に入り記事がありません。")


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
        database.log_auto_collect(total_new, total_err)

        st.success(f"✅ 新規 {total_new}件を収集しました")
        if total_err:
            st.warning(f"⚠️ {total_err}件のフィードでエラー")

        with st.expander("詳細"):
            for r in results:
                if r["new"] > 0:
                    st.write(f"• {r['name']}: +{r['new']}件")

    st.divider()
    st.markdown("### 📊 蓄積状況")
    try:
        count = database.get_article_count()
        memo_count = len(database.get_memos())
        fav_count = len(database.get_favorite_articles())

        col1, col2, col3 = st.columns(3)
        col1.metric("記事", f"{count:,}")
        col2.metric("メモ", f"{memo_count}")
        col3.metric("お気に入り", f"{fav_count}")

        stats = database.get_source_stats()
        if stats:
            with st.expander("ソース別の内訳"):
                for src, cnt in stats.items():
                    st.write(f"• {src}: {cnt}件")
    except Exception:
        st.info("まだ記事がありません")

    st.divider()

    # 自動収集設定
    st.markdown("### ⏰ 自動収集")
    last = database.get_last_auto_collect()
    if last:
        st.caption(f"最終: {last['collected_at'][:16]} (+{last['new_count']}件)")
    st.info("12時間ごとにアクセス時に自動収集されます")

    st.divider()
    api_ok = bool(analyzer.config.GOOGLE_API_KEY)
    st.caption(f"Gemini API: {'✅ 設定済み' if api_ok else '❌ 未設定（分析タブに必要）'}")

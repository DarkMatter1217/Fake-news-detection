import streamlit as st
from services.news_api_service import get_news_service
from utils.animations import show_spyglass_loader
from datetime import datetime
import time

def show_current_news():
    st.markdown("## 📰 Current News Headlines")
    st.markdown("Stay updated with the latest news from trusted sources worldwide.")
    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox(
            "Select Country:",
            options=['us', 'gb', 'ca', 'au', 'in', 'de', 'fr', 'jp', 'br', 'mx'],
            format_func=lambda x: {
                'us': '🇺🇸 United States',
                'gb': '🇬🇧 United Kingdom', 
                'ca': '🇨🇦 Canada',
                'au': '🇦🇺 Australia',
                'in': '🇮🇳 India',
                'de': '🇩🇪 Germany',
                'fr': '🇫🇷 France',
                'jp': '🇯🇵 Japan',
                'br': '🇧🇷 Brazil',
                'mx': '🇲🇽 Mexico'
            }.get(x, x)
        )
    with col2:
        category = st.selectbox(
            "Select Category:",
            options=[None, 'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'],
            format_func=lambda x: 'All Categories' if x is None else x.title()
        )
    with col3:
        articles_count = st.selectbox(
            "Number of Articles:",
            options=[20, 50, 100],
            index=2
        )
    if st.button("🔄 Refresh News", type="primary"):
        fetch_and_display_news_with_animation(country, category, articles_count)
    if 'news_loaded' not in st.session_state:
        st.session_state.news_loaded = True
        fetch_and_display_news_with_animation(country, category, articles_count)

def fetch_and_display_news_with_animation(country, category, articles_count):
    loader_placeholder = show_spyglass_loader("📡 Connecting to global news networks...")
    time.sleep(1.5)
    loader_placeholder.empty()
    loader_placeholder = show_spyglass_loader("📡 Fetching latest headlines...")
    time.sleep(1)
    news_service = get_news_service()
    articles = news_service.fetch_top_headlines(
        country=country, 
        category=category, 
        page_size=articles_count
    )
    loader_placeholder.empty()
    loader_placeholder = show_spyglass_loader("📡 Processing article data...")
    time.sleep(1)
    loader_placeholder.empty()
    if not articles:
        st.error("Failed to fetch news articles. Please try again later.")
        return
    st.success(f"✅ Loaded {len(articles)} articles")
    for i, article in enumerate(articles):
        if i % 2 == 0:
            col1, col2 = st.columns(2)
            current_col = col1
        else:
            current_col = col2
        with current_col:
            display_article_card_with_animation(article, i + 1)

def display_article_card_with_animation(article, index):
    with st.container():
        st.markdown(f'<div class="metric-card" style="animation-delay: {index*0.1}s;">', unsafe_allow_html=True)
        if article.get('urlToImage'):
            try:
                st.image(article['urlToImage'], use_column_width=True)
            except:
                st.info("📷 Image not available")
        else:
            st.info("📷 No image available")
        st.markdown(f"### {index}. {article.get('title', 'No title')}")
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
        with col2:
            if article.get('publishedAt'):
                pub_date = article['publishedAt'][:10]
                st.caption(f"**Published:** {pub_date}")
        if article.get('description'):
            st.markdown(article['description'])
        if article.get('url'):
            st.markdown(f"[Read Full Article]({article['url']})")
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

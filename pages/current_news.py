import streamlit as st
from services.news_api_service import get_news_service
from datetime import datetime
import requests

def show_current_news():
    """Display current news headlines with proper error handling"""
    
    st.markdown("## 📰 Current News Headlines")
    st.markdown("Stay updated with the latest news from trusted sources worldwide.")
    
    # News filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country = st.selectbox(
            "Select Country:",
            options=['us', 'gb', 'ca', 'au', 'in'],
            format_func=lambda x: {
                'us': '🇺🇸 United States',
                'gb': '🇬🇧 United Kingdom', 
                'ca': '🇨🇦 Canada',
                'au': '🇦🇺 Australia',
                'in': '🇮🇳 India'
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
    
    # Fetch and display news
    if st.button("🔄 Refresh News", type="primary"):
        fetch_and_display_current_news(country, category, articles_count)
    
    # Auto-load news on page load
    if 'current_news_loaded' not in st.session_state:
        st.session_state.current_news_loaded = True
        fetch_and_display_current_news(country, category, articles_count)

def fetch_and_display_current_news(country, category, articles_count):
    """Fetch and display current news using direct API call"""
    
    with st.spinner("📰 Fetching latest headlines..."):
        try:
            # Get news service
            news_service = get_news_service()
            
            # Try to use fetch_top_headlines if it exists, otherwise use alternative
            if hasattr(news_service, 'fetch_top_headlines'):
                articles = news_service.fetch_top_headlines(
                    country=country,
                    category=category,
                    page_size=articles_count
                )
            else:
                # Alternative: Use direct API call
                articles = fetch_headlines_direct(country, category, articles_count)
            
            if articles:
                st.success(f"✅ Loaded {len(articles)} articles")
                display_news_articles(articles)
            else:
                st.warning("⚠️ No articles found. Please try again later.")
                
        except Exception as e:
            st.error(f"❌ Error loading news: {str(e)}")

def fetch_headlines_direct(country, category, articles_count):
    """Direct API call to NewsAPI for headlines"""
    
    try:
        # Try to get API key from news service
        news_service = get_news_service()
        api_key = getattr(news_service, 'api_key', '5857f31b267648b88056c8dc2663c998')
        
        if not api_key or api_key == "5857f31b267648b88056c8dc2663c998":
            return 
        
        # Direct API call to NewsAPI
        url = "https://newsapi.org/v2/top-headlines"
        
        params = {
            'country': country,
            'apiKey': api_key,
            'pageSize': min(articles_count, 100)
        }
        
        if category:
            params['category'] = category
        
        st.info(f"🔍 Fetching {category or 'general'} headlines from {country.upper()}")
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'ok':
            articles = data.get('articles', [])
            
            # Add relevance scores for consistency
            for article in articles:
                article['relevance_score'] = 0.9  # High relevance for top headlines
                article['similarity_score'] = 0.9
                article['score'] = 0.9
            
            return articles
        else:
            st.error(f"NewsAPI Error: {data.get('message', 'Unknown error')}")
            return 
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching headlines: {str(e)}")
        return "No headlines available at the moment. Please try again later."
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return 

def display_news_articles(articles):
    """Display news articles in a clean, readable format"""
    
    if not articles:
        st.info("No articles to display.")
        return
    
    for i, article in enumerate(articles, 1):
        if not article:
            continue
            
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Extract article information
                title = article.get('title', 'No title available')
                description = article.get('description', 'No description available')
                source = article.get('source', {})
                
                # Handle different source formats
                if isinstance(source, dict):
                    source_name = source.get('name', 'Unknown Source')
                else:
                    source_name = str(source)
                
                url = article.get('url', '')
                published_at = article.get('publishedAt', article.get('published_at', ''))
                
                # Format published date
                try:
                    if published_at:
                        if 'T' in published_at:
                            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            formatted_date = pub_date.strftime('%Y-%m-%d %H:%M')
                        else:
                            formatted_date = published_at
                    else:
                        formatted_date = 'Recent'
                except Exception:
                    formatted_date = 'Recent'
                
                # Display article with enhanced styling
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; 
                           border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #1e293b; margin-bottom: 0.5rem;">{i}. {title}</h3>
                    <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        <strong>Source:</strong> {source_name} | <strong>Published:</strong> {formatted_date}
                    </p>
                    <p style="color: #475569; line-height: 1.6; margin-bottom: 1rem;">{description}</p>
                    {f'<a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">🔗 Read full article</a>' if url else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Relevance score and category
                score = article.get('relevance_score', article.get('score', 0.9))
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; text-align: center; 
                           border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: #64748b; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;">RELEVANCE</div>
                    <div style="color: #667eea; font-size: 1.5rem; font-weight: 800;">{score:.2f}</div>
                    <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">📰 Current News</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add separator between articles
        if i < len(articles):
            st.markdown('<hr style="margin: 1.5rem 0; border: 1px solid #e2e8f0;">', unsafe_allow_html=True)


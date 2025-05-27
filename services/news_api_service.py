import requests
import streamlit as st
from datetime import datetime, timedelta
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
import os
load_dotenv()

class NewsAPIService:
    def __init__(self):
        self.api_key = "5857f31b267648b88056c8dc2663c998"
        self.base_url = "https://newsapi.org/v2"
    def fetch_top_headlines(self, country='us', category=None, page_size=100):
        
        if not self.api_key or self.api_key == "your_api_key_here":
            st.warning("NewsAPI key not configured. Using mock data.")
            return self._get_mock_articles()
        
        try:
            url = f"{self.base_url}/top-headlines"
            
            params = {
                'country': country,
                'apiKey': self.api_key,
                'pageSize': min(page_size, 100)
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
                    article['relevance_score'] = 0.9
                    article['similarity_score'] = 0.9
                    article['score'] = 0.9
                
                st.success(f"✅ Fetched {len(articles)} headlines")
                return articles
            else:
                st.error(f"NewsAPI Error: {data.get('message', 'Unknown error')}")
                return self._get_mock_articles()
                
        except Exception as e:
            st.error(f"Error fetching headlines: {str(e)}")
            return self._get_mock_articles()

    def extract_keywords(self, text):
        """Extract keywords from input text for better search"""
        # Remove special characters and convert to lowercase
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        
        # Use TextBlob for basic keyword extraction
        blob = TextBlob(clean_text)
        
        # Get noun phrases and important words
        keywords = []
        
        # Add noun phrases
        for phrase in blob.noun_phrases:
            if len(phrase.split()) <= 3:  # Limit phrase length
                keywords.append(phrase)
        
        # Add important single words (nouns, proper nouns)
        for word, tag in blob.tags:
            if tag in ['NN', 'NNP', 'NNS', 'NNPS'] and len(word) > 3:
                keywords.append(word)
        
        # Remove duplicates and return top keywords
        unique_keywords = list(set(keywords))
        return unique_keywords[:10]  # Limit to top 10 keywords
    
    def fetch_related_articles(self, input_text, max_articles=100):
        """Fetch news articles related to input text using everything endpoint"""
        
        if not self.api_key or self.api_key == "your_api_key_here":
            st.warning("NewsAPI key not configured. Using mock data.")
            return self._get_mock_articles()
        
        try:
            # Extract keywords from input text
            keywords = self.extract_keywords(input_text)
            
            if not keywords:
                # Fallback to first few words if no keywords found
                words = input_text.split()[:5]
                search_query = ' '.join(words)
            else:
                # Use top keywords for search
                search_query = ' OR '.join(keywords[:5])
            
            # Use everything endpoint for broader search
            url = f"{self.base_url}/everything"
            
            # Search in last 30 days for more relevant results
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            params = {
                'q': search_query,
                'apiKey': self.api_key,
                'pageSize': min(max_articles, 100),
                'sortBy': 'relevancy',  # Sort by relevancy instead of publishedAt
                'from': from_date,
                'language': 'en',
                'excludeDomains': 'youtube.com,facebook.com,twitter.com'  # Exclude social media
            }
            
            st.info(f"🔍 Searching for articles related to: {search_query}")
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                articles = data.get('articles', [])
                
                # Filter and score articles based on relevance to input
                scored_articles = self._score_article_relevance(articles, input_text, keywords)
                
                st.success(f"✅ Found {len(scored_articles)} related articles")
                return scored_articles
            else:
                st.error(f"NewsAPI Error: {data.get('message', 'Unknown error')}")
                return self._get_mock_articles()
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching related articles: {str(e)}")
            return self._get_mock_articles()
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return self._get_mock_articles()
    
    def _score_article_relevance(self, articles, input_text, keywords):
        """Score articles based on relevance to input text"""
        
        if not articles:
            return []
        
        scored_articles = []
        
        # Prepare texts for similarity calculation
        input_text_clean = self._clean_text(input_text)
        
        article_texts = []
        for article in articles:
            # Combine title and description for better matching
            title = article.get('title', '') or ''
            description = article.get('description', '') or ''
            content = article.get('content', '') or ''
            
            combined_text = f"{title} {description} {content}"
            article_texts.append(self._clean_text(combined_text))
        
        # Calculate similarity scores using TF-IDF
        try:
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            all_texts = [input_text_clean] + article_texts
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Score articles
            for i, article in enumerate(articles):
                similarity_score = similarities[i]
                
                # Additional scoring factors
                keyword_bonus = self._calculate_keyword_bonus(article, keywords)
                source_bonus = self._calculate_source_bonus(article)
                recency_bonus = self._calculate_recency_bonus(article)
                
                # Combined score
                final_score = (
                    similarity_score * 0.6 +  # 60% similarity
                    keyword_bonus * 0.2 +     # 20% keyword match
                    source_bonus * 0.1 +      # 10% source credibility
                    recency_bonus * 0.1       # 10% recency
                )
                
                # Only include articles with reasonable relevance
                if final_score > 0.1:  # Threshold for relevance
                    article_copy = article.copy()
                    article_copy['relevance_score'] = final_score
                    article_copy['similarity_score'] = similarity_score
                    scored_articles.append(article_copy)
        
        except Exception as e:
            st.warning(f"Error calculating relevance scores: {e}")
            # Fallback: return articles with basic scoring
            for article in articles:
                article_copy = article.copy()
                article_copy['relevance_score'] = 0.5
                article_copy['similarity_score'] = 0.5
                scored_articles.append(article_copy)
        
        # Sort by relevance score (highest first)
        scored_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return scored_articles
    
    def _clean_text(self, text):
        """Clean text for similarity calculation"""
        if not text:
            return ""
        
        # Remove special characters and normalize
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _calculate_keyword_bonus(self, article, keywords):
        """Calculate bonus score based on keyword presence"""
        if not keywords:
            return 0
        
        title = (article.get('title', '') or '').lower()
        description = (article.get('description', '') or '').lower()
        
        combined_text = f"{title} {description}"
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in combined_text:
                matches += 1
        
        return min(matches / len(keywords), 1.0)  # Normalize to 0-1
    
    def _calculate_source_bonus(self, article):
        """Calculate bonus based on source credibility"""
        source_name = article.get('source', {}).get('name', '').lower()
        
        # Trusted news sources (you can expand this list)
        trusted_sources = [
            'reuters', 'bbc', 'associated press', 'cnn', 'npr', 'the guardian',
            'the new york times', 'the washington post', 'abc news', 'cbs news',
            'nbc news', 'fox news', 'usa today', 'wall street journal'
        ]
        
        for trusted in trusted_sources:
            if trusted in source_name:
                return 1.0
        
        return 0.5  # Default score for other sources
    
    def _calculate_recency_bonus(self, article):
        """Calculate bonus based on article recency"""
        try:
            published_at = article.get('publishedAt', '')
            if not published_at:
                return 0.5
            
            # Parse date
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            days_old = (datetime.now().replace(tzinfo=pub_date.tzinfo) - pub_date).days
            
            # More recent articles get higher scores
            if days_old <= 1:
                return 1.0
            elif days_old <= 7:
                return 0.8
            elif days_old <= 30:
                return 0.6
            else:
                return 0.3
        
        except Exception:
            return 0.5
    
    def calculate_confidence_score(self, articles, input_text):
        """Calculate confidence score based on related articles"""
        
        if not articles:
            return 0.0
        
        # Filter articles with good relevance scores
        relevant_articles = [a for a in articles if a.get('relevance_score', 0) > 0.3]
        
        if not relevant_articles:
            return 0.2  # Low confidence if no relevant articles
        
        # Calculate confidence based on multiple factors
        factors = {
            'article_count': min(len(relevant_articles) / 10, 1.0),  # More articles = higher confidence
            'avg_relevance': np.mean([a.get('relevance_score', 0) for a in relevant_articles]),
            'source_diversity': self._calculate_source_diversity(relevant_articles),
            'recency_factor': self._calculate_avg_recency(relevant_articles)
        }
        
        # Weighted confidence score
        confidence = (
            factors['article_count'] * 0.3 +
            factors['avg_relevance'] * 0.4 +
            factors['source_diversity'] * 0.2 +
            factors['recency_factor'] * 0.1
        )
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _calculate_source_diversity(self, articles):
        """Calculate diversity of sources"""
        sources = set()
        for article in articles:
            source_name = article.get('source', {}).get('name', '')
            if source_name:
                sources.add(source_name)
        
        # More diverse sources = higher confidence
        return min(len(sources) / 5, 1.0)  # Normalize to 0-1
    
    def _calculate_avg_recency(self, articles):
        """Calculate average recency factor"""
        recency_scores = []
        for article in articles:
            recency_scores.append(self._calculate_recency_bonus(article))
        
        return np.mean(recency_scores) if recency_scores else 0.5
    

_news_service = None

def get_news_service():
    """Get singleton instance of NewsAPIService"""
    global _news_service
    if _news_service is None:
        _news_service = NewsAPIService()
    return _news_service

import numpy as np
from datetime import datetime

class ConfidenceAnalyzer:
    def __init__(self):
        pass
    
    def analyze_articles(self, articles, input_text):
        """Analyze articles and calculate confidence based on relevance"""
        
        if not articles:
            return 0.0, []
        
        # Filter and sort articles by relevance score
        relevant_articles = []
        for article in articles:
            relevance_score = article.get('relevance_score', 0)
            similarity_score = article.get('similarity_score', 0)
            
            # Create enhanced article info
            enhanced_article = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'score': relevance_score,
                'similarity': similarity_score
            }
            
            relevant_articles.append(enhanced_article)
        
        # Sort by relevance score
        relevant_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Calculate overall confidence
        if relevant_articles:
            # Base confidence on top articles
            top_articles = relevant_articles[:20]  # Consider top 20
            avg_score = np.mean([a.get('score', 0) for a in top_articles])
            
            # Adjust confidence based on number of relevant articles
            article_count_factor = min(len([a for a in top_articles if a.get('score', 0) > 0.5]) / 10, 1.0)
            
            # Calculate final confidence
            confidence = (avg_score * 0.7) + (article_count_factor * 0.3)
        else:
            confidence = 0.1
        
        return confidence, relevant_articles
    
    def get_final_prediction(self, confidence_score):
        """Get final prediction based on confidence score"""
        
        if confidence_score >= 0.7:
            return "True", confidence_score
        elif confidence_score >= 0.4:
            return "Likely False", confidence_score
        else:
            return "False", confidence_score

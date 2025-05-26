import streamlit as st
import requests
from config.settings import PERPLEXITY_API_KEY
import json
import time

class PerplexityService:
    def __init__(self):
        self.api_key = PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        # Debug: Check if API key is loaded
        if not self.api_key or self.api_key == "your_actual_perplexity_key_here":
            st.warning("⚠️ Perplexity API key not configured. Some features may be limited.")
            st.info("Get your API key from: https://perplexity.ai → Settings → API")
        else:
            st.success(f"✅ Perplexity API key configured: {self.api_key[:8]}...")
    
    def predict_news_credibility(self, input_text):
        """Use Perplexity sonar-pro to predict if news is true or fake"""
        if not self.api_key or self.api_key == "your_actual_perplexity_key_here":
            return "Not Available", "Perplexity API key not configured - analysis skipped"
        
        # Validate input
        if not input_text or not isinstance(input_text, str):
            return "Error", "Invalid input text provided"
        
        prompt = f"""
        Analyze the following news content for factual accuracy and credibility.
        Search the web for current information and cross-reference with reliable sources.
        
        Determine if this news is TRUE or FAKE based on:
        1. Factual accuracy of claims
        2. Source credibility
        3. Current events verification
        4. Logical consistency
        
        News content: "{input_text[:1000]}"
        
        Respond with only "TRUE" or "FAKE" followed by a brief 2-3 sentence explanation with citations.
        """
        
        try:
            response = self._make_api_call(
                prompt=prompt, 
                model="sonar-pro",
                max_tokens=200,
                temperature=0.1,
                search_domain_filter=['reuters.com', 'bbc.com', 'apnews.com', 'cnn.com', 'nytimes.com'],
                search_recency_filter='month'
            )
            
            if "TRUE" in response.upper():
                return "True", response
            elif "FAKE" in response.upper():
                return "Fake", response
            else:
                return "Uncertain", response
                
        except Exception as e:
            return "Error", f"Perplexity API error: {str(e)}"
    
    def generate_detailed_report(self, input_text, roberta_prediction, roberta_confidence,newsapi_confidence, final_prediction, top_articles):
        """Generate comprehensive analysis using sonar-deep-research"""
        
        if not self.api_key or self.api_key == "your_actual_perplexity_key_here":
            return "Perplexity API key not configured. Unable to generate detailed report."
        
        # Validate input
        if not input_text or not isinstance(input_text, str):
            return "Invalid input text provided for detailed analysis."
        
        prompt = self._create_deep_research_prompt(
            input_text, roberta_prediction, roberta_confidence,
            newsapi_confidence, final_prediction, top_articles
        )
        
        try:
            return self._make_api_call(
                prompt=prompt, 
                model="sonar-deep-research",
                max_tokens=4000,
                temperature=0.1,
                search_domain_filter=[
                    'reuters.com', 'bbc.com', 'apnews.com', 'cnn.com', 'nytimes.com',
                    'washingtonpost.com', 'theguardian.com', 'npr.org', 'pbs.org',
                    'factcheck.org', 'snopes.com', 'politifact.com'
                ],
                search_recency_filter='week'
            )
        except Exception as e:
            return f"Error generating detailed report: {str(e)}"
    
    def _make_api_call(self, prompt, model, max_tokens=1500, temperature=0.3,search_domain_filter=None, search_recency_filter=None):
        """Make API call to Perplexity with proper configuration"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert fact-checker and misinformation analyst. Provide accurate, well-sourced analysis based on current information from reliable sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "return_citations": True,
            "return_related_questions": False
        }
        
        # Add search filters if provided
        if search_domain_filter:
            payload["search_domain_filter"] = search_domain_filter
        
        if search_recency_filter:
            payload["search_recency_filter"] = search_recency_filter
        
        try:
            response = requests.post(
                self.base_url, 
                json=payload, 
                headers=headers, 
                timeout=60  # Longer timeout for deep research
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                
                # Add citations if available
                if 'citations' in data:
                    citations = data.get('citations', [])
                    if citations:
                        content += "\n\n**Sources:**\n"
                        for i, citation in enumerate(citations[:5], 1):
                            content += f"{i}. {citation.get('title', 'Source')} - {citation.get('url', '')}\n"
                
                return content
            else:
                return "No response generated from Perplexity API"
                
        except requests.exceptions.Timeout:
            raise Exception("Request timed out - this is normal for deep research queries")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _create_deep_research_prompt(self, input_text, roberta_prediction, roberta_confidence,newsapi_confidence, final_prediction, top_articles):
        """Create comprehensive prompt for deep research analysis"""
        
        # Summarize top articles
        articles_summary = ""
        if top_articles:
            articles_summary = "\n".join([
                f"- {article.get('source', 'Unknown')}: {article.get('title', 'No title')[:100]}... (Credibility: {article.get('score', 0):.2f})"
                for article in top_articles[:5]
            ])
        else:
            articles_summary = "No related articles found in initial analysis"
        
        prompt = f"""
        Conduct a comprehensive fact-checking and credibility analysis for the following news content.
        Use your web search capabilities to gather current, authoritative information from multiple reliable sources.

        **NEWS CONTENT TO ANALYZE:**
        "{input_text[:1000]}"

        **INITIAL AI ANALYSIS RESULTS:**
        - RoBERTa Model Prediction: {roberta_prediction} (Confidence: {roberta_confidence:.2f})
        - News Correlation Confidence: {newsapi_confidence:.2f}
        - System Prediction: {final_prediction}

        **RELATED ARTICLES FROM INITIAL SEARCH:**
        {articles_summary}

        **REQUIRED COMPREHENSIVE ANALYSIS:**

        ## 1. FACTUAL VERIFICATION
        - Verify each specific claim made in the content
        - Cross-reference with multiple authoritative sources
        - Identify any false, misleading, or unsubstantiated information
        - Check for context manipulation or selective reporting

        ## 2. SOURCE CREDIBILITY ASSESSMENT
        - Evaluate the reliability of any sources mentioned
        - Check for bias, conflicts of interest, or agenda
        - Assess the expertise and authority of quoted individuals
        - Verify institutional affiliations and credentials

        ## 3. TEMPORAL AND CONTEXTUAL ANALYSIS
        - Verify dates, timelines, and sequence of events
        - Check if information is current or outdated
        - Assess whether context has been properly preserved
        - Identify any anachronisms or timeline inconsistencies

        ## 4. CORROBORATION AND CONSENSUS
        - Find independent verification from multiple sources
        - Check scientific or expert consensus where applicable
        - Identify any contradictory evidence
        - Assess the weight of evidence for and against claims

        ## 5. MISINFORMATION PATTERNS
        - Look for common misinformation tactics
        - Check for emotional manipulation or sensationalism
        - Identify logical fallacies or reasoning errors
        - Assess whether claims are extraordinary without extraordinary evidence

        ## 6. FINAL CREDIBILITY ASSESSMENT
        - Provide an overall credibility rating (1-10 scale)
        - Summarize key evidence supporting or refuting the content
        - Identify the most reliable sources found
        - Give specific recommendations for readers

        **Please provide a detailed, well-sourced analysis with proper citations from your web search.**
        """
        
        return prompt
    
    def get_service_status(self):
        """Check Perplexity API service status"""
        if not self.api_key or self.api_key == "your_actual_perplexity_key_here":
            return {"status": "error", "message": "API key not configured"}
        
        try:
            # Simple test request
            test_prompt = "Test API connection"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.base_url, 
                json=payload, 
                headers=headers, 
                timeout=10
            )
            
            return {
                "status": "ok" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "message": "Service available" if response.status_code == 200 else "Service unavailable"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

@st.cache_resource
def get_perplexity_service():
    return PerplexityService()

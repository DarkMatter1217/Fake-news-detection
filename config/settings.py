import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys - loaded from .env file
NEWS_API_KEY = "5857f31b267648b88056c8dc2663c998"
PERPLEXITY_API_KEY = "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"

# Debug: Print to check if keys are loaded (remove after testing)
print(f"NEWS_API_KEY loaded: {'Yes' if NEWS_API_KEY else 'No'}")
print(f"PERPLEXITY_API_KEY loaded: {'Yes' if PERPLEXITY_API_KEY else 'No'}")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fake_news_app.db")

# Model Configuration
ROBERTA_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
CONFIDENCE_THRESHOLD_HIGH = 0.75
CONFIDENCE_THRESHOLD_LOW = 0.50

# News API Configuration
NEWS_API_BASE_URL = "https://newsapi.org/v2"
MAX_ARTICLES = 1000

# Top 100 Trusted Global News Sources
TRUSTED_GLOBAL_SOURCES = [
    # Global Wire Services & International
    "reuters", "associated press", "ap", "bbc", "al jazeera", "france 24", 
    "voice of america", "deutsche welle", "dw news", "euronews",
    
    # Major US Sources
    "new york times", "washington post", "cnn", "nbc news", "cbs news", 
    "abc news", "npr", "pbs", "fox news", "wall street journal", "usa today",
    "bloomberg", "forbes", "business insider", "cnbc", "time", "newsweek",
    "the atlantic", "the hill", "daily beast", "u.s. news", "huffpost",
    "los angeles times", "new york post", "houston chronicle", "sfgate",
    "politico", "axios", "vox", "buzzfeed news", "vice news", "propublica",
    
    # UK Sources
    "the guardian", "daily mail", "the sun", "mirror", "telegraph", 
    "the independent", "sky news", "financial times", "evening standard",
    
    # Canadian Sources
    "globe and mail", "toronto star", "cbc news", "national post", "ctv news",
    
    # European Sources
    "le monde", "der spiegel", "corriere della sera", "el país", "la repubblica",
    "süddeutsche zeitung", "the irish times", "de volkskrant", "aftonbladet",
    "liberation", "el mundo", "la stampa", "público", "diário de notícias",
    
    # Asian Sources
    "south china morning post", "japan times", "straits times", "bangkok post",
    "jakarta post", "times of india", "hindustan times", "the hindu",
    "indian express", "dawn", "daily star", "china daily", "korea herald",
    "nikkei", "asahi shimbun", "mainichi", "yomiuri shimbun",
    
    # Middle Eastern Sources
    "haaretz", "saudi gazette", "al arabiya", "the national", "gulf news",
    "jordan times", "daily sabah", "tehran times",
    
    # African Sources
    "daily sun", "vanguard", "the herald", "mail & guardian", "news24",
    "daily nation", "the citizen", "cape times",
    
    # Latin American Sources
    "folha de s.paulo", "clarín", "el universal", "la nación", "o globo",
    "reforma", "excélsior", "el tiempo", "el comercio", "la tercera",
    
    # Australian/Oceanian Sources
    "news.com.au", "new zealand herald", "sydney morning herald", "the age",
    "australian financial review", "stuff.co.nz",
    
    # Digital-First Global Sources
    "yahoo news", "google news", "msn news", "the intercept",
    
    # Specialized Sources
    "factcheck.org", "snopes", "politifact", "the diplomat", "foreign affairs",
    "foreign policy", "nature", "science", "new scientist", "scientific american",
    "the lancet", "nejm", "ieee spectrum"
]

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "fake_news_detector_secret_key")

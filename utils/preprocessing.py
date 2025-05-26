import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
import unicodedata

# Download required NLTK data
def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Initialize NLTK data
download_nltk_data()

class TextPreprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Add custom stop words for news analysis
        self.stop_words.update([
            'said', 'says', 'according', 'reported', 'report', 'reports',
            'news', 'article', 'story', 'breaking', 'update', 'latest'
        ])
    
    def preprocess_text(self, text, level='basic'):
        """
        Preprocess text for model input
        
        Args:
            text: Input text to preprocess
            level: 'basic', 'moderate', or 'advanced'
        """
        # Handle None or empty input
        if not text or not isinstance(text, str):
            return ""
        
        # Basic preprocessing
        text = self._basic_cleaning(text)
        
        if level in ['moderate', 'advanced']:
            text = self._moderate_cleaning(text)
        
        if level == 'advanced':
            text = self._advanced_cleaning(text)
        
        return text.strip() if text else ""
    
    def _basic_cleaning(self, text):
        """Basic text cleaning"""
        if not text or not isinstance(text, str):
            return ""
            
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip() if text else ""
    
    def _moderate_cleaning(self, text):
        """Moderate text cleaning"""
        if not text or not isinstance(text, str):
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\'"()-]', '', text)
        
        # Fix common encoding issues
        text = text.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        # Remove repeated punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        return text.strip() if text else ""
    
    def _advanced_cleaning(self, text):
        """Advanced text cleaning"""
        if not text or not isinstance(text, str):
            return ""
            
        # Remove stop words while preserving sentence structure
        try:
            sentences = sent_tokenize(text)
            cleaned_sentences = []
            
            for sentence in sentences:
                if not sentence or not isinstance(sentence, str):
                    continue
                    
                words = word_tokenize(sentence)
                # Keep important words and structure
                filtered_words = [
                    word for word in words 
                    if word.lower() not in self.stop_words or len(word) <= 2
                ]
                
                if filtered_words:  # Only add non-empty sentences
                    cleaned_sentences.append(' '.join(filtered_words))
            
            return '. '.join(cleaned_sentences)
        except Exception:
            return text.strip() if text else ""
    
    def extract_keywords(self, text, max_keywords=10, min_length=3):
        """Extract key phrases from text"""
        if not text or not isinstance(text, str):
            return []
        
        try:
            # Tokenize and clean
            words = word_tokenize(text.lower())
            
            # Filter words
            keywords = [
                word for word in words 
                if (word.isalpha() and 
                    len(word) >= min_length and 
                    word not in self.stop_words)
            ]
            
            # Count frequency
            from collections import Counter
            word_freq = Counter(keywords)
            
            # Return most frequent words
            return [word for word, freq in word_freq.most_common(max_keywords)]
        except Exception:
            return []

# Global preprocessing function for backward compatibility
def preprocess_text(text, level='basic'):
    """Global preprocessing function"""
    # Handle None or empty input
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove user mentions and hashtags
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text.strip() if text else ""

def extract_keywords(text, max_keywords=10):
    """Global keyword extraction function"""
    if not text or not isinstance(text, str):
        return []
        
    preprocessor = TextPreprocessor()
    return preprocessor.extract_keywords(text, max_keywords)

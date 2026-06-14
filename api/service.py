import joblib
import os
import nltk
import requests
from bs4 import BeautifulSoup
from newspaper import Article

# Pre-emptive safety check for tokenizers
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Absolute paths validation setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'model', 'fake_news_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'model', 'tfidf_vectorizer.pkl')

# Load weights
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def extract_text_from_url(url: str) -> str:
    """Extracts clean text from a news URL with a resilient BeautifulSoup fallback."""
    # Engine A: Try specialized Newspaper3k extraction
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text.strip():
            return article.text
    except Exception:
        pass 

    # Engine B: Advanced HTML parsing fallback
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 20]
            text_content = " ".join(paragraphs)
            
            if text_content.strip():
                return text_content
                
        raise ValueError(f"Target URL returned a non-200 status code: {response.status_code}")
    except Exception as e:
        raise ValueError(f"Resilient Extraction Failure: {str(e)}")

def get_prediction(text: str):
    """Computes NLP inference metrics on raw input string data streams."""
    cleaned_input = [text.lower()]
    vectorized = vectorizer.transform(cleaned_input)
    
    prediction = model.predict(vectorized)[0]
    probabilities = model.predict_proba(vectorized)
    confidence = probabilities[0][prediction] * 100
    
    return {
        "is_fake": bool(prediction == 0),
        "confidence": round(confidence, 2)
    }
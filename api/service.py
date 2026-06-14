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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'model', 'fake_news_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'model', 'tfidf_vectorizer.pkl')

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
        pass # Move to Engine B if blocked by cloud sandbox file write paths

    # Engine B: Pure HTML stream parsing fallback (Highly resilient to cloud sandboxes)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Strip out clutter elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Extract paragraphs from the main content body
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            text_content = " ".join(paragraphs)
            
            if text_content.strip():
                return text_content
                
        raise ValueError("Target URL returned empty content streams.")
    except Exception as e:
        raise ValueError(f"Resilient Extraction Failure: {str(e)}")

def get_prediction(text):
    cleaned_input = [text.lower()]
    vectorized = vectorizer.transform(cleaned_input)
    
    prediction = model.predict(vectorized)[0]
    probabilities = model.predict_proba(vectorized)
    confidence = probabilities[0][prediction] * 100
    
    return {
        "is_fake": bool(prediction == 0),
        "confidence": round(confidence, 2)
    }